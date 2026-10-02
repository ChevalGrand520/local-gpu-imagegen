"""Read-only screening inventory for the private paired Windows capture.

This reports marker categories, never matching values. It does not certify that
an archive is safe to publish.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import tarfile


MARKERS = {
    "mac_home": re.compile(rb"/Users/[^/\s\"']+", re.I),
    "windows_home": re.compile(rb"[A-Z]:\\(?:Users|CodexWorkspace)\\", re.I),
    "host_or_device": re.compile(rb"(?:LAPTOP-[A-Z0-9-]+|GPU-[A-F0-9-]{8,})", re.I),
    "account_name": re.compile(rb"Capricorn|chevalgrand", re.I),
    "private_field": re.compile(rb'"(?:positive_prompt|negative_prompt|output_root|product_root|route_token|model_identity_token|authorization_scope)"', re.I),
    "credential_field": re.compile(rb'"(?:api[_-]?key|password|secret|access[_-]?token)"', re.I),
}


def category(name: str) -> str:
    if "/source-snapshot/backend/" in name:
        return "backend_source_snapshot"
    if "/source-snapshot/" in name or "/observer/sources/" in name:
        return "other_source_snapshot"
    if "/outputs/" in name:
        return "product_output"
    if name.endswith("/observer/oracle-raw.json"):
        return "raw_transport"
    if "/client/" in name:
        return "client_record"
    if "/observer/" in name:
        return "observer_record"
    if name.endswith(".log") or name.endswith(".jsonl"):
        return "operational_log"
    return "campaign_metadata"


def marker_counts(data: bytes) -> Counter[str]:
    return Counter({key: len(pattern.findall(data)) for key, pattern in MARKERS.items()
                    if pattern.search(data)})


def inspect(archive: Path) -> dict[str, object]:
    rows = []
    aggregate: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            parts = PurePosixPath(member.name).parts
            if member.name.startswith("/") or ".." in parts or member.issym() or member.islnk():
                raise ValueError("unsafe archive member")
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError("unsupported archive member type")
            stream = bundle.extractfile(member)
            if stream is None:
                raise ValueError("unreadable archive member")
            data = stream.read()
            markers = marker_counts(data)
            decoded_count = 0
            if member.name.endswith("/observer/oracle-raw.json"):
                record = json.loads(data)
                for item in record["websocket_messages"] + record["history_responses"]:
                    payload = base64.b64decode(item["body_base64"], validate=True)
                    if sha256(payload).hexdigest() != item["body_sha256"]:
                        raise ValueError("embedded payload hash mismatch")
                    markers.update(marker_counts(payload))
                    decoded_count += 1
            kind = category(member.name)
            categories[kind] += 1
            aggregate.update(markers)
            rows.append({"member": member.name, "category": kind, "size": member.size,
                         "marker_counts": dict(sorted(markers.items())),
                         "decoded_payloads_checked": decoded_count})
    return {"scope": "private_file_inventory_not_release_clearance",
            "archive_sha256": sha256(archive.read_bytes()).hexdigest(),
            "files": len(rows), "categories": dict(sorted(categories.items())),
            "marker_counts": dict(sorted(aggregate.items())), "members": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.archive)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.output.chmod(0o600)
    print(json.dumps({key: report[key] for key in
                      ("scope", "archive_sha256", "files", "categories", "marker_counts")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
