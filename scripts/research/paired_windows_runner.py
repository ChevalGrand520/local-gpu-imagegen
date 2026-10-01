"""Six-operation paired runner core; CLI plans unless --execute is supplied.

The Windows adapter and supervisor are separate from this testable schedule.
CPU test doubles are never classified as a Windows or GPU measurement.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import platform
import subprocess
import sys
from pathlib import Path
import time

from scripts.research.f02_capture import write_private_json
from scripts.research.f02_campaign import CaseSpec
from scripts.research.paired_ambiguity import PRODUCTS, PROTOCOL, WINDOWS_ORDER

SCOPE = "exactly six paired-ambiguity-v1 F00/F02/FPRE single-stage operations"
BUDGET = {"operations": 6, "product_calls": 10, "proxy_posts": 10,
          "upstream_attempts": 8, "wall_seconds": 3600, "storage_bytes": 1024 ** 3}
CACHE_POLICY = "owned_process_per_operation_no_reset_between_calls"
CLEANUP_MARGIN_SECONDS = 15


class RunnerStop(RuntimeError):
    pass


def parse_utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("reservation timestamps must have a timezone")
    return parsed.astimezone(timezone.utc)


def plan(config):
    """Pure static checks: no process, network, GPU or output directory access."""
    if config.get("protocol") != PROTOCOL or config.get("budget") != BUDGET:
        raise ValueError("explicit paired protocol and exact reviewed budgets required")
    if config.get("cache_policy") != CACHE_POLICY:
        raise ValueError("reviewed cache policy required")
    preflight = config["preflight"]
    for variant, revision in PRODUCTS.items():
        if preflight["clients"][variant]["sha"] != revision:
            raise ValueError("frozen product revision mismatch")
    reservation = preflight["reservation"]
    if reservation.get("scope") != SCOPE or reservation.get("hard_timeout_seconds") != 3600:
        raise ValueError("six-operation reservation required; historical four-case scope is invalid")
    if parse_utc(reservation["end"]) <= parse_utc(reservation["start"]):
        raise ValueError("invalid reservation interval")
    if not isinstance(reservation.get("owner"), str) or not reservation["owner"].strip():
        raise ValueError("explicit reservation owner required")
    if reservation.get("no_concurrent_gpu_work") is not True:
        raise ValueError("explicit exclusive-resource declaration required")
    if not isinstance(reservation.get("authorization"), str) or not reservation["authorization"].strip():
        raise ValueError("explicit launch authorization reference required")
    return {"protocol": PROTOCOL, "status": "PLAN_ONLY", "execution_performed": False,
            "launch_enabled": config.get("launch_enabled") is True,
            "training_state": reservation.get("training_state", "unknown"),
            "order": [f"{variant}_{fault}" for variant, fault in WINDOWS_ORDER], "budget": dict(BUDGET),
            "reservation_is_not_created_or_extended": True}


def check_window(config, now):
    reservation = config["preflight"]["reservation"]
    if config.get("launch_enabled") is not True or reservation.get("training_state") != "idle":
        raise RunnerStop("launch_disabled_or_training_not_idle")
    if not parse_utc(reservation["start"]) <= now < parse_utc(reservation["end"]):
        raise RunnerStop("reservation_inactive")


def directory_bytes(root):
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def freeze_sources(config, root):
    """Snapshot actual files before any backend startup, including CRLF bytes."""
    destination = root / "source-snapshot"
    destination.mkdir()
    hashes = {}
    for path in sorted(Path(__file__).parent.glob("*.py")):
        target = destination / "harness" / path.name
        target.parent.mkdir(exist_ok=True)
        content = path.read_bytes()
        target.write_bytes(content)
        hashes[f"harness/{path.name}"] = sha256(content).hexdigest()
    for variant in PRODUCTS:
        product = Path(config["preflight"]["clients"][variant]["root"]).resolve()
        # Include runtime sources and configured product registry resources.
        paths = {product / "scripts/mcp_server.py"}
        paths.update((product / "scripts/local_gpu_imagegen").rglob("*.py"))
        for directory in ("config", "data", "assets", "profiles"):
            paths.update(p for p in (product / directory).rglob("*")
                         if p.is_file() and p.suffix in {".json", ".yaml", ".yml"})
        for path in sorted(paths):
            if not path.is_file():
                raise RunnerStop("missing_product_source")
            relative = path.relative_to(product)
            target = destination / variant / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            content = path.read_bytes()
            target.write_bytes(content)
            hashes[f"{variant}/{relative.as_posix()}"] = sha256(content).hexdigest()
    # Freeze tracked backend source/resources, not model weights or outputs.
    backend = Path(config["preflight"]["environment"]["comfy_root"]).resolve()
    files = subprocess.check_output(["git", "-C", str(backend), "ls-files", "-z"], timeout=10)
    for relative in files.decode("utf-8").split("\0"):
        if relative and Path(relative).suffix in {".py", ".json", ".yaml", ".yml"}:
            path = backend / relative
            content = path.read_bytes()
            target = destination / "backend" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            hashes[f"backend/{relative}"] = sha256(content).hexdigest()
    write_private_json(root, "source-freeze.json", {"products": PRODUCTS, "sha256": hashes,
        "frozen_at": datetime.now(timezone.utc).isoformat(), "before_backend_start": True})
    return hashes


def verify_sources(config, hashes):
    for name, digest in hashes.items():
        label, relative = name.split("/", 1)
        if label == "harness":
            parent = Path(__file__).parent
        elif label == "backend":
            parent = Path(config["preflight"]["environment"]["comfy_root"])
        else:
            parent = Path(config["preflight"]["clients"][label]["root"])
        if sha256((parent / relative).read_bytes()).hexdigest() != digest:
            raise RunnerStop("source_changed_after_freeze")


def run_reserved(config, root, *, ops, clock=time.monotonic,
                 now=lambda: datetime.now(timezone.utc), freezer=freeze_sources, verifier=verify_sources):
    """Run with a resource-owning adapter. Test doubles report synthetic evidence.

    Adapter methods: prepare_root, before_start, start_backend, stop_backend,
    preflight_backend, run_operation, close. No method may acquire others' jobs.
    """
    plan(config)
    check_window(config, now())  # Busy training prevents even directory creation.
    if root.exists():
        raise FileExistsError("fresh private root required")
    original_config = json.dumps(config, sort_keys=True)
    started = clock()
    wall_remaining = (parse_utc(config["preflight"]["reservation"]["end"]) - now()).total_seconds()
    campaign_deadline = started + min(BUDGET["wall_seconds"], wall_remaining)
    work_deadline = campaign_deadline - CLEANUP_MARGIN_SECONDS
    records, controls, pairs = [], [], {}
    totals = {"operations": 0, "product_calls": 0, "proxy_posts": 0, "upstream_attempts": 0}
    stop_reason, hashes, current_case = None, None, None
    ops.prepare_root(root)

    def check_budget():
        check_window(config, now())
        if clock() >= work_deadline:
            raise RunnerStop("campaign_time_budget")
        if directory_bytes(root) > BUDGET["storage_bytes"]:
            raise RunnerStop("campaign_storage_budget")
        if any(totals[k] > BUDGET[k] for k in totals):
            raise RunnerStop("campaign_count_budget")

    try:
        write_private_json(root, "configuration.json", config)
        write_private_json(root, "runtime.json", {"python_version": sys.version,
            "python_executable": sys.executable, "platform": platform.platform(),
            "evidence_class": ops.evidence_class, "wall_time": now().isoformat(), "monotonic": started})
        hashes = freezer(config, root)
        for index, (variant, fault) in enumerate(WINDOWS_ORDER):
            current_case = f"{variant}_{fault}"
            check_budget()
            if index == 2:
                fault_timeout = max(60.0, 3 * max(controls))
                if fault_timeout > 300:
                    raise RunnerStop("control_calibrated_deadline_exceeds_300")
            timeout = 300.0 if fault == "F00" else fault_timeout
            if work_deadline - clock() <= timeout + 10:
                raise RunnerStop("insufficient_window_for_operation_and_cleanup")
            verifier(config, hashes)
            op_root = root / f"{index + 1:02d}-{variant}-{fault}"
            op_root.mkdir()
            ops.before_start(config, op_root, min(work_deadline, clock() + 60))
            owned = None
            record = None
            try:
                owned = ops.start_backend(config, op_root, min(work_deadline, clock() + 180))
                boot_identity = ops.preflight_backend(config, owned, op_root)
                verifier(config, hashes)
                remaining = work_deadline - clock()
                if remaining <= timeout + 10:
                    raise RunnerStop("startup_consumed_remaining_window")
                spec = CaseSpec(case_id=f"{variant}_{fault}", system=variant, fault_mode=fault,
                    command=tuple(ops.client_command()),
                    working_directory=config["preflight"]["clients"][variant]["root"],
                    research_model_path=config["preflight"]["environment"]["model_path"],
                    output_root=str(op_root / "outputs"), operation_key=f"{root.name}-{variant}-{fault}",
                    backend_url=config["preflight"]["environment"]["backend_url"],
                    retry_scope="paired_same_run", private_capture_root=str(op_root / "client"))
                begin = clock()
                totals["operations"] += 1
                record = ops.run_operation(spec, op_root, boot_identity, begin + timeout)
                records.append(record)
                totals["product_calls"] += record["product_call_count"]
                metrics = record.get("metrics")
                if isinstance(metrics, dict):
                    totals["proxy_posts"] += metrics["S_proxy"]
                    totals["upstream_attempts"] += metrics["S_upstream"]
                if record["status"] != "COMPLETED":
                    raise RunnerStop("operation_stopped:" + str(record.get("stop_reason")))
                outcome = json.loads((op_root / "observer/operation-outcomes.json").read_text())
                digest = outcome["semantic_digest"]
                if fault in pairs and pairs[fault] != digest:
                    raise RunnerStop("paired_semantics_differ")
                pairs[fault] = digest
                if fault == "F00":
                    returned = record["calls"][0]["generation_return_monotonic_ns"]
                    requested = record["calls"][0]["generation_request_monotonic_ns"]
                    elapsed = (returned - requested) / 1e9
                    if elapsed <= 0:
                        raise RunnerStop("control_rpc_latency_invalid")
                    controls.append(elapsed)
                    if not outcome["client_completion"] or metrics.get("E_bound") != 1:
                        raise RunnerStop("control_not_complete")
                check_budget()
            finally:
                if owned is not None:
                    cleanup = ops.stop_backend(owned, op_root, campaign_deadline)
                    write_private_json(op_root, "cleanup.json", cleanup)
                    if not cleanup.get("stopped"):
                        raise RunnerStop("owned_backend_cleanup_failed")
            verifier(config, hashes)
    except Exception as error:
        stop_reason = str(error) if isinstance(error, RunnerStop) else type(error).__name__
        write_private_json(root, "runner-error.json", {"exception_class": type(error).__name__, "reason": stop_reason})
    finally:
        ops.close()
    if json.dumps(config, sort_keys=True) != original_config:
        stop_reason = "supplied_configuration_was_mutated"
    if clock() > campaign_deadline:
        stop_reason = "campaign_wall_budget_exceeded"
    if directory_bytes(root) > BUDGET["storage_bytes"]:
        stop_reason = "campaign_storage_budget_exceeded"
    report = {"protocol": PROTOCOL, "status": "COMPLETED" if len(records) == 6 and stop_reason is None else "STOPPED",
              "stop_reason": stop_reason, "evidence_class": ops.evidence_class,
              "records": records, "totals": totals, "control_rpc_seconds": controls,
              "scheduled_operations": 6, "recorded_operations": len(records),
              "case_at_stop": current_case if stop_reason is not None else None,
              "budget": BUDGET, "elapsed_seconds": clock() - started,
              "storage_bytes_at_final_check": directory_bytes(root),
              "training_tasks_terminated": False, "reservation_modified": False,
              "storage_limit_enforcement": "sampled_stop_condition_not_filesystem_quota"}
    write_private_json(root, "runner-report.json", report)
    return report
