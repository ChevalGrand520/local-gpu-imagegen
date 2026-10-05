"""Cross-process CPU integration probes; fake HTTP backend, no model or GPU.

The parent owns the server; each product action gets a fresh interpreter and
RunStore. Catalog/route authorization and visual review are synthetic fixtures.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from tests import test_asset_run_engine as engine_fixtures
from tests import test_comfyui_adapter as adapter_fixtures
from tests.test_asset_run_engine import TEST_MODEL_ID, write_test_png
from tests.fake_backend_server import FakeResponse
from local_gpu_imagegen.backends.comfyui import ComfyUIAdapter
from local_gpu_imagegen.errors import AssetEngineError, ValidationError
from local_gpu_imagegen.run_store import RunStore
from local_gpu_imagegen.workflow_templates import WorkflowTemplateRegistry


def worker(directory: Path, action: str) -> dict:
    config = json.loads((directory / "config.json").read_text())
    if action.startswith("stop_"):
        return stop_worker(directory, config, action)
    fixture = engine_fixtures.AssetRunEngineTests()
    fixture.setUp()
    try:
        model = config["model"]
        fixture.catalog.identity_token = model["identity_token"]
        fixture.catalog.model = lambda: {
            **copy.deepcopy(model), "id": TEST_MODEL_ID, "source": "test-fixture",
            "license_id": "test-only", "license_status": "approved",
        }
        fixture.capabilities["available_backends"].append("comfyui")
        fixture.output_root = directory / "outputs"
        engine = fixture.engine
        engine.store = RunStore(fixture.output_root)
        engine.workflows = WorkflowTemplateRegistry(ROOT / "workflows/comfyui", directory / "workflow-state")
        adapter = ComfyUIAdapter(config["url"], timeout=0, poll_interval=0, sleep=lambda _: None)

        def run_backend(request):
            if action == "crash_before_send":
                submission = request["backend_submission_callback"]

                def crash_before_send():
                    submission()
                    os._exit(73)

                request["backend_submission_callback"] = crash_before_send
            if action == "disk_failure_before_send":
                def disk_failure():
                    raise OSError("Injected persistence failure before POST")
                request["backend_submission_callback"] = disk_failure
            if action in {"crash_before_binding", "crash_after_binding"}:
                callback = request.get("backend_job_callback")

                def crash(job_id):
                    if action == "crash_after_binding" and callable(callback):
                        callback(job_id)
                    os._exit(71 if action == "crash_before_binding" else 72)

                request["backend_job_callback"] = crash
            return adapter.generate(request)

        engine.backend_runner = run_backend
        state_file = directory / "operation.json"
        if not state_file.exists():
            start = fixture.start_arguments(max_rounds=1)
            start["backend"] = "comfyui"
            route = fixture.router.issue(start)
            route.update({
                "endpoint_identity": model["endpoint_identity"],
                "identity_token": model["identity_token"],
                "identity_strength": model["identity_strength"],
                "workflow_template_id": "sd15-txt2img", "workflow_template_version": 1,
            })
            fixture.router.routes[route["route_token"]] = copy.deepcopy(route)
            start["route_token"] = route["route_token"]
            run_id = engine.start_run(start)["run_id"]
            args = fixture.generate_arguments(run_id, max_rounds=1)
            plan = fixture.plan(route=route, max_rounds=1, parameters={"sampler": "euler", "scheduler": "normal", "steps": 4})
            plan["backend"] = "comfyui"
            args["plan"] = plan
            state_file.write_text(json.dumps(args))
        args = json.loads(state_file.read_text())
        run_id = args["run_id"]
        before = engine.get_run({"run_id": run_id})
        if action == "inspect":
            return {"pid": os.getpid(), "run": before}
        if action == "changed_key":
            args["idempotency_key"] = "changed-key"
        elif action == "changed_seed":
            args["seed"] += 1
        elif action == "changed_prompt":
            args["plan"]["positive_prompt"] += " changed"
        elif action == "changed_model":
            fixture.catalog.drift()
        if action == "finalize":
            # This is a fabricated acceptance input for API validation, not
            # evidence of human image quality review.
            reviewed = fixture.review(run_id, 1)
            engine.finalize_run({
                "run_id": run_id, "round_number": 1,
                "summary": "Synthetic CPU API acceptance only.",
                "confirmation": reviewed["finalization_candidate"]["confirmation"],
            })
        else:
            try:
                engine.generate_round(args)
            except AssetEngineError as error:
                return {"pid": os.getpid(), "error": error.code, "details": str(error), "run": engine.get_run({"run_id": run_id})}
            except OSError as error:
                return {"pid": os.getpid(), "error": "OSError", "details": str(error), "run": engine.get_run({"run_id": run_id})}
        after = engine.get_run({"run_id": run_id})
        return {"pid": os.getpid(), "run": after}
    finally:
        fixture.tearDown()


def stop_worker(directory, config, action):
    """Explicit tiny comparator: durable stop + optional manual retrieval.

    Single sequential owner and atomic replacement only. No concurrent locks,
    route verification, role-specific output validation or quality review.
    It receives the same submitted graph as the tool, not a weakened request.
    """
    record = directory / "stop.json"

    def save(value):
        temporary = record.with_suffix(".pending")
        temporary.write_text(json.dumps(value, sort_keys=True))
        os.replace(temporary, record)

    def request(path, payload=None):
        req = urllib.request.Request(config["url"] + path, data=json.dumps(payload).encode() if payload is not None else None, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read()

    if not record.exists():
        payload = json.loads((directory / "control-request.json").read_text())
        state = {"state": "unresolved", "request_hash": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(), "job_id": None}
        save(state)  # conservative send intent, just as in the full tool
        result = json.loads(request("/prompt", payload))
        state["job_id"] = result["prompt_id"]
        save(state)
    state = json.loads(record.read_text())
    if action == "stop_recover":
        job_id = state["job_id"]
        history = json.loads(request("/history/" + job_id))
        image = history[job_id]["outputs"]["9"]["images"][0]
        data = request("/view?" + urllib.parse.urlencode(image))
        (directory / "stop-final.png").write_bytes(data)
        state.update(state="finalized", sha256=hashlib.sha256(data).hexdigest())
        save(state)
    return {"pid": os.getpid(), "run": state, "record_bytes": record.stat().st_size}


class ProcessRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.http = adapter_fixtures.ComfyUIAdapterTests()
        self.http.setUp()
        (self.directory / "config.json").write_text(json.dumps({"model": self.http.model, "url": self.http.server.url}))
        image = self.directory / "synthetic.png"
        write_test_png(image)
        self.image_bytes = image.read_bytes()
        self.http.server.routes[("GET", "/view?filename=result.png&subfolder=&type=output")] = FakeResponse(body=self.image_bytes)
        self.http.server.requests.clear()
        self.receipts = []

    def tearDown(self):
        self.http.tearDown()
        self.temp.cleanup()

    def invoke(self, action, exit_code=0):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker", str(self.directory), action], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, exit_code, result.stderr + result.stdout)
        if exit_code:
            self.receipts.append({"action": action, "exit": exit_code})
            return None
        receipt = json.loads(result.stdout)
        self.receipts.append({"action": action, "pid": receipt["pid"], "state": receipt["run"]["state"], "error": receipt.get("error")})
        return receipt

    def pending(self):
        self.http.server.routes[("GET", "/history/prompt-1")] = FakeResponse.json({})
        self.http.server.routes[("GET", "/queue")] = FakeResponse.json({"queue_pending": [[1, "prompt-1", {}, {}, []]], "queue_running": []})

    def posts(self):
        return sum(r["method"] == "POST" and r["path"] == "/prompt" for r in self.http.server.requests)

    def publish_receipt(self, name, **extra):
        target = os.environ.get("SPE_CPU_RECEIPT_DIR")
        if target:
            # Runner explicitly chooses a fresh local artifact directory.
            path = Path(target)
            path.mkdir(parents=True, exist_ok=True)
            (path / (name + ".json")).write_text(json.dumps({
                "scope": "CPU subprocess + real adapter + fake HTTP; no real ComfyUI/GPU",
                "process_actions": self.receipts, "prompt_posts": self.posts(),
                "http_requests": [{"method": r["method"], "path": r["path"]} for r in self.http.server.requests],
                **extra,
            }, indent=2) + "\n")

    def test_known_job_restart_recovery_and_finalization(self):
        self.pending()
        first = self.invoke("submit")
        self.assertEqual(first["error"], "comfyui_job_timed_out")
        self.assertEqual(first["run"]["state"], "unresolved")
        binding = first["run"]["attempts"][-1]
        self.assertEqual(binding["backend_job"]["job_id"], "prompt-1")
        self.assertEqual(self.invoke("inspect")["run"]["attempts"][-1]["request_hash"], binding["request_hash"])
        for action, error in [("changed_key", "backend_job_unresolved"), ("changed_seed", "idempotency_conflict"), ("changed_prompt", "idempotency_conflict"), ("changed_model", "model_identity_drifted")]:
            self.assertEqual(self.invoke(action)["error"], error)
            self.assertEqual(self.posts(), 1)
        self.http.server.routes[("GET", "/history/prompt-1")] = FakeResponse.json(self.http.completed_history())
        recovered = self.invoke("recover")["run"]
        self.assertEqual(recovered["state"], "generated")
        self.assertEqual(len(recovered["rounds"]), 1)
        round_image = recovered["rounds"][0]["image"]
        run_root = self.directory / "outputs/runs" / recovered["run_id"]
        self.assertEqual((run_root / round_image["path"]).read_bytes(), self.image_bytes)
        request_count = len(self.http.server.requests)
        self.invoke("recover")  # completed replay
        self.assertEqual(len(self.http.server.requests), request_count)
        final = self.invoke("finalize")["run"]
        self.assertEqual(final["state"], "finalized")
        self.assertEqual((run_root / "final.png").read_bytes(), self.image_bytes)
        self.assertEqual(self.invoke("inspect")["run"]["state"], "finalized")
        self.assertEqual(self.posts(), 1)
        pids = [r["pid"] for r in self.receipts]
        self.assertEqual(len(pids), len(set(pids)))
        self.publish_receipt("known-job", final_sha256=hashlib.sha256(self.image_bytes).hexdigest(), manifest_bytes=(run_root / "manifest.json").stat().st_size, run_file_bytes=sum(f.stat().st_size for f in run_root.rglob('*') if f.is_file()), review_is_synthetic=True)

    def test_crash_after_send_before_job_binding_blocks_all_keys(self):
        self.pending()
        self.invoke("crash_before_binding", 71)
        restarted = self.invoke("inspect")["run"]
        self.assertEqual(self.posts(), 1)
        self.assertEqual(restarted["state"], "unresolved")
        self.assertEqual(restarted["attempts"][-1]["submission_outcome"], "unknown")
        for action in ("recover", "changed_key"):
            self.assertEqual(self.invoke(action)["error"], "submission_outcome_unknown")
        self.assertEqual(self.posts(), 1)
        self.publish_receipt("crash-before-binding")

    def test_crash_after_job_binding_recovers_without_post(self):
        self.pending()
        self.invoke("crash_after_binding", 72)
        restarted = self.invoke("inspect")["run"]
        self.assertEqual(restarted["state"], "unresolved")
        self.assertEqual(restarted["attempts"][-1]["backend_job"]["job_id"], "prompt-1")
        self.http.server.routes[("GET", "/history/prompt-1")] = FakeResponse.json(self.http.completed_history())
        self.assertEqual(self.invoke("recover")["run"]["state"], "generated")
        self.assertEqual(self.posts(), 1)
        self.publish_receipt("crash-after-binding")

    def test_crash_between_intent_and_send_is_false_block(self):
        self.invoke("crash_before_send", 73)
        self.assertEqual(self.invoke("inspect")["run"]["state"], "unresolved")
        self.assertEqual(self.invoke("recover")["error"], "submission_outcome_unknown")
        self.assertEqual(self.posts(), 0)
        self.publish_receipt("intent-before-send-false-block")

    def test_manual_stop_retrieval_can_match_artifact_completion(self):
        self.pending()
        self.invoke("submit")
        tool_post = next(r for r in self.http.server.requests if r["path"] == "/prompt")
        (self.directory / "control-request.json").write_bytes(tool_post["body"])
        first_stop = self.invoke("stop_submit")
        request_count = len(self.http.server.requests)
        self.assertEqual(self.invoke("stop_inspect")["run"]["state"], "unresolved")
        self.assertEqual(len(self.http.server.requests), request_count)
        self.assertEqual(self.posts(), 2)  # one per separate path, no retry
        self.http.server.routes[("GET", "/history/prompt-1")] = FakeResponse.json(self.http.completed_history())
        self.invoke("recover")
        self.invoke("finalize")
        manual = self.invoke("stop_recover")
        self.assertEqual(manual["run"]["state"], "finalized")
        self.assertEqual((self.directory / "stop-final.png").read_bytes(), self.image_bytes)
        self.assertEqual(self.posts(), 2)
        self.publish_receipt("stop-manual-comparison", stop_record_bytes=first_stop["record_bytes"], manual_record_bytes=manual["record_bytes"], stop_only_state="unresolved", manual_retrieval_matches_bytes=True, control_scope="single sequential owner; same graph; synthetic backend; no execution count")

    def test_failed_intent_persistence_prevents_post(self):
        first = self.invoke("disk_failure_before_send")
        self.assertEqual(first["error"], "OSError")
        self.assertEqual(self.posts(), 0)
        self.assertEqual(first["run"]["state"], "created")
        self.publish_receipt("persistence-before-send-failure")

    def test_invalid_lifecycle_controls_fail_before_http(self):
        for controls in (
            {"recovery_job_id": "../wrong"},
            {"backend_job_callback": "not-callable"},
            {"backend_submission_callback": "not-callable"},
        ):
            with self.subTest(controls=controls), self.assertRaises(ValidationError):
                self.http.adapter.generate(self.http.request(**controls))
        self.assertEqual(self.http.server.requests, [])

    def test_view_failure_retains_job_for_another_recovery(self):
        self.http.server.routes[("GET", "/view?filename=result.png&subfolder=&type=output")] = FakeResponse(body=b"not-png")
        failed = self.invoke("submit")
        self.assertEqual(failed["run"]["state"], "unresolved")
        self.assertEqual(failed["run"]["attempts"][-1]["backend_job"]["job_id"], "prompt-1")
        self.http.server.routes[("GET", "/view?filename=result.png&subfolder=&type=output")] = FakeResponse(body=self.image_bytes)
        self.assertEqual(self.invoke("recover")["run"]["state"], "generated")
        self.assertEqual(self.posts(), 1)
        self.publish_receipt("view-failure-recovery")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        print(json.dumps(worker(Path(sys.argv[2]), sys.argv[3])))
    else:
        unittest.main()
