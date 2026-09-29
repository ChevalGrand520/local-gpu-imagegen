"""Build a deterministic, direct-identifier-sanitized offline demo candidate."""

from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

from package_reviewer_demo import FILES, ROOT


DEST = ROOT / "paper/delivery/evidence-tool-anonymous-demo-v0.3.zip"
PRIVATE_MAP = ROOT / "paper/delivery/evidence-tool-anonymous-mapping-v0.3.json"
EPOCH = (2020, 1, 1, 0, 0, 0)
SOURCE_README = "paper/examples/README.md"
ANONYMOUS_README = "paper/examples/anonymous-demo-README.md"
SOURCE_PACKAGE = "scripts/local_gpu_imagegen/"
ANONYMOUS_PACKAGE = "scripts/prototype_core/"
DIRECT_IDENTIFIERS = (b"chevalgrand", b"local-gpu-imagegen", b"local_gpu_imagegen", b"/Users/")


def delivered_name(source_name: str) -> str:
    if source_name == SOURCE_README:
        return "README.md"
    if source_name.startswith(SOURCE_PACKAGE):
        return ANONYMOUS_PACKAGE + source_name[len(SOURCE_PACKAGE):]
    return source_name


def delivered_bytes(source_name: str) -> bytes:
    if source_name == SOURCE_README:
        return (ROOT / ANONYMOUS_README).read_bytes()
    payload = (ROOT / source_name).read_bytes()
    if source_name == "scripts/research/export_records.py":
        old = b"from local_gpu_imagegen.run_store import request_hash"
        if payload.count(old) != 1:
            raise ValueError("exporter import anchor changed; review transformation")
        payload = payload.replace(old, b"from prototype_core.run_store import request_hash")
    return payload


def archive_member(name: str, payload: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, date_time=EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info, payload


def main() -> None:
    records: dict[str, bytes] = {}
    private_rows: list[dict[str, str]] = []
    for source_name in FILES:
        target_name = delivered_name(source_name)
        payload = delivered_bytes(source_name)
        if target_name in records:
            raise ValueError(f"duplicate delivered path: {target_name}")
        records[target_name] = payload
        source_bytes = (ROOT / (ANONYMOUS_README if source_name == SOURCE_README else source_name)).read_bytes()
        private_rows.append({
            "source_path": ANONYMOUS_README if source_name == SOURCE_README else source_name,
            "delivered_path": target_name,
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "delivered_sha256": hashlib.sha256(payload).hexdigest(),
        })

    manifest = {
        "scope": "offline exporter demonstration and retained-record consistency only",
        "files": {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(records.items())},
    }
    records["PACKAGE_MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    for name, payload in records.items():
        lower = (name.encode() + b"\n" + payload).lower()
        for marker in DIRECT_IDENTIFIERS:
            if marker.lower() in lower:
                raise ValueError(f"direct identifier marker {marker!r} in {name}")

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DEST, "w") as bundle:
        for name, payload in sorted(records.items()):
            info, data = archive_member(name, payload)
            bundle.writestr(info, data)
    PRIVATE_MAP.write_text(json.dumps({
        "scope": "author-side mapping; never include in reviewer archive",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "archive_sha256": hashlib.sha256(DEST.read_bytes()).hexdigest(),
        "files": private_rows,
    }, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"{DEST}: {len(records)} deterministic entries; sha256={hashlib.sha256(DEST.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
