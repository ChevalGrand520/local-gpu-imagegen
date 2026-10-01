"""Plan or explicitly execute the frozen paired-ambiguity-v1 Windows campaign.

No SSH or remote configuration changes are made. Planning works offline on any
platform. Execution requires Windows, explicit launch configuration, an active
reservation and idle-resource checks. It never creates a reservation itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.f02_capture import write_private_json
from scripts.research.paired_windows_runner import (
    BUDGET, CLEANUP_MARGIN_SECONDS, RunnerStop, check_window, directory_bytes, parse_utc, plan, run_reserved,
)


def supervise(config, config_path, root, *, popen=subprocess.Popen, clock=time.monotonic,
              sleep=time.sleep, now=lambda: datetime.now(timezone.utc)):
    from scripts.research.paired_windows_ops import private_directory, stop_owned_process
    plan(config)
    check_window(config, now())
    if sys.platform != "win32":
        raise RunnerStop("Windows_only_no_execution")
    if root.exists():
        raise FileExistsError("fresh private parent required")
    private_directory(root)
    # Freeze the exact supplied bytes. The worker reads these, never a mutable
    # template during execution. Its own JSON copy is retained before startup.
    payload = config_path.read_bytes()
    if json.loads(payload) != config:
        raise RunnerStop("configuration_changed_after_plan")
    frozen_config = root / "supplied-configuration.json"
    frozen_config.write_bytes(payload)
    report = {"status": "STOPPED", "stop_reason": None, "worker_exit_code": None,
              "gpu_compute_execution_verified": False, "training_tasks_terminated": False}
    start = clock()
    seconds = min(BUDGET["wall_seconds"], (parse_utc(config["preflight"]["reservation"]["end"]) - now()).total_seconds())
    deadline = start + seconds
    process = None
    command = [sys.executable, "-B", str(Path(__file__).resolve()), str(frozen_config),
               "--private-root", str(root / "campaign"), "--execute", "--worker"]
    with (root / "worker.stdout.log").open("xb") as stdout, (root / "worker.stderr.log").open("xb") as stderr:
        try:
            process = popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
            while process.poll() is None:
                if clock() >= deadline - CLEANUP_MARGIN_SECONDS:
                    report["stop_reason"] = "supervisor_wall_limit"
                    break
                if now() >= parse_utc(config["preflight"]["reservation"]["end"]):
                    report["stop_reason"] = "reservation_expired"
                    break
                if directory_bytes(root) > BUDGET["storage_bytes"]:
                    report["stop_reason"] = "supervisor_storage_limit"
                    break
                sleep(.2)
            if process.poll() is None:
                report["worker_cleanup"] = stop_owned_process(process)
            report["worker_exit_code"] = process.poll()
            child_report = root / "campaign/runner-report.json"
            if child_report.is_file():
                child = json.loads(child_report.read_text())
                report["worker_status"] = child["status"]
                if report["stop_reason"] is None and child["status"] == "COMPLETED" and process.returncode == 0:
                    report["status"] = "COMPLETED"
                elif report["stop_reason"] is None:
                    report["stop_reason"] = child.get("stop_reason") or "worker_did_not_complete"
            elif report["stop_reason"] is None:
                report["stop_reason"] = "worker_exited_without_complete_report"
            if clock() > deadline or directory_bytes(root) > BUDGET["storage_bytes"]:
                report.update(status="STOPPED", stop_reason=report["stop_reason"] or "final_resource_limit_exceeded")
        finally:
            if process is not None and process.poll() is None:
                stop_owned_process(process)
            report["elapsed_seconds"] = clock() - start
            write_private_json(root, "supervisor-report.json", report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configuration", type=Path)
    parser.add_argument("--private-root", type=Path)
    parser.add_argument("--execute", action="store_true", help="requires live Windows reservation and idle checks")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.configuration.read_text(encoding="utf-8"))
        planned = plan(config)
        if not args.execute:
            print(json.dumps(planned, sort_keys=True))
            return 0
        check_window(config, datetime.now(timezone.utc))
        if sys.platform != "win32":
            raise RunnerStop("Windows_only_no_execution")
        if args.private_root is None:
            raise RunnerStop("explicit_fresh_private_root_required")
        if args.worker:
            from scripts.research.paired_windows_ops import WindowsOps
            report = run_reserved(config, args.private_root, ops=WindowsOps())
        else:
            report = supervise(config, args.configuration, args.private_root)
        print(json.dumps({"status": report["status"], "stop_reason": report.get("stop_reason")}))
        return 0 if report["status"] == "COMPLETED" else 2
    except (RunnerStop, ValueError, KeyError, OSError) as error:
        print(json.dumps({"status": "NOT_RUN", "exception_class": type(error).__name__,
                          "reason": str(error), "execution_verified": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
