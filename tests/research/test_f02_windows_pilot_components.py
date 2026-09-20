from __future__ import annotations

import http.client
import http.server
import json
import socket
import threading
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.research.f02_loopback import OneShotLoopbackFaultProxy, ProxyConfigurationError
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.f02_preflight import run_preflight


class _Upstream:
    def __init__(self) -> None:
        self.prompt_bodies: list[bytes] = []
        self._server: http.server.ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def url(self) -> str:
        assert self._server is not None
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def __enter__(self) -> "_Upstream":
        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, _format: str, *_args: object) -> None:
                return

            def do_GET(self) -> None:  # noqa: N802
                body = b'{"system":{"comfyui_version":"v0.30.0"}}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                owner.prompt_bodies.append(body)
                response = json.dumps({"prompt_id": f"server-{len(owner.prompt_bodies)}"}, separators=(",", ":")).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        assert self._server is not None and self._thread is not None
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


def _post(url: str, body: bytes) -> tuple[int, bytes]:
    parts = url.removeprefix("http://").split(":", 1)
    connection = http.client.HTTPConnection(parts[0], int(parts[1]), timeout=3)
    try:
        connection.request("POST", "/prompt", body=body, headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


class LoopbackFaultProxyTests(unittest.TestCase):
    def test_f00_preserves_prompt_body_and_response(self) -> None:
        payload = b'{"prompt":{"4":{"inputs":{"text":"red cup"}}}}'
        with _Upstream() as upstream, OneShotLoopbackFaultProxy(upstream.url, fault_mode="F00") as proxy:
            status, response = _post(proxy.base_url, payload)
            self.assertEqual(status, 200)
            self.assertEqual(response, b'{"prompt_id":"server-1"}')
            self.assertEqual(upstream.prompt_bodies, [payload])
            receipt = proxy.receipts[0]
            self.assertFalse(receipt.response_dropped)
            self.assertEqual(receipt.body_sha256, __import__("hashlib").sha256(payload).hexdigest())

    def test_f02_drops_only_the_first_accepted_response(self) -> None:
        payload = b'{"prompt":{"4":{"inputs":{"text":"red cup"}}}}'
        with _Upstream() as upstream, OneShotLoopbackFaultProxy(upstream.url, fault_mode="F02") as proxy:
            with self.assertRaises((http.client.RemoteDisconnected, ConnectionResetError, OSError)):
                _post(proxy.base_url, payload)
            status, response = _post(proxy.base_url, payload)
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(response)["prompt_id"], "server-2")
            self.assertEqual(upstream.prompt_bodies, [payload, payload])
            self.assertEqual(proxy.hidden_job_id, "server-1")
            self.assertEqual([item.response_dropped for item in proxy.receipts], [True, False])

    def test_proxy_rejects_non_loopback_upstream(self) -> None:
        with self.assertRaises(ProxyConfigurationError):
            OneShotLoopbackFaultProxy("http://192.0.2.1:8202", fault_mode="F00")


class EventOracleTests(unittest.TestCase):
    def test_backend_events_plus_completed_history_are_evaluable(self) -> None:
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="pid:1", observer_id="observer")
        oracle._record_payload(json.dumps({"type": "execution_start", "data": {"prompt_id": "job-1"}}).encode())
        oracle._record_payload(json.dumps({"type": "executing", "data": {"prompt_id": "job-1", "node": None}}).encode())
        with patch.object(oracle, "_history", return_value={"job-1": {"status": {"status_str": "success"}, "outputs": {"9": {"images": [{"filename": "one.png"}]}}}}):
            decision = oracle._decision({"job-1"})
        self.assertTrue(decision.oracle_evaluable)
        self.assertEqual(len(decision.bindings), 1)
        self.assertEqual(decision.bindings[0].prompt_id, "job-1")
        self.assertTrue(decision.bindings[0].execution_instance_id.startswith("execution:"))

    def test_history_without_backend_start_is_not_evaluable(self) -> None:
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="pid:1", observer_id="observer")
        with patch.object(oracle, "_history", return_value={"job-1": {"status": {"status_str": "success"}}}):
            decision = oracle._decision({"job-1"})
        self.assertFalse(decision.oracle_evaluable)
        self.assertIn("missing_execution_start:job-1", decision.reason)


class PreflightReservationTests(unittest.TestCase):
    def test_expired_reservation_fails_before_hardware_or_backend_queries(self) -> None:
        config = {
            "ledger": {"root": "unused", "anchor": "unused"},
            "environment": {
                "host_id": "LAPTOP-7QD7KR9F", "gpu_uuid": "GPU-test", "gpu_model": "test",
                "model_path": "unused", "model_sha256": "unused", "backend_url": "http://127.0.0.1:8202",
                "comfy_version": "v0.30.0", "comfy_sha": "unused", "comfy_root": "unused",
            },
            "clients": {
                "B2": {"root": "unused", "sha": "da65d57047b5a59e3403b49adf4605a1c0497c58"},
                "W3": {"root": "unused", "sha": "d45173af75d404ad79dc14568edd4c45f654abd2"},
            },
            "fresh_output_roots": {"B2": "unused-b2", "W3": "unused-w3"},
            "reservation": {"owner": "Capricorn", "start": "2026-09-17T03:52:22Z", "end": "2026-09-17T04:22:22Z", "hard_timeout_seconds": 900},
        }
        report = run_preflight(config, now=datetime(2026, 9, 19, tzinfo=timezone.utc))
        self.assertEqual(report.status, "FAIL")
        self.assertEqual([check.name for check in report.checks], ["reservation"])
        self.assertIn("active=False", report.checks[0].summary)

    def test_active_reservation_with_wrong_frozen_identity_stops_before_hardware(self) -> None:
        config = {
            "ledger": {"root": "unused", "anchor": "wrong"},
            "environment": {
                "host_id": "LAPTOP-7QD7KR9F", "gpu_uuid": "GPU-wrong", "gpu_model": "wrong",
                "model_path": "unused\\wrong.safetensors", "model_sha256": "wrong", "backend_url": "http://127.0.0.1:8202",
                "comfy_version": "v0.30.0", "comfy_sha": "wrong", "comfy_root": "unused",
            },
            "clients": {
                "B2": {"root": "unused", "sha": "da65d57047b5a59e3403b49adf4605a1c0497c58"},
                "W3": {"root": "unused", "sha": "d45173af75d404ad79dc14568edd4c45f654abd2"},
            },
            "fresh_output_roots": {
                "B2_F00": "unused-b2-f00", "W3_F00": "unused-w3-f00",
                "B2_F02": "unused-b2-f02", "W3_F02": "unused-w3-f02",
            },
            "reservation": {
                "owner": "Capricorn", "start": "2026-09-17T03:52:22Z", "end": "2026-09-17T04:22:22Z",
                "hard_timeout_seconds": 900, "scope": "exactly four reviewed F00/F02 single-stage cases",
                "no_concurrent_gpu_work": True,
            },
        }
        with patch("scripts.research.f02_preflight._contract_check", side_effect=AssertionError("must not query")), \
             patch("scripts.research.f02_preflight._gpu_check", side_effect=AssertionError("must not query")), \
             patch("scripts.research.f02_preflight._backend_check", side_effect=AssertionError("must not query")):
            report = run_preflight(config, now=datetime(2026, 9, 17, 4, 0, tzinfo=timezone.utc))
        self.assertEqual(report.status, "FAIL")
        self.assertEqual([check.name for check in report.checks], ["reservation", "frozen_identity_config"])
        self.assertIn("ledger_anchor", report.checks[1].summary)


if __name__ == "__main__":
    unittest.main()
