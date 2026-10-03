"""Build and audit a local-only minimized paired-capture candidate.

This transformation discards original payload bytes and is not release approval.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import tarfile


CASES = ("B2_F00", "W3_F00", "W3_F02", "B2_F02", "B2_FPRE", "W3_FPRE")
ROOT = "paired-windows-20261001-c/campaign"
SCHEMA = "paired-sanitized-v1"
SOURCE_SHA256 = "141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3"
ALLOWED_EVENTS = {"status", "execution_start", "execution_cached", "progress_state",
                  "executing", "progress", "executed", "execution_success", "execution_error"}
ALLOWED_ERRORS = {None, "backend_request_failed", "submission_outcome_unknown"}
ALLOWED_STATES = {"created", "unresolved", "generated"}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def strict_object(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def token(key: bytes, value: object) -> str:
    if not isinstance(value, (str, int, float, bool)):
        raise ValueError("unsupported pseudonym value")
    return "id-" + hmac.new(key, canonical(value), "sha256").hexdigest()[:24]


def opaque_tree(key: bytes, value: object) -> object:
    if isinstance(value, dict):
        return {token(key, field): opaque_tree(key, item)
                for field, item in sorted(value.items())}
    if isinstance(value, list):
        return [opaque_tree(key, item) for item in value]
    if value is None:
        return None
    return token(key, value)


def semantic_tree(key: bytes, arguments: dict) -> dict:
    selected = {name: value for name, value in arguments.items()
                if name not in {"run_id", "idempotency_key", "change_summary"}}
    plan = strict_object(selected.get("plan"))
    selected["plan"] = {name: value for name, value in plan.items()
                        if name not in {"route_token", "endpoint_identity"}}
    return strict_object(opaque_tree(key, selected))


def member_bytes(bundle: tarfile.TarFile, name: str) -> bytes:
    member = bundle.getmember(name)
    parts = PurePosixPath(member.name).parts
    if member.name.startswith("/") or ".." in parts or not member.isfile():
        raise ValueError("unsafe or non-file archive member")
    stream = bundle.extractfile(member)
    if stream is None:
        raise ValueError("unreadable archive member")
    return stream.read()


def member_json(bundle: tarfile.TarFile, name: str) -> object:
    return json.loads(member_bytes(bundle, name))


def transformed_case(bundle: tarfile.TarFile, case: str, index: int, key: bytes) -> dict:
    system, fault = case.split("_")
    base = f"{ROOT}/{index:02d}-{system}-{fault}"
    observer = base + "/observer/"
    receipts = member_json(bundle, observer + "proxy-receipts.json")
    stages = [json.loads(line) for line in member_bytes(bundle, observer + "proxy-stages.jsonl").splitlines() if line]
    report = strict_object(member_json(bundle, observer + "operation-report.json"))
    outcomes = strict_object(member_json(bundle, observer + "operation-outcomes.json"))
    raw = strict_object(member_json(bundle, observer + "oracle-raw.json"))
    session = strict_object(member_json(bundle, base + "/client/session.json"))
    if report["case_id"] != case or len(report["calls"]) != report["product_call_count"]:
        raise ValueError("case/call mismatch")

    posts = []
    for receipt in receipts:
        if receipt["method"] != "POST" or receipt["path"].split("?")[0] != "/prompt":
            raise ValueError("unexpected proxy receipt")
        job = receipt.get("accepted_job_id")
        posts.append({"sequence": receipt["sequence"], "request_sequence": receipt["request_sequence"],
                      "job": token(key, job) if job else None,
                      "status": receipt.get("upstream_status")})
    sends = []
    for stage in stages:
        if stage["stage"] == "upstream_send_started" and stage["method"] == "POST" and stage["path"].split("?")[0] == "/prompt":
            sends.append(stage["request_sequence"])

    events = []
    for record in raw["websocket_messages"]:
        body = base64.b64decode(record["body_base64"], validate=True)
        if digest(body) != record["body_sha256"]:
            raise ValueError("WebSocket byte hash mismatch")
        value = strict_object(json.loads(body))
        kind = value.get("type")
        if kind not in ALLOWED_EVENTS:
            raise ValueError("unknown event type")
        data = strict_object(value.get("data"))
        prompt = data.get("prompt_id")
        node = data.get("node")
        events.append({"sequence": record["sequence"], "type": kind,
                       "job": token(key, prompt) if isinstance(prompt, str) else None,
                       "node": token(key, node) if node is not None else None})
    histories = []
    for record in raw["history_responses"]:
        body = base64.b64decode(record["body_base64"], validate=True)
        if digest(body) != record["body_sha256"]:
            raise ValueError("history byte hash mismatch")
        value = strict_object(json.loads(body))
        job = record["prompt_id"]
        entry = value.get(job)
        status = entry.get("status") if isinstance(entry, dict) else None
        histories.append({"job": token(key, job), "http_status": record["http_status"],
                          "completed": isinstance(status, dict) and status.get("status_str") == "success"})

    calls = []
    for call in report["calls"]:
        error = call.get("client_error_code")
        if error not in ALLOWED_ERRORS:
            raise ValueError("unexpected client error")
        number = call["call_index"]
        after = strict_object(member_json(bundle, f"{base}/client/call-{number}-after.json"))
        if after["state"] not in ALLOWED_STATES:
            raise ValueError("unexpected run state")
        calls.append({"index": number, "run": token(key, after["run_id"]),
                      "state": after["state"], "error": error})
    if calls[-1]["state"] != outcomes["original_run_state"]:
        raise ValueError("final manifest and outcome disagree")
    return {"case": case, "posts": posts, "upstream_send_sequences": sends,
            "events": events, "histories": histories, "calls": calls,
            "semantics": semantic_tree(key, strict_object(session["generate_arguments"]))}


def build(archive: Path, output: Path, private_key_output: Path, projection: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    if private_key_output.exists() or private_key_output.parent == output or output in private_key_output.parents:
        raise ValueError("private key must be new and outside candidate")
    if digest(archive.read_bytes()) != SOURCE_SHA256:
        raise ValueError("unexpected source archive")
    expected = strict_object(json.loads(projection.read_bytes()))
    if expected.get("schema") != "paired-windows-projection-v1":
        raise ValueError("unexpected projection schema")
    output.mkdir(mode=0o700, parents=True)
    key = secrets.token_bytes(32)
    with tarfile.open(archive, "r:gz") as bundle:
        cases = [transformed_case(bundle, case, index, key)
                 for index, case in enumerate(CASES, 1)]
    payload = {"schema": SCHEMA, "scope": "transformed_event_and_manifest_subset_not_raw_replay",
               "cases": cases}
    content = canonical(payload) + b"\n"
    (output / "capture.json").write_bytes(content)
    (output / "capture.json").chmod(0o600)
    verifier = Path(__file__).read_bytes()
    (output / "verify.py").write_bytes(verifier)
    (output / "verify.py").chmod(0o600)
    projection_bytes = canonical(expected) + b"\n"
    (output / "projection.json").write_bytes(projection_bytes)
    (output / "projection.json").chmod(0o600)
    manifest = {"schema": SCHEMA, "source_archive_sha256": SOURCE_SHA256,
                "files": {"capture.json": digest(content), "verify.py": digest(verifier),
                          "projection.json": digest(projection_bytes)},
                "omitted_original_checks": ["source_snapshot_hashes", "raw_payload_hashes",
                                             "original_manifest_hashes", "client_png_byte_hashes",
                                             "process_and_cleanup_receipts"]}
    (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
    (output / "manifest.json").chmod(0o600)
    key_fd = os.open(private_key_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(key_fd, "w", encoding="ascii") as stream:
        stream.write(key.hex() + "\n")
    output.chmod(0o700)
    return manifest


def audit(root: Path, expected: Path | None = None) -> dict:
    manifest = strict_object(json.loads((root / "manifest.json").read_bytes()))
    raw = (root / "capture.json").read_bytes()
    if manifest["schema"] != SCHEMA or manifest["source_archive_sha256"] != SOURCE_SHA256:
        raise ValueError("candidate integrity mismatch")
    if set(manifest["files"]) != {"capture.json", "verify.py", "projection.json"}:
        raise ValueError("unexpected candidate file list")
    if any(digest((root / name).read_bytes()) != expected_hash
           for name, expected_hash in manifest["files"].items()):
        raise ValueError("candidate integrity mismatch")
    payload = strict_object(json.loads(raw))
    if payload["schema"] != SCHEMA or len(payload["cases"]) != len(CASES):
        raise ValueError("candidate schema or case count mismatch")
    rows = []
    totals = Counter(operations=0, product_calls=0, proxy_posts=0, upstream_attempts=0)
    by_fault = {}
    for case, record in zip(CASES, payload["cases"], strict=True):
        if record["case"] != case:
            raise ValueError("case order mismatch")
        posts = record["posts"]
        sends = set(record["upstream_send_sequences"])
        request_sequences = [post["request_sequence"] for post in posts]
        if (len(request_sequences) != len(set(request_sequences))
                or len(sends) != len(record["upstream_send_sequences"])
                or not sends <= set(request_sequences)):
            raise ValueError("invalid proxy send sequence")
        jobs = {post["job"] for post in posts if post["job"] is not None
                and isinstance(post["status"], int) and 200 <= post["status"] < 300}
        if any(post["job"] is not None and post["job"] not in jobs for post in posts):
            raise ValueError("job without acceptance")
        events = record["events"]
        sequences = [event["sequence"] for event in events]
        if sequences != list(range(1, len(events) + 1)):
            raise ValueError("event sequence gap")
        event_counts = Counter(event["type"] for event in events)
        history = {item["job"]: item["completed"] and item["http_status"] == 200
                   for item in record["histories"]}
        if len(history) != len(record["histories"]):
            raise ValueError("duplicate history job")
        bound = 0
        for job in jobs:
            starts = sum(event["job"] == job and event["type"] == "execution_start" for event in events)
            terminals = sum(event["job"] == job and event["type"] == "executing"
                            and event["node"] is None for event in events)
            if not starts or terminals < starts or not history.get(job):
                raise ValueError("accepted job lacks bindable lifecycle")
            bound += starts
        calls = record["calls"]
        if [call["index"] for call in calls] != list(range(1, len(calls) + 1)):
            raise ValueError("call sequence gap")
        if any(call["state"] not in ALLOWED_STATES or call["error"] not in ALLOWED_ERRORS
               for call in calls):
            raise ValueError("unexpected call state or error")
        if len({call["run"] for call in calls}) != 1:
            raise ValueError("operation changed run")
        completion = calls[-1]["state"] == "generated"
        guard = calls[-1]["error"] == "submission_outcome_unknown"
        fault = case.split("_")[1]
        prior = by_fault.setdefault(fault, record["semantics"])
        if prior != record["semantics"]:
            raise ValueError("paired semantics differ")
        metrics = {"S_proxy": len(posts), "S_upstream": len(sends),
                   "A": len(jobs), "E_bound": bound}
        rows.append({"case": case, "metrics": metrics, "client_completion": completion,
                     "guard": guard, "events": dict(event_counts)})
        totals.update(operations=1, product_calls=len(calls), proxy_posts=len(posts), upstream_attempts=len(sends))
    report = {"status": "PASS", "schema": SCHEMA, "rows": rows, "totals": dict(totals),
              "scope": "transformed_subset_consistency_not_original_raw_or_execution_authentication",
              "omitted_original_checks": manifest["omitted_original_checks"]}
    if expected is None:
        expected = root / "projection.json"
    if expected is not None:
        projection = strict_object(json.loads(expected.read_bytes()))
        for actual, published in zip(rows, projection["rows"], strict=True):
            if any(actual[name] != published[name] for name in ("case", "metrics", "client_completion", "guard", "events")):
                raise ValueError("published projection differs")
        if report["totals"] != projection["totals"]:
            raise ValueError("published totals differ")
        report["published_projection_match"] = True
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("archive", type=Path)
    builder.add_argument("output", type=Path)
    builder.add_argument("--private-key-output", type=Path, required=True)
    builder.add_argument("--projection", type=Path, required=True)
    auditor = commands.add_parser("audit")
    auditor.add_argument("candidate", type=Path)
    auditor.add_argument("--expected", type=Path)
    args = parser.parse_args()
    result = (build(args.archive, args.output, args.private_key_output, args.projection)
              if args.command == "build" else audit(args.candidate, args.expected))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
