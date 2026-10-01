"""Twelve offline contract probes against a same-information field baseline.

Constructed answers are declared with the worker/manifest scenario, before
either view runs. Counts describe synthetic probes, not real-backend accuracy.
"""
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.export_records import export_record
from scripts.research.f02_capture import write_private_json
from tests.test_asset_run_engine import write_test_png


def field_baseline(record):
    """Small independent parser for the preregistered probe schema only."""
    reported = record["reported_state"]
    oracle = record.get("oracle_state", {})
    if (record.get("job_id") and oracle.get("job_id") and record["job_id"] != oracle["job_id"]
            or record.get("artifact_hash") and oracle.get("artifact_hash")
            and record["artifact_hash"] != oracle["artifact_hash"]):
        return "conflict"
    validation = record.get("artifact_validation", {})
    complete = (oracle.get("execution_state") == "succeeded" and oracle.get("oracle_evaluable") is True
                and oracle.get("execution_started") == oracle.get("execution_finished") == 1
                and record.get("job_id") == oracle.get("job_id") and record.get("job_id") is not None
                and record.get("artifact_hash") == oracle.get("artifact_hash") and record.get("artifact_hash") is not None
                and validation.get("status") == "verified" and validation.get("independent") is True)
    if not complete:
        return "unknown"
    if reported.get("state") == "unresolved":
        return "completed_recovery_required"
    if reported.get("state") == "generated" and record.get("approval_state") == "valid":
        return "verified_complete"
    return "unknown"


def contract_view(output):
    value = output["interpreted_state"]
    if value["evidence_state"] == "mismatch":
        return "conflict"
    if value["execution_state"] == "unknown" or value["evidence_state"] != "verified":
        return "unknown"
    if value["execution_state"] == "succeeded" and value["recovery_state"] == "required":
        return "completed_recovery_required"
    return "verified_complete" if value["execution_verified"] else "unknown"


def run(output: Path):
    output.mkdir(mode=0o700, parents=True)
    (output / "sources").mkdir()
    source_hashes = {}
    for name in ("paired_evidence_probes.py", "export_records.py", "f02_capture.py"):
        content = Path(__file__).with_name(name).read_bytes()
        (output / "sources" / name).write_bytes(content)
        source_hashes[name] = sha256(content).hexdigest()
    # Freeze the fixture and the imported product helpers too, before probes.
    dependencies = {}
    for name, module in tuple(sys.modules.items()):
        location = getattr(module, "__file__", None)
        if location and (name.startswith("local_gpu_imagegen") or name == "tests.test_asset_run_engine"):
            path = Path(location).resolve()
            relative = path.relative_to(ROOT)
            target = output / "sources" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = path.read_bytes()
            target.write_bytes(payload)
            dependencies[str(relative)] = sha256(payload).hexdigest()
    write_private_json(output, "source-freeze.json", source_hashes)
    write_private_json(output, "dependency-freeze.json", dependencies)
    probes = []
    for index in range(3):
        # The synthetic worker produces bytes; the separate validator reopens
        # the file and hashes them. No exporter supplies either fact.
        artifact = output / f"artifact-{index}.png"
        write_test_png(artifact, pixel=bytes((index + 1, 40, 80)))
        digest = sha256(artifact.read_bytes()).hexdigest()
        base = {"record_id": f"probe-{index}", "job_id": f"worker-{index}", "artifact_hash": digest,
                "reported_state": {"state": "generated"}, "approval_state": "valid",
                "artifact_validation": {"status": "verified", "independent": True},
                "oracle_state": {"execution_state": "succeeded", "oracle_evaluable": True,
                                 "execution_started": 1, "execution_finished": 1,
                                 "job_id": f"worker-{index}", "artifact_hash": digest}}
        for category in ("completed_recovery_required", "verified_complete", "conflict", "unknown"):
            value = copy.deepcopy(base)
            if category == "completed_recovery_required":
                value["reported_state"]["state"] = "unresolved"
            elif category == "conflict":
                if index == 0:
                    value["job_id"] = "wrong-job"
                elif index == 1:
                    value["artifact_hash"] = "0" * 64
                else:
                    value["oracle_state"]["job_id"] = "wrong-oracle-job"
            elif category == "unknown":
                if index == 0:
                    value.pop("oracle_state")
                elif index == 1:
                    value["oracle_state"]["execution_finished"] = 0
                else:
                    value.pop("artifact_validation")
            before = json.dumps(value, sort_keys=True).encode()
            expected = category  # Declared independently before either view.
            name = f"{index}-{category}"
            input_bytes_sha = write_private_json(output, name + "-input.json", value)
            exported = export_record(value)
            observed = contract_view(exported)
            simple = field_baseline(value)
            checks = []
            if observed != expected or simple != expected:
                checks.append("view_disagrees_with_constructed_answer")
            if before != json.dumps(value, sort_keys=True).encode():
                checks.append("input_mutated")
            if sha256((output / (name + "-input.json")).read_bytes()).hexdigest() != input_bytes_sha:
                checks.append("input_file_bytes_changed")
            if not exported.get("mapping_reason"):
                checks.append("mapping_reasons_missing")
            if category == "completed_recovery_required" and exported["interpreted_state"]["execution_verified"]:
                checks.append("recovery_veto_missing")
            if category == "verified_complete" and not exported["interpreted_state"]["execution_verified"]:
                checks.append("positive_calibration_failed")
            write_private_json(output, name + "-export.json", exported)
            probes.append({"probe_id": name, "expected": expected, "exporter": observed,
                           "field_baseline": simple, "input_sha256": input_bytes_sha,
                           "input_canonical_sha256": sha256(before).hexdigest(), "checks": checks})
    counts = {}
    for view in ("exporter", "field_baseline"):
        counts[view] = {"correct": sum(p[view] == p["expected"] for p in probes),
                        "unknown": sum(p[view] == "unknown" for p in probes),
                        "false_affirmations": sum(p[view] == "verified_complete" and p["expected"] != "verified_complete" for p in probes)}
    unchanged = all(sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() == d for n, d in source_hashes.items())
    unchanged = unchanged and all(sha256((ROOT / n).read_bytes()).hexdigest() == d for n, d in dependencies.items())
    report = {"evidence_class": "synthetic_offline_contract_probes", "python": platform.python_version(),
              "status": "PASS" if all(not p["checks"] for p in probes) and unchanged else "STOPPED",
              "probes": probes, "counts": counts, "same_information": True,
              "observed_information_or_accuracy_advantage": False,
              "source_hashes": source_hashes, "sources_unchanged": unchanged,
              "dependency_hashes": dependencies,
              "windows_executed": False, "gpu_executed": False}
    write_private_json(output, "evidence-probes-report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output)
    print(json.dumps({"status": report["status"], "probes": len(report["probes"]), "counts": report["counts"]}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
