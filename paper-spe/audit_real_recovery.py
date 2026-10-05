"""Recompute receipt consistency. Not an independent reviewer or GPU oracle."""
from __future__ import annotations

import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def audit(root):
    worker = read(root, "worker-report.json")
    status = read(root, "status.json")
    assert status["status"] == "FINISHED" and status["worker_exit_code"] == 0
    assert worker["status"] == "GENERATED_PENDING_AUTHOR_REVIEW"
    assert worker["author_review"] is False and worker["finalized"] is False
    assert worker["backend_cleanup"]["stopped"] is True
    ledger = [json.loads(line) for line in (root / "http.jsonl").read_text().splitlines()]
    intents = [row for row in ledger if row["event"] == "send_intent"]
    responses = [row for row in ledger if row["event"] == "response"]
    assert len(intents) == len(responses) == worker["prompt_sends"] == 2
    assert worker["recovery_new_posts"] == 0
    assert [r["response"]["prompt_id"] for r in responses] == [worker["known_job_id"], worker["manual_job_id"]]
    assert read(root, "retained-job.json")["job_id"] == worker["known_job_id"]
    jobs = {}
    for label in ("known", "manual"):
        prompt_id = worker[label + "_job_id"]
        oracle = read(root, label + "-oracle.json")
        capture = read(root, label + "-oracle-private.json")
        assert oracle["status"] == "evaluable"
        events = []
        for message in capture["websocket_messages"]:
            body = base64.b64decode(message["body_base64"], validate=True)
            assert digest(body) == message["body_sha256"]
            events.append(json.loads(body))
        starts = [e for e in events if e["type"] == "execution_start" and e["data"]["prompt_id"] == prompt_id]
        terminals = [e for e in events if e["type"] == "execution_success" and e["data"]["prompt_id"] == prompt_id]
        assert len(starts) == len(terminals) == 1
        histories = []
        for response in capture["history_responses"]:
            body = base64.b64decode(response["body_base64"], validate=True)
            assert digest(body) == response["body_sha256"]
            histories.append(json.loads(body))
        history = next(item[prompt_id] for item in reversed(histories) if prompt_id in item)
        assert history["status"]["completed"] is True
        assert history["prompt"][1] == prompt_id
        payload = read(root, "prompt-1.json" if label == "known" else "prompt-2.json")
        assert history["prompt"][2] == payload["prompt"]
        assert history["prompt"][3]["client_id"] == capture["observer_id"] == payload["client_id"]
        binding = oracle["bindings"][0]
        assert binding["prompt_id"] == prompt_id and binding["history_completed"] is True
        jobs[label] = {
            "prompt_id": prompt_id,
            "execution_instance_id": binding["execution_instance_id"],
            "backend_event_span_seconds": binding["finished_at"] - binding["started_at"],
            "event_counts": dict(Counter(e["type"] for e in events)),
            "cached_nodes": [e["data"]["nodes"] for e in events if e["type"] == "execution_cached"],
            "output_node": "9",
            "output_images": history["outputs"]["9"]["images"],
        }
    a = read(root, "prompt-1.json")["prompt"]
    b = read(root, "prompt-2.json")["prompt"]
    assert a == b
    before, after = read(root, "restart-inspect.json"), read(root, "recovered-inspect.json")
    assert before["state"] == "unresolved" and after["state"] == "generated"
    assert len(before["rounds"]) == 0 and len(after["rounds"]) == 1
    assert before["attempts"][0]["request_hash"] == after["attempts"][-1]["request_hash"]
    assert before["attempts"][0]["backend_job"] == after["attempts"][-1]["backend_job"]
    assert after["attempts"][-1]["status"] == "completed"
    replay = read(root, "completed-replay.json")
    recovered = read(root, "recovered.json")
    assert replay["round"]["image"]["sha256"] == recovered["round"]["image"]["sha256"]
    assert recovered["round"]["backend_result"]["workflow_job_id"] == worker["known_job_id"]
    for field, expected in [("key", "backend_job_unresolved"), ("seed", "idempotency_conflict"), ("prompt", "idempotency_conflict")]:
        assert read(root, "rejected-" + field + ".json")["code"] == expected
    comparison = read(root, "artifact-comparison.json")
    manual = root / "manual.png"
    image_hash = digest(manual.read_bytes())
    assert image_hash == comparison["sha256"] == recovered["round"]["image"]["sha256"]
    files = list((root / "outputs").rglob("*.png"))
    assert len(files) == 1 and digest(files[0].read_bytes()) == image_hash
    from PIL import Image
    with Image.open(manual) as image:
        image.load()
        assert image.size == (1024, 1024)
    run_files = list(files[0].parent.glob("*"))
    return {
        "verdict": "RECEIPT_CONSISTENCY_PASS",
        "independent_reviewer": False,
        "source_sha": read(root, "configuration.json")["source_sha"],
        "jobs": jobs,
        "prompt_sends": 2,
        "recovery_new_posts": 0,
        "request_hash_preserved": before["attempts"][0]["request_hash"],
        "rejections": ["backend_job_unresolved", "idempotency_conflict", "idempotency_conflict"],
        "graph_sha256": digest(json.dumps(a, sort_keys=True, separators=(",", ":")).encode()),
        "image_sha256": image_hash,
        "dimensions": [1024, 1024],
        "run_file_bytes": {f.name: f.stat().st_size for f in run_files if f.is_file()},
        "simple_stop_record_bytes": (root / "simple-stop.json").stat().st_size,
        "manual_image_bytes": manual.stat().st_size,
        "completed_epoch": status["ended"],
        "worker_started_epoch_in_final_receipt": status.get("started"),
        "author_review": False,
        "finalized": False,
        "observer_architecture": "backend-origin read-only observer component in controller worker; separate from MCP product process, not a standalone observer-only process",
    }


if __name__ == "__main__":
    print(json.dumps(audit(Path(sys.argv[1])), indent=2, sort_keys=True))
