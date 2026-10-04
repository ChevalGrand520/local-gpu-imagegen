"""Run deterministic CPU fault coverage through the existing product entrance."""

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
import tests.test_asset_run_engine as asset_run_engine_module  # noqa: E402
from tests.test_asset_run_engine import (  # noqa: E402
    AssetRunEngineTests,
    FakeBackendRunner,
    TwoStageBackendRunner,
)


BASELINE_SHA = "da65d57047b5a59e3403b49adf4605a1c0497c58"
LEDGER_SHA = "d8ef0bccc84269b7d4a627adce5f6025a17ab024"
BOUNDARY_MAPPING_VERSION = "deterministic-fault-coverage-v2"
RESEARCH_MODEL_ID = "research-cpu-fake-model"
CASE_SPECS = (
    ("F00-single-stage", "F00", "single-stage"),
    ("F00-two-stage", "F00", "two-stage"),
    ("F02-single-stage", "F02", "single-stage"),
    ("F02-two-stage", "F02", "two-stage"),
    ("F03-single-stage", "F03", "single-stage"),
    ("F03-two-stage", "F03", "two-stage"),
)


class CpuFakeBackendWorker:
    """A model-free backend whose lifecycle events come from its worker entry."""

    def __init__(self, oracle: ExecutionOracle, fault_id: str, path_kind: str) -> None:
        self.oracle = oracle
        self.fault_id = fault_id
        self.path_kind = path_kind
        self.delegate = FakeBackendRunner() if path_kind == "single-stage" else TwoStageBackendRunner()
        self.calls: list[dict[str, object]] = []
        self.submitted_job_ids: list[str] = []
        self.worker_execution_entry_ids: list[str] = []
        self.recovery_calls = 0
        self.call_number = 0

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        """Act as the fake backend's real request/worker boundary."""
        self.call_number += 1
        self.calls.append(copy.deepcopy(request))
        recovery_job_id = request.get("recovery_job_id")
        if recovery_job_id is not None:
            self.recovery_calls += 1
            if not self.submitted_job_ids or recovery_job_id != self.submitted_job_ids[0]:
                raise AssertionError("recovery used a different job ID")
            result = self.delegate(request)
            return self._with_job_id(result, str(recovery_job_id))

        operation_id = str(request["idempotency_key"])
        job_id = self._new_job_id()
        self.submitted_job_ids.append(job_id)
        self.oracle.request_received(operation_id, job_id, operation_id)
        self.oracle.queue_item_created(operation_id, job_id, operation_id)

        # F02 drops the response before the product's job callback is reached.
        if self.fault_id != "F02" or self.call_number != 1:
            self._record_job_id_known(request, operation_id, job_id)

        result = self._run_worker(request, operation_id, job_id)
        if self.fault_id == "F02" and self.call_number == 1:
            raise AssetEngineError(
                "backend_request_failed",
                "Synthetic F02 response loss after backend execution.",
                "backend",
                {"barrier": "after_execution_before_job_id_response"},
            )
        if self.fault_id == "F03" and self.call_number == 1:
            raise StateError(
                "comfyui_job_timed_out",
                "Synthetic F03 completion response loss after job ID became known.",
                {
                    "barrier": "after_job_id_known_before_completion_response",
                    "job_id": job_id,
                    "state": "completed",
                },
            )
        return self._with_job_id(result, job_id) if self.path_kind == "two-stage" else result

    def _run_worker(
        self,
        request: dict[str, object],
        operation_id: str,
        job_id: str,
    ) -> dict[str, object]:
        """Record execution around the delegate's actual synthetic work."""
        execution_id = self.oracle.execution_started(operation_id, job_id, operation_id)
        self.worker_execution_entry_ids.append(execution_id)
        try:
            result = self.delegate(request)
            artifact_hash = _result_artifact_hash(result, self.path_kind)
        except Exception:
            self.oracle.execution_finished(execution_id, outcome="failed")
            raise
        self.oracle.execution_finished(execution_id, artifact_hash=artifact_hash)
        return result

    def _record_job_id_known(
        self,
        request: dict[str, object],
        operation_id: str,
        job_id: str,
    ) -> None:
        # This is an oracle event, not a client-side idempotency claim.
        self.oracle.job_id_revealed(operation_id, job_id, operation_id)
        callback = request.get("backend_job_callback")
        if callable(callback):
            callback(job_id)

    def _new_job_id(self) -> str:
        return f"cpu-{self.path_kind}-{self.fault_id.lower()}-{self.call_number:04d}"

    @staticmethod
    def _with_job_id(result: dict[str, object], job_id: str) -> dict[str, object]:
        value = copy.deepcopy(result)
        value["workflow_job_id"] = job_id
        return value


