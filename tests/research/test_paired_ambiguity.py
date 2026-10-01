"""New protocol checks: real loopback transport, admission, clocks and units."""
from __future__ import annotations

import copy
import http.client
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from scripts.research.f02_loopback import OneShotLoopbackFaultProxy
from scripts.research.paired_ambiguity import (
    caller_unknown, lifecycle_count, prompt_metrics, run_schedule, semantic_digest,
)
from tests.research.test_f02_windows_pilot_components import _Upstream, _post
from scripts.research.run_paired_fault_matrix import LocalhostJsonServer
from scripts.research.paired_ambiguity_operation import run_operation
from scripts.research.f02_capture import write_private_json
from scripts.research.f02_campaign import CaseSpec, ProductCallOutcome
from scripts.research.f02_product_client import _digest
from scripts.research.f02_oracle import ExecutionBinding, OracleDecision


class PairedProxyTests(unittest.TestCase):
    def test_fpre_records_complete_body_without_entering_forward_and_is_one_shot(self):
        with tempfile.TemporaryDirectory() as folder, _Upstream() as upstream:
            journal = Path(folder) / "stages.jsonl"
            with OneShotLoopbackFaultProxy(upstream.url, fault_mode="FPRE", stage_log_path=journal) as proxy:
                with patch.object(proxy, "_forward", wraps=proxy._forward) as forward:
                    with self.assertRaises((http.client.RemoteDisconnected, ConnectionResetError, OSError)):
                        _post(proxy.base_url, b'{"seed":4101}')
                    forward.assert_not_called()
                    self.assertEqual(upstream.prompt_bodies, [])
                    self.assertEqual(_post(proxy.base_url, b'{"seed":4101}')[0], 200)
                    self.assertEqual(forward.call_count, 1)
                first = [s["stage"] for s in proxy.stages if s["request_sequence"] == 1]
                self.assertEqual(first, ["body_received", "fault_injected_before_upstream", "connection_closed"])
                self.assertEqual(prompt_metrics(proxy.evidence(), proxy.stages), {"S_proxy": 2, "S_upstream": 1, "A": 1})
                expected = list(proxy.stages)
            self.assertEqual([json.loads(line) for line in journal.read_text().splitlines()], expected)
            with self.assertRaises(FileExistsError):
                OneShotLoopbackFaultProxy(upstream.url, fault_mode="F00", stage_log_path=journal).start()

    def test_post_send_response_loss_is_not_zero_upstream_send(self):
        with LocalhostJsonServer(lambda _: (None, True)) as upstream, \
             OneShotLoopbackFaultProxy(upstream.url, fault_mode="F00") as proxy:
            self.assertEqual(_post(proxy.base_url, b'{"seed":4101}')[0], 502)
            self.assertEqual(len(upstream.requests), 1)
            self.assertFalse(proxy.receipts[0].forwarded)
            stages = [s["stage"] for s in proxy.stages]
            self.assertIn("upstream_send_started", stages)
            self.assertIn("request_body_sent", stages)
            self.assertIn("upstream_failure", stages)
            self.assertEqual(prompt_metrics(proxy.evidence(), proxy.stages), {"S_proxy": 1, "S_upstream": 1, "A": 0})


