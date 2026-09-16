"""Read-only normalization of product run evidence.

The exporter never calls the product engine and never writes to an input run.
It keeps the product's reported state separate from conservative interpretation
and from an independently supplied oracle state.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from pathlib import Path


if __package__ in {None, ""}:
    _scripts_root = Path(__file__).resolve().parents[1]
    if str(_scripts_root) not in sys.path:
        sys.path.insert(0, str(_scripts_root))

from local_gpu_imagegen.run_store import request_hash


EXPORT_SCHEMA_VERSION = 1
EXPORTER_VERSION = "research-exporter-v1"
MAPPING_VERSION = "research-normalization-v2"
UNKNOWN = "unknown"
_MISSING = object()

_EXECUTION_STATES = frozenset({
    "not_started",
    "queued",
    "running",
    "succeeded",
    "failed",
    UNKNOWN,
})
_EVIDENCE_STATES = frozenset({"missing", "partial", "verified", "mismatch"})
_DOMAIN_STATES = frozenset({"not_evaluated", "accepted", "rejected", UNKNOWN})
_APPROVAL_STATES = frozenset({"not_required", "required", "valid", "invalid", UNKNOWN})


def export_record(
    record: dict[str, object],
    *,
    source_path: Path | None = None,
    source_sha: object = _MISSING,
    validator_version: object = _MISSING,
) -> dict[str, object]:
    """Return one normalized record without mutating ``record`` or its inputs."""
    if not isinstance(record, dict):
        raise ValueError("research evidence record must be an object")

    reported = record.get("reported_state", _MISSING)
    if reported is _MISSING:
        reported = record.get("manifest", record)
    reported_copy = copy.deepcopy(reported)
    reported_object = reported if isinstance(reported, dict) else {}

    oracle_value = record.get("oracle_state")
    if isinstance(oracle_value, dict):
        oracle_copy: object = copy.deepcopy(oracle_value)
        oracle_reason = "provided_by_independent_oracle"
    else:
        oracle_copy = {
            "state": UNKNOWN,
            "reason": "oracle_state_missing_or_not_an_object",
        }
        oracle_reason = "oracle_state_missing_or_not_an_object"

    reported_job_id = _reported_job_id(reported_object)
    oracle_job_id = _oracle_job_id(oracle_value if isinstance(oracle_value, dict) else {})
    job_id, job_reason = _field_value(
        record,
        "job_id",
        aliases=("backend_job_id",),
        fallback=reported_job_id,
        fallback_reason="derived_from_durable_reported_backend_job",
    )

    reported_artifact_hash = _reported_artifact_hash(reported_object)
    oracle_artifact_hash = _oracle_artifact_hash(oracle_value if isinstance(oracle_value, dict) else {})
    artifact_hash, artifact_reason = _artifact_hash(record, reported_artifact_hash, source_path)
    if (
        artifact_hash not in {None, UNKNOWN}
        and oracle_artifact_hash not in {None, UNKNOWN}
        and artifact_hash != oracle_artifact_hash
    ):
        artifact_reason = "reported_artifact_hash_differs_from_oracle_artifact_hash"

    source_value, source_reason = _source_value(record, source_sha)
    request_digest, request_reason = _request_digest(record, reported_object)
    input_digest, input_reason = _input_digest(record, source_path)
    backend_instance, backend_reason = _backend_instance(record, reported_object)
    validator_value, validator_reason = _validator_value(record, validator_version)

    interpreted_state, mapping_reason = _interpret_state(
        reported_object,
        record,
        oracle_value if isinstance(oracle_value, dict) else None,
        job_id,
        artifact_hash,
        oracle_artifact_hash,
        oracle_job_id,
    )

    record_id = record.get("record_id", reported_object.get("run_id"))
    output: dict[str, object] = {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "exporter_version": EXPORTER_VERSION,
        "record_id": copy.deepcopy(record_id),
        "reported_state": reported_copy,
        "interpreted_state": interpreted_state,
        "mapping_version": MAPPING_VERSION,
        "mapping_reason": mapping_reason,
        "oracle_state": oracle_copy,
        "oracle_state_reason": oracle_reason,
        "source_sha": source_value,
        "request_digest": request_digest,
        "input_digest": input_digest,
        "backend_instance": backend_instance,
        "job_id": job_id,
        "reported_job_id": reported_job_id,
        "oracle_job_id": oracle_job_id,
        "artifact_hash": artifact_hash,
        "validator_version": validator_value,
        "field_reasons": {
            "source_sha": source_reason,
            "request_digest": request_reason,
            "input_digest": input_reason,
            "backend_instance": backend_reason,
            "job_id": job_reason,
            "artifact_hash": artifact_reason,
            "validator_version": validator_reason,
        },
    }
    return output


def load_record(path: Path) -> dict[str, object]:
    """Load one JSON record or a RunStore ``manifest.json`` from a run root."""
    input_path = Path(path).resolve()
    if input_path.is_dir():
        candidates = (input_path / "manifest.json", input_path / "run-manifest.json")
        input_path = next((candidate for candidate in candidates if candidate.is_file()), input_path / "manifest.json")
    try:
        value = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON evidence: {input_path}") from error
    if not isinstance(value, dict):
        raise ValueError("JSON evidence record must be an object")
    return value


def write_export(path: Path, value: dict[str, object]) -> None:
    """Create a new export and refuse to overwrite an existing evidence file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    try:
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    except FileExistsError as error:
        raise ValueError(f"refusing to overwrite existing export: {destination}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export one local run as read-only research evidence.")
    parser.add_argument("--input", type=Path, required=True, help="JSON record or RunStore run directory")
    parser.add_argument("--output", type=Path, required=True, help="new normalized JSON destination")
    parser.add_argument("--source-sha", default=None, help="source checkout SHA, if known")
    parser.add_argument("--validator-version", default=None, help="validator version, if known")
    args = parser.parse_args(argv)
    try:
        record = load_record(args.input)
        exported = export_record(
            record,
            source_path=args.input if args.input.is_file() else args.input / "manifest.json",
            source_sha=args.source_sha if args.source_sha is not None else _MISSING,
            validator_version=args.validator_version if args.validator_version is not None else _MISSING,
        )
        write_export(args.output, exported)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


