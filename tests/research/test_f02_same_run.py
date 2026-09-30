"""CPU preflight for same-run capture; no model, GPU or live ComfyUI."""

from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from scripts.research import f02_product_client as client
from scripts.research.f02_capture import write_private_json
from scripts.research.f02_campaign import CampaignConfigurationError, ProductCallOutcome, run_campaign
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.f02_preflight import PreflightReport
from scripts.research.f02_same_run_campaign import PROTOCOL, run_same_run_campaign
from scripts.research import run_paired_fault_matrix as paired
from tests.research.test_f02_campaign_controller import _FakeProxy, _FakeOracle


class _CapturedOracle(_FakeOracle):
    def __init__(self, *args, retain_raw_transport=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.retained = retain_raw_transport

    def private_capture(self):
        return {"retained": self.retained, "websocket_messages": [], "history_responses": []}


class SameRunControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _FakeProxy.created.clear()
        _FakeOracle.non_evaluable_cases.clear()
        self.calls = []
        self.frozen = dict(zip(("canonical_request_digest", "compiled_prompt_digest", "workflow_graph_digest",
                               "input_digest", "route_identity", "validator_version"),
                              ("a" * 64, "b" * 64, "c" * 64, "d" * 64, "private-route-identity", "validator")))

    def config(self):
        roots = {c: str(self.root / c) for c in ("B2_F00", "W3_F00", "B2_F02", "W3_F02")}
        now = datetime.now(timezone.utc)
        return {"preflight": {"environment": {"backend_url": "http://127.0.0.1:8202", "model_path": "fixture"},
                 "reservation": {"owner": "CPU fixture only", "start": (now - timedelta(minutes=1)).isoformat(),
                                 "end": (now + timedelta(minutes=30)).isoformat(), "hard_timeout_seconds": 900},
                 "clients": {"B2": {"root": "b2", "sha": "da65d57047b5a59e3403b49adf4605a1c0497c58"},
                             "W3": {"root": "w3", "sha": "d45173af75d404ad79dc14568edd4c45f654abd2"}},
                 "fresh_output_roots": roots},
                "campaign": {"protocol_version": PROTOCOL, "same_run_capture_root": str(self.root / "private"),
                 "observer_window_seconds": 180, "case_hard_timeout_seconds": 900,
                 "evidence_file": str(self.root / "public.json"), "frozen_request": self.frozen,
                 "client_commands": {"B2": ["unused"], "W3": ["fixture"]}, "output_roots": roots,
                 "operation_keys": {c: f"op-{c}" for c in roots}}}

    @staticmethod
    def preflight(_):
        return PreflightReport("PASS", datetime.now(timezone.utc).isoformat(), "private-boot", ())

    def invoke(self, *, unknown=True, extra_post=False, wrong_run=False,
               guard_code="submission_outcome_unknown", capture_error=False):
        def call(spec, index, _url, _timeout):
            self.calls.append((spec.case_id, index))
            root = Path(spec.private_capture_root)
            root.mkdir(exist_ok=True)
            run_id = f"private-run-{spec.case_id}"
            arguments = {"run_id": run_id, "seed": 4101, "idempotency_key": spec.operation_key}
            request = {"route": "fixture"}
            unresolved = spec.fault_mode == "F02" and unknown
            manifest = {"run_id": run_id, "state": "unresolved" if unresolved else "generated",
                        "request": request, "attempts": [{"status": "unresolved", "submission_outcome": "unknown",
                                      "idempotency_key": spec.operation_key, "backend_job": None}] if unresolved else []}
            if index == 1:
                write_private_json(root, "session.json", {"schema": "f02-same-run-session-v1",
                                                         "run_id": run_id, "generate_arguments": arguments,
                                                         "generate_arguments_sha256": client._digest(arguments),
                                                         "request_sha256": client._digest(request)})
            result = {**self.frozen, "operation_key": spec.operation_key, "retry_scope": "same_run",
                      "artifact_hashes": [], "reported_state": "unresolved" if unresolved else "resolved",
                      "run_id_sha256": sha256(run_id.encode()).hexdigest(),
                      "generate_arguments_sha256": client._digest(arguments)}
            for phase in ("before", "after"):
                result[f"manifest_{phase}_sha256"] = write_private_json(root, f"call-{index}-{phase}.json", manifest)
            if index == 1 or extra_post:
                _FakeProxy.active.add_prompt(dropped=spec.fault_mode == "F02" and index == 1)
            if index == 2:
                result.update(client_error_code=guard_code, client_error_stage="generate_round")
                if wrong_run:
                    result["run_id_sha256"] = "0" * 64
            if capture_error:
                result["capture_error_code"] = "server_eof"
            return ProductCallOutcome(0, False, result["reported_state"], result, "0" * 64, "1" * 64, None)
        return call

    def run_gate(self, **options):
        return run_same_run_campaign(self.config(), preflight_runner=self.preflight,
                                    product_invoker=self.invoke(**options), proxy_factory=_FakeProxy,
                                    oracle_factory=_CapturedOracle)

    def test_same_run_block_requires_manifest_guard_code_and_zero_extra_post(self):
        report = self.run_gate()
        self.assertEqual(report["status"], "COMPLETED")
        self.assertEqual(self.calls, [("W3_F00", 1), ("W3_F02", 1), ("W3_F02", 2)])
        case = report["records"][-1]
        self.assertTrue(case["submission_guard_observed"])
        self.assertEqual(case["proxy_prompt_count"], 1)
        self.assertEqual(case["unique_execution_start_count"], 1)
        public = json.dumps(report)
        self.assertNotIn("private-run", public)
        self.assertNotIn("private-boot", public)
        self.assertNotIn("private-route-identity", public)
        self.assertNotIn(str(self.root), public)
        self.assertTrue((self.root / "private/W3_F02/oracle-snapshot-1.json").is_file())

    def test_non_unknown_original_manifest_stops_before_second_call(self):
        report = self.run_gate(unknown=False)
        self.assertEqual(report["status"], "STOPPED")
        self.assertNotIn(("W3_F02", 2), self.calls)

    def test_extra_submission_is_not_guard_evidence(self):
        report = self.run_gate(extra_post=True)
        self.assertFalse(report["records"][-1]["submission_guard_observed"])
        self.assertEqual(report["records"][-1]["stop_reason"], "second_call_created_submission")

    def test_changed_run_identity_is_not_guard_evidence(self):
        report = self.run_gate(wrong_run=True)
        self.assertFalse(report["records"][-1]["submission_guard_observed"])
        self.assertEqual(report["status"], "STOPPED")

    def test_other_error_with_zero_post_is_not_guard_evidence(self):
        report = self.run_gate(guard_code="server_eof")
        self.assertFalse(report["records"][-1]["submission_guard_observed"])
        self.assertEqual(report["records"][-1]["stop_reason"], "guard_rejection_not_observed")

    def test_missing_manifest_capture_stops_before_second_call(self):
        report = self.run_gate(capture_error=True)
        self.assertEqual(report["status"], "STOPPED")
        self.assertNotIn(("W3_F02", 2), self.calls)

    def test_failed_control_stops_before_fault_case(self):
        _FakeOracle.non_evaluable_cases.add("W3_F00")
        report = self.run_gate()
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(self.calls, [("W3_F00", 1)])

    def test_preflight_failure_creates_no_capture_or_product_call(self):
        report = run_same_run_campaign(self.config(),
            preflight_runner=lambda _: PreflightReport("FAIL", "fixture", None, ()),
            product_invoker=self.invoke(), proxy_factory=_FakeProxy, oracle_factory=_CapturedOracle)
        self.assertEqual(report["status"], "PRECHECK_FAILED")
        self.assertEqual(self.calls, [])
        self.assertFalse((self.root / "private").exists())
        self.assertFalse((self.root / "public.json").exists())

    def test_same_run_config_cannot_silently_use_fresh_run_controller(self):
        with self.assertRaises(CampaignConfigurationError), patch("scripts.research.f02_campaign.run_preflight") as preflight:
            run_campaign(self.config(), product_invoker=self.invoke())
        preflight.assert_not_called()
        self.assertEqual(self.calls, [])

    def test_reservation_expired_after_preflight_stops_before_capture(self):
        config = self.config()
        config["preflight"]["reservation"]["end"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        report = run_same_run_campaign(config, preflight_runner=self.preflight,
                                      product_invoker=self.invoke(), proxy_factory=_FakeProxy,
                                      oracle_factory=_CapturedOracle)
        self.assertEqual(report["status"], "PRECHECK_FAILED")
        self.assertEqual(self.calls, [])
        self.assertFalse((self.root / "private").exists())

    def test_unbindable_first_execution_stops_second_call(self):
        _FakeOracle.non_evaluable_cases.add("W3_F02")
        report = self.run_gate()
        self.assertEqual(report["status"], "STOPPED")
        self.assertNotIn(("W3_F02", 2), self.calls)


class SameRunEngineIntegrationTests(unittest.TestCase):
    def test_captured_retry_exercises_real_product_guard_with_one_cpu_submission(self):
        fixture = paired.AssetRunEngineTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        generated_arguments, started_runs = [], []
        owner = self

        class EngineClient:
            def __init__(self, _root, _env):
                pass

            def call(self, name, arguments):
                try:
                    if name == "local_gpu_start_run":
                        started = fixture.start(max_rounds=1)
                        started_runs.append(started["run_id"])
                        return started
                    if name == "local_gpu_get_run":
                        return fixture.engine.get_run(arguments)
                    if name == "local_gpu_generate_round":
                        generated_arguments.append(copy.deepcopy(arguments))
                        return fixture.engine.generate_round(arguments)
                    owner.fail(f"unexpected tool {name}")
                except paired.AssetEngineError as error:
                    raise client.ProductClientError(error.code) from error

            def close(self):
                pass

        oracle = paired.ExecutionOracle("same-run-preflight")
        with paired.PairedCpuBackend(oracle, "F02", "single-stage") as backend:
            fixture.engine.backend_runner = backend
            with tempfile.TemporaryDirectory() as folder:
                capture = Path(folder) / "capture"
                boundary = {"profile": "standalone-illustration", "model_choice": "fixture", "backend": "webui",
                            "authorization_scope": "private", "route_token": "fixture"}
                with patch.object(client, "StdioMcp", EngineClient), patch.object(client, "_initialise"), \
                     patch.object(client, "_discover_route", return_value={"boundary": boundary}), \
                     patch.object(client, "_build_plan", side_effect=lambda request, seed: fixture.plan(max_rounds=1, route=request["route"])):
                    kwargs = dict(case_id="W3_F02", operation_key="same-run-operation",
                                  output_root=str(fixture.output_root), capture_root=capture)
                    first = client.run_same_run(Path(folder), call_index=1, **kwargs)
                    with self.assertRaisesRegex(client.ProductClientError, "context_mismatch"), \
                         patch.object(client, "StdioMcp") as forbidden:
                        client.run_same_run(Path(folder), call_index=2,
                                            **{**kwargs, "output_root": "changed-output-root"})
                    forbidden.assert_not_called()
                    session_path = capture / "session.json"
                    original_session = session_path.read_bytes()
                    changed = json.loads(original_session)
                    changed["generate_arguments"]["seed"] += 1
                    changed["generate_arguments_sha256"] = client._digest(changed["generate_arguments"])
                    session_path.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaisesRegex(client.ProductClientError, "changed_since_first_call"), \
                         patch.object(client, "StdioMcp") as forbidden:
                        client.run_same_run(Path(folder), call_index=2, **kwargs)
                    forbidden.assert_not_called()
                    session_path.write_bytes(original_session)
                    second = client.run_same_run(Path(folder), call_index=2, **kwargs)
                    self.assertEqual(first["durable_submission_outcome"], "unknown")
                    self.assertEqual(second["client_error_code"], "submission_outcome_unknown")
                    self.assertEqual(second["client_error_stage"], "generate_round")
                    self.assertEqual(first["run_id_sha256"], second["run_id_sha256"])
                    self.assertEqual(generated_arguments[0], generated_arguments[1])
                    self.assertEqual(len(started_runs), 1)
                    self.assertEqual(len(backend._server.requests), 1)
                    self.assertEqual(oracle.snapshot()["execution_started"], 1)
                    self.assertEqual(second["durable_run_state"], "unresolved")
                    self.assertTrue((capture / "call-2-after.json").is_file())
                    with self.assertRaises(FileExistsError), patch.object(client, "StdioMcp") as process:
                        client.run_same_run(Path(folder), call_index=2, **kwargs)
                    process.assert_not_called()
                    with self.assertRaisesRegex(client.ProductClientError, "call_index_invalid"):
                        client.run_same_run(Path(folder), call_index=3, **kwargs)


class RawOracleCaptureTests(unittest.TestCase):
    def test_raw_history_response_can_be_replayed_and_hashed(self):
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="fixture",
                                   observer_id="fixture", retain_raw_transport=True)
        body = b'{"job-1":{"status":{"status_str":"success"},"outputs":{}}}'
        with patch("scripts.research.f02_oracle.http.client.HTTPConnection") as connection:
            response = connection.return_value.getresponse.return_value
            response.status = 200
            response.read.return_value = body
            history = oracle._history("job-1")
        raw = oracle.private_capture()["history_responses"][0]
        self.assertEqual(base64.b64decode(raw["body_base64"]), body)
        self.assertEqual(raw["body_sha256"], sha256(body).hexdigest())
        self.assertEqual(history, json.loads(body))

    def test_raw_text_payload_retains_terminal_discriminator_and_long_content(self):
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="fixture",
                                   observer_id="fixture", retain_raw_transport=True)
        payload = json.dumps({"type": "executing", "data": {"prompt_id": "job-1", "node": None,
                                                             "private": "x" * 600}}).encode()
        oracle._record_payload(payload)
        raw = oracle.private_capture()["websocket_messages"][0]
        self.assertEqual(base64.b64decode(raw["body_base64"]), payload)
        self.assertEqual(raw["body_sha256"], sha256(payload).hexdigest())
        self.assertIsNone(oracle.raw_events[0].node)
        self.assertNotEqual(oracle.raw_events[0].payload["private"], "x" * 600)

    def test_raw_capture_is_opt_in(self):
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="fixture", observer_id="fixture")
        oracle._record_payload(b'{"type":"status","data":{}}')
        self.assertEqual(oracle.private_capture()["websocket_messages"], [])
