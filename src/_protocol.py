"""Stdio transport, JSON-RPC framing, and backend script execution."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _constants import DEFAULT_COMMAND_TIMEOUT_SECONDS, PYTHON, ROOT, SCRIPTS


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def text_content(text: str) -> list[dict[str, str]]:
    return [{"type": "text", "text": text}]


def tool_error(
    code: str,
    category: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "code": code,
        "category": category,
        "message": message,
    }
    if details:
        error["details"] = details
    return {
        "content": text_content(message),
        "structuredContent": {"error": error},
        "isError": True,
    }


def jsonrpc_error(
    request_id: object,
    code: int,
    message: str,
    category: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"category": category}
    if details:
        data["details"] = details
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message, "data": data},
    }


def command_error(
    script: str,
    return_code: int,
    stdout: str,
    stderr: str,
) -> dict[str, Any]:
    diagnostic = stderr.strip() or stdout.strip() or f"{script} exited without an error message."
    if return_code == 124:
        return tool_error(
            "command_timeout",
            "timeout",
            diagnostic,
            {"script": script, "timeoutSeconds": DEFAULT_COMMAND_TIMEOUT_SECONDS},
        )
    return tool_error(
        "backend_command_failed",
        "execution",
        diagnostic,
        {"script": script, "exitCode": return_code},
    )


def tool_success(data: dict[str, Any], preview: dict[str, str] | None = None) -> dict[str, Any]:
    content: list[dict[str, str]] = text_content(json.dumps(data, indent=2))
    if preview:
        content.append({"type": "image", "data": preview["data"], "mimeType": preview["mimeType"]})
    return {
        "content": content,
        "structuredContent": data,
        "isError": False,
    }


def script_json_result(
    script: str,
    return_code: int,
    stdout: str,
    stderr: str,
    accepted_return_codes: set[int] | None = None,
) -> dict[str, Any]:
    accepted = accepted_return_codes or {0}
    if return_code not in accepted:
        return command_error(script, return_code, stdout, stderr)
    if not stdout.strip():
        return command_error(script, return_code, stdout, stderr)
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return tool_error(
            "invalid_backend_response",
            "execution",
            f"{script} did not return a valid JSON object.",
            {"script": script, "exitCode": return_code},
        )
    if not isinstance(data, dict):
        return tool_error(
            "invalid_backend_response",
            "execution",
            f"{script} returned JSON, but the top-level value was not an object.",
            {"script": script, "exitCode": return_code},
        )
    return tool_success(data)


def run_script(script: str, args: list[str] | None = None) -> tuple[int, str, str]:
    script_path = SCRIPTS / script
    command = [PYTHON, str(script_path)] if script_path.is_file() else [PYTHON, "-m", Path(script).stem]
    if args:
        command.extend(args)
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            cwd=str(ROOT),
            timeout=DEFAULT_COMMAND_TIMEOUT_SECONDS,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"{script} exceeded the {DEFAULT_COMMAND_TIMEOUT_SECONDS}s timeout."