def _field_value(
    record: dict[str, object],
    key: str,
    *,
    aliases: tuple[str, ...] = (),
    fallback: object = _MISSING,
    fallback_reason: str = "",
) -> tuple[object, str]:
    if key in record:
        value = record[key]
        if value is None:
            return None, f"{key}_is_null"
        return copy.deepcopy(value), f"provided_{key}"
    for alias in aliases:
        if alias in record:
            value = record[alias]
            if value is None:
                return None, f"{alias}_is_null"
            return copy.deepcopy(value), f"provided_{alias}"
    if fallback is not _MISSING and fallback is not None:
        return copy.deepcopy(fallback), fallback_reason
    return None, f"{key}_missing"


def _source_value(record: dict[str, object], override: object) -> tuple[object, str]:
    if override is not _MISSING:
        if override is None:
            return None, "source_sha_override_is_null"
        return copy.deepcopy(override), "provided_by_export_command"
    for key in ("source_sha", "source_commit", "git_sha"):
        if key in record:
            value = record[key]
            if value is None:
                return None, f"{key}_is_null"
            return copy.deepcopy(value), f"provided_{key}"
    return None, "source_sha_missing"


def _request_digest(record: dict[str, object], reported: dict[str, object]) -> tuple[object, str]:
    if "request_digest" in record:
        value = record["request_digest"]
        return copy.deepcopy(value), "provided_request_digest" if value is not None else "request_digest_is_null"
    if "request_hash" in record:
        value = record["request_hash"]
        return copy.deepcopy(value), "provided_request_hash" if value is not None else "request_hash_is_null"
    for collection_name in ("attempts", "rounds"):
        collection = reported.get(collection_name)
        if not isinstance(collection, list):
            continue
        for value in reversed(collection):
            if isinstance(value, dict) and "request_hash" in value:
                stored = value["request_hash"]
                return copy.deepcopy(stored), f"provided_reported_{collection_name}.request_hash"
    request = reported.get("request")
    if not isinstance(request, dict):
        request = record.get("request")
    if isinstance(request, dict):
        try:
            return request_hash(request), "computed_with_run_store.request_hash"
        except (TypeError, ValueError, RecursionError):
            return None, "request_is_not_json_serializable"
    return None, "request_digest_missing_request"


