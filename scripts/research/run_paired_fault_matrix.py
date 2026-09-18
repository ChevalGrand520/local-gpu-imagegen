"""Run the frozen deterministic B2/W3 CPU fault protocol."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import socket
import subprocess
import sys
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    _scripts_root = ROOT / "scripts"
    if str(_scripts_root) not in sys.path:
        sys.path.insert(0, str(_scripts_root))

from local_gpu_imagegen.backends.base import BoundedJsonClient  # noqa: E402
from local_gpu_imagegen.errors import AssetEngineError, StateError  # noqa: E402
from scripts.research.execution_oracle import ExecutionOracle, run_oracle_self_checks  # noqa: E402
import tests.test_asset_run_engine as asset_run_engine_module  # noqa: E402
from tests.test_asset_run_engine import (  # noqa: E402
    AssetRunEngineTests,
    FakeBackendRunner,
    TwoStageBackendRunner,
)


PROTOCOL_VERSION = "paired-ambiguous-submit-v1"
LEDGER_SHA = "d8ef0bccc84269b7d4a627adce5f6025a17ab024"
RESEARCH_MODEL_ID = "research-cpu-fake-model"
CASE_SPECS = (
    ("F00-single-stage", "F00", "single-stage"),
    ("F00-two-stage", "F00", "two-stage"),
    ("F02-single-stage", "F02", "single-stage"),
    ("F02-two-stage", "F02", "two-stage"),
    ("F03-single-stage", "F03", "single-stage"),
    ("F03-two-stage", "F03", "two-stage"),
)


PostHandler = Callable[[dict[str, object]], tuple[dict[str, object] | None, bool]]


class LocalhostJsonServer:
    """A localhost fixture that can drop a response after accepting a POST."""

    def __init__(self, post_handler: PostHandler) -> None:
        self.post_handler = post_handler
        self.requests: list[dict[str, object]] = []
        self.handler_errors: list[str] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length else b""
                try:
                    value = json.loads(body.decode("utf-8"))
                    if not isinstance(value, dict):
                        raise ValueError("request body must be an object")
                    owner.requests.append(copy.deepcopy(value))
                    response, disconnect = owner.post_handler(value)
                except Exception as error:
                    owner.handler_errors.append(f"{type(error).__name__}: {error}")
                    self.send_response(500)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if disconnect:
                    self.close_connection = True
                    try:
                        self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    self.connection.close()
                    return
                encoded = json.dumps(response, allow_nan=False, separators=(",", ":")).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, _format: str, *args: object) -> None:
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        host, port = self._server.server_address
        self.url = f"http://{host}:{port}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "LocalhostJsonServer":
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


class PairedCpuBackend:
    """Use the checked-out HTTP client and record worker-entry execution events."""

    def __init__(self, oracle: ExecutionOracle, fault_id: str, path_kind: str) -> None:
        self.oracle = oracle
        self.fault_id = fault_id
        self.path_kind = path_kind
        self.delegate = FakeBackendRunner() if path_kind == "single-stage" else TwoStageBackendRunner()
        self.calls: list[dict[str, object]] = []
        self.submitted_job_ids: list[str] = []
        self.worker_execution_entry_ids: list[str] = []
        self.recovery_calls = 0
        self.response_losses = 0
        self._request_counter = 0
        self._pending: dict[str, dict[str, object]] = {}
        self._results: dict[str, dict[str, object]] = {}
        self._artifact_bytes: dict[str, dict[Path, bytes]] = {}
        self._server = LocalhostJsonServer(self._handle_post)
        self._client: BoundedJsonClient | None = None

    def __enter__(self) -> "PairedCpuBackend":
        self._server.__enter__()
        self._client = BoundedJsonClient(self._server.url, timeout=5.0)
        return self

    def __exit__(self, *args: object) -> None:
        self._server.__exit__(*args)

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.calls.append(_copy_request(request))
        recovery_job_id = request.get("recovery_job_id")
        if isinstance(recovery_job_id, str):
            return self._recover(recovery_job_id)

        self._request_counter += 1
        token = f"request-{self._request_counter:04d}"
        self._pending[token] = request
        assert self._client is not None
        try:
            response = self._client.post_json("/submit", {"request_token": token})
        except AssetEngineError as error:
            if self.fault_id == "F02" and self._request_counter == 1:
                error.details = {
                    **error.details,
                    "barrier": "after_execution_before_job_id_response",
                }
            raise
        if self._server.handler_errors:
            raise AssertionError(self._server.handler_errors[-1])
        if not isinstance(response, dict):
            raise AssertionError("localhost backend response must be an object")
        job_id = response.get("job_id")
        result = response.get("result")
        if not isinstance(job_id, str) or not isinstance(result, dict):
            raise AssertionError("localhost backend response lacks job/result binding")
        operation_id = str(request["idempotency_key"])
        self.oracle.job_id_revealed(operation_id, job_id, operation_id)
        callback = request.get("backend_job_callback")
        if callable(callback):
            callback(job_id)
        if self.fault_id == "F03" and self._request_counter == 1:
            raise StateError(
                "comfyui_job_timed_out",
                "Synthetic completion response loss after the job ID became known.",
                {
                    "barrier": "after_job_id_known_before_completion_response",
                    "job_id": job_id,
                    "state": "completed",
                },
            )
        return copy.deepcopy(result)

    def _handle_post(self, value: dict[str, object]) -> tuple[dict[str, object] | None, bool]:
        token = value.get("request_token")
        if not isinstance(token, str) or token not in self._pending:
            raise AssertionError("unknown request token")
        request = self._pending.pop(token)
        operation_id = str(request["idempotency_key"])
        job_id = f"cpu-{self.path_kind}-{self.fault_id.lower()}-{len(self.submitted_job_ids) + 1:04d}"
        self.submitted_job_ids.append(job_id)
        self.oracle.request_received(operation_id, job_id, operation_id)
        self.oracle.queue_item_created(operation_id, job_id, operation_id)
        execution_id = self.oracle.execution_started(operation_id, job_id, operation_id)
        self.worker_execution_entry_ids.append(execution_id)
        try:
            result = self.delegate(request)
            result = _with_job_id(result, job_id)
            artifact_hash = _result_artifact_hash(result, self.path_kind)
        except Exception:
            self.oracle.execution_finished(execution_id, outcome="failed")
            raise
        self.oracle.execution_finished(execution_id, artifact_hash=artifact_hash)
        self._results[job_id] = copy.deepcopy(result)
        self._artifact_bytes[job_id] = _capture_artifacts(result)
        disconnect = self.fault_id == "F02" and len(self.submitted_job_ids) == 1
        if disconnect:
            self.response_losses += 1
        return {"job_id": job_id, "result": result}, disconnect

    def _recover(self, job_id: str) -> dict[str, object]:
        self.recovery_calls += 1
        if job_id not in self._results:
            raise AssertionError("recovery used an unknown job ID")
        for path, data in self._artifact_bytes[job_id].items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return copy.deepcopy(self._results[job_id])


def run_case(case_id: str, fault_id: str, path_kind: str) -> dict[str, object]:
    previous_model_id = asset_run_engine_module.TEST_MODEL_ID
    asset_run_engine_module.TEST_MODEL_ID = RESEARCH_MODEL_ID
    fixture = AssetRunEngineTests("runTest")
    fixture.setUp()
    try:
        oracle = ExecutionOracle(case_id)
        with PairedCpuBackend(oracle, fault_id, path_kind) as worker:
            fixture.engine.backend_runner = worker
            if path_kind == "single-stage":
                started = fixture.start(max_rounds=2)
                run_id = str(started["run_id"])
                request = fixture.generate_arguments(run_id, key=f"{case_id}-operation", max_rounds=2)
            else:
                started = fixture.engine.start_run(fixture.two_stage_start_arguments())
                run_id = str(started["run_id"])
                manifest = fixture.engine.get_run({"run_id": run_id})
                route = manifest["request"]["route"]
                assert isinstance(route, dict)
                request = {
                    "run_id": run_id,
                    "idempotency_key": f"{case_id}-operation",
                    "action": "initial",
                    "edit_mode": "txt2img",
                    "seed": 42,
                    "change_summary": "Paired deterministic CPU fault characterization.",
                    "plan": fixture.two_stage_plan(route),
                }

            first_error = _call_and_capture(fixture.engine.generate_round, request)
            first_manifest = fixture.engine.get_run({"run_id": run_id})
            second_error: dict[str, object] | None = None
            if fault_id in {"F02", "F03"}:
                second_error = _call_and_capture(fixture.engine.generate_round, request)
            final_manifest = fixture.engine.get_run({"run_id": run_id})
            oracle_state = oracle.snapshot()
            injection_confirmed = _fault_confirmed(fault_id, first_error, worker)
            boundary = _classify_boundary(first_error, second_error, final_manifest, oracle_state, worker)
            attempts = final_manifest.get("attempts")
            attempt_statuses = (
                [value.get("status") for value in attempts if isinstance(value, dict)]
                if isinstance(attempts, list)
                else []
            )
            first_details = _error_details(first_error)
            return {
                "case_id": case_id,
                "fault_id": fault_id,
                "fault_class": "control" if fault_id == "F00" else "fault",
                "path_kind": path_kind,
                "scheduled": True,
                "started": True,
                "injection_confirmed": injection_confirmed,
                "oracle_evaluable": bool(oracle_state["oracle_evaluable"]),
                "observation_window_closed": True,
                "boundary_classification": boundary,
                "first_product_state": first_manifest.get("state"),
                "final_product_state": final_manifest.get("state"),
                "first_error": first_error,
                "second_error": second_error,
                "first_error_code": _error_code(first_error),
                "second_error_code": _error_code(second_error),
                "first_error_barrier": first_details.get("barrier"),
                "first_error_submission_outcome": first_details.get("submission_outcome"),
                "first_error_job_id": first_details.get("job_id"),
                "reported_attempt_statuses": attempt_statuses,
                "backend_submission_count": oracle_state["request_received"],
                "oracle_execution_count": oracle_state["execution_started"],
                "worker_execution_entry_count": len(worker.worker_execution_entry_ids),
                "submitted_job_ids": copy.deepcopy(worker.submitted_job_ids),
                "worker_execution_entry_ids": copy.deepcopy(worker.worker_execution_entry_ids),
                "duplicate_submission": int(oracle_state["request_received"]) >= 2,
                "duplicate_execution": int(oracle_state["execution_started"]) >= 2,
                "valid_completion": final_manifest.get("state") == "generated",
                "recovery": {
                    "state": boundary["recovery_state"],
                    "same_job": boundary["recovery_state"] == "same_job_reconciled",
                    "recovery_invocation_count": worker.recovery_calls,
                },
                "raw_reported_state": copy.deepcopy(final_manifest),
                "oracle_state": oracle_state,
            }
    finally:
        fixture.tearDown()
        asset_run_engine_module.TEST_MODEL_ID = previous_model_id


def run_matrix(*, system_label: str, source_sha: str) -> dict[str, object]:
    if not system_label or not isinstance(system_label, str):
        raise ValueError("system_label must be a non-empty string")
    if not isinstance(source_sha, str) or len(source_sha) != 40:
        raise ValueError("source_sha must be a 40-character commit identity")
    self_checks = run_oracle_self_checks()
    preflight = _transport_preflight()
    cases = [run_case(*spec) for spec in CASE_SPECS]
    controls = [case for case in cases if case["fault_class"] == "control"]
    faults = [case for case in cases if case["fault_class"] == "fault"]
    return {
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "system_label": system_label,
        "source_sha": source_sha,
        "ledger_trusted_sha": LEDGER_SHA,
        "runtime_identity": _runtime_identity(),
        "transport_preflight": preflight,
        "oracle_self_checks": self_checks,
        "denominators": {
            "control_cases": _denominators(controls, include_injection=False),
            "fault_cases": _denominators(faults, include_injection=True),
        },
        "interpretation": {
            "scope": "deterministic_cpu_synthetic_worker_observation",
            "post_counts_are_not_execution_counts": True,
            "not_deployment_failure_or_duplicate_execution_rate": True,
            "failed": "product attempt status only; not backend execution failure truth",
        },
        "cases": cases,
    }


def compare_results(b2: dict[str, object], w3: dict[str, object]) -> dict[str, object]:
    if b2.get("protocol_version") != PROTOCOL_VERSION or w3.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("paired results must use the frozen protocol version")
    b2_cases = _case_map(b2)
    w3_cases = _case_map(w3)
    if tuple(b2_cases) != tuple(w3_cases):
        raise ValueError("paired results must contain the same ordered case IDs")
    pairs = []
    for case_id in b2_cases:
        before = b2_cases[case_id]
        after = w3_cases[case_id]
        pairs.append({
            "case_id": case_id,
            "fault_id": before.get("fault_id"),
            "path_kind": before.get("path_kind"),
            "b2_submission_count": before.get("backend_submission_count"),
            "w3_submission_count": after.get("backend_submission_count"),
            "submission_count_delta_w3_minus_b2": _integer_delta(
                after.get("backend_submission_count"), before.get("backend_submission_count")
            ),
            "b2_execution_count": before.get("oracle_execution_count"),
            "w3_execution_count": after.get("oracle_execution_count"),
            "execution_count_delta_w3_minus_b2": _integer_delta(
                after.get("oracle_execution_count"), before.get("oracle_execution_count")
            ),
            "b2_recovery_state": _recovery_state(before),
            "w3_recovery_state": _recovery_state(after),
            "b2_valid_completion": before.get("valid_completion"),
            "w3_valid_completion": after.get("valid_completion"),
            "both_oracle_evaluable": bool(before.get("oracle_evaluable")) and bool(after.get("oracle_evaluable")),
        })
    return {
        "schema_version": 1,
        "protocol_version": PROTOCOL_VERSION,
        "b2_source_sha": b2.get("source_sha"),
        "w3_source_sha": w3.get("source_sha"),
        "paired_case_count": len(pairs),
        "deterministic_coverage_not_deployment_rate": True,
        "pairs": pairs,
    }


def write_json_exclusive(path: Path, value: dict[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
        stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or compare paired deterministic CPU fault coverage.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--system-label", required=True)
    run_parser.add_argument("--source-sha", required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--b2", type=Path, required=True)
    compare_parser.add_argument("--w3", type=Path, required=True)
    compare_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "run":
        write_json_exclusive(
            args.output,
            run_matrix(system_label=args.system_label, source_sha=args.source_sha),
        )
    else:
        b2 = json.loads(args.b2.read_text(encoding="utf-8"))
        w3 = json.loads(args.w3.read_text(encoding="utf-8"))
        write_json_exclusive(args.output, compare_results(b2, w3))
    return 0


def _transport_preflight() -> dict[str, object]:
    accepted = 0

    def drop_response(_value: dict[str, object]) -> tuple[None, bool]:
        nonlocal accepted
        accepted += 1
        return None, True

    with LocalhostJsonServer(drop_response) as server:
        client = BoundedJsonClient(server.url, timeout=5.0)
        try:
            client.post_json("/submit", {"probe": "response-loss"})
        except AssetEngineError as error:
            return {
                "request_accepted": accepted == 1,
                "error_code": error.code,
                "error_details": copy.deepcopy(error.details),
                "submission_outcome_unknown": error.details.get("submission_outcome") == "unknown",
            }
    raise AssertionError("response-loss preflight unexpectedly returned a response")


def _runtime_identity() -> dict[str, object]:
    files = {
        "execution_oracle.py": ROOT / "scripts" / "research" / "execution_oracle.py",
        "run_paired_fault_matrix.py": Path(__file__).resolve(),
        "test_paired_fault_matrix.py": ROOT / "tests" / "research" / "test_paired_fault_matrix.py",
    }
    return {
        "checkout_head": _git_value("rev-parse", "HEAD"),
        "checkout_branch": _git_value("branch", "--show-current") or "detached",
        "python_version": platform.python_version(),
        "output_root_policy": "isolated_temporary_run_root_per_case",
        "harness_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in files.items()
        },
    }


def _git_value(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _call_and_capture(callable_value: object, request: dict[str, object]) -> dict[str, object] | None:
    try:
        assert callable(callable_value)
        callable_value(request)
    except AssetEngineError as error:
        return {
            "raised": True,
            "code": error.code,
            "category": error.category,
            "details": copy.deepcopy(error.details),
        }
    return None


def _fault_confirmed(
    fault_id: str,
    first_error: dict[str, object] | None,
    worker: PairedCpuBackend,
) -> bool | None:
    if fault_id == "F00":
        return None
    details = _error_details(first_error)
    if fault_id == "F02":
        return (
            _error_code(first_error) == "backend_request_failed"
            and details.get("barrier") == "after_execution_before_job_id_response"
            and worker.response_losses == 1
            and details.get("job_id") is None
        )
    return (
        _error_code(first_error) == "comfyui_job_timed_out"
        and details.get("barrier") == "after_job_id_known_before_completion_response"
        and isinstance(details.get("job_id"), str)
    )


def _classify_boundary(
    first_error: dict[str, object] | None,
    second_error: dict[str, object] | None,
    final_manifest: dict[str, object],
    oracle_state: dict[str, object],
    worker: PairedCpuBackend,
) -> dict[str, str]:
    if first_error is None:
        return {
            "state": "resolved",
            "reason": "no_first_call_product_error_observed",
            "recovery_state": "not_needed",
        }
    details = _error_details(first_error)
    first_job_id = details.get("job_id")
    if (
        isinstance(first_job_id, str)
        and final_manifest.get("state") == "generated"
        and worker.recovery_calls == 1
        and oracle_state.get("request_received") == 1
        and oracle_state.get("execution_started") == 1
        and worker.submitted_job_ids == [first_job_id]
    ):
        return {
            "state": "resolved",
            "reason": "same_job_reconciliation_observed_without_worker_reentry",
            "recovery_state": "same_job_reconciled",
        }
    if _error_code(second_error) == "submission_outcome_unknown":
        return {
            "state": "unresolved",
            "reason": "new_submission_blocked_after_unknown_submission_outcome",
            "recovery_state": "outcome_unknown_blocked",
        }
    if int(oracle_state.get("request_received", 0)) > 1:
        return {
            "state": "unresolved",
            "reason": "new_backend_submission_observed_after_fault",
            "recovery_state": "new_submission_after_fault",
        }
    if isinstance(first_job_id, str):
        return {
            "state": "unresolved",
            "reason": "known_job_not_reconciled_by_product_path",
            "recovery_state": "known_job_not_reconciled",
        }
    return {
        "state": "unresolved",
        "reason": "first_call_outcome_ambiguous_without_durable_job_recovery",
        "recovery_state": "outcome_unknown",
    }


def _denominators(cases: list[dict[str, object]], *, include_injection: bool) -> dict[str, int]:
    result = {
        "scheduled": len(cases),
        "started": sum(bool(case["started"]) for case in cases),
        "oracle-evaluable": sum(bool(case["oracle_evaluable"]) for case in cases),
        "resolved": sum(case["boundary_classification"]["state"] == "resolved" for case in cases),
        "unresolved": sum(case["boundary_classification"]["state"] == "unresolved" for case in cases),
        "failed": sum("failed" in case["reported_attempt_statuses"] for case in cases),
        "not-run": sum(not bool(case["started"]) for case in cases),
    }
    if include_injection:
        result["injection-confirmed"] = sum(case["injection_confirmed"] is True for case in cases)
    return result


def _capture_artifacts(result: dict[str, object]) -> dict[Path, bytes]:
    paths: set[Path] = set()
    path_value = result.get("path")
    if isinstance(path_value, str):
        paths.add(Path(path_value))
    for field in ("stage_outputs",):
        mapping = result.get(field)
        if isinstance(mapping, dict):
            for item in mapping.values():
                if isinstance(item, dict) and isinstance(item.get("path"), str):
                    paths.add(Path(item["path"]))
    mask = result.get("mask_output")
    if isinstance(mask, dict) and isinstance(mask.get("path"), str):
        paths.add(Path(mask["path"]))
    return {path: path.read_bytes() for path in paths}


def _result_artifact_hash(result: dict[str, object], path_kind: str) -> str:
    if path_kind == "two-stage":
        stages = result.get("stage_outputs")
        if not isinstance(stages, dict) or not isinstance(stages.get("final"), dict):
            raise AssertionError("two-stage result lacks final stage output")
        path_value = stages["final"].get("path")
    else:
        path_value = result.get("path")
    if not isinstance(path_value, str):
        raise AssertionError("worker result lacks artifact path")
    return hashlib.sha256(Path(path_value).read_bytes()).hexdigest()


def _with_job_id(result: dict[str, object], job_id: str) -> dict[str, object]:
    value = copy.deepcopy(result)
    value["workflow_job_id"] = job_id
    return value


def _copy_request(request: dict[str, object]) -> dict[str, object]:
    return {
        key: ("<callable>" if callable(value) else copy.deepcopy(value))
        for key, value in request.items()
    }


def _error_details(error: dict[str, object] | None) -> dict[str, object]:
    details = error.get("details") if isinstance(error, dict) else None
    return details if isinstance(details, dict) else {}


def _error_code(error: dict[str, object] | None) -> object:
    return error.get("code") if isinstance(error, dict) else None


def _case_map(result: dict[str, object]) -> dict[str, dict[str, object]]:
    cases = result.get("cases")
    if not isinstance(cases, list):
        raise ValueError("paired result has no case list")
    mapped: dict[str, dict[str, object]] = {}
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            raise ValueError("paired result contains an invalid case")
        case_id = case["case_id"]
        if case_id in mapped:
            raise ValueError("paired result contains a duplicate case ID")
        mapped[case_id] = case
    return mapped


def _integer_delta(after: object, before: object) -> int | None:
    if type(after) is not int or type(before) is not int:
        return None
    return after - before


def _recovery_state(case: dict[str, object]) -> object:
    recovery = case.get("recovery")
    return recovery.get("state") if isinstance(recovery, dict) else None


if __name__ == "__main__":
    raise SystemExit(main())
