"""Private, exclusive research capture; never a public evidence sanitizer."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path


def write_private_json(root: Path, name: str, value: object) -> str:
    if Path(name).name != name:
        raise ValueError("capture name must be a local filename")
    payload = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    descriptor = os.open(root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
    return sha256(payload).hexdigest()


def manifest_summary(manifest: dict[str, object]) -> dict[str, object]:
    attempts = manifest.get("attempts")
    last = attempts[-1] if isinstance(attempts, list) and attempts else {}
    last = last if isinstance(last, dict) else {}
    job = last.get("backend_job")
    job_present = job is not None  # A non-null job object is outside the no-job gate.
    return {
        "durable_run_state": manifest.get("state"),
        "durable_attempt_status": last.get("status"),
        "durable_submission_outcome": last.get("submission_outcome"),
        "durable_job_present": job_present,
        "manifest_revision": manifest.get("manifest_revision"),
    }


def unknown_submission(manifest: dict[str, object], operation_key: str) -> bool:
    summary = manifest_summary(manifest)
    attempts = manifest.get("attempts")
    last = attempts[-1] if isinstance(attempts, list) and attempts else {}
    return (
        summary["durable_run_state"] == "unresolved"
        and summary["durable_attempt_status"] == "unresolved"
        and summary["durable_submission_outcome"] == "unknown"
        and summary["durable_job_present"] is False
        and isinstance(last, dict)
        and last.get("idempotency_key") == operation_key
    )