def _input_digest(record: dict[str, object], source_path: Path | None) -> tuple[object, str]:
    if "input_digest" in record:
        value = record["input_digest"]
        return copy.deepcopy(value), "provided_input_digest" if value is not None else "input_digest_is_null"
    value = record.get("input")
    if isinstance(value, dict):
        for key in ("sha256", "digest", "input_digest"):
            if key in value:
                return copy.deepcopy(value[key]), f"provided_input_{key}"
        value = value.get("path")
    if isinstance(value, str) and value:
        path, path_reason = _safe_evidence_file(value, source_path, "input")
        if path is None:
            return None, path_reason
        try:
            return _sha256_file(path), "computed_from_explicit_input_path"
        except OSError:
            return None, "input_path_missing_or_unreadable"
    return None, "input_digest_missing"


def _backend_instance(record: dict[str, object], reported: dict[str, object]) -> tuple[object, str]:
    if "backend_instance" in record:
        value = record["backend_instance"]
        return copy.deepcopy(value), "provided_backend_instance" if value is not None else "backend_instance_is_null"
    backend = record.get("backend", reported.get("backend"))
    endpoint = record.get("endpoint_identity", reported.get("endpoint_identity"))
    if backend is not None and endpoint is not None:
        return {
            "backend": copy.deepcopy(backend),
            "endpoint_identity": copy.deepcopy(endpoint),
        }, "derived_from_explicit_backend_and_endpoint_identity"
    return None, "backend_instance_missing"


def _validator_value(record: dict[str, object], override: object) -> tuple[object, str]:
    if override is not _MISSING:
        return copy.deepcopy(override), "provided_by_export_command" if override is not None else "validator_version_override_is_null"
    if "validator_version" in record:
        value = record["validator_version"]
        return copy.deepcopy(value), "provided_validator_version" if value is not None else "validator_version_is_null"
    validator = record.get("validator")
    if isinstance(validator, dict) and "version" in validator:
        return copy.deepcopy(validator["version"]), "provided_validator.version"
    return None, "validator_version_missing"


def _reported_job_id(reported: dict[str, object]) -> object:
    active = reported.get("active_attempt")
    attempts = reported.get("attempts")
    candidates: list[object] = [active]
    if isinstance(attempts, list):
        candidates.extend(reversed(attempts))
    rounds = reported.get("rounds")
    if isinstance(rounds, list):
        candidates.extend(reversed(rounds))
    for value in candidates:
        if not isinstance(value, dict):
            continue
        backend_job = value.get("backend_job")
        if isinstance(backend_job, dict) and backend_job.get("job_id") is not None:
            return copy.deepcopy(backend_job["job_id"])
        backend_result = value.get("backend_result")
        if isinstance(backend_result, dict) and backend_result.get("workflow_job_id") is not None:
            return copy.deepcopy(backend_result["workflow_job_id"])
    return None


def _oracle_job_id(oracle: dict[str, object]) -> object:
    for key in ("job_id", "backend_job_id"):
        if oracle.get(key) is not None:
            return copy.deepcopy(oracle[key])
    job_ids = oracle.get("job_ids")
    if isinstance(job_ids, list) and len(job_ids) == 1:
        return copy.deepcopy(job_ids[0])
    return None


def _reported_artifact_hash(reported: dict[str, object]) -> object:
    rounds = reported.get("rounds")
    if isinstance(rounds, list):
        for value in reversed(rounds):
            if not isinstance(value, dict):
                continue
            image = value.get("image")
            if isinstance(image, dict) and image.get("sha256") is not None:
                return copy.deepcopy(image["sha256"])
    return None


def _oracle_artifact_hash(oracle: dict[str, object]) -> object:
    artifact = oracle.get("artifact")
    if isinstance(artifact, dict) and artifact.get("sha256") is not None:
        return copy.deepcopy(artifact["sha256"])
    return oracle.get("artifact_hash")


