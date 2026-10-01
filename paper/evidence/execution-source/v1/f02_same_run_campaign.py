"""W3 F00 + F02 same-run scope check with private replay evidence.

This is a separate protocol from the historical four-case fresh-run pilot.
It inherits its frozen-client, endpoint and reservation preflight. It performs
no B2 product calls, no third call, no backend lifecycle action or recovery.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from scripts.research.f02_capture import unknown_submission, write_private_json
from scripts.research.f02_campaign import (
    CampaignConfigurationError, _case_record, _invoke_subprocess, _matches_frozen,
    _parse_config, _prompt_receipts, _remaining,
)
from scripts.research.f02_loopback import OneShotLoopbackFaultProxy
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.f02_preflight import run_preflight, _parse_time, _reservation_check
from scripts.research.f02_product_client import _digest


PROTOCOL = "same-run-guard-v1"


def _captured_call(root: Path, result: dict[str, object] | None, index: int,
                   operation_key: str, *, require_unknown: bool = True) -> tuple[dict, dict]:
    """Check actual retained files, rather than a client's recovery label."""
    if not isinstance(result, dict) or result.get("capture_error_code") or result.get("retry_scope") != "same_run":
        raise ValueError("product_capture_incomplete")
    for phase in ("before", "after"):
        payload = (root / f"call-{index}-{phase}.json").read_bytes()
        if sha256(payload).hexdigest() != result.get(f"manifest_{phase}_sha256"):
            raise ValueError("manifest_capture_hash_mismatch")
    session = json.loads((root / "session.json").read_text(encoding="utf-8"))
    before = json.loads((root / f"call-{index}-before.json").read_text(encoding="utf-8"))
    after = json.loads((root / f"call-{index}-after.json").read_text(encoding="utf-8"))
    if not all(isinstance(value, dict) for value in (session, before, after)):
        raise ValueError("captured_record_shape_invalid")
    run_id = session.get("run_id")
    arguments = session.get("generate_arguments")
    if (session.get("schema") != "f02-same-run-session-v1"
            or not isinstance(run_id, str) or not isinstance(arguments, dict)):
        raise ValueError("session_identity_missing")
    if (after.get("run_id") != run_id or before.get("run_id") != run_id
            or sha256(run_id.encode()).hexdigest() != result.get("run_id_sha256")
            or arguments.get("run_id") != run_id
            or arguments.get("idempotency_key") != operation_key
            or _digest(arguments) != result.get("generate_arguments_sha256")
            or _digest(arguments) != session.get("generate_arguments_sha256")
            or _digest(before.get("request")) != session.get("request_sha256")
            or _digest(after.get("request")) != session.get("request_sha256")):
        raise ValueError("captured_run_or_request_mismatch")
    if require_unknown and not unknown_submission(after, operation_key):
        raise ValueError("captured_unknown_submission_missing")
    return session, after


