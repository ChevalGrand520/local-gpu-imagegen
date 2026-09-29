"""Create a small local reviewer demo; it is not anonymity-certified or published."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "paper/examples/README.md",
    "paper/examples/complete.json",
    "paper/examples/unresolved.json",
    "paper/scripts/verify_reviewer_demo.py",
    "paper/scripts/audit_retained_evidence.py",
    "paper/evidence/windows-audit.json",
    "docs/research/runs/paired-v2-b2.json",
    "docs/research/runs/paired-v2-w3.json",
    "docs/research/runs/paired-v2-comparison.json",
    "scripts/research/__init__.py",
    "scripts/research/export_records.py",
    "tests/research/test_export_records.py",
    "scripts/local_gpu_imagegen/__init__.py",
    "scripts/local_gpu_imagegen/artifacts.py",
    "scripts/local_gpu_imagegen/errors.py",
    "scripts/local_gpu_imagegen/run_store.py",
    "scripts/local_gpu_imagegen/two_stage_layout.py",
    "scripts/local_gpu_imagegen/visual_review.py",
)


def main() -> None:
    dest = ROOT / "paper/delivery/evidence-tool-reviewer-demo-v0.1.zip"
    dest.parent.mkdir(exist_ok=True)
    manifest = {
        "purpose": "local reviewer demonstration; not anonymity-certified or a complete backend distribution",
        "files": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES},
    }
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in FILES:
            bundle.write(ROOT / name, name)
        bundle.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    print(f"{dest}: {len(FILES)} files")


if __name__ == "__main__":
    main()
