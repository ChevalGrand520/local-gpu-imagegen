"""Bounded, author-authorized Windows known-job probe. Never performs review.

Task Scheduler starts the supervisor, which owns a worker and its backend tree.
All evidence is private; source travels through Git, not this configuration.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.f02_product_client import (
    StdioMcp, ProductClientError, _initialise, _discover_route, _build_plan,
    INTENT, SUBTYPE, CONSTRAINTS, MODEL_SHA256,
)
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.paired_windows_ops import (
    private_directory, require_free_backend_port, stop_owned_process, compute_idle_report,
)
from scripts.research.prepare_paired_windows_reservation import DESKTOP_NAMES
from local_gpu_imagegen.backends.base import BoundedJsonClient
from local_gpu_imagegen.artifacts import atomic_write_json


def receipt(root, name, value):
    atomic_write_json(Path(root) / name, value)


def audit(path, event):
    with Path(path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"wall_time": time.time(), **event}, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def sends(path):
    return sum(json.loads(line).get("event") == "send_intent" for line in
               Path(path).read_text().splitlines()) if Path(path).exists() else 0


def check_send_budget(path, end, now=None):
    if (time.time() if now is None else now) >= end:
        raise RuntimeError("wall_budget_exhausted")
    if sends(path) >= 3:
        raise RuntimeError("prompt_budget_exhausted")


def install_audit(root, end):
    original = BoundedJsonClient.post_json

    def post(self, path, payload):
        if path != "/prompt":
            raise RuntimeError("unexpected_backend_mutation")
        check_send_budget(Path(root) / "http.jsonl", end)
        index = sends(Path(root) / "http.jsonl") + 1
        receipt(root, f"prompt-{index}.json", payload)
        audit(Path(root) / "http.jsonl", {"event": "send_intent", "index": index,
                                          "endpoint": self.endpoint_identity})
        result = original(self, path, payload)
        audit(Path(root) / "http.jsonl", {"event": "response", "index": index,
                                          "response": result})
        return result

    BoundedJsonClient.post_json = post


class Client(StdioMcp):
    def __init__(self, env):
        self.root, self.sequence = ROOT, 0
        self.process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "server"], cwd=ROOT,
            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            # Persistent file avoids deadlock on an unconsumed stderr pipe.
            stderr=open(Path(env["SPE_PRIVATE_ROOT"]) / "mcp.stderr.log", "ab"),
            text=True, encoding="utf-8", errors="replace",
        )
        _initialise(self)


def server():
    root = Path(os.environ["SPE_PRIVATE_ROOT"])
    install_audit(root, float(os.environ["SPE_WALL_END"]))
    if os.environ.get("SPE_CRASH_AFTER_ID") == "1":
        from local_gpu_imagegen.run_store import RunStore
        original = RunStore.mark_attempt_backend_job

        def mark(self, handle, backend, job_id):
            original(self, handle, backend, job_id)
            receipt(root, "retained-job.json", {"job_id": job_id, "pid": os.getpid()})
            os._exit(72)

        RunStore.mark_attempt_backend_job = mark
    runpy.run_path(str(ROOT / "scripts/mcp_server.py"), run_name="__main__")


def fresh_call(env, args=None, inspect_id=None):
    client = Client(env)
    try:
        _discover_route(client)  # Real runtime discovery/fingerprint, never fixtures.
        if inspect_id:
            return client.call("local_gpu_get_run", {"run_id": inspect_id})
        return client.call("local_gpu_generate_round", args)
    finally:
        client.close()


def hash_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def worker(config, root):
    backend = None
    lock = Path(config["lock_root"])
    acquired = False
    end = time.time() + 1170  # Leaves cleanup margin inside the 20-minute supervisor.
    report = {"status": "STOPPED", "author_review": False, "finalized": False}
    try:
        actual = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        if actual != config["source_sha"]:
            raise RuntimeError("source_mismatch")
        if subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True).strip():
            raise RuntimeError("dirty_execution_source")
        uuids = subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).splitlines()
        if config["gpu_uuid"] not in [value.strip() for value in uuids]:
            raise RuntimeError("gpu_identity_mismatch")
        require_free_backend_port("127.0.0.1", 8202)
        gpu = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name",
                                       "--format=csv,noheader"], text=True)
        baseline = compute_idle_report(gpu, config["gpu_uuid"])["target_compute_processes"]
        receipt(root, "gpu-process-query.json", {"raw": gpu, "processes": baseline})
        extra_desktop = set()
        for desktop_path in config.get("additional_desktop_paths", []):
            normalized = desktop_path.replace("/", "\\").lower()
            if (not normalized.startswith("c:\\program files\\windowsapps\\microsoft.windowsterminal_")
                    or not normalized.endswith("_8wekyb3d8bbwe\\windowsterminal.exe")):
                raise RuntimeError("additional_desktop_path_not_terminal")
            command = ("Get-AuthenticodeSignature -FilePath '" + desktop_path.replace("'", "''") +
                       "' | Select-Object Status,@{Name='Signer';Expression={$_.SignerCertificate.Subject}} | ConvertTo-Json -Compress")
            result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                                    capture_output=True, text=True, timeout=15, check=True)
            signature = json.loads(result.stdout)
            receipt(root, "terminal-signature.json", signature)
            if signature.get("Status") != 0 or signature.get("Signer") != "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US":
                raise RuntimeError("additional_desktop_signature_invalid")
            extra_desktop.add(normalized)
        if any(p["process_name"].replace("/", "\\").rsplit("\\", 1)[-1].lower()
               not in DESKTOP_NAMES and p["process_name"].replace("/", "\\").lower()
               not in extra_desktop for p in baseline):
            raise RuntimeError("unreviewed_gpu_process")
        receipt(root, "gpu-preflight.json", compute_idle_report(gpu, config["gpu_uuid"], baseline))
        if shutil.disk_usage(root).free < 1024 ** 3:
            raise RuntimeError("insufficient_disk")
        lock.mkdir()
        acquired = True
        receipt(lock, "reservation.json", {"source_sha": actual, "owner_pid": os.getpid(),
                "end_epoch": end, "authorization": config["authorization"],
                "scope": "advisory research lock; desktop process baseline is not hardware exclusivity proof"})
        model = Path(config["model_path"])
        if hash_file(model) != MODEL_SHA256:
            raise RuntimeError("model_fingerprint_mismatch")
        comfy = Path(config["comfy_root"])
        if subprocess.check_output(["git", "-C", str(comfy), "rev-parse", "HEAD"], text=True).strip() != config["comfy_sha"]:
            raise RuntimeError("comfy_source_mismatch")
        state = root / "state"
        state.mkdir()
        old_state = Path(os.environ["LOCALAPPDATA"]) / "local-gpu-imagegen"
        # Reuse the author's existing private approval without changing shared state.
        for name in ("trust.json", "file-verifications.json"):
            shutil.copy2(old_state / name, state / name)
        env = os.environ.copy()
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env.pop(key, None)
        env.update({"LOCAL_GPU_IMAGEGEN_STATE_DIR": str(state),
                    "LOCAL_GPU_IMAGEGEN_OUTPUT_DIR": str(root / "outputs"),
                    "LOCAL_GPU_IMAGEGEN_COMFYUI_URL": "http://127.0.0.1:8202",
                    "LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED": "0",
                    "LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS": "0",
                    "LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH": str(model),
                    "SPE_PRIVATE_ROOT": str(root), "SPE_WALL_END": str(end)})
        os.environ["LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH"] = str(model)
        with (root / "backend.stdout.log").open("xb") as out, (root / "backend.stderr.log").open("xb") as err:
            backend = subprocess.Popen([str(comfy.parent / "python_embeded/python.exe"), "-s", str(comfy / "main.py"),
                        "--windows-standalone-build", "--listen", "127.0.0.1", "--port", "8202"],
                        cwd=comfy.parent, env=env, stdout=out, stderr=err)
        boot = f"spe-owned:{backend.pid}:{time.time_ns()}"
        receipt(root, "backend-start.json", {"pid": backend.pid, "boot_identity": boot})
        http = BoundedJsonClient("http://127.0.0.1:8202")
        startup_end = min(end, time.time() + 120)
        while True:
            if backend.poll() is not None or time.time() >= startup_end:
                raise RuntimeError("backend_start_failed")
            try:
                queue = http.get_json("/queue")
                break
            except Exception:
                time.sleep(.5)
        receipt(root, "initial-queue.json", queue)
        if queue.get("queue_running") or queue.get("queue_pending"):
            raise RuntimeError("queue_not_empty")
        receipt(root, "system-stats.json", http.get_json("/system_stats"))
        key = "spe-known-20261006"
        with ComfyUIEventOracle(http.base_url, backend_boot_identity=boot,
                               observer_id=key, retain_raw_transport=True) as oracle:
            client = Client({**env, "SPE_CRASH_AFTER_ID": "1"})
            try:
                info = _discover_route(client)
                boundary = info["boundary"]
                start = {k: boundary.get(k) for k in ("profile", "style", "model_choice", "backend", "authorization_scope", "route_token")}
                start.update(intent=INTENT, subtype=SUBTYPE, constraints=dict(CONSTRAINTS), max_rounds=1, upscale_policy="off")
                run_id = client.call("local_gpu_start_run", start)["run_id"]
                before = client.call("local_gpu_get_run", {"run_id": run_id})
                args = {"run_id": run_id, "idempotency_key": key, "action": "initial", "edit_mode": "txt2img",
                        "plan": _build_plan(before["request"], 4101), "seed": 4101, "change_summary": "Known-job real recovery validation"}
                receipt(root, "request.json", args)
                try:
                    client.call("local_gpu_generate_round", args)
                    raise RuntimeError("expected_owned_client_exit_missing")
                except ProductClientError as error:
                    if str(error) != "server_eof":
                        raise
            finally:
                client.close()
            if client.process.returncode != 72:
                raise RuntimeError("crash_checkpoint_not_confirmed")
            job = json.loads((root / "retained-job.json").read_text())["job_id"]
            decision = oracle.observe_until([job], deadline_monotonic=time.monotonic() + max(0, end - time.time()))
            receipt(root, "known-oracle.json", decision.evidence())
            receipt(root, "known-oracle-private.json", oracle.private_capture())
            if not decision.oracle_evaluable:
                raise RuntimeError("known_execution_oracle_missing")
        receipt(root, "restart-inspect.json", fresh_call(env, inspect_id=run_id))
        for change, expected in (("key", "backend_job_unresolved"), ("seed", "idempotency_conflict"), ("prompt", "idempotency_conflict")):
            altered = copy.deepcopy(args)
            if change == "key": altered["idempotency_key"] += "-changed"
            if change == "seed": altered["seed"] += 1
            if change == "prompt": altered["plan"]["positive_prompt"] += " changed"
            try:
                fresh_call(env, altered)
                raise RuntimeError("changed_request_accepted:" + change)
            except ProductClientError as error:
                receipt(root, "rejected-" + change + ".json", {"code": str(error), "expected": expected})
                if str(error) != expected: raise
        n = sends(root / "http.jsonl")
        receipt(root, "recovered.json", fresh_call(env, args))
        receipt(root, "recovered-inspect.json", fresh_call(env, inspect_id=run_id))
        receipt(root, "completed-replay.json", fresh_call(env, args))
        if sends(root / "http.jsonl") != n or n != 1:
            raise RuntimeError("recovery_submitted_again")
        # The same graph is an explicit manual-retrieval comparator, not stop-only.
        payload = json.loads((root / "prompt-1.json").read_text())
        payload["client_id"] = "spe-manual-20261006"
        install_audit(root, end)
        with ComfyUIEventOracle(http.base_url, backend_boot_identity=boot,
                observer_id=payload["client_id"], retain_raw_transport=True) as oracle:
            manual_id = http.post_json("/prompt", payload)["prompt_id"]
            receipt(root, "simple-stop.json", {"state": "unresolved", "job_id": manual_id,
                        "request_sha256": hashlib.sha256(json.dumps(payload["prompt"], sort_keys=True).encode()).hexdigest()})
            decision = oracle.observe_until([manual_id], deadline_monotonic=time.monotonic() + max(0, end-time.time()))
            receipt(root, "manual-oracle.json", decision.evidence())
            receipt(root, "manual-oracle-private.json", oracle.private_capture())
            if not decision.oracle_evaluable: raise RuntimeError("manual_execution_oracle_missing")
        history = http.get_json("/history/" + manual_id)
        images = [(node, image) for node, output in history[manual_id]["outputs"].items() for image in output.get("images", [])]
        if len(images) != 1: raise RuntimeError("manual_output_not_unique")
        node, image = images[0]
        data = http.get_bytes("/view?" + urlencode(image), max_bytes=32 * 1024 ** 2)
        (root / "manual.png").write_bytes(data)
        hashes = {str(p.relative_to(root)): hash_file(p) for p in (root / "outputs").rglob("*.png")}
        from PIL import Image
        with Image.open(root / "manual.png") as img:
            img.load()
            dimensions = list(img.size)
        digest = hashlib.sha256(data).hexdigest()
        if dimensions != [1024, 1024] or digest not in hashes.values():
            raise RuntimeError("manual_vs_product_artifact_mismatch")
        receipt(root, "artifact-comparison.json", {"manual_job_id": manual_id, "output_node": node,
                 "image": image, "sha256": digest, "dimensions": dimensions, "product_files": hashes,
                 "same_bytes": True, "operator_time_benefit_verified": False})
        report.update(status="GENERATED_PENDING_AUTHOR_REVIEW", known_job_id=job,
                      manual_job_id=manual_id, recovery_new_posts=0, prompt_sends=sends(root / "http.jsonl"))
    except Exception as error:
        report.update(stop_reason=type(error).__name__ + ":" + str(error))
    finally:
        cleaned = True
        if backend is not None:
            try:
                report["backend_cleanup"] = stop_owned_process(backend)
            except Exception as error:
                cleaned = False
                report.update(status="STOPPED", cleanup_error=str(error))
        if acquired and cleaned:
            (lock / "reservation.json").unlink()
            lock.rmdir()
        report["prompt_sends"] = sends(root / "http.jsonl")
        receipt(root, "worker-report.json", report)
    return 0 if report["status"] == "GENERATED_PENDING_AUTHOR_REVIEW" else 2


def supervise(config_path):
    if sys.platform != "win32": raise RuntimeError("Windows_only")
    config = json.loads(config_path.read_text())
    root = Path(config["private_root"])
    private_directory(root)
    receipt(root, "configuration.json", config)
    receipt(root, "status.json", {"status": "RUNNING", "started": time.time()})
    with (root / "worker.stdout.log").open("xb") as out, (root / "worker.stderr.log").open("xb") as err:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "worker", str(root / "configuration.json")],
                                 cwd=ROOT, stdout=out, stderr=err)
        receipt(root, "supervisor-audit.json", {"supervisor_pid": os.getpid(), "worker_pid": child.pid, "wall_limit_seconds": 1200})
        try:
            code = child.wait(timeout=1190)
        except subprocess.TimeoutExpired:
            stop_owned_process(child)
            code = 124
            # taskkill /T /F stopped only this supervisor's worker tree.
            lock = Path(config["lock_root"])
            marker = lock / "reservation.json"
            if marker.is_file() and json.loads(marker.read_text()).get("owner_pid") == child.pid:
                marker.unlink()
                lock.rmdir()
        receipt(root, "status.json", {"status": "FINISHED", "worker_exit_code": code, "ended": time.time(),
                "worker_report_exists": (root / "worker-report.json").is_file()})
    return code


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "server": server()
    elif mode == "supervise": raise SystemExit(supervise(Path(sys.argv[2])))
    elif mode == "worker":
        config = json.loads(Path(sys.argv[2]).read_text())
        raise SystemExit(worker(config, Path(config["private_root"])))
    else: raise SystemExit("unknown mode")