def run_case(case_id: str, fault_id: str, path_kind: str) -> dict[str, object]:
    previous_model_id = asset_run_engine_module.TEST_MODEL_ID
    asset_run_engine_module.TEST_MODEL_ID = RESEARCH_MODEL_ID
    fixture = AssetRunEngineTests("runTest")
    fixture.setUp()
    try:
        oracle = ExecutionOracle(case_id)
        worker = CpuFakeBackendWorker(oracle, fault_id, path_kind)
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
        injection_confirmed = _fault_confirmed(fault_id, first_error, first_manifest)
        boundary = _classify_boundary(first_error, final_manifest, oracle_state, worker)
        reported_attempts = final_manifest.get("attempts")
        attempt_statuses = (
            [value.get("status") for value in reported_attempts if isinstance(value, dict)]
            if isinstance(reported_attempts, list)
            else []
        )
        first_details = first_error.get("details") if isinstance(first_error, dict) else None
        first_error_job_id = (
            first_details.get("job_id")
            if isinstance(first_details, dict) and isinstance(first_details.get("job_id"), str)
            else None
        )
        record = {
            "record_id": case_id,
            "source_sha": BASELINE_SHA,
            "request": {
                "idempotency_key": request["idempotency_key"],
                "path_kind": path_kind,
                "fault_id": fault_id,
            },
            "backend_instance": {"backend": "cpu-fake", "instance": case_id},
            "approval_state": "not_required",
            "reported_state": copy.deepcopy(final_manifest),
            "oracle_state": oracle_state,
            "validator_version": "product-validate-v1",
            "research_metadata": {
                "scheduled": True,
                "started": True,
                "injection_confirmed": injection_confirmed,
                "boundary_classification": copy.deepcopy(boundary),
                "worker_execution_entry_ids": copy.deepcopy(worker.worker_execution_entry_ids),
            },
        }
        normalized = export_record(record)
        return {
            "case_id": case_id,
            "fault_id": fault_id,
            "fault_class": "control" if fault_id == "F00" else "fault",
            "path_kind": path_kind,
            "scheduled": True,
            "started": True,
            "injection_confirmed": injection_confirmed,
            "oracle_evaluable": bool(oracle_state["oracle_evaluable"]),
            "boundary_classification": boundary,
            "first_product_state": first_manifest.get("state"),
            "final_product_state": final_manifest.get("state"),
            "first_error": first_error,
            "second_error": second_error,
            "first_error_code": first_error.get("code") if isinstance(first_error, dict) else None,
            "first_error_barrier": first_details.get("barrier") if isinstance(first_details, dict) else None,
            "first_error_job_id": first_error_job_id,
            "reported_attempt_statuses": attempt_statuses,
            "backend_worker_invocation_count": len(worker.calls),
            "backend_submission_count": oracle_state["request_received"],
            "oracle_execution_count": oracle_state["execution_started"],
            "submitted_job_ids": copy.deepcopy(worker.submitted_job_ids),
            "worker_execution_entry_ids": copy.deepcopy(worker.worker_execution_entry_ids),
            "duplicate_submission": int(oracle_state["request_received"]) >= 2,
            "duplicate_execution": int(oracle_state["execution_started"]) >= 2,
            "recovery": {
                "state": boundary["recovery_state"],
                "same_job": boundary["recovery_state"] == "same_job_reconciled",
                "recovery_invocation_count": worker.recovery_calls,
            },
            "product_second_call_succeeded": fault_id in {"F02", "F03"} and second_error is None,
            "raw_and_normalized": {
                "raw_record": record,
                "normalized_record": normalized,
            },
        }
    finally:
        fixture.tearDown()
        asset_run_engine_module.TEST_MODEL_ID = previous_model_id


