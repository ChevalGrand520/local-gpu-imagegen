"""Read-only preflight for the reviewed Windows/ComfyUI F02 pilot.

The command intentionally creates neither an output root nor a GPU job.  It
returns PASS only when the supplied, explicit reservation is presently active
and all frozen identities are independently observed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
from urllib.parse import urlsplit
from urllib.request import urlopen


TRUSTED_LEDGER_ANCHOR = "d8ef0bccc84269b7d4a627adce5f6025a17ab024"
EXPECTED_HOST_ID = "LAPTOP-7QD7KR9F"
EXPECTED_GPU_UUID = "GPU-25c43be6-ab43-2700-35f9-1db584b84dd8"
EXPECTED_GPU_MODEL = "NVIDIA GeForce RTX 5070 Ti Laptop GPU"
EXPECTED_BACKEND_URL = "http://127.0.0.1:8202"
EXPECTED_COMFY_VERSION = "v0.30.0"
EXPECTED_COMFY_SHA = "b1693ecba9f5b65f8c80ab36b195ab963ec92413"
EXPECTED_MODEL_FILENAME = "sd_xl_base_1.0.safetensors"
EXPECTED_MODEL_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    command: list[str]
    exit_code: int | None
    summary: str
    details: dict[str, object]


@dataclass(frozen=True)
class PreflightReport:
    status: str
    checked_at: str
    backend_boot_identity: str | None
    checks: tuple[Check, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "checked_at": self.checked_at,
            "backend_boot_identity": self.backend_boot_identity,
            "checks": [asdict(check) for check in self.checks],
        }


def run_preflight(config: dict[str, object], *, now: datetime | None = None) -> PreflightReport:
    """Run only identity and read-only backend checks from an explicit config."""
    now = now or datetime.now(timezone.utc)
    checks: list[Check] = []
    try:
        ledger = _object(config, "ledger")
        environment = _object(config, "environment")
        reservation = _object(config, "reservation")
        clients = _object(config, "clients")
        outputs = _object(config, "fresh_output_roots")
    except ValueError as exc:
        return PreflightReport("FAIL", now.isoformat(), None, (Check("config", False, [], None, str(exc), {}),))

    try:
        ledger_root = _string(ledger, "root")
        ledger_anchor = _string(ledger, "anchor")
        host_id = _string(environment, "host_id")
        gpu_uuid = _string(environment, "gpu_uuid")
        gpu_model = _string(environment, "gpu_model")
        model_path = _string(environment, "model_path")
        model_sha256 = _string(environment, "model_sha256")
        _string(environment, "backend_url")
        _string(environment, "comfy_version")
        _string(environment, "comfy_sha")
        _string(environment, "comfy_root")
        for label in ("B2", "W3"):
            client = clients.get(label)
            if not isinstance(client, dict):
                raise ValueError(f"missing client configuration: {label}")
            _string(client, "root")
            _string(client, "sha")
    except ValueError as exc:
        return PreflightReport("FAIL", now.isoformat(), None, (Check("config", False, [], None, str(exc), {}),))

    # Reservation is an explicit owner declaration, not an inference from a
    # process owner.  It is checked before any hardware/backend observation so
    # an expired window cannot trigger even read-only pilot setup by accident.
    reservation_check = _reservation_check(reservation, now)
    checks.append(reservation_check)
    if not reservation_check.passed:
        return PreflightReport("FAIL", now.isoformat(), None, tuple(checks))

    frozen_check = _frozen_identity_config_check(ledger_anchor, environment, reservation)
    checks.append(frozen_check)
    if not frozen_check.passed:
        return PreflightReport("FAIL", now.isoformat(), None, tuple(checks))

    checks.append(_contract_check(ledger_root, ledger_anchor))
    checks.extend(_client_checks(clients))
    checks.append(_hostname_check(host_id))
    checks.append(_gpu_check(gpu_uuid, gpu_model))
    checks.append(_model_hash_check(model_path, model_sha256))
    backend_check, boot_identity = _backend_check(environment)
    checks.append(backend_check)
    checks.append(_fresh_roots_check(outputs))
    return PreflightReport(
        "PASS" if all(check.passed for check in checks) else "FAIL",
        now.isoformat(),
        boot_identity,
        tuple(checks),
    )


def _contract_check(root: str, anchor: str) -> Check:
    show = _run(["git", "-C", root, "show", f"{anchor}:scripts/verify_research_contract.py"])
    if show.returncode != 0:
        return _check("research_contract", False, show.args, show.returncode, "trusted verifier is unavailable", {"stderr": _brief(show.stderr)})
    verify = _run([sys.executable, "-", "--root", root, "--anchor", anchor], input_text=show.stdout)
    passed = verify.returncode == 0 and '"status": "PASS"' in verify.stdout
    return _check("research_contract", passed, verify.args, verify.returncode, _brief(verify.stdout or verify.stderr), {})


def _client_checks(clients: dict[str, object]) -> list[Check]:
    checks: list[Check] = []
    for label, expected_sha in (("B2", "da65d57047b5a59e3403b49adf4605a1c0497c58"), ("W3", "d45173af75d404ad79dc14568edd4c45f654abd2")):
        value = clients.get(label)
        if not isinstance(value, dict):
            checks.append(_check(f"client_{label}", False, [], None, "missing client configuration", {}))
            continue
        root = _string(value, "root")
        configured_sha = _string(value, "sha")
        head = _run(["git", "-C", root, "rev-parse", "HEAD"])
        status = _run(["git", "-C", root, "status", "--porcelain", "--branch"])
        branch = _run(["git", "-C", root, "branch", "--show-current"])
        actual = head.stdout.strip()
        clean_detached = status.returncode == 0 and not status.stdout.strip() and branch.returncode == 0 and not branch.stdout.strip()
        passed = actual == expected_sha == configured_sha and clean_detached
        summary = f"head={actual or 'unavailable'}; detached_clean={clean_detached}"
        checks.append(_check(f"client_{label}", passed, head.args, head.returncode, summary, {"expected": expected_sha}))
    return checks


def _frozen_identity_config_check(
    ledger_anchor: str,
    environment: dict[str, object],
    reservation: dict[str, object],
) -> Check:
    try:
        host_id = _string(environment, "host_id")
        gpu_uuid = _string(environment, "gpu_uuid")
        gpu_model = _string(environment, "gpu_model")
        model_path = _string(environment, "model_path")
        model_sha256 = _string(environment, "model_sha256")
        backend_url = _string(environment, "backend_url").rstrip("/")
        comfy_version = _string(environment, "comfy_version")
        comfy_sha = _string(environment, "comfy_sha")
        _string(environment, "comfy_root")
        scope = _string(reservation, "scope")
        no_concurrent_gpu_work = reservation.get("no_concurrent_gpu_work")
    except ValueError as exc:
        return _check("frozen_identity_config", False, [], None, str(exc), {})

    expected = {
        "ledger_anchor": ledger_anchor == TRUSTED_LEDGER_ANCHOR,
        "host_id": host_id.casefold() == EXPECTED_HOST_ID.casefold(),
        "gpu_uuid": gpu_uuid == EXPECTED_GPU_UUID,
        "gpu_model": gpu_model == EXPECTED_GPU_MODEL,
        "backend_url": backend_url == EXPECTED_BACKEND_URL,
        "comfy_version": comfy_version == EXPECTED_COMFY_VERSION,
        "comfy_sha": comfy_sha == EXPECTED_COMFY_SHA,
        "model_filename": Path(model_path).name == EXPECTED_MODEL_FILENAME,
        "model_sha256": model_sha256 == EXPECTED_MODEL_SHA256,
        "reservation_scope": scope == "exactly four reviewed F00/F02 single-stage cases",
        "no_concurrent_gpu_work": no_concurrent_gpu_work is True,
    }
    passed = all(expected.values())
    mismatches = [name for name, matched in expected.items() if not matched]
    summary = "frozen identities match" if passed else "mismatches=" + ",".join(mismatches)
    return _check("frozen_identity_config", passed, [], 0, summary, {"expected": expected})


def _hostname_check(expected: str) -> Check:
    actual = socket.gethostname()
    return _check("hostname", actual.casefold() == expected.casefold(), ["hostname"], 0, actual, {"expected": expected})


def _reservation_check(value: dict[str, object], now: datetime) -> Check:
    try:
        owner = _string(value, "owner")
        start = _parse_time(_string(value, "start"))
        end = _parse_time(_string(value, "end"))
        timeout = value.get("hard_timeout_seconds")
        valid = bool(owner.strip()) and start <= now <= end and timeout == 900
        summary = f"owner_declared={bool(owner.strip())}; active={start <= now <= end}; hard_timeout_seconds={timeout}"
        return _check("reservation", valid, [], 0, summary, {"start": start.isoformat(), "end": end.isoformat()})
    except ValueError as exc:
        return _check("reservation", False, [], None, str(exc), {})


def _gpu_check(expected_uuid: str, expected_model: str) -> Check:
    command = ["nvidia-smi", "--query-gpu=name,uuid,memory.total,driver_version", "--format=csv,noheader"]
    result = _run(command)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    passed = result.returncode == 0 and any(expected_uuid in line and expected_model in line for line in lines)
    return _check("gpu", passed, result.args, result.returncode, _brief(" | ".join(lines) or result.stderr), {"expected_uuid": expected_uuid, "expected_model": expected_model})


def _model_hash_check(path_text: str, expected: str) -> Check:
    path = Path(path_text)
    if not path.is_file():
        return _check("model_sha256", False, ["sha256", str(path)], None, "model path is not a file", {})
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    return _check("model_sha256", actual == expected, ["sha256", str(path)], 0, actual, {"bytes": path.stat().st_size})


def _backend_check(environment: dict[str, object]) -> tuple[Check, str | None]:
    url = _string(environment, "backend_url").rstrip("/")
    expected_version = _string(environment, "comfy_version")
    expected_sha = _string(environment, "comfy_sha")
    root = _string(environment, "comfy_root")
    pid = environment.get("comfy_pid")
    try:
        with urlopen(url + "/system_stats", timeout=10) as response:
            body = response.read()
            http_status = response.status
        stats = json.loads(body.decode("utf-8"))
    except Exception as exc:
        return _check("backend", False, ["GET", url + "/system_stats"], None, f"system_stats failed: {type(exc).__name__}", {}), None
    sha = _run(["git", "-C", root, "rev-parse", "HEAD"])
    describe = _run(["git", "-C", root, "describe", "--tags", "--always"])
    described_version = describe.stdout.strip()
    version_ok = expected_version in json.dumps(stats, sort_keys=True) or expected_version in described_version or expected_version.lstrip("v") in described_version
    sha_ok = sha.returncode == 0 and sha.stdout.strip() == expected_sha
    port = urlsplit(url).port or 80
    process = _windows_process_identity(pid, root, port) if isinstance(pid, int) else None
    process_ok = process is not None and process["root_match"] == "True" and process["port_match"] == "True"
    boot_identity = None
    if process is not None:
        boot_identity = "boot:" + sha256(json.dumps(process, sort_keys=True).encode("utf-8")).hexdigest()
    passed = http_status == 200 and version_ok and sha_ok and process_ok
    return _check(
        "backend",
        passed,
        ["GET", url + "/system_stats"],
        0 if passed else (sha.returncode if sha.returncode else None),
        f"http={http_status}; version_match={version_ok}; sha_match={sha_ok}; process_identity={process_ok}",
        {
            "system_stats_sha256": sha256(body).hexdigest(),
            "git_sha": sha.stdout.strip() if sha.returncode == 0 else None,
            "git_describe": described_version if describe.returncode == 0 else None,
            "process_identity": process,
        },
    ), boot_identity


def _windows_process_identity(pid: int, expected_root: str, expected_port: int) -> dict[str, str] | None:
    command = [
        "powershell", "-NoProfile", "-NonInteractive", "-Command",
        f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}'; if($null -eq $p){{exit 3}}; $p | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress",
    ]
    result = _run(command)
    if result.returncode != 0:
        return None
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    # Command line itself is intentionally never stored in the report.
    command_line = str(value.get("CommandLine", ""))
    normalized_command = command_line.replace("/", "\\").casefold()
    normalized_root = str(Path(expected_root).resolve()).replace("/", "\\").casefold()
    port_match = any(token in normalized_command for token in (f"--port {expected_port}", f"--port={expected_port}", f"-p {expected_port}"))
    return {
        "pid": str(value.get("ProcessId")),
        "creation": str(value.get("CreationDate")),
        "command_sha256": sha256(command_line.encode("utf-8")).hexdigest(),
        "root_match": str(normalized_root in normalized_command),
        "port_match": str(port_match),
    }


def _fresh_roots_check(value: dict[str, object]) -> Check:
    labels = ("B2_F00", "W3_F00", "B2_F02", "W3_F02")
    missing = [label for label in labels if not isinstance(value.get(label), str) or not value[label]]
    if missing:
        return _check("fresh_output_roots", False, [], None, "missing roots: " + ",".join(missing), {})
    roots = {label: Path(str(value[label])).resolve() for label in labels}
    exists = {label: path.exists() for label, path in roots.items()}
    different = len(set(roots.values())) == len(roots)
    overlapping = any(
        left != right and (left in right.parents or right in left.parents)
        for index, left in enumerate(roots.values())
        for right in list(roots.values())[index + 1:]
    )
    # Preflight does not create data roots.  A nonexistent path is the only
    # unambiguous proof here that a later run will receive a fresh namespace.
    passed = different and not overlapping and not any(exists.values())
    return _check("fresh_output_roots", passed, [], 0, f"different={different}; overlapping={overlapping}; exists={exists}", {})


def _run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=input_text, text=True, capture_output=True, check=False)


def _object(value: dict[str, object], name: str) -> dict[str, object]:
    item = value.get(name)
    if not isinstance(item, dict):
        raise ValueError(f"missing object: {name}")
    return item


def _string(value: dict[str, object], name: str) -> str:
    item = value.get(name)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"missing nonempty string: {name}")
    return item


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("reservation timestamps must include an offset")
    return parsed.astimezone(timezone.utc)


def _brief(value: str, limit: int = 500) -> str:
    compact = " ".join(value.split())
    return compact if len(compact) <= limit else compact[:limit] + "…"


def _check(name: str, passed: bool, command: list[str], exit_code: int | None, summary: str, details: dict[str, object]) -> Check:
    return Check(name, passed, command, exit_code, summary, details)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only preflight for the reviewed Windows F02 pilot.")
    parser.add_argument("--config", required=True, help="JSON configuration containing explicit frozen identities and reservation.")
    args = parser.parse_args(argv)
    try:
        value = json.loads(Path(args.config).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "reason": f"config_read_failed:{type(exc).__name__}"}, sort_keys=True))
        return 2
    if not isinstance(value, dict):
        print(json.dumps({"status": "FAIL", "reason": "config_must_be_object"}, sort_keys=True))
        return 2
    report = run_preflight(value)
    print(json.dumps(report.as_dict(), sort_keys=True))
    return 0 if report.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