def _case(spec, *, boot_identity, frozen_request, invoker, proxy_factory, oracle_factory,
          monotonic, campaign_deadline):
    deadline = min(monotonic() + 900, campaign_deadline)
    calls, decisions, refs = [], [], {}
    root = Path(spec.private_capture_root)
    finishing = False

    def capture(name, value):
        refs[name] = write_private_json(root, name, value)

    with proxy_factory(spec.backend_url, fault_mode=spec.fault_mode, timeout_seconds=30) as proxy:
        oracle = oracle_factory(spec.backend_url, backend_boot_identity=boot_identity,
                                observer_id=spec.operation_key, timeout_seconds=5,
                                retain_raw_transport=True)

        def finish(reason=None, guard=False):
            nonlocal finishing
            finishing = True
            # A client may fail before creating its directory. Keep that case's
            # observer/receipt evidence independently of client success.
            root.mkdir(mode=0o700, exist_ok=True)
            capture("proxy-receipts.json", [asdict(r) for r in proxy.receipts])
            capture("oracle-transport-final.json", oracle.private_capture())
            for name in ("session.json", "call-1-invocation.json", "call-2-invocation.json",
                         "call-1-before.json", "call-1-after.json", "call-2-before.json", "call-2-after.json",
                         "call-1-result.json", "call-2-result.json"):
                path = root / name
                if path.is_file():
                    refs[name] = sha256(path.read_bytes()).hexdigest()
            record = _case_record(spec, "completed" if reason is None else "stopped",
                                  reason, calls, proxy.receipts, decisions, frozen_request).as_dict()
            record.update({"retry_scope": "same_run", "submission_guard_observed": guard,
                           "private_capture_sha256": refs})
            return record

        try:
            oracle.connect()
            calls.append(invoker(spec, 1, proxy.base_url, _remaining(deadline, monotonic)))
            root.mkdir(mode=0o700, exist_ok=True)
            capture("call-1-outcome.json", asdict(calls[-1]))
            receipts = _prompt_receipts(proxy.receipts)
            if len(receipts) != 1 or not receipts[0].accepted_job_id:
                return finish("first_acceptance_not_unique")
            if spec.fault_mode == "F02" and not receipts[0].response_dropped:
                return finish("accepted_response_not_suppressed")
            decision = oracle.observe_until([receipts[0].accepted_job_id],
                                           deadline_monotonic=min(deadline, monotonic() + 180))
            decisions.append(decision)
            capture("oracle-snapshot-1.json", {"decision": decision.evidence(),
                                              "transport": oracle.private_capture()})
            if not decision.oracle_evaluable:
                return finish("first_execution_not_bindable")
            if not _matches_frozen(calls[0].result, frozen_request, spec.operation_key):
                return finish("first_request_not_frozen")
            try:
                session, after = _captured_call(root, calls[0].result, 1, spec.operation_key,
                                               require_unknown=spec.fault_mode == "F02")
            except (OSError, ValueError, KeyError):
                return finish("original_run_capture_not_unknown" if spec.fault_mode == "F02"
                              else "control_capture_invalid")
            if spec.fault_mode == "F00":
                return finish(None if calls[0].reported_state == "resolved" and after.get("state") == "generated"
                              else "control_not_complete")
            before_second = len(receipts)
            calls.append(invoker(spec, 2, proxy.base_url, _remaining(deadline, monotonic)))
            capture("call-2-outcome.json", asdict(calls[-1]))
            if len(_prompt_receipts(proxy.receipts)) != before_second:
                return finish("second_call_created_submission")
            result = calls[-1].result or {}
            try:
                second_session, _ = _captured_call(root, result, 2, spec.operation_key)
            except (OSError, ValueError, KeyError):
                return finish("second_run_capture_invalid")
            if (second_session != session
                    or result.get("run_id_sha256") != calls[0].result.get("run_id_sha256")
                    or result.get("generate_arguments_sha256") != calls[0].result.get("generate_arguments_sha256")
                    or not _matches_frozen(result, frozen_request, spec.operation_key)):
                return finish("second_call_changed_run_or_arguments")
            if (calls[-1].timed_out or calls[-1].exit_code != 0
                    or result.get("client_error_code") != "submission_outcome_unknown"
                    or result.get("client_error_stage") != "generate_round"):
                return finish("guard_rejection_not_observed")
            return finish(guard=True)
        except TimeoutError:
            return finish("case_hard_timeout")
        except Exception as exc:
            if finishing:
                raise  # A failed exclusive evidence write cannot become success.
            # Private diagnostic retains the class, never arbitrary message text
            # in the public report. No exception permits a second/third retry.
            root.mkdir(mode=0o700, exist_ok=True)
            capture("case-error.json", {"exception_class": type(exc).__name__})
            return finish("case_capture_or_observation_error")
        finally:
            oracle.close()


