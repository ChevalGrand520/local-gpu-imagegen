"""Execute one owner-authorized Windows same-run campaign; preserve all files.

This operational runner starts only its own pinned ComfyUI process, creates a
fresh private configuration from a retained template, and always stops its own
process. It never changes frozen product checkouts or downloads assets.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import ProxyHandler, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("private_root", type=Path)
    args = parser.parse_args()
    if sys.platform != "win32":
        raise SystemExit("Windows only")
    root = args.private_root.resolve()
    root.mkdir(exist_ok=False)
    acl = subprocess.run(["icacls", str(root), "/inheritance:r", "/grant:r",
                          os.environ["USERNAME"] + ":(OI)(CI)F"], capture_output=True)
    if acl.returncode:
        raise SystemExit("private ACL setup failed; no backend started")
    config = json.loads(args.template.read_text(encoding="utf-8"))
    env = config["preflight"]["environment"]
    comfy = Path(env["comfy_root"])
    actual = subprocess.check_output(["git", "-C", str(comfy), "rev-parse", "HEAD"], text=True).strip()
    if actual != env["comfy_sha"]:
        raise SystemExit("pinned ComfyUI identity mismatch")
    opener = build_opener(ProxyHandler({}))
    try:
        opener.open(env["backend_url"] + "/system_stats", timeout=2).close()
    except OSError:
        pass
    else:
        raise SystemExit("backend already running; refusing to acquire it")
    start = datetime.now(timezone.utc)
    config["preflight"]["reservation"].update(
        start=start.isoformat(), end=(start + timedelta(minutes=30)).isoformat(),
        owner="Capricorn", no_concurrent_gpu_work=True,
        authorization="user explicitly authorized unattended bounded execution on 2026-10-01",
        desktop_memory_baseline_accepted=True,
        actual_schedule="W3_F00 and W3_F02 only; legacy preflight four-case namespace retained")
    campaign = config["campaign"]
    campaign["protocol_version"] = "same-run-guard-v1"
    campaign["same_run_capture_root"] = str(root / "capture")
    campaign["evidence_file"] = str(root / "public-evidence.json")
    source = Path(__file__).resolve().parent
    for label in ("B2", "W3"):
        campaign["client_commands"][label] = [sys.executable, str(source / "f02_product_client.py")]
    output_parent = root / "outputs"
    output_parent.mkdir()
    for label in ("B2_F00", "W3_F00", "B2_F02", "W3_F02"):
        fresh = str(output_parent / label.lower())
        campaign["output_roots"][label] = fresh
        config["preflight"]["fresh_output_roots"][label] = fresh
        campaign["operation_keys"][label] = "same-run-" + root.name + "-" + label
    command = [str(comfy.parent / "python_embeded" / "python.exe"), "-s",
               str(comfy / "main.py"), "--windows-standalone-build", "--listen", "127.0.0.1", "--port", "8202"]
    child_env = os.environ.copy()
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        child_env.pop(key, None)
    proc = None
    result = {"status": "SETUP_FAILED", "started_at": start.isoformat()}
    with (root / "comfy.stdout.log").open("xb") as out, (root / "comfy.stderr.log").open("xb") as err:
        try:
            proc = subprocess.Popen(command, cwd=comfy.parent, stdout=out, stderr=err, env=child_env)
            env["comfy_pid"] = proc.pid
            (root / "configuration.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError("owned ComfyUI exited during startup")
                try:
                    with opener.open(env["backend_url"] + "/queue", timeout=3) as response:
                        queue = json.load(response)
                    if queue.get("queue_running") or queue.get("queue_pending"):
                        raise RuntimeError("backend queue not empty")
                    break
                except OSError:
                    time.sleep(1)
            else:
                raise TimeoutError("backend startup timeout")
            with (root / "campaign.stdout.log").open("xb") as cout, (root / "campaign.stderr.log").open("xb") as cerr:
                remaining = max(1, int((start + timedelta(minutes=30) - datetime.now(timezone.utc)).total_seconds()))
                run = subprocess.run([sys.executable, "-B", "-m", "scripts.research.f02_same_run_campaign",
                                      str(root / "configuration.json")],
                                     cwd=source.parents[1], env=child_env, stdout=cout, stderr=cerr, timeout=remaining)
            result.update(status="FINISHED", campaign_exit_code=run.returncode)
        except Exception as exc:
            result.update(status="STOPPED", exception_class=type(exc).__name__)
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
            result["owned_backend_exit_code"] = None if proc is None else proc.poll()
            result["finished_at"] = datetime.now(timezone.utc).isoformat()
            (root / "runner-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0 if result.get("campaign_exit_code") == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
