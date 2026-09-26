"""Four-case controller for the reviewed Windows/ComfyUI F00/F02 pilot.

This is deliberately research-only orchestration.  It never starts or stops a
backend, never calls a model API itself, and refuses to invoke a product client
until the reservation-first preflight has returned ``PASS``.  The only backend
traffic it introduces after a pass is the reviewed loopback proxy's allowlist
and the observer's read-only WebSocket/history requests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import argparse
import json
from pathlib import Path
import os
import re
import subprocess
import time
from typing import Callable, Mapping, Sequence

from scripts.research.f02_loopback import OneShotLoopbackFaultProxy, ProxyReceipt
from scripts.research.f02_oracle import ComfyUIEventOracle, OracleDecision
from scripts.research.f02_preflight import PreflightReport, run_preflight


B2_SHA = "da65d57047b5a59e3403b49adf4605a1c0497c58"
W3_SHA = "d45173af75d404ad79dc14568edd4c45f654abd2"
CASE_ORDER: tuple[tuple[str, str], ...] = (
    ("B2", "F00"),
    ("W3", "F00"),
    ("B2", "F02"),
    ("W3", "F02"),
)
_REQUEST_FIELDS = (
    "canonical_request_digest",
    "compiled_prompt_digest",
    "workflow_graph_digest",
    "input_digest",
    "route_identity",
    "validator_version",
)
_CLIENT_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_CLIENT_ERROR_STAGES = frozenset({
    "initialize", "private_catalog", "model_route", "start_run", "read_run",
    "generate_round", "artifact_validation", "route_probe", "catalog_probe", "launch",
})


class CampaignConfigurationError(ValueError):
    """Raised before a campaign can acquire backend or GPU-facing resources."""


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    system: str
    fault_mode: str
    command: tuple[str, ...]
    working_directory: str
    research_model_path: str
    output_root: str
    operation_key: str


@dataclass(frozen=True)
class ProductCallOutcome:
    exit_code: int | None
    timed_out: bool
    reported_state: str
    result: dict[str, object] | None
    stdout_sha256: str
    stderr_sha256: str
    failure: str | None


@dataclass(frozen=True)
class CaseRecord:
    case_id: str
    system: str
    fault_mode: str
    status: str
    stop_reason: str | None
    product_call_count: int
    proxy_prompt_count: int
    backend_acceptance_count: int
    unique_execution_start_count: int | None
    execution_finish_count: int | None
    artifact_count: int | None
    classifications: dict[str, int | str]
    product_calls: tuple[dict[str, object], ...]
    proxy_receipts: tuple[dict[str, object], ...]
    oracle: dict[str, object]
    request_matches_frozen: bool
    product_command_sha256: str
    working_directory_sha256: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CampaignReport:
    status: str
    preflight: dict[str, object]
    records: tuple[CaseRecord, ...]
    stop_reason: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "preflight": self.preflight,
            "records": [record.as_dict() for record in self.records],
            "stop_reason": self.stop_reason,
        }


ProductInvoker = Callable[[CaseSpec, int, str, float], ProductCallOutcome]
PreflightRunner = Callable[[dict[str, object]], PreflightReport]


def run_campaign(
    config: dict[str, object],
    *,
    preflight_runner: PreflightRunner = run_preflight,
    product_invoker: ProductInvoker | None = None,
    proxy_factory: Callable[..., OneShotLoopbackFaultProxy] = OneShotLoopbackFaultProxy,
    oracle_factory: Callable[..., ComfyUIEventOracle] = ComfyUIEventOracle,
    monotonic: Callable[[], float] = time.monotonic,
) -> CampaignReport:
    """Run the fixed four-case schedule only after the read-only preflight passes.

    A non-evaluable F00 prevents both F02 cases from making a product call.  If
    an F02 first call has an accepted-but-hidden response yet lacks a bindable
    finish within the 180-second observer window, that *case* is downgraded to
    submission-level evidence and its second call is not made.  No code path
    issues a retry, third call, F03 case, or backend/service lifecycle action.
    """
    preflight_config, campaign, case_specs, frozen_request, evidence_path = _parse_config(config)
    preflight = preflight_runner(preflight_config)
    if preflight.status != "PASS":
        # In particular, this path does not create the evidence file.  The
        # preflight's reservation check is intentionally before hardware and
        # backend observations.
        return CampaignReport("PRECHECK_FAILED", preflight.as_dict(), (), "preflight_not_pass")
    if not preflight.backend_boot_identity:
        return CampaignReport("PRECHECK_FAILED", preflight.as_dict(), (), "backend_boot_identity_missing")

    invoker = product_invoker or _invoke_subprocess
    records: list[CaseRecord] = []
    f00_ok = True
    for system in ("B2", "W3"):
        spec = case_specs[f"{system}_F00"]
        record = _run_case(
            spec,
            backend_url=_backend_url(preflight_config),
            backend_boot_identity=preflight.backend_boot_identity,
            frozen_request=frozen_request,
            allow_second_call=False,
            product_invoker=invoker,
            proxy_factory=proxy_factory,
            oracle_factory=oracle_factory,
            monotonic=monotonic,
        )
        records.append(record)
        f00_ok = f00_ok and record.request_matches_frozen and record.oracle.get("status") == "evaluable"
        _append_evidence(evidence_path, preflight, record)

    if not f00_ok:
        for system in ("B2", "W3"):
            spec = case_specs[f"{system}_F02"]
            record = _not_run_record(
                spec,
                "F00 oracle or frozen-request comparison was not evaluable; execution-metric F02 is stopped",
            )
            records.append(record)
            _append_evidence(evidence_path, preflight, record)
        return CampaignReport("DOWNGRADED_SUBMISSION_ONLY", preflight.as_dict(), tuple(records), "f00_oracle_not_evaluable")

    for system in ("B2", "W3"):
        spec = case_specs[f"{system}_F02"]
        record = _run_case(
            spec,
            backend_url=_backend_url(preflight_config),
            backend_boot_identity=preflight.backend_boot_identity,
            frozen_request=frozen_request,
            allow_second_call=True,
            product_invoker=invoker,
            proxy_factory=proxy_factory,
            oracle_factory=oracle_factory,
            monotonic=monotonic,
        )
        records.append(record)
        _append_evidence(evidence_path, preflight, record)
        if record.oracle.get("status") != "evaluable":
            remaining_systems = ("W3",) if system == "B2" else ()
            for remaining_system in remaining_systems:
                remaining_spec = case_specs[f"{remaining_system}_F02"]
                remaining_record = _not_run_record(
                    remaining_spec,
                    "F02 oracle became not_evaluable; remaining execution-metric cases stopped",
                )
                records.append(remaining_record)
                _append_evidence(evidence_path, preflight, remaining_record)
            return CampaignReport(
                "DOWNGRADED_SUBMISSION_ONLY",
                preflight.as_dict(),
                tuple(records),
                "f02_oracle_not_evaluable",
            )

    submission_only = any(record.status == "submission_only" for record in records)
    return CampaignReport(
        "COMPLETED_SUBMISSION_ONLY" if submission_only else "COMPLETED",
        preflight.as_dict(),
        tuple(records),
        None,
    )


def _run_case(
    spec: CaseSpec,
    *,
    backend_url: str,
    backend_boot_identity: str,
    frozen_request: dict[str, str],
    allow_second_call: bool,
    product_invoker: ProductInvoker,
    proxy_factory: Callable[..., OneShotLoopbackFaultProxy],
    oracle_factory: Callable[..., ComfyUIEventOracle],
    monotonic: Callable[[], float],
) -> CaseRecord:
    case_started = monotonic()
    deadline = case_started + 900.0
    calls: list[ProductCallOutcome] = []
    decisions: list[OracleDecision] = []
    stop_reason: str | None = None
    status = "completed"

    with proxy_factory(backend_url, fault_mode=spec.fault_mode, timeout_seconds=30.0) as proxy:
        observer_id = f"f02-pilot-{_safe_token(spec.case_id)}-{sha256(spec.operation_key.encode()).hexdigest()[:12]}"
        oracle = oracle_factory(
            backend_url,
            backend_boot_identity=backend_boot_identity,
            observer_id=observer_id,
            timeout_seconds=5.0,
        )
        try:
            oracle.connect()
        except Exception as exc:  # Observer setup is a case stop, not a backend repair.
            stop_reason = f"observer_connect_failed:{type(exc).__name__}"
            status = "not_run"
            return _case_record(spec, status, stop_reason, calls, proxy.receipts, decisions, frozen_request)
        try:
            calls.append(product_invoker(spec, 1, proxy.base_url, _remaining(deadline, monotonic)))
            first_receipts = _prompt_receipts(proxy.receipts)
            first_ids = [receipt.accepted_job_id for receipt in first_receipts if receipt.accepted_job_id]
            if len(first_receipts) != 1 or len(first_ids) != 1:
                stop_reason = "first_call_did_not_produce_exactly_one_backend_acceptance"
                status = "submission_only" if first_receipts else "not_evaluable"
                return _case_record(spec, status, stop_reason, calls, proxy.receipts, decisions, frozen_request)

            if spec.fault_mode == "F02" and not first_receipts[0].response_dropped:
                stop_reason = "F02_first_backend_acceptance_was_not_hidden"
                return _case_record(spec, "not_evaluable", stop_reason, calls, proxy.receipts, decisions, frozen_request)

            try:
                first_decision = oracle.observe_until(
                    first_ids,
                    deadline_monotonic=min(deadline, monotonic() + 180.0),
                )
            except Exception as exc:
                stop_reason = f"oracle_observation_failed:{type(exc).__name__}"
                return _case_record(spec, "not_evaluable", stop_reason, calls, proxy.receipts, decisions, frozen_request)
            decisions.append(first_decision)
            if spec.fault_mode == "F00":
                if not first_decision.oracle_evaluable:
                    stop_reason = "F00_oracle_not_evaluable"
                    status = "not_evaluable"
                return _case_record(spec, status, stop_reason, calls, proxy.receipts, decisions, frozen_request)

            # The response-loss arm can make its second *product* call only
            # after the first backend execution has a bindable completion.
            if not first_decision.oracle_evaluable:
                stop_reason = "F02_first_execution_not_bindable_within_observer_window"
                return _case_record(spec, "submission_only", stop_reason, calls, proxy.receipts, decisions, frozen_request)
            if not allow_second_call:
                return _case_record(spec, "submission_only", "second_call_not_authorized", calls, proxy.receipts, decisions, frozen_request)

            before_second = len(_prompt_receipts(proxy.receipts))
            calls.append(product_invoker(spec, 2, proxy.base_url, _remaining(deadline, monotonic)))
            all_prompt_receipts = _prompt_receipts(proxy.receipts)
            second_receipts = all_prompt_receipts[before_second:]
            if len(second_receipts) > 1:
                stop_reason = "second_call_created_more_than_one_backend_submission"
                return _case_record(spec, "not_evaluable", stop_reason, calls, proxy.receipts, decisions, frozen_request)
            if not second_receipts:
                # This is sound local blocked-resubmission evidence only.  It
                # intentionally makes no execution-count claim.
                return _case_record(spec, "submission_only", "second_call_blocked_before_proxy", calls, proxy.receipts, decisions, frozen_request)
            second_id = second_receipts[0].accepted_job_id
            if not second_id:
                return _case_record(spec, "not_evaluable", "second_backend_acceptance_missing_job_id", calls, proxy.receipts, decisions, frozen_request)
            try:
                second_decision = oracle.observe_until(
                    [second_id],
                    deadline_monotonic=min(deadline, monotonic() + 180.0),
                )
            except Exception as exc:
                stop_reason = f"oracle_observation_failed:{type(exc).__name__}"
                return _case_record(spec, "not_evaluable", stop_reason, calls, proxy.receipts, decisions, frozen_request)
            decisions.append(second_decision)
            if not second_decision.oracle_evaluable:
                stop_reason = "F02_second_execution_not_bindable_within_observer_window"
                status = "submission_only"
            return _case_record(spec, status, stop_reason, calls, proxy.receipts, decisions, frozen_request)
        except TimeoutError:
            return _case_record(spec, "timeout", "case_hard_timeout", calls, proxy.receipts, decisions, frozen_request)
        finally:
            oracle.close()


def _case_record(
    spec: CaseSpec,
    status: str,
    stop_reason: str | None,
    calls: Sequence[ProductCallOutcome],
    receipts: Sequence[ProxyReceipt],
    decisions: Sequence[OracleDecision],
    frozen_request: dict[str, str],
) -> CaseRecord:
    prompt_receipts = _prompt_receipts(receipts)
    bindings = [binding for decision in decisions for binding in decision.bindings]
    artifact_fingerprints = {
        sha256(path.encode("utf-8")).hexdigest()
        for binding in bindings for path in binding.artifact_paths
    }
    request_matches = bool(calls) and all(_matches_frozen(call.result, frozen_request, spec.operation_key) for call in calls)
    oracle_status = _oracle_status(decisions)
    classifications: dict[str, int | str] = {
        "scheduled": 1,
        "started": int(bool(calls)),
        "injection_confirmed": "N/A" if spec.fault_mode == "F00" else int(any(receipt.response_dropped for receipt in prompt_receipts)),
        "oracle_evaluable": int(bool(decisions) and all(decision.oracle_evaluable for decision in decisions)),
        "resolved": int(any(call.reported_state == "resolved" for call in calls)),
        "unresolved": int(any(call.reported_state == "unresolved" for call in calls)),
        "failed": int(any(call.reported_state == "failed" or call.exit_code not in (0, None) or call.timed_out for call in calls)),
        "not_run": int(not calls),
    }
    return CaseRecord(
        case_id=spec.case_id,
        system=spec.system,
        fault_mode=spec.fault_mode,
        status=status,
        stop_reason=stop_reason,
        product_call_count=len(calls),
        proxy_prompt_count=len(prompt_receipts),
        backend_acceptance_count=sum(receipt.accepted_job_id is not None for receipt in prompt_receipts),
        unique_execution_start_count=len({binding.execution_instance_id for binding in bindings}) if decisions else None,
        execution_finish_count=len(bindings) if decisions else None,
        artifact_count=len(artifact_fingerprints) if decisions else None,
        classifications=classifications,
        product_calls=tuple(_sanitize_call(call) for call in calls),
        proxy_receipts=tuple(_sanitize_receipt(receipt) for receipt in prompt_receipts),
        oracle=_sanitize_oracle(decisions, oracle_status),
        request_matches_frozen=request_matches,
        product_command_sha256=_digest_text("\x00".join(spec.command)),
        working_directory_sha256=_digest_text(spec.working_directory),
    )


def _not_run_record(spec: CaseSpec, reason: str) -> CaseRecord:
    return CaseRecord(
        case_id=spec.case_id,
        system=spec.system,
        fault_mode=spec.fault_mode,
        status="not_run",
        stop_reason=reason,
        product_call_count=0,
        proxy_prompt_count=0,
        backend_acceptance_count=0,
        unique_execution_start_count=None,
        execution_finish_count=None,
        artifact_count=None,
        classifications={
            "scheduled": 1, "started": 0,
            "injection_confirmed": "N/A" if spec.fault_mode == "F00" else 0,
            "oracle_evaluable": 0, "resolved": 0, "unresolved": 0,
            "failed": 0, "not_run": 1,
        },
        product_calls=(),
        proxy_receipts=(),
        oracle={"status": "not_evaluable", "reason": reason, "bindings": [], "event_counts": {}},
        request_matches_frozen=False,
        product_command_sha256=_digest_text("\x00".join(spec.command)),
        working_directory_sha256=_digest_text(spec.working_directory),
    )


def _invoke_subprocess(spec: CaseSpec, call_index: int, proxy_url: str, timeout_seconds: float) -> ProductCallOutcome:
    if timeout_seconds <= 0:
        raise TimeoutError("case hard timeout elapsed before product call")
    env = os.environ.copy()
    env.update({
        "LOCAL_GPU_IMAGEGEN_COMFYUI_URL": proxy_url,
        "LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED": "0",
        "LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS": "0",
        "LOCAL_GPU_IMAGEGEN_OUTPUT_DIR": spec.output_root,
        "LOCAL_GPU_IMAGEGEN_OUTPUT_ROOT": spec.output_root,
        "LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH": spec.research_model_path,
        "LOCAL_GPU_IMAGEGEN_F02_CASE_ID": spec.case_id,
        "LOCAL_GPU_IMAGEGEN_F02_FAULT_MODE": spec.fault_mode,
        "LOCAL_GPU_IMAGEGEN_F02_CALL_INDEX": str(call_index),
        "LOCAL_GPU_IMAGEGEN_F02_OPERATION_KEY": spec.operation_key,
    })
    try:
        result = subprocess.run(
            list(spec.command), cwd=spec.working_directory, env=env, check=False,
            capture_output=True, text=True, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr)
        return ProductCallOutcome(None, True, "failed", None, _digest_text(stdout), _digest_text(stderr), "product_call_timeout")
    except OSError as exc:
        return ProductCallOutcome(None, False, "failed", None, _digest_text(""), _digest_text(""), f"product_call_oserror:{type(exc).__name__}")
    parsed, failure = _parse_product_result(result.stdout)
    state = _reported_state(parsed, result.returncode)
    return ProductCallOutcome(result.returncode, False, state, parsed, _digest_text(result.stdout), _digest_text(result.stderr), failure)


def _parse_config(config: dict[str, object]) -> tuple[dict[str, object], dict[str, object], dict[str, CaseSpec], dict[str, str], Path]:
    if not isinstance(config, dict):
        raise CampaignConfigurationError("campaign configuration must be an object")
    preflight = _mapping(config.get("preflight"), "preflight")
    campaign = _mapping(config.get("campaign"), "campaign")
    if campaign.get("observer_window_seconds") != 180 or campaign.get("case_hard_timeout_seconds") != 900:
        raise CampaignConfigurationError("reviewed campaign requires observer_window_seconds=180 and case_hard_timeout_seconds=900")
    evidence_text = _text(campaign.get("evidence_file"), "campaign.evidence_file")
    frozen = _mapping(campaign.get("frozen_request"), "campaign.frozen_request")
    frozen_request = {field: _text(frozen.get(field), f"campaign.frozen_request.{field}") for field in _REQUEST_FIELDS}
    for field in _REQUEST_FIELDS[:4]:
        if not _sha256_hex(frozen_request[field]):
            raise CampaignConfigurationError(f"campaign.frozen_request.{field} must be a SHA-256 digest")
    commands = _mapping(campaign.get("client_commands"), "campaign.client_commands")
    output_roots = _mapping(campaign.get("output_roots"), "campaign.output_roots")
    operation_keys = _mapping(campaign.get("operation_keys"), "campaign.operation_keys")
    clients = _mapping(preflight.get("clients"), "preflight.clients")
    environment = _mapping(preflight.get("environment"), "preflight.environment")
    research_model_path = _text(environment.get("model_path"), "preflight.environment.model_path")
    specs: dict[str, CaseSpec] = {}
    for system, fault in CASE_ORDER:
        case_id = f"{system}_{fault}"
        client = _mapping(clients.get(system), f"preflight.clients.{system}")
        expected = B2_SHA if system == "B2" else W3_SHA
        if _text(client.get("sha"), f"preflight.clients.{system}.sha") != expected:
            raise CampaignConfigurationError(f"{system} must remain bound to frozen SHA {expected}")
        command_value = commands.get(system)
        if not isinstance(command_value, list) or not command_value or not all(isinstance(item, str) and item for item in command_value):
            raise CampaignConfigurationError(f"campaign.client_commands.{system} must be a non-empty argv list")
        specs[case_id] = CaseSpec(
            case_id=case_id, system=system, fault_mode=fault, command=tuple(command_value),
            working_directory=_text(client.get("root"), f"preflight.clients.{system}.root"),
            research_model_path=research_model_path,
            output_root=_text(output_roots.get(case_id), f"campaign.output_roots.{case_id}"),
            operation_key=_text(operation_keys.get(case_id), f"campaign.operation_keys.{case_id}"),
        )
    _validate_fresh_roots(preflight, specs)
    return preflight, campaign, specs, frozen_request, Path(evidence_text)


def _validate_fresh_roots(preflight: dict[str, object], specs: Mapping[str, CaseSpec]) -> None:
    declared = _mapping(preflight.get("fresh_output_roots"), "preflight.fresh_output_roots")
    roots = {spec.output_root for spec in specs.values()}
    if len(roots) != 4:
        raise CampaignConfigurationError("each of the four scheduled cases requires a distinct fresh output root")
    if set(declared) != set(specs):
        raise CampaignConfigurationError("preflight.fresh_output_roots must declare exactly B2_F00, W3_F00, B2_F02, W3_F02")
    for case_id, spec in specs.items():
        if _text(declared.get(case_id), f"preflight.fresh_output_roots.{case_id}") != spec.output_root:
            raise CampaignConfigurationError(f"preflight output root mismatch for {case_id}")


def _backend_url(preflight: dict[str, object]) -> str:
    environment = _mapping(preflight.get("environment"), "preflight.environment")
    return _text(environment.get("backend_url"), "preflight.environment.backend_url")


def _prompt_receipts(receipts: Sequence[ProxyReceipt]) -> list[ProxyReceipt]:
    return [receipt for receipt in receipts if receipt.method == "POST" and receipt.path.split("?", 1)[0] == "/prompt"]


def _matches_frozen(result: dict[str, object] | None, frozen: Mapping[str, str], operation_key: str) -> bool:
    if not isinstance(result, dict) or result.get("operation_key") != operation_key:
        return False
    return all(result.get(field) == value for field, value in frozen.items())


def _oracle_status(decisions: Sequence[OracleDecision]) -> str:
    if not decisions:
        return "not_evaluable"
    return "evaluable" if all(decision.oracle_evaluable for decision in decisions) else "not_evaluable"


def _sanitize_call(call: ProductCallOutcome) -> dict[str, object]:
    result = call.result or {}
    sanitized = {
        "exit_code": call.exit_code,
        "timed_out": call.timed_out,
        "reported_state": call.reported_state,
        "stdout_sha256": call.stdout_sha256,
        "stderr_sha256": call.stderr_sha256,
        "failure": call.failure,
        "result_digests": {field: result.get(field) for field in _REQUEST_FIELDS if isinstance(result.get(field), str)},
        "artifact_hashes": [value for value in result.get("artifact_hashes", []) if isinstance(value, str) and _sha256_hex(value)] if isinstance(result.get("artifact_hashes"), list) else [],
    }
    error_code = result.get("client_error_code")
    if result.get("client_error_schema_version") == 1 and isinstance(error_code, str) and _CLIENT_ERROR_CODE.fullmatch(error_code):
        sanitized["client_error_schema_version"] = 1
        sanitized["client_error_code"] = error_code
    error_stage = result.get("client_error_stage")
    if isinstance(error_stage, str) and error_stage in _CLIENT_ERROR_STAGES:
        sanitized["client_error_stage"] = error_stage
    return sanitized


def _sanitize_receipt(receipt: ProxyReceipt) -> dict[str, object]:
    return {
        "sequence": receipt.sequence,
        "received_at": receipt.received_at,
        "method": receipt.method,
        "path": receipt.path,
        "body_sha256": receipt.body_sha256,
        "body_bytes": receipt.body_bytes,
        "upstream_status": receipt.upstream_status,
        "response_dropped": receipt.response_dropped,
        "forwarded": receipt.forwarded,
        "failure": receipt.failure,
        # Prompt IDs remain oracle-only; public/sanitized case evidence carries
        # an irreversible reference, never the identifier itself.
        "oracle_job_id_sha256": sha256(receipt.accepted_job_id.encode("utf-8")).hexdigest() if receipt.accepted_job_id else None,
    }


def _sanitize_oracle(decisions: Sequence[OracleDecision], status: str) -> dict[str, object]:
    event_counts: dict[str, int] = {}
    bindings: list[dict[str, object]] = []
    reasons: list[str] = []
    for decision in decisions:
        reasons.append(_sanitize_reason(decision.reason))
        for event in decision.raw_events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        for binding in decision.bindings:
            bindings.append({
                "execution_instance_id": binding.execution_instance_id,
                "started_at": binding.started_at,
                "finished_at": binding.finished_at,
                "terminal_event": binding.terminal_event,
                "history_completed": binding.history_completed,
                "artifact_path_sha256": [sha256(path.encode("utf-8")).hexdigest() for path in binding.artifact_paths],
            })
    return {"status": status, "reason": ";".join(reasons), "bindings": bindings, "event_counts": event_counts}


def _sanitize_reason(reason: str) -> str:
    """Keep reason codes while replacing any prompt-ID suffix with a digest."""
    sanitized: list[str] = []
    for part in reason.split(";"):
        if ":" not in part:
            sanitized.append(part)
            continue
        code, value = part.split(":", 1)
        sanitized.append(f"{code}:job_id_sha256={sha256(value.encode('utf-8')).hexdigest()}")
    return ";".join(sanitized)


def _append_evidence(path: Path, preflight: PreflightReport, record: CaseRecord) -> None:
    # This happens only after PASS.  The path's parent must already exist so the
    # controller never creates a campaign/output directory as a side effect.
    if not path.parent.is_dir():
        raise CampaignConfigurationError("campaign.evidence_file parent must already exist")
    payload = {
        "schema": "f02-pilot-case-evidence-v1",
        "preflight_checked_at": preflight.checked_at,
        "backend_boot_identity": preflight.backend_boot_identity,
        "case": record.as_dict(),
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")


def _parse_product_result(stdout: str) -> tuple[dict[str, object] | None, str | None]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, "product_result_missing"
    try:
        value = json.loads(lines[-1])
    except json.JSONDecodeError:
        return None, "product_result_not_json"
    if not isinstance(value, dict):
        return None, "product_result_not_object"
    return value, None


def _reported_state(result: dict[str, object] | None, exit_code: int) -> str:
    if isinstance(result, dict) and result.get("reported_state") in {"resolved", "unresolved", "failed"}:
        return str(result["reported_state"])
    return "failed" if exit_code != 0 else "unresolved"


def _remaining(deadline: float, monotonic: Callable[[], float]) -> float:
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise TimeoutError("case hard timeout elapsed")
    return remaining


def _mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise CampaignConfigurationError(f"{name} must be an object")
    return value


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CampaignConfigurationError(f"{name} must be a non-empty string")
    return value


def _sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value.lower())


def _safe_token(value: str) -> str:
    return "".join(character if character.isalnum() or character in "-_" else "-" for character in value)


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the reviewed F00/F02 research pilot after preflight PASS.")
    parser.add_argument("config", help="private reviewed JSON configuration; do not commit it")
    args = parser.parse_args(argv)
    try:
        with Path(args.config).open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        if not isinstance(config, dict):
            raise CampaignConfigurationError("top-level configuration must be an object")
        report = run_campaign(config)
    except (CampaignConfigurationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "CONFIG_ERROR", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report.as_dict(), sort_keys=True))
    return 0 if report.status == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