def _artifact_hash(
    record: dict[str, object],
    reported_hash: object,
    source_path: Path | None,
) -> tuple[object, str]:
    if "artifact_hash" in record:
        value = record["artifact_hash"]
        return copy.deepcopy(value), "provided_artifact_hash" if value is not None else "artifact_hash_is_null"
    artifact = record.get("artifact")
    if isinstance(artifact, dict):
        if "sha256" in artifact:
            value = artifact["sha256"]
            return copy.deepcopy(value), "provided_artifact.sha256" if value is not None else "artifact.sha256_is_null"
        path_value = artifact.get("path")
    else:
        path_value = artifact
    if isinstance(path_value, str) and path_value:
        path, path_reason = _safe_evidence_file(path_value, source_path, "artifact")
        if path is None:
            return None, path_reason
        try:
            return _sha256_file(path), "computed_from_explicit_artifact_path"
        except OSError:
            return None, "artifact_path_missing_or_unreadable"
    if reported_hash is not None:
        return copy.deepcopy(reported_hash), "derived_from_reported_round_artifact"
    return None, "artifact_hash_missing"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_evidence_file(
    value: str,
    source_path: Path | None,
    field: str,
) -> tuple[Path | None, str]:
    """Resolve a referenced file only inside the source evidence root."""
    if source_path is None:
        return None, f"{field}_path_requires_evidence_root"
    source = Path(source_path)
    try:
        source_resolved = source.resolve()
    except (OSError, RuntimeError):
        return None, "evidence_root_unresolvable"
    root = source_resolved if source_resolved.is_dir() else source_resolved.parent
    candidate = Path(value)
    lexical = candidate if candidate.is_absolute() else root / candidate
    lexical_normalized = Path(os.path.abspath(str(lexical)))
    try:
        resolved = lexical.resolve(strict=False)
    except (OSError, RuntimeError):
        return None, f"{field}_path_unresolvable"
    if not _is_within(root, lexical_normalized):
        return None, f"{field}_path_outside_evidence_root"
    if not _is_within(root, resolved):
        return None, f"{field}_path_symlink_escapes_evidence_root"
    if not resolved.is_file():
        return None, f"{field}_path_missing_or_unreadable"
    return resolved, ""


def _is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _interpret_state(
    reported: dict[str, object],
    record: dict[str, object],
    oracle: dict[str, object] | None,
    job_id: object,
    artifact_hash: object,
    oracle_artifact_hash: object,
    oracle_job_id: object,
) -> tuple[dict[str, object], dict[str, str]]:
    reasons: dict[str, str] = {}
    reported_name = reported.get("state")
    active = reported.get("active_attempt")
    attempts = reported.get("attempts")
    has_attempt = isinstance(active, dict) or (isinstance(attempts, list) and bool(attempts))
    if job_id not in {None, UNKNOWN}:
        submission = "job_identified"
        reasons["submission_state"] = "explicit_or_observed_job_id_is_available"
    elif reported_name in {"unresolved", "interrupted"}:
        submission = "outcome_unknown"
        reasons["submission_state"] = "reported_attempt_is_unresolved_without_a_durable_job_id"
    elif has_attempt or reported_name in {"generating", "generated", "reviewed", "finalized"}:
        submission = "intent_recorded"
        reasons["submission_state"] = "reported_attempt_or_terminal_run_proves_intent_not_execution"
    elif reported_name == UNKNOWN:
        submission = UNKNOWN
        reasons["submission_state"] = "reported_state_is_explicitly_unknown"
    else:
        submission = "not_submitted"
        reasons["submission_state"] = "no_reported_attempt_or_submission_fact"

    execution, execution_reason = _oracle_execution(oracle)
    reasons["execution_state"] = execution_reason

    evidence, evidence_reason = _evidence_state(
        record,
        reported,
        oracle,
        artifact_hash,
        oracle_artifact_hash,
        job_id,
        oracle_job_id,
    )
    reasons["evidence_state"] = evidence_reason

    recovery, recovery_reason = _recovery_state(reported, execution)
    reasons["recovery_state"] = recovery_reason

    domain, domain_reason = _dimension_value(
        record,
        reported,
        "domain_verdict",
        _DOMAIN_STATES,
        "not_evaluated",
        "domain_verdict_missing_is_not_evaluated",
    )
    approval, approval_reason = _dimension_value(
        record,
        reported,
        "approval_state",
        _APPROVAL_STATES,
        UNKNOWN,
        "approval_state_missing_is_unknown",
    )
    reasons["domain_verdict"] = domain_reason
    reasons["approval_state"] = approval_reason

    execution_verified = (
        execution == "succeeded"
        and evidence == "verified"
        and job_id not in {None, UNKNOWN}
        and oracle_job_id not in {None, UNKNOWN}
        and job_id == oracle_job_id
        and artifact_hash not in {None, UNKNOWN}
        and oracle_artifact_hash not in {None, UNKNOWN}
        and oracle_artifact_hash == artifact_hash
        and _oracle_evaluable(oracle)
        and not _oracle_contradiction(oracle)
        and approval in {"valid", "not_required"}
    )
    if execution_verified:
        verification_reason = "independent_execution_and_artifact_evidence_satisfy_all_required_bindings"
    else:
        verification_reason = "required_independent_execution_artifact_job_or_approval_evidence_is_incomplete"

    state = {
        "submission_state": submission,
        "execution_state": execution,
        "evidence_state": evidence,
        "recovery_state": recovery,
        "domain_verdict": domain,
        "approval_state": approval,
        "execution_verified": execution_verified,
        "execution_verified_reason": verification_reason,
    }
    return state, reasons