def run_same_run_campaign(config, *, preflight_runner=run_preflight, product_invoker=None,
                          proxy_factory=OneShotLoopbackFaultProxy,
                          oracle_factory=ComfyUIEventOracle, monotonic=time.monotonic,
                          now=lambda: datetime.now(timezone.utc)):
    preflight_config, campaign, specs, frozen, evidence = _parse_config(config)
    if campaign.get("protocol_version") != PROTOCOL:
        raise CampaignConfigurationError("same-run protocol_version must be explicit")
    capture_value = campaign.get("same_run_capture_root")
    if not isinstance(capture_value, str) or not capture_value:
        raise CampaignConfigurationError("same_run_capture_root is required")
    capture_root = Path(capture_value).resolve()
    if capture_root.exists() or not capture_root.parent.is_dir() or evidence.exists() or not evidence.parent.is_dir():
        raise CampaignConfigurationError("capture/evidence paths must be fresh with existing parents")
    for spec in specs.values():
        output = Path(spec.output_root).resolve()
        if capture_root == output or capture_root in output.parents or output in capture_root.parents:
            raise CampaignConfigurationError("private capture must be separate from product outputs")
    preflight = preflight_runner(preflight_config)
    public_preflight = {"status": preflight.status, "checked_at": preflight.checked_at}
    reservation = preflight_config.get("reservation", {})
    checked_now = now()
    if (preflight.status != "PASS" or not preflight.backend_boot_identity
            or not _reservation_check(reservation, checked_now).passed):
        public_preflight["status"] = "FAIL"
        return {"protocol_version": PROTOCOL, "status": "PRECHECK_FAILED",
                "preflight": public_preflight, "records": []}
    campaign_deadline = monotonic() + (_parse_time(reservation["end"]) - checked_now).total_seconds()
    capture_root.mkdir(mode=0o700)
    preflight_sha = write_private_json(capture_root, "preflight.json", preflight.as_dict())
    config_sha = write_private_json(capture_root, "configuration.json", config)
    source_files = ("f02_same_run_campaign.py", "f02_product_client.py", "f02_capture.py",
                    "f02_campaign.py", "f02_oracle.py", "f02_loopback.py", "f02_preflight.py",
                    "f02_transport_launcher.py", "f02_transport_shim.py")
    source_hashes = {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in source_files}
    write_private_json(capture_root, "harness-source-hashes.json", source_hashes)
    public_preflight.update({"private_capture_sha256": preflight_sha,
                             "private_configuration_sha256": config_sha,
                             "backend_boot_identity_sha256": sha256(preflight.backend_boot_identity.encode()).hexdigest()})
    invoker = product_invoker or _invoke_subprocess
    records = []
    # Claim the report before touching the proxy or product to refuse overwrite.
    with evidence.open("x", encoding="utf-8") as handle:
        for fault in ("F00", "F02"):
            if monotonic() >= campaign_deadline:
                break
            spec = replace(specs[f"W3_{fault}"], retry_scope="same_run",
                           private_capture_root=str(capture_root / f"W3_{fault}"))
            record = _case(spec, boot_identity=preflight.backend_boot_identity,
                           frozen_request=frozen, invoker=invoker, proxy_factory=proxy_factory,
                           oracle_factory=oracle_factory, monotonic=monotonic,
                           campaign_deadline=campaign_deadline)
            records.append(record)
            if record["status"] != "completed":
                break
        report = {"protocol_version": PROTOCOL, "preflight": public_preflight,
                  "harness_source_sha256": source_hashes, "records": records,
                  "status": "COMPLETED" if len(records) == 2 and records[-1]["submission_guard_observed"] else "STOPPED",
                  "scope": "same-run submission rejection; no natural rates, physical GPU execution or eventual completion claim"}
        handle.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="private configuration; includes explicit active reservation")
    args = parser.parse_args()
    try:
        report = run_same_run_campaign(json.loads(args.config.read_text(encoding="utf-8")))
    except (CampaignConfigurationError, OSError, ValueError):
        print(json.dumps({"status": "CONFIG_ERROR"}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
