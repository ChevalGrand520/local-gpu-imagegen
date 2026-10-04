"""Explicit human-authorized reservation preparation; never launches a backend."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.research.paired_windows_ops import private_directory, compute_idle_report
from scripts.research.paired_windows_runner import SCOPE, parse_utc, plan, check_window


DESKTOP_NAMES = {
    "dwm.exe", "crossdeviceresume.exe", "explorer.exe", "searchhost.exe",
    "startmenuexperiencehost.exe", "shellexperiencehost.exe", "logioptionsplus_agent.exe",
    "logioptionsplus_logivoice.exe", "msedgewebview2.exe", "nvidia overlay.exe", "main.exe",
    "tabtip.exe", "textinputhost.exe", "phoneexperiencehost.exe", "wdadesktopservice.exe",
    "applicationframehost.exe", "systemsettings.exe", "lockapp.exe", "rtkuwp_rs5.exe",
    "steam++.exe", "tabbit browser.exe", "shellhost.exe", "browser.exe", "hipsdaemon.exe",
    "chatgpt.exe", "logonui.exe", "lockscreencontentserver.exe", "promecefpluginhost.exe",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("historical_template", type=Path)
    parser.add_argument("fresh_private_root", type=Path)
    parser.add_argument("lock_root", type=Path)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--operator-training-released", action="store_true", required=True)
    args = parser.parse_args()
    if sys.platform != "win32" or args.owner != os.environ["USERNAME"]:
        raise SystemExit("explicit local owner on Windows required")
    start, end = parse_utc(args.start), parse_utc(args.end)
    if not start <= datetime.now(timezone.utc) < end or (end-start).total_seconds() > 3600:
        raise SystemExit("active window at most one hour required")
    config = json.loads((ROOT / "docs/research/paired-windows-config.example.json").read_text())
    old = json.loads(args.historical_template.read_text())
    for field in ("ledger", "environment", "clients"):
        config["preflight"][field] = old["preflight"][field]
    config["preflight"]["environment"].pop("comfy_pid", None)
    config["launch_enabled"] = True
    config["preflight"]["reservation"] = {
        "owner": args.owner, "authorization": args.authorization, "scope": SCOPE,
        "start": args.start, "end": args.end, "hard_timeout_seconds": 3600,
        "training_state": "idle", "no_concurrent_gpu_work": True,
        "declaration_source": "explicit human training-release and autonomous execution authorization",
    }
    plan(config)
    check_window(config, datetime.now(timezone.utc))
    query = subprocess.run(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=15, check=True)
    initial = compute_idle_report(query.stdout, config["preflight"]["environment"]["gpu_uuid"])
    baseline = initial["target_compute_processes"]
    for process in baseline:
        name = process["process_name"].replace("/", "\\").lower()
        if name.rsplit("\\", 1)[-1] not in DESKTOP_NAMES:
            raise SystemExit("unreviewed GPU process; no reservation prepared")
    compute_idle_report(query.stdout, config["preflight"]["environment"]["gpu_uuid"], baseline)
    # An advisory lock coordinates these research runners, not every desktop app.
    args.lock_root.mkdir()
    try:
        private_directory(args.fresh_private_root)
        config["resource_policy"] = {"wddm_desktop_baseline": baseline,
                                     "classification": "reviewed desktop executable names; not hardware exclusivity proof"}
        (args.lock_root / "reservation.json").write_text(json.dumps(config["preflight"]["reservation"], indent=2))
        (args.fresh_private_root / "configuration.json").write_text(json.dumps(config, indent=2))
        (args.fresh_private_root / "baseline-query.txt").write_text(query.stdout)
        print(json.dumps({"status": "RESERVED_NOT_EXECUTED", "configuration": str(args.fresh_private_root / "configuration.json"),
                          "desktop_processes": len(baseline), "end": args.end}))
    except Exception:
        # Only this invocation's newly acquired empty lock may be released here.
        if not any(args.lock_root.iterdir()):
            args.lock_root.rmdir()
        raise


if __name__ == "__main__":
    main()
