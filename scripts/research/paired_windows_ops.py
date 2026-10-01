"""Windows process adapter. Never invoked by plan-only mode or CPU fixtures."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener

from scripts.research import f02_preflight as legacy
from scripts.research.f02_capture import write_private_json
from scripts.research.f02_campaign import ProductCallOutcome, _parse_product_result, _reported_state
from scripts.research.paired_ambiguity_operation import run_operation
from scripts.research.paired_windows_runner import RunnerStop, SCOPE


def stop_owned_process(process, *, timeout=5):
    """Only the still-live process represented by this Popen object and its tree."""
    if process.poll() is None:
        if sys.platform == "win32":
            killed = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                    capture_output=True, timeout=timeout)
            if killed.returncode != 0 and process.poll() is None:
                raise RunnerStop("owned_process_tree_cleanup_failed")
        else:
            # Used only for locally owned CPU subprocess tests.
            process.terminate()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=timeout)
    return {"stopped": process.poll() is not None, "pid": process.pid, "exit_code": process.poll()}


def private_directory(root):
    if sys.platform != "win32":
        raise RunnerStop("Windows_execution_adapter_requires_Windows")
    root.mkdir(mode=0o700)
    result = subprocess.run(["icacls", str(root), "/inheritance:r", "/grant:r",
                             os.environ["USERNAME"] + ":(OI)(CI)F"], capture_output=True, timeout=10)
    if result.returncode != 0:
        raise RunnerStop("private_ACL_setup_failed")


def compute_idle_report(stdout, target_uuid, desktop_baseline=()):
    """Reject missing UUIDs/unsupported rows rather than infer idleness."""
    processes = []
    baseline = set()
    for item in desktop_baseline:
        name = item["process_name"].replace("/", "\\").lower()
        executable = name.rsplit("\\", 1)[-1]
        if not name or not isinstance(item["pid"], int) or not name[1:3] == ":\\":
            raise RunnerStop("invalid_WDDM_desktop_baseline")
        if any(token in executable for token in ("python", "comfy", "train", "cuda", "wsl")):
            raise RunnerStop("compute_process_cannot_be_desktop_baseline")
        baseline.add((item["pid"], name))
    for line in stdout.splitlines():
        if not line.strip():
            continue
        fields = [s.strip() for s in line.split(",", 2)]
        if len(fields) != 3 or not fields[0].startswith("GPU-") or not fields[1].isdigit():
            raise RunnerStop("GPU_compute_query_uninterpretable")
        if fields[0] == target_uuid:
            processes.append({"gpu_uuid": fields[0], "pid": int(fields[1]), "process_name": fields[2]})
    unexpected = [p for p in processes if (p["pid"], p["process_name"].replace("/", "\\").lower()) not in baseline]
    return {"target_compute_processes": processes, "unexpected_processes": unexpected,
            "idle": not unexpected, "desktop_baseline_count": len(baseline),
            "scope": "process_view_with_explicit_WDDM_baseline_not_global_exclusivity_proof"}


class WindowsOps:
    evidence_class = "Windows_real_backend_campaign"

    def __init__(self):
        if sys.platform != "win32":
            raise RunnerStop("Windows_only")
        self.opener = build_opener(ProxyHandler({}))
        self.backend = None
        self.log_handles = []

    def prepare_root(self, root):
        private_directory(root)

    def client_command(self):
        return [sys.executable, str(Path(__file__).with_name("f02_product_client.py"))]

    def before_start(self, config, op_root, deadline):
        # GPU-idle check precedes checkpoint hashing and every backend startup.
        env = config["preflight"]["environment"]
        command = ["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name", "--format=csv,noheader"]
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=max(.01, min(10, deadline - time.monotonic())))
        if result.returncode != 0:
            raise RunnerStop("GPU_compute_query_failed")
        baseline = config.get("resource_policy", {}).get("wddm_desktop_baseline", [])
        idle = compute_idle_report(result.stdout, env["gpu_uuid"], baseline)
        write_private_json(op_root, "GPU-availability.json", {"command": command, "exit_code": result.returncode,
                                                              "stdout": result.stdout, **idle})
        if not idle["idle"]:
            raise RunnerStop("GPU_busy_no_backend_started")
        identities = [legacy._frozen_identity_config_check(config["preflight"]["ledger"]["anchor"],
                        env, config["preflight"]["reservation"], expected_scope=SCOPE),
                      legacy._hostname_check(env["host_id"]), legacy._gpu_check(env["gpu_uuid"], env["gpu_model"])]
        if any(not item.passed for item in identities):
            write_private_json(op_root, "site-identity-checks.json", [item.__dict__ for item in identities])
            raise RunnerStop("frozen_site_identity_failed")
        # Existing listeners belong to somebody else, even if HTTP is broken.
        url = urlsplit(env["backend_url"])
        try:
            with socket.create_connection((url.hostname, url.port or 80), timeout=1):
                pass
        except ConnectionRefusedError:
            pass
        except OSError:
            raise RunnerStop("backend_port_state_unknown")
        else:
            raise RunnerStop("existing_backend_or_listener_not_owned")
        checks = [legacy._contract_check(config["preflight"]["ledger"]["root"],
                                         config["preflight"]["ledger"]["anchor"])]
        checks += legacy._client_checks(config["preflight"]["clients"])
        checks += [legacy._model_hash_check(env["model_path"], env["model_sha256"])]
        comfy = Path(env["comfy_root"])
        revision = subprocess.check_output(["git", "-C", str(comfy), "rev-parse", "HEAD"], text=True, timeout=10).strip()
        dirty = subprocess.check_output(["git", "-C", str(comfy), "status", "--porcelain", "--untracked-files=no"], text=True, timeout=10).strip()
        write_private_json(op_root, "pre-start-checks.json", {"checks": [item.__dict__ for item in checks],
                                                            "comfy_revision": revision, "comfy_tracked_dirty": bool(dirty)})
        if any(not item.passed for item in checks) or revision != env["comfy_sha"] or dirty:
            raise RunnerStop("pre_start_source_or_model_checks_failed")
        if time.monotonic() >= deadline:
            raise RunnerStop("pre_start_check_timeout")

    def start_backend(self, config, op_root, deadline):
        env = config["preflight"]["environment"]
        comfy = Path(env["comfy_root"])
        command = [str(comfy.parent / "python_embeded/python.exe"), "-s", str(comfy / "main.py"),
                   "--windows-standalone-build", "--listen", "127.0.0.1", "--port", "8202"]
        child_env = os.environ.copy()
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            child_env.pop(key, None)
        stdout = (op_root / "backend.stdout.log").open("xb")
        stderr = (op_root / "backend.stderr.log").open("xb")
        self.log_handles = [stdout, stderr]
        try:
            self.backend = subprocess.Popen(command, cwd=comfy.parent, env=child_env, stdout=stdout, stderr=stderr)
            write_private_json(op_root, "backend-start.json", {"command": command, "pid": self.backend.pid,
                                                               "wall_time": time.time(), "monotonic": time.monotonic()})
            while time.monotonic() < deadline:
                if self.backend.poll() is not None:
                    raise RunnerStop("owned_backend_exited_during_startup")
                try:
                    with self.opener.open(env["backend_url"] + "/queue", timeout=1) as response:
                        queue = json.load(response)
                    if queue.get("queue_running") or queue.get("queue_pending"):
                        raise RunnerStop("owned_backend_initial_queue_not_empty")
                    return self.backend
                except OSError:
                    time.sleep(.2)
            raise RunnerStop("backend_startup_timeout")
        except Exception:
            # Startup may fail before returning its handle to the scheduler.
            if self.backend is not None:
                write_private_json(op_root, "startup-failure-cleanup.json", stop_owned_process(self.backend))
                self.backend = None
            self._close_logs()
            raise

    def preflight_backend(self, config, owned, op_root):
        environment = dict(config["preflight"]["environment"], comfy_pid=owned.pid)
        check, identity = legacy._backend_check(environment)
        write_private_json(op_root, "backend-preflight.json", {"check": check.__dict__, "boot_identity": identity})
        if not check.passed or not identity:
            raise RunnerStop("owned_backend_preflight_failed")
        return identity

    def run_operation(self, spec, op_root, boot_identity, deadline):
        return run_operation(spec, evidence_root=op_root / "observer", boot_identity=boot_identity,
                             deadline=deadline, invoker=self.invoke_product)

    def invoke_product(self, spec, index, proxy_url, timeout):
        env = os.environ.copy()
        env.update({"LOCAL_GPU_IMAGEGEN_COMFYUI_URL": spec.backend_url,
                    "LOCAL_GPU_IMAGEGEN_RESEARCH_PROMPT_PROXY_URL": proxy_url,
                    "LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED": "0", "LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS": "0",
                    "LOCAL_GPU_IMAGEGEN_OUTPUT_DIR": spec.output_root, "LOCAL_GPU_IMAGEGEN_OUTPUT_ROOT": spec.output_root,
                    "LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH": spec.research_model_path,
                    "LOCAL_GPU_IMAGEGEN_F02_CASE_ID": spec.case_id, "LOCAL_GPU_IMAGEGEN_F02_FAULT_MODE": spec.fault_mode,
                    "LOCAL_GPU_IMAGEGEN_F02_CALL_INDEX": str(index), "LOCAL_GPU_IMAGEGEN_F02_OPERATION_KEY": spec.operation_key,
                    "LOCAL_GPU_IMAGEGEN_F02_RETRY_SCOPE": spec.retry_scope,
                    "LOCAL_GPU_IMAGEGEN_F02_PRIVATE_CAPTURE_DIR": spec.private_capture_root,
                    "LOCAL_GPU_IMAGEGEN_CLIENT_ROOT": spec.working_directory})
        process = subprocess.Popen(spec.command, cwd=spec.working_directory, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            stop_owned_process(process)
            stdout, stderr = process.communicate(timeout=5)
        result, failure = _parse_product_result(stdout)
        state = _reported_state(result, process.returncode)
        return ProductCallOutcome(process.returncode, timed_out, state, result,
                                  sha256(stdout.encode()).hexdigest(), sha256(stderr.encode()).hexdigest(),
                                  "product_call_timeout" if timed_out else failure)

    def _close_logs(self):
        for handle in self.log_handles:
            handle.close()
        self.log_handles = []

    def stop_backend(self, owned, op_root, deadline):
        del op_root
        if owned is not self.backend:
            raise RunnerStop("unowned_backend_handle")
        result = stop_owned_process(owned, timeout=max(.01, min(5, deadline - time.monotonic())))
        self.backend = None
        self._close_logs()
        return result

    def close(self):
        if self.backend is not None:
            stop_owned_process(self.backend)
            self.backend = None
        self._close_logs()
