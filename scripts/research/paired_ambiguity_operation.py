"""One paired-v1 operation controller, without backend lifecycle ownership.

This is a component, not a Windows launcher. The reserved six-operation runner
must own cache/start/reset/cleanup, source freeze and an active preflight before
using it. It never consults observer completion to decide when to retry.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import time

from scripts.research.f02_capture import write_private_json
from scripts.research.f02_campaign import _invoke_subprocess
from scripts.research.f02_loopback import OneShotLoopbackFaultProxy
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.f02_product_client import _digest
from scripts.research.paired_ambiguity import PROTOCOL, prompt_metrics, run_schedule, semantic_digest


def run_operation(spec, *, evidence_root: Path, boot_identity: str, deadline: float,
                  invoker=_invoke_subprocess, proxy_factory=OneShotLoopbackFaultProxy,
                  oracle_factory=ComfyUIEventOracle, clock=time.monotonic, sleep=time.sleep):
    if spec.retry_scope != "paired_same_run" or spec.system not in {"B2", "W3"}:
        raise ValueError("paired operation requires native B2/W3 and paired_same_run caller")
    if evidence_root.exists() or Path(spec.private_capture_root).exists():
        raise FileExistsError("operation evidence/client roots must be fresh")
    if deadline <= clock() or not boot_identity:
        raise ValueError("active deadline and observed backend identity required")
    evidence_root.mkdir(mode=0o700)
    outcomes, calls, decision = [], [], None
    reason, schedule_reason = None, None
    metrics = None
    proof = {"F02_acceptance_suppressed": False, "FPRE_first_no_send": False}
    source_names = ("paired_ambiguity_operation.py", "paired_ambiguity.py", "f02_product_client.py",
                    "f02_campaign.py", "f02_capture.py", "f02_loopback.py", "f02_oracle.py",
                    "f02_transport_launcher.py", "f02_transport_shim.py")
    sources = evidence_root / "sources"
    sources.mkdir()
    hashes = {}
    for name in source_names:
        content = Path(__file__).with_name(name).read_bytes()
        (sources / name).write_bytes(content)
        hashes[name] = sha256(content).hexdigest()
    write_private_json(evidence_root, "source-freeze.json", hashes)
    with proxy_factory(spec.backend_url, fault_mode=spec.fault_mode,
                       stage_log_path=evidence_root / "proxy-stages.jsonl") as proxy:
        oracle = oracle_factory(spec.backend_url, backend_boot_identity=boot_identity,
                                observer_id=spec.operation_key, timeout_seconds=1,
                                retain_raw_transport=True)
        try:
            oracle.connect()

            def invoke(index, remaining):
                outcome = invoker(spec, index, proxy.base_url, remaining)
                outcomes.append(outcome)
                write_private_json(evidence_root, f"call-{index}-process.json", asdict(outcome))
                if outcome.timed_out or outcome.exit_code != 0 or not isinstance(outcome.result, dict):
                    raise ValueError("product_invocation_failed")
                if index == 1:
                    received = [r for r in proxy.evidence() if r["method"] == "POST" and r["path"] == "/prompt"]
                    if len(received) != 1:
                        raise ValueError("first_prompt_submission_not_unique")
                    first_stages = [s["stage"] for s in proxy.stages
                                    if s["request_sequence"] == received[0]["request_sequence"]]
                    if spec.fault_mode == "F02" and not (received[0]["accepted_job_id"]
                            and "accepted_response_suppressed" in first_stages):
                        raise ValueError("f02_injection_not_confirmed_before_retry")
                    if spec.fault_mode == "FPRE" and not ("fault_injected_before_upstream" in first_stages
                            and "connection_closed" in first_stages and "upstream_send_started" not in first_stages):
                        raise ValueError("fpre_injection_not_confirmed_before_retry")
                return outcome.result

            calls, schedule_reason = run_schedule(invoke, fault=spec.fault_mode, strategy=spec.system,
                                                   deadline=deadline, clock=clock, sleep=sleep)
            client = Path(spec.private_capture_root)
            session = json.loads((client / "session.json").read_text())
            for index, call in enumerate(calls, 1):
                before = json.loads((client / f"call-{index}-before.json").read_text())
                after = json.loads((client / f"call-{index}-after.json").read_text())
                request = json.loads((client / f"call-{index}-generation-request.json").read_text())
                if (not call.get("generation_rpc_entered")
                        or request["arguments"] != session["generate_arguments"]
                        or before["run_id"] != session["run_id"] or after["run_id"] != session["run_id"]
                        or _digest(before["request"]) != session["request_sha256"]
                        or _digest(after["request"]) != session["request_sha256"]):
                    raise ValueError("generation_path_or_run_changed")
                for phase in ("before", "after"):
                    payload = (client / f"call-{index}-{phase}.json").read_bytes()
                    if sha256(payload).hexdigest() != call[f"manifest_{phase}_sha256"]:
                        raise ValueError("manifest_capture_changed")
            if spec.fault_mode != "F00" and schedule_reason != "retried_same_run":
                raise ValueError("fault_did_not_produce_retryable_caller_unknown")
            receipts = [r for r in proxy.evidence() if r["method"] == "POST" and r["path"] == "/prompt"]
            if not receipts or len(receipts) > (1 if spec.fault_mode == "F00" else 2):
                raise ValueError("prompt_submission_budget_or_path_failed")
            first = receipts[0]["request_sequence"]
            stages = [s["stage"] for s in proxy.stages if s["request_sequence"] == first]
            proof["F02_acceptance_suppressed"] = bool(receipts[0]["accepted_job_id"] and
                                                       "accepted_response_suppressed" in stages)
            proof["FPRE_first_no_send"] = ("fault_injected_before_upstream" in stages
                                           and "connection_closed" in stages and "upstream_send_started" not in stages)
            if spec.fault_mode == "F02" and not proof["F02_acceptance_suppressed"]:
                raise ValueError("f02_injection_not_confirmed")
            if spec.fault_mode == "FPRE" and not proof["FPRE_first_no_send"]:
                raise ValueError("fpre_injection_not_confirmed")
            metrics = prompt_metrics(proxy.evidence(), proxy.stages)
            jobs = [r["accepted_job_id"] for r in receipts if r["accepted_job_id"]]
            if jobs:
                # Measurement begins after the scheduled retry, never before it.
                decision = oracle.observe_until(jobs, deadline_monotonic=deadline)
                write_private_json(evidence_root, "oracle-decision.json", decision.evidence())
                bound = len({b.execution_instance_id for b in decision.bindings}) if decision.oracle_evaluable else None
            else:
                bound = 0 if spec.fault_mode == "FPRE" and metrics["S_upstream"] == 0 else None
            metrics["E_bound"] = bound
            final = json.loads((client / f"call-{len(calls)}-after.json").read_text())
            guard = (spec.fault_mode != "F00" and calls[-1].get("client_error_stage") == "generate_round"
                     and calls[-1].get("client_error_code") == "submission_outcome_unknown"
                     and metrics["S_proxy"] == 1 and final["state"] == "unresolved")
            if spec.system == "W3" and spec.fault_mode != "F00" and not guard:
                raise ValueError("native_guard_not_observed")
            if calls[-1].get("client_error_code") and not guard:
                raise ValueError("non_target_product_rejection")
            if spec.fault_mode == "F00" and (final["state"] != "generated" or bound != 1):
                raise ValueError("control_not_complete_or_bindable")
            if jobs and bound is None:
                raise ValueError("accepted_lifecycle_not_bindable")
            # These fields stay operation-level; they are never natural rates.
            write_private_json(evidence_root, "operation-outcomes.json", {
                "original_run_state": final["state"], "client_completion": final["state"] == "generated",
                "submission_guard_observed": guard, "semantic_digest": semantic_digest(session["generate_arguments"]),
            })
        except Exception as error:
            reason = str(error) if isinstance(error, ValueError) else type(error).__name__
            write_private_json(evidence_root, "operation-error.json", {"exception_class": type(error).__name__, "reason": reason})
        finally:
            write_private_json(evidence_root, "proxy-receipts.json", proxy.evidence())
            write_private_json(evidence_root, "oracle-raw.json", oracle.private_capture())
            oracle.close()
    unchanged = all(sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() == d for n, d in hashes.items())
    if not unchanged:
        reason = "harness_changed_during_operation"
    report = {"protocol": PROTOCOL, "case_id": spec.case_id,
              "status": "COMPLETED" if reason is None else "STOPPED", "stop_reason": reason,
              "schedule_reason": schedule_reason, "calls": calls, "metrics": metrics,
              "product_call_count": len(outcomes), "process_outcomes": [asdict(o) for o in outcomes],
              "injection": proof, "source_unchanged": unchanged,
              "requires_reserved_runner": True, "not_gpu_compute_measurement": True}
    write_private_json(evidence_root, "operation-report.json", report)
    return report