def _oracle_execution(oracle: dict[str, object] | None) -> tuple[str, str]:
    if oracle is None:
        return UNKNOWN, "independent_oracle_missing; reported_product_state_not_used_as_execution_truth"
    explicit = oracle.get("execution_state")
    contradiction = _oracle_contradiction(oracle)
    if contradiction is not None:
        return UNKNOWN, f"oracle_contradictory:{contradiction}"
    if isinstance(explicit, str) and explicit in _EXECUTION_STATES:
        if explicit == UNKNOWN:
            return UNKNOWN, "oracle_explicitly_reports_unknown_execution"
        return explicit, "execution_state_supplied_by_independent_oracle"
    started = _count_or_bool(oracle, "execution_started", "execution_started_count")
    finished = _count_or_bool(oracle, "execution_finished", "execution_finished_count")
    if started and not finished:
        return UNKNOWN, "oracle_observed_execution_start_without_completion_signal"
    if started and finished:
        return "failed" if oracle.get("execution_failed") is True else "succeeded", "derived_from_independent_oracle_start_and_finish_events"
    if "execution_started" in oracle or "execution_started_count" in oracle or "execution_instances" in oracle:
        return "not_started", "oracle_observed_no_execution_start"
    return UNKNOWN, "oracle_has_no_execution_truth"


def _oracle_evaluable(oracle: dict[str, object] | None) -> bool:
    if not isinstance(oracle, dict):
        return False
    value = oracle.get("oracle_evaluable")
    if isinstance(value, bool):
        return value
    started = _integer_count(oracle, "execution_started", "execution_started_count")
    finished = _integer_count(oracle, "execution_finished", "execution_finished_count")
    if started is None or finished is None or started != finished:
        return False
    instances = oracle.get("execution_instances")
    return not isinstance(instances, list) or len(instances) == started


