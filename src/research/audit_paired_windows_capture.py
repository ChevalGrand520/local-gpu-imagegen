"""Read-only audit of retained paired capture bytes; no backend calls."""
import argparse
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.research.f02_oracle import ComfyUIEventOracle
from scripts.research.paired_ambiguity import prompt_metrics, semantic_digest, WINDOWS_ORDER


def load(path):
    return json.loads(path.read_bytes())


def audit(root):
    checks, rows, pairs = [], [], {}

    def require(condition, name):
        checks.append({"check": name, "passed": bool(condition)})

    runner = load(root / "runner-report.json")
    freeze = load(root / "source-freeze.json")
    for name, digest in freeze["sha256"].items():
        require(sha256((root / "source-snapshot" / name).read_bytes()).hexdigest() == digest, "source:"+name)
    totals = Counter(operations=0, product_calls=0, proxy_posts=0, upstream_attempts=0)
    for index, (variant, fault) in enumerate(WINDOWS_ORDER):
        case = f"{variant}_{fault}"
        op = root / f"{index+1:02d}-{variant}-{fault}"
        observer = op / "observer"
        report = load(observer / "operation-report.json")
        receipts = load(observer / "proxy-receipts.json")
        stages = [json.loads(line) for line in (observer / "proxy-stages.jsonl").read_text().splitlines() if line]
        metrics = prompt_metrics(receipts, stages)
        require(all(report["metrics"][key] == val for key, val in metrics.items()), case+":proxy_counts")
        raw = load(observer / "oracle-raw.json")
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity=raw["backend_boot_identity"], observer_id=raw["observer_id"])
        histories = {}
        for record in raw["history_responses"]:
            body = base64.b64decode(record["body_base64"], validate=True)
            require(sha256(body).hexdigest() == record["body_sha256"], case+":history_hash")
            if record["http_status"] == 200:
                histories[record["prompt_id"]] = json.loads(body)
        event_counts = Counter()
        for record in raw["websocket_messages"]:
            body = base64.b64decode(record["body_base64"], validate=True)
            require(sha256(body).hexdigest() == record["body_sha256"], case+":websocket_hash")
            oracle._record_payload(body)
            event_counts[json.loads(body).get("type")] += 1
        oracle._history = lambda job: histories.get(job, {})
        jobs = {r["accepted_job_id"] for r in receipts if r.get("accepted_job_id")}
        decision = oracle._decision(jobs) if jobs else None
        bound = len(decision.bindings) if decision and decision.oracle_evaluable else (0 if not jobs and metrics["S_upstream"] == 0 else None)
        require(bound == report["metrics"]["E_bound"], case+":replayed_bindings")
        session = load(op / "client/session.json")
        digest = semantic_digest(session["generate_arguments"])
        require(fault not in pairs or pairs[fault] == digest, case+":paired_semantics")
        pairs[fault] = digest
        for call in report["calls"]:
            num = call["call_index"]
            for phase in ("before", "after"):
                body = (op / f"client/call-{num}-{phase}.json").read_bytes()
                require(sha256(body).hexdigest() == call[f"manifest_{phase}_sha256"], case+":manifest_"+phase)
        outcome = load(observer / "operation-outcomes.json")
        require(outcome["semantic_digest"] == digest, case+":outcome_semantics")
        cleanup = load(op / "cleanup.json")
        require(cleanup["stopped"] is True, case+":cleanup_receipt")
        hashes = {sha256(p.read_bytes()).hexdigest() for p in (op / "outputs").rglob("*.png")}
        reported_hashes = {h for c in report["calls"] for h in c.get("artifact_hashes", [])}
        require(reported_hashes <= hashes, case+":retained_client_artifact_bytes")
        totals.update(operations=1, product_calls=report["product_call_count"], proxy_posts=metrics["S_proxy"], upstream_attempts=metrics["S_upstream"])
        rows.append({"case": case, "metrics": dict(metrics, E_bound=bound),
                     "client_completion": outcome["client_completion"],
                     "guard": outcome["submission_guard_observed"], "events": dict(event_counts),
                     "retained_png_files": len(list((op / "outputs").rglob("*.png")))})
    require(dict(totals) == runner["totals"], "campaign_totals")
    require(runner["status"] == "COMPLETED", "campaign_completed")
    return {"status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
            "check_count": len(checks), "failed_checks": [c["check"] for c in checks if not c["passed"]],
            "rows": rows, "totals": dict(totals),
            "scope": "retained_byte_consistency_and_event_replay_not_execution_authentication"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--write-public-projection", type=Path)
    args = parser.parse_args()
    result = audit(args.campaign)
    if args.write_public_projection:
        if result["status"] != "PASS":
            raise ValueError("failed audit cannot produce projection")
        runner = load(args.campaign / "runner-report.json")
        public = {"schema": "paired-windows-projection-v1", "execution_source": "08539d5",
                  "scope": "derived fixed-case record; raw private evidence excluded; not execution authentication",
                  "rows": result["rows"], "totals": result["totals"],
                  "control_rpc_seconds": runner["control_rpc_seconds"],
                  "elapsed_seconds": runner["elapsed_seconds"],
                  "private_archive_sha256": "141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3",
                  "cache_second_B2_F02_nodes": ["3", "4", "5", "6", "7", "8", "9"],
                  "audit_checks": result["check_count"]}
        args.write_public_projection.write_text(json.dumps(public, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
