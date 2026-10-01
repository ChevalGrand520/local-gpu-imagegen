"""Archive exact product/harness bytes, then run bounded synthetic CPU checks."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.f02_capture import write_private_json
from scripts.research.paired_ambiguity import PRODUCTS, PROTOCOL


def check_result(result):
    strategy, fault, probe = result["strategy"], result["fault"], result["scope_probe"]
    error = result["calls"][-1].get("client_error_code")
    guarded = strategy == "W3" and fault != "F00" and probe != "unknown-new-run"
    stopped = strategy == "P-stop" and fault != "F00"
    sends = 1 if fault == "F00" or probe == "healthy-replay" else (0 if fault == "FPRE" else 1)
    if not guarded and not stopped and fault != "F00":
        sends += 1
    expected = {"S_proxy": sends + (1 if fault == "FPRE" else 0),
                "S_upstream": sends, "A": sends, "E_bound_cpu": sends}
    failures = []
    if result["metrics"] != expected:
        failures.append("constructed_worker_counts_differ")
    if guarded and error != "submission_outcome_unknown":
        failures.append("native_guard_not_reached")
    if guarded and probe is None and result["calls"][0]["manifest_after_sha256"] != result["calls"][1]["manifest_after_sha256"]:
        failures.append("guard_mutated_original_manifest")
    if not result.get("retained_artifact_bytes_revalidated"):
        failures.append("artifact_bytes_not_revalidated")
    if not guarded and not stopped and error is not None:
        failures.append("unexpected_product_rejection")
    # A new-run scope probe succeeds elsewhere; it cannot repair the old run.
    expected_completion = not (guarded or stopped or probe == "unknown-new-run")
    if result["client_completion"] != expected_completion:
        failures.append("original_run_completion_differs")
    if fault == "FPRE" and not result["fpre_first_not_sent"]:
        failures.append("fpre_no_send_not_proven")
    if not all(call.get("generation_rpc_entered") for call in result["calls"]):
        failures.append("caller_rejected_before_generation")
    if probe is None and fault != "F00" and result["calls"][0].get("client_error_code") != "backend_request_failed":
        failures.append("first_transport_loss_not_observed")
    return failures


def run(output: Path):
    output.mkdir(mode=0o700, parents=True)  # Never overwrite failed attempts.
    deadline = time.monotonic() + 30 * 60
    sources = output / "sources"
    sources.mkdir()
    harness = sources / "harness"
    harness.mkdir()
    names = ("run_paired_ambiguity_cpu.py", "paired_cpu_worker.py", "paired_ambiguity.py",
             "f02_product_client.py", "f02_loopback.py", "f02_capture.py",
             "run_paired_fault_matrix.py", "execution_oracle.py")
    source_hashes = {}
    for name in names:
        content = Path(__file__).with_name(name).read_bytes()
        (harness / name).write_bytes(content)
        source_hashes[name] = sha256(content).hexdigest()
    trees = {}
    product_hashes = {}
    for variant, revision in PRODUCTS.items():
        tree = sources / variant
        tree.mkdir()
        archive = subprocess.check_output(["git", "archive", revision], cwd=ROOT, timeout=30)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(tree, filter="data")
        trees[variant] = tree
        product_hashes[variant] = {str(p.relative_to(tree)): sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(tree.rglob("*")) if p.is_file()}
    write_private_json(output, "source-freeze.json", {
        "products": PRODUCTS, "harness_sha256": source_hashes, "product_file_sha256": product_hashes,
        "frozen_at": datetime.now(timezone.utc).isoformat(), "before_first_operation": True,
    })
    operations = [(s, f, None) for s in ("B2", "W3", "P-stop") for f in ("F00", "F02", "FPRE")]
    operations += [("W3", "F00", "healthy-replay"), ("W3", "F02", "unknown-new-key"),
                   ("W3", "F02", "unknown-new-run")]
    records = []
    for index, (strategy, fault, probe) in enumerate(operations, 1):
        capture = output / f"op-{index:02d}-{strategy}-{fault}-{probe or 'same-run'}"
        capture.mkdir()
        command = [sys.executable, str(Path(__file__).with_name("paired_cpu_worker.py")),
                   "--product-root", str(trees["B2" if strategy == "P-stop" else strategy]),
                   "--strategy", strategy, "--fault", fault, "--capture", str(capture)]
        if probe:
            command += ["--probe", probe]
        start = time.monotonic()
        try:
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                       timeout=min(60, max(0.001, deadline - start)))
            (capture / "stdout.txt").write_text(completed.stdout)
            (capture / "stderr.txt").write_text(completed.stderr)
            receipt = {"command": command, "exit_code": completed.returncode,
                       "elapsed_seconds": time.monotonic() - start, "timed_out": False}
            write_private_json(capture, "process-receipt.json", receipt)
            if completed.returncode != 0:
                records.append({"strategy": strategy, "fault": fault, "probe": probe,
                                "exit_code": completed.returncode, "checks": ["worker_process_failed"]})
                break
            result = json.loads(completed.stdout)
            result["checks"] = check_result(result)
            records.append(result)
            if result["checks"]:
                break
        except subprocess.TimeoutExpired as error:
            write_private_json(capture, "process-receipt.json", {"command": command,
                "timed_out": True, "elapsed_seconds": time.monotonic() - start})
            (capture / "stderr.txt").write_bytes(error.stderr or b"")
            records.append({"strategy": strategy, "fault": fault, "checks": ["worker_timeout"]})
            break
    unchanged = all(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == digest
                    for name, digest in source_hashes.items())
    pair_checks = []
    for fault in ("F00", "F02", "FPRE"):
        pair = [r for r in records if r.get("fault") == fault and r.get("strategy") in {"B2", "W3"}
                and r.get("scope_probe") is None and r.get("semantic_digests")]
        if len(pair) != 2 or pair[0]["semantic_digests"][0] != pair[1]["semantic_digests"][0]:
            pair_checks.append(f"paired_generation_semantics_differ:{fault}")
    report = {"protocol": PROTOCOL, "evidence_class": "synthetic_cpu_public_engine_dispatch",
              "status": "PASS" if len(records) == 12 and all(not r["checks"] for r in records) and unchanged and not pair_checks else "STOPPED",
              "planned_operations": 12, "recorded_operations": len(records), "records": records,
              "python": platform.python_version(), "platform": platform.system(),
              "source_freeze_sha256": sha256((output / "source-freeze.json").read_bytes()).hexdigest(),
              "harness_unchanged_after_execution": unchanged, "windows_executed": False, "gpu_executed": False}
    report["pair_checks"] = pair_checks
    write_private_json(output, "cpu-report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run(args.output)
    print(json.dumps({k: report[k] for k in ("status", "planned_operations", "recorded_operations", "python")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