class ScheduleAndUnitsTests(unittest.TestCase):
    def test_retry_is_one_second_after_return_without_observer_wait(self):
        now, entries = [10.0], []
        def invoke(index, remaining):
            entries.append((index, now[0], remaining))
            now[0] += 2
            return {"client_error_stage": "generate_round", "client_error_code": "backend_request_failed"}
        def sleep(duration):
            now[0] += duration
        calls, reason = run_schedule(invoke, fault="F02", strategy="B2", deadline=20,
                                     clock=lambda: now[0], sleep=sleep)
        self.assertEqual([e[:2] for e in entries], [(1, 10.0), (2, 13.0)])
        self.assertEqual(reason, "retried_same_run")
        self.assertEqual(len(calls), 2)

    def test_stop_uses_only_caller_visible_error(self):
        unknown = {"client_error_stage": "generate_round", "client_error_code": "backend_request_failed"}
        for strategy, fault, deadline, expected in (("P-stop", "F02", 10, "caller_stop_after_unknown"),
                ("B2", "FPRE", .5, "deadline_before_retry")):
            calls, reason = run_schedule(lambda *_: unknown, fault=fault, strategy=strategy,
                                        deadline=deadline, clock=lambda: 0, sleep=lambda _: None)
            self.assertEqual(len(calls), 1)
            self.assertEqual(reason, expected)
        self.assertFalse(caller_unknown({**unknown, "client_error_stage": "model_route"}))

    def test_other_rejection_cannot_be_guard_or_unknown(self):
        calls, reason = run_schedule(lambda *_: {"client_error_code": "model_identity_drifted"},
                                     fault="F02", strategy="W3", deadline=10, clock=lambda: 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(reason, "first_call_not_unknown")

    def test_semantic_digest_includes_seed_and_model_but_excludes_route_run_ids(self):
        value = {"run_id": "a", "idempotency_key": "a", "seed": 4101,
                 "plan": {"model_choice": "m", "route_token": "r", "parameters": {"steps": 30}}}
        changed = copy.deepcopy(value)
        changed.update(run_id="b", idempotency_key="b")
        changed["plan"]["route_token"] = "q"
        self.assertEqual(semantic_digest(value), semantic_digest(changed))
        changed["seed"] = 4102
        self.assertNotEqual(semantic_digest(value), semantic_digest(changed))
        changed = copy.deepcopy(value)
        changed["plan"]["model_choice"] = "other"
        self.assertNotEqual(semantic_digest(value), semantic_digest(changed))

    def test_cumulative_snapshots_are_not_summed_and_incomplete_binding_is_unknown(self):
        start = {"event": "execution_started", "job_id": "j", "execution_instance_id": "e"}
        end = {"event": "execution_finished", "execution_instance_id": "e"}
        received = {"event": "request_received", "job_id": "j"}
        full = {"events": [received, start, end]}
        self.assertEqual(lifecycle_count([full, full]), 1)
        self.assertIsNone(lifecycle_count([{"events": [received, start]}]))
        self.assertIsNone(lifecycle_count([{"events": [received]}]))
        self.assertEqual(lifecycle_count([{"events": []}]), 0)


class OperationControllerTests(unittest.TestCase):
    """Constructed controller records; the separate matrix covers real engines."""

    def exercise(self, system, *, confirm_fault=True):
        with tempfile.TemporaryDirectory() as folder:
            root, order = Path(folder), []
            args = {"run_id": "original-run", "idempotency_key": "fixed", "seed": 4101, "plan": {"seed": 4101}}
            request = {"seed": 4101}

            class Proxy:
                active = None
                def __init__(self, *_a, **_kw):
                    self.records, self.stages = [], []
                    self.base_url = "http://127.0.0.1:1"
                def __enter__(self):
                    Proxy.active = self
                    return self
                def __exit__(self, *_):
                    pass
                def evidence(self):
                    return self.records
                def prompt(self, index):
                    self.records.append({"request_sequence": index, "method": "POST", "path": "/prompt",
                                         "upstream_status": 200, "accepted_job_id": f"job-{index}"})
                    self.stages += [{"request_sequence": index, "method": "POST", "path": "/prompt", "stage": s}
                                    for s in (["body_received", "upstream_send_started", "accepted_response_suppressed"]
                                              if index == 1 and confirm_fault else ["body_received", "upstream_send_started"])]

            class Oracle:
                def __init__(self, *_a, **_kw):
                    pass
                def connect(self):
                    order.append("observer_connect")
                def close(self):
                    pass
                def private_capture(self):
                    return {"synthetic": True}
                def observe_until(self, jobs, **_kw):
                    order.append("observer_measure")
                    return OracleDecision("evaluable", "synthetic", tuple(ExecutionBinding(
                        prompt_id=j, execution_instance_id=j, started_at=1, finished_at=2,
                        terminal_event="executing", history_completed=True, artifact_paths=()) for j in jobs), (), {})

            def invoke(spec, index, _url, _remaining):
                order.append(f"call-{index}")
                capture = Path(spec.private_capture_root)
                capture.mkdir(exist_ok=True)
                if index == 1:
                    write_private_json(capture, "session.json", {"run_id": args["run_id"], "generate_arguments": args,
                                                               "request_sha256": _digest(request)})
                manifest = {"run_id": args["run_id"], "request": request,
                            "state": "generated" if system == "B2" and index == 2 else "unresolved"}
                result = {"generation_rpc_entered": True, "reported_state": "unresolved"}
                for phase in ("before", "after"):
                    result[f"manifest_{phase}_sha256"] = write_private_json(capture, f"call-{index}-{phase}.json", manifest)
                write_private_json(capture, f"call-{index}-generation-request.json", {"arguments": args})
                if index == 1 or system == "B2":
                    Proxy.active.prompt(index)
                if index == 1:
                    result.update(client_error_stage="generate_round", client_error_code="backend_request_failed")
                elif system == "W3":
                    result.update(client_error_stage="generate_round", client_error_code="submission_outcome_unknown")
                return ProductCallOutcome(0, False, "unresolved", result, "0" * 64, "0" * 64, None)

            spec = CaseSpec(f"{system}_F02", system, "F02", (), "unused", "unused", "unused", "fixed",
                            backend_url="http://127.0.0.1:1", retry_scope="paired_same_run",
                            private_capture_root=str(root / "client"))
            report = run_operation(spec, evidence_root=root / "observer", boot_identity="CPU-only",
                                   deadline=20, invoker=invoke, proxy_factory=Proxy, oracle_factory=Oracle,
                                   clock=lambda: 0, sleep=lambda _: order.append("retry_delay"))
            return report, order

    def test_b2_extra_post_is_recorded_not_rejected_as_w3_guard_failure(self):
        result, order = self.exercise("B2")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["metrics"], {"S_proxy": 2, "S_upstream": 2, "A": 2, "E_bound": 2})
        self.assertLess(order.index("call-2"), order.index("observer_measure"))

    def test_w3_guard_has_zero_additional_post_and_original_run_unresolved(self):
        result, order = self.exercise("W3")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["metrics"]["S_proxy"], 1)
        self.assertLess(order.index("call-2"), order.index("observer_measure"))

    def test_unconfirmed_injection_stops_before_retry_and_retains_first_call(self):
        result, order = self.exercise("B2", confirm_fault=False)
        self.assertEqual(result["status"], "STOPPED")
        self.assertNotIn("call-2", order)
        self.assertEqual(result["product_call_count"], 1)
        self.assertEqual(result["metrics"]["S_proxy"], 1)
        self.assertIsNone(result["metrics"]["E_bound"])


if __name__ == "__main__":
    unittest.main()
