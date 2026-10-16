"""Experimental durable client for a separately installed ComfyUI MCP server.

No model/backend requests occur until submit/read_history is explicitly invoked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import threading


class BridgeError(RuntimeError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class StdioMCP:
    """Sequential MCP requests; notifications are consumed, never mistaken for replies."""

    def __init__(self, command, *, timeout=30, env=None):
        if not command or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Command and a positive finite timeout are required")
        self.timeout = timeout
        self.messages = queue.Queue()
        self.sequence = 0
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=sys.stderr, text=True, encoding="utf-8", env=env,
        )
        threading.Thread(target=self._read, daemon=True).start()
        try:
            result = self.request("initialize", {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "durable-comfyui-client", "version": "0.1.0"},
            })
            if result.get("protocolVersion") not in {"2024-11-05", "2025-03-26", "2025-06-18"}:
                raise BridgeError("Unsupported MCP protocol version")
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except BaseException:
            self.close()
            raise

    def _read(self):
        try:
            for line in self.process.stdout:
                self.messages.put(json.loads(line))
        except (ValueError, OSError) as exc:
            self.messages.put(exc)
        finally:
            self.messages.put(EOFError("Upstream MCP closed stdout"))

    def send(self, value):
        self.process.stdin.write(json.dumps(value, allow_nan=False) + "\n")
        self.process.stdin.flush()

    def request(self, method, params):
        import time
        self.sequence += 1
        request_id = self.sequence
        self.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                reply = self.messages.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty as exc:
                raise BridgeError("Upstream MCP deadline exceeded; submission may be unknown") from exc
            if isinstance(reply, Exception):
                raise BridgeError(str(reply))
            if not isinstance(reply, dict) or reply.get("jsonrpc") != "2.0":
                raise BridgeError("Malformed upstream MCP message")
            if "method" in reply:
                if "id" in reply:
                    self.send({"jsonrpc": "2.0", "id": reply["id"], "error": {
                        "code": -32601, "message": "Client capability not supported"}})
                continue
            if reply.get("id") != request_id:
                raise BridgeError("Unexpected upstream response ID")
            if "error" in reply or not isinstance(reply.get("result"), dict):
                raise BridgeError("Upstream returned JSON-RPC error or malformed result")
            return reply["result"]

    def call(self, name, arguments):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            # Don't expose backend diagnostics/secrets via an automatic exception.
            raise BridgeError("Upstream tool returned isError; delivery is uncertain")
        return result

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()


def job_id(result):
    """Only exact structured prompt_id fields; never guess IDs from prose or latest history."""
    candidates = []
    if isinstance(result.get("structuredContent"), dict):
        candidates.append(result["structuredContent"].get("prompt_id"))
    for item in result.get("content", []):
        if isinstance(item, dict) and item.get("type") == "text":
            try:
                value = json.loads(item.get("text", ""))
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict):
                candidates.append(value.get("prompt_id"))
    valid = {v for v in candidates if isinstance(v, str) and v.strip()}
    if len(valid) != 1:
        raise BridgeError("No unique prompt_id in enqueue result; outcome remains unknown")
    return valid.pop()


class DurableClient:
    def __init__(self, database, command, endpoint, *, mode="full", timeout=30):
        if mode not in {"native", "stop", "full"}:
            raise ValueError("Invalid control mode")
        if not command or not endpoint or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Explicit upstream command and endpoint identity required")
        self.command, self.endpoint = list(command), endpoint
        self.environment = dict(os.environ)
        self.mode, self.timeout = mode, timeout
        self.db = None
        if mode != "native":
            self.db = sqlite3.connect(database, timeout=10)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("""CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY, request_digest TEXT NOT NULL,
                state TEXT NOT NULL, prompt_id TEXT, result TEXT, context_digest TEXT NOT NULL)""")
            self.db.commit()

    def close(self):
        if self.db:
            self.db.close()

    def inspect(self, run_id):
        if not self.db:
            raise BridgeError("Native mode has no durable records")
        row = self.db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise BridgeError("Unknown run_id")
        record = dict(row)
        if record["state"] == "submitting":
            record["state"] = "unknown"
        if record["result"] is not None:
            record["result"] = json.loads(record["result"])
        return record

    def _call(self, name, arguments):
        client = StdioMCP(self.command, timeout=self.timeout, env=self.environment)
        try:
            return client.call(name, arguments)
        finally:
            client.close()

    def context_digest(self):
        return digest({"endpoint": self.endpoint, "command": self.command,
                       "runtime_config": {k: v for k, v in self.environment.items()
                                          if k.startswith(("COMFY", "MCP_"))}})

    def submit(self, run_id, key, workflow):
        if not isinstance(run_id, str) or not run_id or not isinstance(key, str) or not key:
            raise ValueError("Nonempty run_id and key required")
        if not isinstance(workflow, dict) or not workflow:
            raise ValueError("Nonempty API workflow object required")
        binding = digest({"key": key, "workflow": workflow,
                          "context": self.context_digest()})
        if self.mode == "native":
            return self._call("enqueue_workflow", {"action": "enqueue", "workflow": workflow})
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row:
                if row["request_digest"] != binding:
                    raise BridgeError("Request binding conflict: key, graph, endpoint or command changed")
            else:
                self.db.execute("INSERT INTO runs VALUES (?, ?, 'submitting', NULL, NULL, ?)",
                                (run_id, binding, self.context_digest()))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        if row:
            if not row["prompt_id"]:
                raise BridgeError("Submission outcome unknown; no automatic resubmission")
            if self.mode == "stop":
                return self.inspect(run_id)
            return self.read_history(run_id)
        try:
            result = self._call("enqueue_workflow", {"action": "enqueue", "workflow": workflow})
            prompt = job_id(result)
            self.db.execute("UPDATE runs SET state='known_job', prompt_id=?, result=? WHERE run_id=?",
                            (prompt, canonical(result), run_id))
            self.db.commit()
        except BaseException:
            # Intent is already committed even if this update fails / process dies.
            self.db.rollback()
            raise
        return self.inspect(run_id)

    def read_history(self, run_id):
        record = self.inspect(run_id)
        if record["context_digest"] != self.context_digest():
            raise BridgeError("Recovery context conflict: endpoint, command or configuration changed")
        if not record["prompt_id"]:
            raise BridgeError("No retained prompt_id; history matching is not supported")
        result = self._call("get_history", {"action": "list", "prompt_id": record["prompt_id"]})
        return {"state": "known_job", "prompt_id": record["prompt_id"], "history_reply": result,
                "completion_verified": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--endpoint", required=True, help="Identity of the upstream-configured ComfyUI endpoint")
    p.add_argument("--mode", choices=["native", "stop", "full"], default="full")
    p.add_argument("--timeout", type=float, default=30)
    p.add_argument("--action", choices=["inspect", "submit", "read_history", "tools"], required=True)
    p.add_argument("--run-id", default="")
    p.add_argument("--key", default="")
    p.add_argument("--workflow", type=Path)
    p.add_argument("command", nargs=argparse.REMAINDER, help="-- node /absolute/upstream/dist/index.js")
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ["--"] else a.command
    client = DurableClient(a.database, command, a.endpoint, mode=a.mode, timeout=a.timeout)
    try:
        if a.action == "tools":
            upstream = StdioMCP(command, timeout=a.timeout, env=client.environment)
            try:
                result = upstream.request("tools/list", {})
            finally:
                upstream.close()
        elif a.action == "submit":
            if a.workflow is None:
                p.error("--workflow is required for submit")
            result = client.submit(a.run_id, a.key, json.loads(a.workflow.read_text()))
        else:
            result = getattr(client, a.action)(a.run_id)
        print(json.dumps(result, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