def run_matrix() -> dict[str, object]:
    self_checks = run_oracle_self_checks()
    cases = [run_case(*spec) for spec in CASE_SPECS]
    controls = [case for case in cases if case["fault_class"] == "control"]
    faults = [case for case in cases if case["fault_class"] == "fault"]
    return {
        "schema_version": 2,
        "package": "deterministic-fault-coverage-v2",
        "baseline_sha": BASELINE_SHA,
        "ledger_trusted_sha": LEDGER_SHA,
        "oracle_self_checks": self_checks,
        "denominators": {
            "all_cases": _denominators(cases, include_injection=False),
            "control_cases": _denominators(controls, include_injection=False),
            "fault_cases": _denominators(faults, include_injection=True),
        },
        "deterministic_fault_coverage": {
            "mapping_version": BOUNDARY_MAPPING_VERSION,
            "fault_case_count": len(faults),
            "injection_confirmed_case_count": sum(case["injection_confirmed"] is True for case in faults),
            "oracle_evaluable_case_count": sum(bool(case["oracle_evaluable"]) for case in faults),
            "resolved_case_ids": [
                case["case_id"] for case in faults if case["boundary_classification"]["state"] == "resolved"
            ],
            "unresolved_case_ids": [
                case["case_id"] for case in faults if case["boundary_classification"]["state"] == "unresolved"
            ],
            "not_deployment_failure_rate": True,
        },
        "execution_observations": {
            "scope": "deterministic_cpu_fake_backend_only",
            "duplicate_execution_case_ids": [
                case["case_id"] for case in cases if case["duplicate_execution"]
            ],
            "duplicate_submission_case_ids": [
                case["case_id"] for case in cases if case["duplicate_submission"]
            ],
            "counts_are_not_deployment_failure_or_duplicate_execution_rates": True,
            "post_counts_are_not_execution_counts": True,
        },
        "interpretation": {
            "resolved": "the versioned mapping observed either no first-call fault or same-job reconciliation without a new backend submission",
            "unresolved": "the versioned mapping observed an ambiguous first-call boundary followed by no same-job reconciliation",
            "failed": "at least one product attempt was reported failed; this is not backend execution failure truth",
            "not_run": "scheduled cases that were not executed",
        },
        "cases": cases,
    }


def _denominators(cases: list[dict[str, object]], *, include_injection: bool) -> dict[str, object]:
    result: dict[str, object] = {
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


def write_json(path: Path, value: dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic CPU fault coverage.")
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
) -> bool | None:
    if fault_id == "F00":
        return None
    if not isinstance(first_error, dict) or not first_manifest.get("attempts"):
        return False
    details = first_error.get("details")
    if not isinstance(details, dict):
        return False
    expected = {
        "F02": ("backend_request_failed", "after_execution_before_job_id_response"),
        "F03": ("comfyui_job_timed_out", "after_job_id_known_before_completion_response"),
    }[fault_id]
    if (first_error.get("code"), details.get("barrier")) != expected:
        return False
    if fault_id == "F02":
        return "job_id" not in details
    return isinstance(details.get("job_id"), str) and bool(details["job_id"])


def _classify_boundary(
    first_error: dict[str, object] | None,
    final_manifest: dict[str, object],
    oracle_state: dict[str, object],
    worker: CpuFakeBackendWorker,
) -> dict[str, str]:
    if first_error is None:
        return {
            "state": "resolved",
            "mapping_version": BOUNDARY_MAPPING_VERSION,
            "reason": "no_first_call_product_error_observed",
            "recovery_state": "not_needed",
        }
    details = first_error.get("details") if isinstance(first_error, dict) else None
    first_job_id = details.get("job_id") if isinstance(details, dict) else None
    same_job_reconciled = (
        isinstance(first_job_id, str)
        and final_manifest.get("state") == "generated"
        and worker.recovery_calls == 1
        and oracle_state.get("request_received") == 1
        and oracle_state.get("execution_started") == 1
        and worker.submitted_job_ids == [first_job_id]
    )
    if same_job_reconciled:
        return {
            "state": "resolved",
            "mapping_version": BOUNDARY_MAPPING_VERSION,
            "reason": "same_job_reconciliation_observed_without_new_backend_submission",
            "recovery_state": "same_job_reconciled",
        }
    if oracle_state.get("request_received", 0) > 1:
        reason = "new_backend_submission_observed_after_ambiguous_first_call"
        recovery_state = "new_submission_after_fault"
    elif isinstance(first_job_id, str):
        reason = "known_job_not_reconciled_by_product_path"
        recovery_state = "known_job_not_reconciled"
    else:
        reason = "first_call_outcome_ambiguous_without_durable_job_recovery"
        recovery_state = "outcome_unknown"
    return {
        "state": "unresolved",
        "mapping_version": BOUNDARY_MAPPING_VERSION,
        "reason": reason,
        "recovery_state": recovery_state,
    }


def _result_artifact_hash(result: dict[str, object], path_kind: str) -> str:
    if path_kind == "two-stage":
        stage_outputs = result.get("stage_outputs")
        if not isinstance(stage_outputs, dict):
            raise AssertionError("two-stage worker result has no stage outputs")
        final = stage_outputs.get("final")
        if not isinstance(final, dict):
            raise AssertionError("two-stage worker result has no final output")
        path_value = final.get("path")
    else:
        path_value = result.get("path")
    if not isinstance(path_value, str):
        raise AssertionError("worker result has no artifact path")
    return _sha256_file(Path(path_value))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
