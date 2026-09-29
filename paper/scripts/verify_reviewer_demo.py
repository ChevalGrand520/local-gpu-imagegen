"""Run a synthetic exporter demonstration and retained-record audit offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def run() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="evidence-tool-demo-") as folder:
        examples = {}
        for name, expected in (("complete", True), ("unresolved", False)):
            source = ROOT / "paper/examples" / f"{name}.json"
            output = Path(folder) / f"{name}-export.json"
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/research/export_records.py"), "--input", str(source), "--output", str(output)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(f"{name}: exporter failed: {completed.stderr.strip()}")
            record = json.loads(output.read_text(encoding="utf-8"))
            state = record["interpreted_state"]
            if state["execution_verified"] is not expected:
                raise ValueError(f"{name}: unexpected verification state")
            if state["execution_state"] != "succeeded":
                raise ValueError(f"{name}: supplied backend evidence was not retained")
            if record["reported_state"]["state"] != ("generated" if expected else "unresolved"):
                raise ValueError(f"{name}: original run status changed")
            if record["source_sha"] is not None or record["backend_instance"] is not None:
                raise ValueError(f"{name}: missing provenance was invented")
            examples[name] = {
                "reported": record["reported_state"]["state"],
                "backend_execution": state["execution_state"],
                "recovery": state["recovery_state"],
                "execution_verified": state["execution_verified"],
                "mapping_version": record["mapping_version"],
                "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        from paper.scripts.audit_retained_evidence import audit
        from scripts.research.export_records import export_record

        retained = audit(ROOT)
        normalized_cpu = []
        for system in ("b2", "w3"):
            source = ROOT / "docs/research/runs" / f"paired-v2-{system}.json"
            for case in json.loads(source.read_text(encoding="utf-8"))["cases"]:
                exported = export_record({
                    "record_id": case["case_id"],
                    "reported_state": case["raw_reported_state"],
                    "oracle_state": case["oracle_state"],
                })
                state = exported["interpreted_state"]
                if exported["reported_state"] != case["raw_reported_state"]:
                    raise ValueError(f"{system}/{case['case_id']}: product manifest changed")
                if exported["oracle_state"] != case["oracle_state"]:
                    raise ValueError(f"{system}/{case['case_id']}: oracle observation changed")
                if state["execution_verified"]:
                    raise ValueError(f"{system}/{case['case_id']}: missing validator was promoted to verified")
                normalized_cpu.append({
                    "system": system,
                    "case_id": case["case_id"],
                    "reported": case["raw_reported_state"].get("state"),
                    "evidence": state["evidence_state"],
                    "recovery": state["recovery_state"],
                    "execution_verified": state["execution_verified"],
                })
        return {
            "scope": "synthetic exporter inputs plus offline normalization and consistency of retained CPU records; no backend execution",
            "examples": examples,
            "retained_windows_cases": len(retained["windows_cases"]),
            "retained_binding_ids": retained["unique_windows_binding_ids"],
            "cpu_synthetic_traces": 2 * len(retained["cpu_cases"]),
            "retained_cpu_normalization": normalized_cpu,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new JSON result (never overwrite)")
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
