"""Offline runner checks. No Windows connection, nvidia-smi or GPU execution."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from scripts.research import paired_windows_runner as runner
from scripts.research import paired_windows_ops as windows
from scripts.research import run_reserved_windows_paired as cli
from scripts.research.f02_capture import write_private_json
from scripts.research.paired_ambiguity import PRODUCTS, PROTOCOL, WINDOWS_ORDER


NOW = datetime(2026, 10, 1, 6, tzinfo=timezone.utc)


def config():
    return {"protocol": PROTOCOL, "launch_enabled": True, "cache_policy": runner.CACHE_POLICY,
            "budget": dict(runner.BUDGET), "preflight": {
                "clients": {v: {"root": "unused-" + v, "sha": h} for v, h in PRODUCTS.items()},
                "environment": {"model_path": "unused.safetensors", "backend_url": "http://127.0.0.1:8202"},
                "reservation": {"owner": "synthetic CPU test owner", "scope": runner.SCOPE,
                    "start": (NOW - timedelta(minutes=1)).isoformat(), "end": (NOW + timedelta(hours=1)).isoformat(),
                    "hard_timeout_seconds": 3600, "training_state": "idle", "no_concurrent_gpu_work": True,
                    "authorization": "CPU fixture; not a real GPU authorization"}}}


class FakeOps:
    evidence_class = "synthetic_cpu_runner_adapter"
    def __init__(self, clock, *, fail=None, latency=2, mismatched_pair=False):
        self.clock = clock
        self.fail = fail
        self.latency = latency
        self.mismatched_pair = mismatched_pair
        self.events, self.handles, self.stopped, self.closed = [], [], [], False
        self.active = None

    def prepare_root(self, root):
        root.mkdir()
        self.root = root
        self.events.append("prepare")

    def client_command(self):
        return ["CPU-fixture-not-real-MCP"]

    def before_start(self, _config, op_root, _deadline):
        self.events.append("availability-" + op_root.name)
        if self.fail == "busy":
            raise runner.RunnerStop("GPU_busy_no_backend_started")

    def start_backend(self, _config, op_root, _deadline):
        self.assert_no_active()
        if not (self.root / "source-freeze.json").is_file():
            raise AssertionError("source not frozen before start")
        self.active = object()
        self.handles.append(self.active)
        self.events.append("start-" + op_root.name)
        return self.active

    def assert_no_active(self):
        if self.active is not None:
            raise AssertionError("previous backend not stopped")

    def preflight_backend(self, _config, owned, _root):
        if owned is not self.active:
            raise AssertionError("wrong owned handle")
        return "CPU-fixture-boot"

    def run_operation(self, spec, op_root, _identity, _deadline):
        self.events.append(spec.case_id)
        self.clock[0] += self.latency
        if self.fail == "raise":
            raise OSError("synthetic operation failure")
        count = 1 if spec.fault_mode == "F00" else 2
        proxy = 2 if spec.system == "B2" and spec.fault_mode != "F00" else 1
        upstream = proxy - (1 if spec.fault_mode == "FPRE" else 0)
        digest = "same-input" if not self.mismatched_pair or spec.system == "B2" else "different-input"
        observer = op_root / "observer"
        observer.mkdir()
        write_private_json(observer, "operation-outcomes.json", {"semantic_digest": digest,
            "client_completion": spec.fault_mode == "F00" or spec.system == "B2"})
        if self.fail == "source_drift":
            (self.root / "source-freeze.json").write_text("changed")
        return {"case_id": spec.case_id, "status": "STOPPED" if self.fail == "control" else "COMPLETED",
                "stop_reason": "synthetic_control_failed" if self.fail == "control" else None,
                "product_call_count": count, "calls": [{"generation_request_monotonic_ns": 100,
                    "generation_return_monotonic_ns": 100 + int(self.latency * 1e9)}] * count,
                "metrics": {"S_proxy": proxy, "S_upstream": upstream, "A": upstream, "E_bound": upstream}}

    def stop_backend(self, owned, op_root, _deadline):
        if owned is not self.active:
            raise AssertionError("attempted to stop an unowned process")
        self.stopped.append(owned)
        self.events.append("stop-" + op_root.name)
        self.active = None
        return {"stopped": self.fail != "cleanup"}

    def close(self):
        self.closed = True


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "campaign"
        self.clock = [0.0]

    @staticmethod
    def freeze(_config, root):
        write_private_json(root, "source-freeze.json", {"synthetic": True})
        return {"synthetic": True}

    @staticmethod
    def verify(_config, _hashes):
        return

    def run_fixture(self, configuration=None, **options):
        cfg = configuration or config()
        ops = FakeOps(self.clock, **options)
        report = runner.run_reserved(cfg, self.root, ops=ops, clock=lambda: self.clock[0], now=lambda: NOW,
                                     freezer=self.freeze, verifier=self.verify)
        return report, ops

    def test_six_operations_use_six_distinct_owned_backends_and_fixed_order(self):
        cfg = config(); original = copy.deepcopy(cfg)
        report, ops = self.run_fixture(cfg)
        self.assertEqual(report["status"], "COMPLETED")
        self.assertEqual(report["evidence_class"], "synthetic_cpu_runner_adapter")
        self.assertEqual([e for e in ops.events if e.startswith(("B2_", "W3_"))],
                         [f"{v}_{f}" for v, f in WINDOWS_ORDER])
        self.assertEqual(len({id(p) for p in ops.handles}), 6)
        self.assertEqual(ops.handles, ops.stopped)
        self.assertEqual(report["totals"], {"operations": 6, "product_calls": 10, "proxy_posts": 8, "upstream_attempts": 6})
        self.assertEqual(cfg, original)
        self.assertTrue(ops.closed)

    def test_training_busy_or_disabled_or_expired_starts_nothing(self):
        for condition in ("busy", "disabled", "expired"):
            cfg = config(); ops = FakeOps(self.clock)
            if condition == "busy": cfg["preflight"]["reservation"]["training_state"] = "busy"
            elif condition == "disabled": cfg["launch_enabled"] = False
            else: cfg["preflight"]["reservation"]["end"] = (NOW - timedelta(seconds=1)).isoformat()
            with self.assertRaises(runner.RunnerStop):
                runner.run_reserved(cfg, self.root, ops=ops, now=lambda: NOW)
            self.assertEqual(ops.events, [])
            self.assertFalse(self.root.exists())

    def test_live_busy_result_does_not_acquire_any_backend(self):
        report, ops = self.run_fixture(fail="busy")
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(ops.handles, [])

    def test_control_failure_preserves_record_cleans_owner_and_skips_faults(self):
        report, ops = self.run_fixture(fail="control")
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(len(report["records"]), 1)
        self.assertEqual(ops.handles, ops.stopped)
        self.assertNotIn("W3_F02", ops.events)

    def test_too_slow_controls_stop_without_clamping_or_starting_faults(self):
        report, ops = self.run_fixture(latency=100.1)
        self.assertEqual(report["stop_reason"], "control_calibrated_deadline_exceeds_300")
        self.assertEqual(len(ops.handles), 2)
        self.assertEqual(ops.handles, ops.stopped)

    def test_deadline_of_exactly_300_is_allowed(self):
        report, _ops = self.run_fixture(latency=100)
        self.assertEqual(report["status"], "COMPLETED")

    def test_operation_exception_still_cleans_only_owned_backend(self):
        report, ops = self.run_fixture(fail="raise")
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(len(ops.stopped), 1)

    def test_cleanup_failure_stops_before_next_operation(self):
        report, ops = self.run_fixture(fail="cleanup")
        self.assertEqual(report["stop_reason"], "owned_backend_cleanup_failed")
        self.assertEqual(len(ops.handles), 1)

    def test_semantic_pair_mismatch_stops_after_controls(self):
        report, ops = self.run_fixture(mismatched_pair=True)
        self.assertEqual(report["stop_reason"], "paired_semantics_differ")
        self.assertEqual(len(ops.handles), 2)

    def test_storage_overage_stops_and_retains_root(self):
        with patch.object(runner, "directory_bytes", return_value=runner.BUDGET["storage_bytes"] + 1):
            report, ops = self.run_fixture()
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(ops.handles, [])
        self.assertTrue(self.root.exists())

    def test_short_window_does_not_start_backend(self):
        cfg = config(); cfg["preflight"]["reservation"]["end"] = (NOW + timedelta(seconds=30)).isoformat()
        report, ops = self.run_fixture(cfg)
        self.assertEqual(report["stop_reason"], "insufficient_window_for_operation_and_cleanup")
        self.assertEqual(ops.handles, [])


class PlanAndAdapterTests(unittest.TestCase):
    def test_plan_is_offline_even_when_training_busy(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "config.json"
            cfg = config(); cfg["launch_enabled"] = False; cfg["preflight"]["reservation"]["training_state"] = "busy"
            file.write_text(json.dumps(cfg))
            with patch("subprocess.Popen") as processes, patch.object(windows, "WindowsOps") as live, \
                 patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(cli.main([str(file)]), 0)
            processes.assert_not_called(); live.assert_not_called()
            self.assertFalse(json.loads(output.getvalue())["execution_performed"])
            self.assertEqual(list(Path(folder).iterdir()), [file])

    def test_legacy_scope_or_changed_budget_cannot_enter_new_runner(self):
        for field in ("scope", "budget"):
            cfg = config()
            if field == "scope": cfg["preflight"]["reservation"]["scope"] = "exactly four reviewed F00/F02 single-stage cases"
            else: cfg["budget"]["product_calls"] = 100
            with self.assertRaises(ValueError): runner.plan(cfg)

    def test_missing_exclusivity_or_authorization_is_not_inferred(self):
        for field in ("authorization", "no_concurrent_gpu_work", "owner"):
            cfg = config(); cfg["preflight"]["reservation"].pop(field)
            with self.assertRaises(ValueError): runner.plan(cfg)
        cfg = config(); cfg["preflight"]["reservation"]["authorization"] = None
        with self.assertRaises(ValueError): runner.plan(cfg)

    def test_gpu_compute_query_busy_unknown_and_idle(self):
        self.assertFalse(windows.compute_idle_report("GPU-target, 42, training.exe", "GPU-target")["idle"])
        self.assertTrue(windows.compute_idle_report("", "GPU-target")["idle"])
        for value in ("N/A, 42, python", "unsupported", "GPU-target, N/A, python"):
            with self.assertRaises(runner.RunnerStop): windows.compute_idle_report(value, "GPU-target")

    def test_wddm_baseline_requires_exact_pid_path_and_excludes_compute(self):
        baseline = [{"pid": 42, "process_name": r"C:\Windows\System32\dwm.exe"}]
        row = r"GPU-target, 42, C:\Windows\System32\dwm.exe"
        self.assertTrue(windows.compute_idle_report(row, "GPU-target", baseline)["idle"])
        self.assertFalse(windows.compute_idle_report(row.replace("42", "43"), "GPU-target", baseline)["idle"])
        self.assertFalse(windows.compute_idle_report(row.replace("dwm.exe", "other.exe"), "GPU-target", baseline)["idle"])
        for name in (r"C:\Python\python.exe", r"D:\work\training.exe", "dwm.exe"):
            with self.assertRaises(runner.RunnerStop):
                windows.compute_idle_report("", "GPU-target", [{"pid": 42, "process_name": name}])

    def test_windows_cleanup_command_targets_exact_owned_pid_only(self):
        class Owned:
            pid = 12345
            result = None
            def poll(self): return self.result
            def wait(self, timeout): return self.result
        process = Owned()
        def kill(command, **_):
            self.assertEqual(command, ["taskkill", "/PID", "12345", "/T", "/F"])
            process.result = -9
            return subprocess.CompletedProcess(command, 0)
        with patch.object(windows.sys, "platform", "win32"), patch.object(windows.subprocess, "run", side_effect=kill) as call:
            self.assertTrue(windows.stop_owned_process(process)["stopped"])
        self.assertEqual(call.call_count, 1)

    def test_execute_on_non_windows_fails_before_process_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "config.json"; cfg = config()
            now = datetime.now(timezone.utc)
            cfg["preflight"]["reservation"].update(start=(now-timedelta(minutes=1)).isoformat(),
                end=(now+timedelta(hours=1)).isoformat())
            file.write_text(json.dumps(cfg))
            with patch.object(cli.sys, "platform", "darwin"), patch("subprocess.Popen") as process, \
                 patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(cli.main([str(file), "--execute", "--private-root", str(Path(folder)/"unused")]), 2)
            process.assert_not_called()
            self.assertFalse((Path(folder)/"unused").exists())

    def test_byte_snapshot_preserves_crlf_and_verifier_detects_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder); cfg = config()
            for variant in PRODUCTS:
                product = parent / variant
                (product / "scripts/local_gpu_imagegen").mkdir(parents=True)
                (product / "scripts/mcp_server.py").write_bytes(b"# synthetic\r\n")
                (product / "scripts/local_gpu_imagegen/example.py").write_bytes(b"pass\r\n")
                cfg["preflight"]["clients"][variant]["root"] = str(product)
            backend = parent / "backend"; backend.mkdir(); (backend / "main.py").write_bytes(b"# synthetic\r\n")
            cfg["preflight"]["environment"]["comfy_root"] = str(backend)
            capture = parent / "capture"; capture.mkdir()
            with patch.object(runner.subprocess, "check_output", return_value=b"main.py\0"):
                hashes = runner.freeze_sources(cfg, capture)
            self.assertEqual((capture / "source-snapshot/B2/scripts/mcp_server.py").read_bytes(), b"# synthetic\r\n")
            runner.verify_sources(cfg, hashes)
            (backend / "main.py").write_bytes(b"changed\r\n")
            with self.assertRaisesRegex(runner.RunnerStop, "source_changed"):
                runner.verify_sources(cfg, hashes)


class SupervisorTests(unittest.TestCase):
    """Mock Windows-owned process handles. No native commands are executed."""
    def exercise(self, *, storage=False, worker_success=False):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder); cfg = config(); file = parent / "input.json"
            file.write_text(json.dumps(cfg)); root = parent / "private"
            clock = [0.0]
            class Process:
                pid = 9876
                returncode = None
                def poll(self): return self.returncode
            process = Process()
            def popen(_command, **_kwargs):
                if worker_success:
                    (root / "campaign").mkdir()
                    write_private_json(root / "campaign", "runner-report.json", {"status": "COMPLETED", "stop_reason": None})
                    process.returncode = 0
                return process
            def stop(p):
                self.assertIs(p, process)
                p.returncode = -9
                return {"stopped": True, "pid": p.pid}
            def sleep(_seconds):
                clock[0] += 3600
            with patch.object(cli.sys, "platform", "win32"), \
                 patch.object(windows, "private_directory", side_effect=lambda p: p.mkdir()), \
                 patch.object(windows, "stop_owned_process", side_effect=stop) as stopped, \
                 patch.object(cli, "directory_bytes", return_value=runner.BUDGET["storage_bytes"]+1 if storage else 0):
                result = cli.supervise(cfg, file, root, popen=popen, clock=lambda: clock[0], sleep=sleep, now=lambda: NOW)
            return result, stopped.call_count

    def test_storage_limit_stops_only_owned_worker_tree(self):
        report, calls = self.exercise(storage=True)
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(report["stop_reason"], "supervisor_storage_limit")
        self.assertEqual(calls, 1)

    def test_wall_limit_stops_only_owned_worker_tree(self):
        report, calls = self.exercise()
        self.assertEqual(report["status"], "STOPPED")
        self.assertEqual(report["stop_reason"], "supervisor_wall_limit")
        self.assertEqual(calls, 1)

    def test_complete_child_does_not_become_gpu_compute_authentication(self):
        report, calls = self.exercise(worker_success=True)
        self.assertEqual(report["status"], "COMPLETED")
        self.assertFalse(report["gpu_compute_execution_verified"])
        self.assertEqual(calls, 0)


if __name__ == "__main__":
    unittest.main()
