"""Synthetic controller tests; no GPU, ComfyUI process, or network is used."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.research.f02_campaign import CaseSpec, ProductCallOutcome, _invoke_subprocess, run_campaign
from scripts.research.f02_loopback import ProxyReceipt
from scripts.research.f02_oracle import ExecutionBinding, OracleDecision
from scripts.research.f02_preflight import PreflightReport


class _FakeProxy:
    active: "_FakeProxy | None" = None
    created: list["_FakeProxy"] = []

    def __init__(self, _backend_url: str, *, fault_mode: str, timeout_seconds: float) -> None:
        self.fault_mode = fault_mode
        self.timeout_seconds = timeout_seconds
        self._receipts: list[ProxyReceipt] = []
        self.base_url = "http://127.0.0.1:39191"
        _FakeProxy.created.append(self)

    @property
    def receipts(self) -> tuple[ProxyReceipt, ...]:
        return tuple(self._receipts)

    def __enter__(self) -> "_FakeProxy":
        _FakeProxy.active = self
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        _FakeProxy.active = None

    def add_prompt(self, *, dropped: bool) -> None:
        sequence = len(self._receipts) + 1
        self._receipts.append(ProxyReceipt(
            sequence=sequence,
            received_at=float(sequence),
            method="POST",
            path="/prompt",
            body_sha256=sha256(f"request-{sequence}".encode()).hexdigest(),
            body_bytes=9,
            upstream_status=200,
            upstream_reason="OK",
            accepted_job_id=f"job-{sequence}",
            response_dropped=dropped,
            forwarded=True,
            failure=None,
        ))


class _FakeOracle:
    non_evaluable_cases: set[str] = set()

    def __init__(self, _backend_url: str, *, backend_boot_identity: str, observer_id: str, timeout_seconds: float) -> None:
        self.case_id = observer_id.split("-")[2]
        self.backend_boot_identity = backend_boot_identity
        self.timeout_seconds = timeout_seconds

    def connect(self) -> None:
        return

    def close(self) -> None:
        return

    def observe_until(self, prompt_ids: list[str], *, deadline_monotonic: float) -> OracleDecision:
        del deadline_monotonic
        if self.case_id in self.non_evaluable_cases:
            return OracleDecision("not_evaluable", "synthetic_missing_start", (), (), {})
        bindings = tuple(ExecutionBinding(
            prompt_id=prompt_id,
            execution_instance_id=f"execution:{self.case_id}:{prompt_id}",
            started_at=1.0,
            finished_at=2.0,
            terminal_event="executing",
            history_completed=True,
            artifact_paths=(),
        ) for prompt_id in prompt_ids)
        return OracleDecision("evaluable", "synthetic_complete", bindings, (), {})


class CampaignControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        _FakeProxy.created.clear()
        _FakeOracle.non_evaluable_cases.clear()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.frozen = {
            "canonical_request_digest": "a" * 64,
            "compiled_prompt_digest": "b" * 64,
            "workflow_graph_digest": "c" * 64,
            "input_digest": "d" * 64,
            "route_identity": "sdxl-txt2img",
            "validator_version": "pilot-v1",
        }

    def test_subprocess_receives_case_output_root_for_client_and_server(self) -> None:
        spec = CaseSpec(
            case_id="B2_F00",
            system="B2",
            fault_mode="F00",
            command=("fake-python", "fake-client.py"),
            working_directory="fake-client-root",
            research_model_path="fake-model.safetensors",
            output_root="fresh-output-root",
            operation_key="op-B2-F00",
        )
        completed = subprocess.CompletedProcess(
            args=list(spec.command),
            returncode=0,
            stdout='{"reported_state":"resolved"}',
            stderr="",
        )
        with patch("scripts.research.f02_campaign.subprocess.run", return_value=completed) as run:
            outcome = _invoke_subprocess(spec, 1, "http://127.0.0.1:39191", 900)

        self.assertEqual(outcome.reported_state, "resolved")
        child_env = run.call_args.kwargs["env"]
        self.assertEqual(child_env["LOCAL_GPU_IMAGEGEN_OUTPUT_ROOT"], spec.output_root)
        self.assertEqual(child_env["LOCAL_GPU_IMAGEGEN_OUTPUT_DIR"], spec.output_root)

    def _config(self) -> dict[str, object]:
        root = Path(self.temp.name)
        roots = {case_id: str(root / case_id) for case_id in ("B2_F00", "W3_F00", "B2_F02", "W3_F02")}
        return {
            "preflight": {
                "environment": {
                    "backend_url": "http://127.0.0.1:8202",
                    "model_path": "fake-model.safetensors",
                },
                "clients": {
                    "B2": {"root": "b2-root", "sha": "da65d57047b5a59e3403b49adf4605a1c0497c58"},
                    "W3": {"root": "w3-root", "sha": "d45173af75d404ad79dc14568edd4c45f654abd2"},
                },
                "fresh_output_roots": roots,
            },
            "campaign": {
                "observer_window_seconds": 180,
                "case_hard_timeout_seconds": 900,
                "evidence_file": str(root / "cases.jsonl"),
                "frozen_request": self.frozen,
                "client_commands": {"B2": ["fake-b2"], "W3": ["fake-w3"]},
                "output_roots": roots,
                "operation_keys": {case_id: f"op-{case_id}" for case_id in roots},
            },
        }

    @staticmethod
    def _preflight(_config: dict[str, object]) -> PreflightReport:
        return PreflightReport("PASS", datetime.now(timezone.utc).isoformat(), "boot-test", ())

    def _invoker(self, calls: list[tuple[str, int]], *, block_w3_second: bool = False) -> object:
        def invoke(spec: object, call_index: int, _proxy_url: str, _timeout: float) -> ProductCallOutcome:
            case_id = getattr(spec, "case_id")
            fault = getattr(spec, "fault_mode")
            operation_key = getattr(spec, "operation_key")
            calls.append((case_id, call_index))
            self.assertIsNotNone(_FakeProxy.active)
            blocked = block_w3_second and case_id == "W3_F02" and call_index == 2
            if not blocked:
                _FakeProxy.active.add_prompt(dropped=(fault == "F02" and call_index == 1))  # type: ignore[union-attr]
            result = dict(self.frozen)
            result.update({"operation_key": operation_key, "artifact_hashes": []})
            state = "failed" if fault == "F02" and call_index == 1 else "resolved"
            result["reported_state"] = state
            return ProductCallOutcome(0, False, state, result, "0" * 64, "1" * 64, None)
        return invoke

    def test_preflight_failure_does_not_create_evidence_or_invoke_product(self) -> None:
        calls: list[tuple[str, int]] = []
        evidence = Path(self.temp.name) / "cases.jsonl"

        def failed_preflight(_config: dict[str, object]) -> PreflightReport:
            return PreflightReport("FAIL", datetime.now(timezone.utc).isoformat(), None, ())

        report = run_campaign(
            self._config(), preflight_runner=failed_preflight, product_invoker=self._invoker(calls),
            proxy_factory=_FakeProxy, oracle_factory=_FakeOracle,
        )
        self.assertEqual(report.status, "PRECHECK_FAILED")
        self.assertEqual(calls, [])
        self.assertFalse(evidence.exists())
    def test_runs_fixed_order_with_only_two_f02_product_calls_each(self) -> None:
        calls: list[tuple[str, int]] = []
        report = run_campaign(
            self._config(), preflight_runner=self._preflight, product_invoker=self._invoker(calls),
            proxy_factory=_FakeProxy, oracle_factory=_FakeOracle,
        )
        self.assertEqual(report.status, "COMPLETED")
        self.assertEqual(calls, [("B2_F00", 1), ("W3_F00", 1), ("B2_F02", 1), ("B2_F02", 2), ("W3_F02", 1), ("W3_F02", 2)])
        self.assertEqual([record.product_call_count for record in report.records], [1, 1, 2, 2])
        self.assertTrue(all(record.request_matches_frozen for record in report.records))
        evidence_lines = (Path(self.temp.name) / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(evidence_lines), 4)
        self.assertNotIn('"job-', "\n".join(evidence_lines))

    def test_f00_not_evaluable_stops_all_f02_product_calls(self) -> None:
        _FakeOracle.non_evaluable_cases.add("B2_F00")
        calls: list[tuple[str, int]] = []
        report = run_campaign(
            self._config(), preflight_runner=self._preflight, product_invoker=self._invoker(calls),
            proxy_factory=_FakeProxy, oracle_factory=_FakeOracle,
        )
        self.assertEqual(report.status, "DOWNGRADED_SUBMISSION_ONLY")
        self.assertEqual(calls, [("B2_F00", 1), ("W3_F00", 1)])
        self.assertEqual([record.status for record in report.records[2:]], ["not_run", "not_run"])
        self.assertTrue(all(record.classifications["not_run"] == 1 for record in report.records[2:]))

    def test_locally_blocked_second_call_is_submission_only_not_execution_count(self) -> None:
        calls: list[tuple[str, int]] = []
        report = run_campaign(
            self._config(), preflight_runner=self._preflight,
            product_invoker=self._invoker(calls, block_w3_second=True),
            proxy_factory=_FakeProxy, oracle_factory=_FakeOracle,
        )
        self.assertEqual(report.status, "COMPLETED_SUBMISSION_ONLY")
        self.assertEqual(calls[-2:], [("W3_F02", 1), ("W3_F02", 2)])
        w3_f02 = report.records[-1]
        self.assertEqual(w3_f02.status, "submission_only")
        self.assertEqual(w3_f02.proxy_prompt_count, 1)
        self.assertEqual(w3_f02.unique_execution_start_count, 1)

    def test_non_evaluable_f02_first_call_never_gets_a_second_call(self) -> None:
        _FakeOracle.non_evaluable_cases.add("B2_F02")
        calls: list[tuple[str, int]] = []
        report = run_campaign(
            self._config(), preflight_runner=self._preflight, product_invoker=self._invoker(calls),
            proxy_factory=_FakeProxy, oracle_factory=_FakeOracle,
        )
        self.assertEqual(report.status, "DOWNGRADED_SUBMISSION_ONLY")
        self.assertIn(("B2_F02", 1), calls)
        self.assertNotIn(("B2_F02", 2), calls)
        self.assertEqual(report.records[2].status, "submission_only")
        self.assertEqual(report.records[2].classifications["oracle_evaluable"], 0)
        self.assertEqual(report.records[3].status, "not_run")
        self.assertNotIn(("W3_F02", 1), calls)


if __name__ == "__main__":
    unittest.main()
