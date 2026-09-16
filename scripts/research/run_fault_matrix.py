"""Run the bounded CPU F00/F02/F03 matrix through the existing product entrance."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


if __package__ in {None, ""}:
    _root = Path(__file__).resolve().parents[2]
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    _scripts_root = _root / "scripts"
    if str(_scripts_root) not in sys.path:
        sys.path.insert(0, str(_scripts_root))

from local_gpu_imagegen.errors import AssetEngineError, StateError  # noqa: E402
from scripts.research.execution_oracle import ExecutionOracle, run_oracle_self_checks  # noqa: E402
from scripts.research.export_records import export_record  # noqa: E402
from tests.test_asset_run_engine import (  # noqa: E402
    AssetRunEngineTests,
    FakeBackendRunner,
    TwoStageBackendRunner,
)


BASELINE_SHA = "da65d57047b5a59e3403b49adf4605a1c0497c58"
LEDGER_SHA = "d8ef0bccc84269b7d4a627adce5f6025a17ab024"
CASE_SPECS = (
    ("F00-single-stage", "F00", "single-stage"),
    ("F00-two-stage", "F00", "two-stage"),
    ("F02-single-stage", "F02", "single-stage"),
    ("F02-two-stage", "F02", "two-stage"),
    ("F03-single-stage", "F03", "single-stage"),
    ("F03-two-stage", "F03", "two-stage"),
)


class SingleStageOracleRunner:
    def __init__(self, oracle: ExecutionOracle, fault_id: str) -> None:
        self.oracle = oracle
        self.fault_id = fault_id
        self.delegate = FakeBackendRunner()
        self.calls: list[dict[str, object]] = []
        self.call_number = 0

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.call_number += 1
        self.calls.append(copy.deepcopy(request))
        operation_id = str(request["idempotency_key"])
        job_id = f"cpu-single-{self.call_number}"
        self.oracle.request_received(operation_id, job_id, operation_id)
        self.oracle.queue_item_created(operation_id, job_id, operation_id)
        execution_id = self.oracle.execution_started(operation_id, job_id, operation_id)
        result = self.delegate(request)
        self.oracle.execution_finished(execution_id)
        if self.fault_id in {"F02", "F03"} and self.call_number == 1:
            details = {"barrier": "after_execution_before_client_response", "job_id": job_id}
            raise AssetEngineError(
                "backend_request_failed",
                f"Synthetic {self.fault_id} response-loss barrier.",
                "backend",
                details,
            )
        return result


class TwoStageOracleRunner:
    def __init__(self, oracle: ExecutionOracle, fault_id: str) -> None:
        self.oracle = oracle
        self.fault_id = fault_id
        self.delegate = TwoStageBackendRunner()
        self.calls: list[dict[str, object]] = []
        self.call_number = 0
        self.job_id = f"cpu-two-stage-{fault_id.lower()}"

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.call_number += 1
        self.calls.append(copy.deepcopy(request))
        operation_id = str(request["idempotency_key"])
        recovery_job_id = request.get("recovery_job_id")
        if recovery_job_id is not None:
            if recovery_job_id != self.job_id:
                raise AssertionError("recovery used a different job ID")
            # Reconciliation reads the same job's outputs; it is not a new execution.
            return self.delegate(request)

        self.oracle.request_received(operation_id, self.job_id, operation_id)
        self.oracle.queue_item_created(operation_id, self.job_id, operation_id)
        execution_id = self.oracle.execution_started(operation_id, self.job_id, operation_id)
        if self.fault_id == "F02" and self.call_number == 1:
            self.oracle.execution_finished(execution_id)
            raise AssetEngineError(
                "backend_request_failed",
                "Synthetic F02 response loss before durable job ID.",
                "backend",
                {"barrier": "after_queue_and_execution_before_job_callback", "job_id": self.job_id},
            )

        callback = request.get("backend_job_callback")
        if not callable(callback):
            raise AssertionError("two-stage submission did not provide a backend job callback")
        callback(self.job_id)
        result = self.delegate(request)
        self.oracle.execution_finished(execution_id)
        if self.fault_id == "F03" and self.call_number == 1:
            raise StateError(
                "comfyui_job_timed_out",
                "Synthetic F03 completion response loss.",
                {"job_id": self.job_id, "state": "completed", "barrier": "after_execution_before_completion_signal"},
            )
        return result


def run_case(case_id: str, fault_id: str, path_kind: str) -> dict[str, object]:
    fixture = AssetRunEngineTests("runTest")
    fixture.setUp()
    try:
        oracle = ExecutionOracle(case_id)
        runner = (
            SingleStageOracleRunner(oracle, fault_id)
            if path_kind == "single-stage"
            else TwoStageOracleRunner(oracle, fault_id)
        )
        fixture.engine.backend_runner = runner
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
                "change_summary": "Bounded CPU fault characterization.",
                "plan": fixture.two_stage_plan(route),
            }

        first_error = _call_and_capture(fixture.engine.generate_round, request)
        first_manifest = fixture.engine.get_run({"run_id": run_id})
        second_error: dict[str, object] | None = None
        if fault_id in {"F02", "F03"}:
            second_error = _call_and_capture(fixture.engine.generate_round, request)
        final_manifest = fixture.engine.get_run({"run_id": run_id})
        oracle_state = oracle.snapshot()
        artifact_hash = _latest_artifact_hash(fixture.output_root, run_id, final_manifest)
        if artifact_hash is not None:
            oracle_state["artifact_hash"] = artifact_hash

        first_state = first_manifest.get("state")
        final_state = final_manifest.get("state")
        fault_confirmed = _fault_confirmed(fault_id, first_error, first_manifest, runner)
        oracle_evaluable = bool(oracle_state["oracle_evaluable"])
        first_boundary = "resolved" if fault_id == "F00" or (fault_id == "F03" and path_kind == "two-stage") else "unresolved"
        reported_attempts = final_manifest.get("attempts")
        attempt_statuses = [
            value.get("status")
            for value in reported_attempts
            if isinstance(value, dict)
        ] if isinstance(reported_attempts, list) else []
        record = {
            "record_id": case_id,
            "source_sha": BASELINE_SHA,
            "request": {"idempotency_key": request["idempotency_key"], "path_kind": path_kind, "fault_id": fault_id},
            "backend_instance": {"backend": "cpu-fake", "instance": case_id},
            "reported_state": copy.deepcopy(final_manifest),
            "oracle_state": oracle_state,
            "validator_version": "product-validate-v1",
            "research_metadata": {
                "scheduled": True,
                "started": True,
                "injection_confirmed": fault_confirmed,
                "oracle_evaluable": oracle_evaluable,
                "first_boundary_resolution": first_boundary,
                "duplicate_submission": len(runner.calls) >= 2,
                "duplicate_execution": int(oracle_state["execution_started"]) >= 2,
            },
        }
        normalized = export_record(record)
        return {
            "case_id": case_id,
            "fault_id": fault_id,
            "path_kind": path_kind,
            "scheduled": True,
            "started": True,
            "injection_confirmed": fault_confirmed,
            "oracle_evaluable": oracle_evaluable,
            "first_boundary_resolution": first_boundary,
            "product_first_call": first_error,
            "product_second_call": second_error,
            "first_product_state": first_state,
            "final_product_state": final_state,
            "reported_attempt_statuses": attempt_statuses,
            "backend_runner_invocation_count": len(runner.calls),
            "submission_count": oracle_state["request_received"],
            "oracle_execution_count": oracle_state["execution_started"],
            "duplicate_submission": int(oracle_state["request_received"]) >= 2,
            "duplicate_execution": int(oracle_state["execution_started"]) >= 2,
            "product_second_call_succeeded": fault_id in {"F02", "F03"} and second_error is None,
            "raw_and_normalized": {
                "raw_record": record,
                "normalized_record": normalized,
            },
        }
    finally:
        fixture.tearDown()


def run_matrix() -> dict[str, object]:
    self_checks = run_oracle_self_checks()
    cases = [run_case(*spec) for spec in CASE_SPECS]
    scheduled = len(cases)
    injection_confirmed = sum(bool(case["injection_confirmed"]) for case in cases)
    oracle_evaluable = sum(bool(case["oracle_evaluable"]) for case in cases)
    resolved = sum(case["first_boundary_resolution"] == "resolved" for case in cases)
    unresolved = scheduled - resolved
    failed = sum("failed" in case["reported_attempt_statuses"] for case in cases)
    not_run = 0
    duplicate_execution = sum(bool(case["duplicate_execution"]) for case in cases if case["oracle_evaluable"] and case["injection_confirmed"])
    return {
        "schema_version": 1,
        "package": "bounded-cpu-w0-w1-w2",
        "baseline_sha": BASELINE_SHA,
        "ledger_trusted_sha": LEDGER_SHA,
        "oracle_self_checks": self_checks,
        "denominators": {
            "scheduled": scheduled,
            "started": scheduled,
            "injection-confirmed": injection_confirmed,
            "oracle-evaluable": oracle_evaluable,
            "resolved": resolved,
            "unresolved": unresolved,
            "failed": failed,
            "not-run": not_run,
        },
        "execution_metrics": {
            "oracle_evaluable_operation_count": oracle_evaluable,
            "duplicate_execution_operation_count": duplicate_execution,
            "duplicate_execution_rate": duplicate_execution / oracle_evaluable if oracle_evaluable else None,
            "post_counts_are_not_execution_counts": True,
        },
        "interpretation": {
            "resolved": "first fault boundary was resolved by the product path, including same-job two-stage recovery",
            "unresolved": "first fault boundary remained ambiguous to the product caller or had no durable recovery binding",
            "failed": "at least one product attempt was reported failed; this is not backend execution failure truth",
            "not_run": "scheduled package cases that were not executed",
        },
        "cases": cases,
    }


def write_json(path: Path, value: dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded CPU image fault matrix.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    write_json(args.output, run_matrix())
    return 0


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
    first_manifest: dict[str, object],
    runner: object,
) -> bool:
    if fault_id == "F00":
        return first_error is None and bool(getattr(runner, "calls", []))
    if first_error is None:
        return False
    details = first_error.get("details")
    if not isinstance(details, dict):
        return False
    expected_barriers = {
        "F02": {"after_execution_before_client_response", "after_queue_and_execution_before_job_callback"},
        "F03": {"after_execution_before_client_response", "after_execution_before_completion_signal"},
    }
    return details.get("barrier") in expected_barriers[fault_id] and bool(first_manifest.get("attempts"))


def _latest_artifact_hash(output_root: Path, run_id: str, manifest: dict[str, object]) -> str | None:
    rounds = manifest.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        return None
    latest = rounds[-1]
    if not isinstance(latest, dict):
        return None
    image = latest.get("image")
    if not isinstance(image, dict) or not isinstance(image.get("path"), str):
        return None
    path = (Path(output_root) / "runs" / run_id / str(image["path"])).resolve()
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