def _oracle_contradiction(oracle: dict[str, object] | None) -> str | None:
    if not isinstance(oracle, dict):
        return None
    explicit = oracle.get("execution_state")
    if explicit is not None and explicit not in _EXECUTION_STATES:
        return "execution_state_invalid"
    evaluable = oracle.get("oracle_evaluable")
    if evaluable is not None and not isinstance(evaluable, bool):
        return "oracle_evaluable_invalid"
    started = _integer_count(oracle, "execution_started", "execution_started_count")
    finished = _integer_count(oracle, "execution_finished", "execution_finished_count")
    if started is not None and finished is not None:
        if started < 0 or finished < 0 or finished > started:
            return "lifecycle_counts_inconsistent"
        if explicit in {"succeeded", "failed"} and (started == 0 or finished != started):
            return "terminal_state_without_balanced_lifecycle"
        if explicit == "not_started" and started != 0:
            return "not_started_with_execution_start"
    if evaluable is False and explicit in {"succeeded", "failed"}:
        return "terminal_state_marked_not_evaluable"
    instances = oracle.get("execution_instances")
    if isinstance(instances, list) and started is not None and len(instances) != started:
        return "execution_instance_count_mismatch"
    explicit_job = oracle.get("job_id")
    job_ids = oracle.get("job_ids")
    if explicit_job is not None and isinstance(job_ids, list) and explicit_job not in job_ids:
        return "job_id_not_in_observed_job_ids"
    return None


def _count_or_bool(value: dict[str, object], bool_key: str, count_key: str) -> bool:
    if value.get(bool_key) is True:
        return True
    count = value.get(count_key)
    return isinstance(count, int) and not isinstance(count, bool) and count > 0


def _integer_count(value: dict[str, object], direct_key: str, count_key: str) -> int | None:
    for key in (direct_key, count_key):
        candidate = value.get(key)
        if isinstance(candidate, int) and not isinstance(candidate, bool):
            return candidate
    return None


def _evidence_state(
    record: dict[str, object],
    reported: dict[str, object],
    oracle: dict[str, object] | None,
    artifact_hash: object,
    oracle_artifact_hash: object,
    job_id: object,
    oracle_job_id: object,
) -> tuple[str, str]:
    if (
        job_id not in {None, UNKNOWN}
        and oracle_job_id not in {None, UNKNOWN}
        and job_id != oracle_job_id
    ):
        return "mismatch", "reported_job_id_differs_from_oracle_job_id"
    if (
        artifact_hash not in {None, UNKNOWN}
        and oracle_artifact_hash not in {None, UNKNOWN}
        and artifact_hash != oracle_artifact_hash
    ):
        return "mismatch", "reported_artifact_hash_differs_from_oracle_artifact_hash"
    validation = record.get("artifact_validation")
    if not isinstance(validation, dict):
        validation = reported.get("artifact_validation")
    if isinstance(validation, dict):
        status = validation.get("status")
        if status == "mismatch":
            return "mismatch", "artifact_validation_reports_mismatch"
        if status == "verified":
            if validation.get("independent") is True:
                return "verified", "independent_artifact_validator_reports_verified"
            return "partial", "product_validator_is_not_an_independent_oracle"
        if status == "partial":
            return "partial", "artifact_validation_reports_partial"
        if status == "missing":
            return "missing", "artifact_validation_reports_missing"
    if artifact_hash in {None, UNKNOWN}:
        return "missing", "artifact_hash_missing"
    return "partial", "artifact_hash_exists_without_independent_validation"


def _recovery_state(reported: dict[str, object], execution: str) -> tuple[str, str]:
    if reported.get("state") in {"unresolved", "interrupted"}:
        return "required", "reported_state_requires_recovery_or_reconciliation"
    active = reported.get("active_attempt")
    if isinstance(active, dict) and active.get("status") == "running":
        return "reconciling", "active_attempt_is_still_running"
    if execution == UNKNOWN:
        return "required", "oracle_execution_is_not_resolved"
    if reported.get("state") == UNKNOWN:
        return UNKNOWN, "reported_state_is_explicitly_unknown"
    return "not_needed", "no_unresolved_report_or_oracle_gap"


def _dimension_value(
    record: dict[str, object],
    reported: dict[str, object],
    key: str,
    allowed: frozenset[str],
    default: str,
    default_reason: str,
) -> tuple[str, str]:
    value = record.get(key, reported.get(key, _MISSING))
    if value is _MISSING:
        return default, default_reason
    if isinstance(value, str) and value in allowed:
        return value, f"provided_{key}"
    return UNKNOWN, f"{key}_missing_or_invalid"


if __name__ == "__main__":
    raise SystemExit(main())
