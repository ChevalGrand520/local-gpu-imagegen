"""Read-only ComfyUI backend-event oracle for the reviewed F02 pilot.

A prompt ID, HTTP POST, history entry, or artifact count alone is deliberately
not interpreted as an execution count.  This observer requires a backend
WebSocket start event and a terminal WebSocket event, then checks read-only
history for completion before declaring an execution instance bindable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import base64
import http.client
import ipaddress
import json
import os
import socket
import struct
import time
from typing import Iterable
from urllib.parse import quote, urlsplit


class OracleConfigurationError(ValueError):
    """Raised when an observer request is outside the read-only loopback scope."""


@dataclass(frozen=True)
class BackendEvent:
    received_at: float
    event_type: str
    prompt_id: str | None
    node: str | None
    payload: dict[str, object]


@dataclass(frozen=True)
class ExecutionBinding:
    prompt_id: str
    execution_instance_id: str
    started_at: float
    finished_at: float
    terminal_event: str
    history_completed: bool
    artifact_paths: tuple[str, ...]


@dataclass(frozen=True)
class OracleDecision:
    status: str
    reason: str
    bindings: tuple[ExecutionBinding, ...]
    raw_events: tuple[BackendEvent, ...]
    history_by_prompt: dict[str, object]

    @property
    def oracle_evaluable(self) -> bool:
        return self.status == "evaluable"

    def evidence(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason": self.reason,
            "bindings": [asdict(value) for value in self.bindings],
            "raw_events": [asdict(value) for value in self.raw_events],
            "history_by_prompt": self.history_by_prompt,
        }


class ComfyUIEventOracle:
    """Collect backend-origin ComfyUI lifecycle events without controlling it."""

    def __init__(
        self,
        backend_url: str,
        *,
        backend_boot_identity: str,
        observer_id: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        _require_loopback_http_url(backend_url)
        if not backend_boot_identity.strip():
            raise OracleConfigurationError("backend_boot_identity is required")
        if not observer_id.strip():
            raise OracleConfigurationError("observer_id is required")
        if timeout_seconds <= 0:
            raise OracleConfigurationError("timeout_seconds must be positive")
        parsed = urlsplit(backend_url)
        self.backend_url = backend_url.rstrip("/")
        self.host = parsed.hostname or ""
        self.port = parsed.port or 80
        self.backend_boot_identity = backend_boot_identity
        self.observer_id = observer_id
        self.timeout_seconds = float(timeout_seconds)
        self._socket: socket.socket | None = None
        self._events: list[BackendEvent] = []
        self._start_sequence = 0
        self._open_starts: dict[str, list[tuple[int, float]]] = {}
        self._terminal: dict[str, list[tuple[str, float]]] = {}

    @property
    def raw_events(self) -> tuple[BackendEvent, ...]:
        return tuple(self._events)

    def connect(self) -> None:
        if self._socket is not None:
            raise RuntimeError("oracle is already connected")
        sock = socket.create_connection((self.host, self.port), timeout=self.timeout_seconds)
        sock.settimeout(self.timeout_seconds)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET /ws?clientId={quote(self.observer_id, safe='')} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        sock.sendall(request)
        response = _read_http_headers(sock)
        if not response.startswith(b"HTTP/1.1 101") and not response.startswith(b"HTTP/1.0 101"):
            sock.close()
            raise OracleConfigurationError("ComfyUI WebSocket upgrade was not accepted")
        self._socket = sock

    def close(self) -> None:
        if self._socket is not None:
            try:
                _send_client_frame(self._socket, opcode=0x8, payload=b"")
            except OSError:
                pass
            self._socket.close()
        self._socket = None

    def __enter__(self) -> "ComfyUIEventOracle":
        self.connect()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.close()

    def observe_until(self, prompt_ids: Iterable[str], *, deadline_monotonic: float) -> OracleDecision:
        requested = {value for value in prompt_ids if isinstance(value, str) and value.strip()}
        if not requested:
            raise OracleConfigurationError("at least one prompt ID is required")
        if self._socket is None:
            raise RuntimeError("oracle must be connected before observation")
        while time.monotonic() < deadline_monotonic:
            remaining = max(0.01, min(self.timeout_seconds, deadline_monotonic - time.monotonic()))
            self._socket.settimeout(remaining)
            try:
                frame = _read_server_frame(self._socket)
            except socket.timeout:
                break
            if frame is None:
                break
            opcode, payload = frame
            if opcode == 0x9:
                _send_client_frame(self._socket, opcode=0xA, payload=payload)
                continue
            if opcode == 0x8:
                break
            if opcode != 0x1:
                continue
            self._record_payload(payload)
            if self._seen_terminal_for_all(requested):
                # ComfyUI can emit the terminal WebSocket event immediately before
                # its read-only history entry is materialized.  Keep observing
                # until history corroborates every terminal event or the fixed
                # window closes; history alone never changes an unevaluable result.
                decision = self._decision(requested)
                if decision.oracle_evaluable:
                    return decision
                time.sleep(0.25)
        return self._decision(requested)

    def _record_payload(self, payload: bytes) -> None:
        try:
            value = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        if not isinstance(value, dict):
            return
        event_type = value.get("type")
        data = value.get("data")
        if not isinstance(event_type, str) or not isinstance(data, dict):
            return
        prompt_id = data.get("prompt_id") if isinstance(data.get("prompt_id"), str) else None
        node_value = data.get("node")
        node = str(node_value) if node_value is not None else None
        event = BackendEvent(
            received_at=time.time(),
            event_type=event_type,
            prompt_id=prompt_id,
            node=node,
            payload=_sanitize_event_payload(data),
        )
        self._events.append(event)
        if prompt_id is None:
            return
        if event_type == "execution_start":
            self._start_sequence += 1
            self._open_starts.setdefault(prompt_id, []).append((self._start_sequence, event.received_at))
        elif event_type == "executing" and node is None:
            self._terminal.setdefault(prompt_id, []).append((event_type, event.received_at))
        elif event_type == "execution_error":
            self._terminal.setdefault(prompt_id, []).append((event_type, event.received_at))

    def _seen_terminal_for_all(self, prompt_ids: set[str]) -> bool:
        return all(self._terminal.get(prompt_id) for prompt_id in prompt_ids)

    def _decision(self, prompt_ids: set[str]) -> OracleDecision:
        histories: dict[str, object] = {}
        bindings: list[ExecutionBinding] = []
        failures: list[str] = []
        for prompt_id in sorted(prompt_ids):
            starts = self._open_starts.get(prompt_id, [])
            terminals = self._terminal.get(prompt_id, [])
            history = self._history(prompt_id)
            histories[prompt_id] = history
            if not starts:
                failures.append(f"missing_execution_start:{prompt_id}")
                continue
            if len(terminals) < len(starts):
                failures.append(f"missing_execution_finish:{prompt_id}")
                continue
            completed, artifacts = _completed_history(history, prompt_id)
            if not completed:
                failures.append(f"history_not_completed:{prompt_id}")
                continue
            for index, (sequence, started_at) in enumerate(starts):
                terminal_type, finished_at = terminals[index]
                if terminal_type != "executing":
                    failures.append(f"execution_error_terminal:{prompt_id}")
                    continue
                bindings.append(ExecutionBinding(
                    prompt_id=prompt_id,
                    execution_instance_id=_execution_instance_id(self.backend_boot_identity, prompt_id, sequence),
                    started_at=started_at,
                    finished_at=finished_at,
                    terminal_event=terminal_type,
                    history_completed=True,
                    artifact_paths=tuple(artifacts),
                ))
        if failures:
            return OracleDecision(
                status="not_evaluable",
                reason=";".join(failures),
                bindings=tuple(bindings),
                raw_events=self.raw_events,
                history_by_prompt=histories,
            )
        return OracleDecision(
            status="evaluable",
            reason="backend websocket starts and terminal events bind to completed history",
            bindings=tuple(bindings),
            raw_events=self.raw_events,
            history_by_prompt=histories,
        )

    def _history(self, prompt_id: str) -> dict[str, object]:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout_seconds)
        try:
            connection.request("GET", "/history/" + quote(prompt_id, safe=""))
            response = connection.getresponse()
            body = response.read()
        except OSError as exc:
            return {"history_transport_error": type(exc).__name__}
        finally:
            connection.close()
        if response.status != 200:
            return {"http_status": response.status, "body_sha256": sha256(body).hexdigest()}
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"http_status": response.status, "body_sha256": sha256(body).hexdigest(), "invalid_json": True}
        return value if isinstance(value, dict) else {"invalid_history_shape": type(value).__name__}


def _execution_instance_id(boot_identity: str, prompt_id: str, sequence: int) -> str:
    material = f"{boot_identity}\x00{prompt_id}\x00{sequence}".encode("utf-8")
    return "execution:" + sha256(material).hexdigest()


def _completed_history(history: dict[str, object], prompt_id: str) -> tuple[bool, list[str]]:
    entry = history.get(prompt_id)
    if not isinstance(entry, dict):
        return False, []
    status = entry.get("status")
    status_text = status.get("status_str") if isinstance(status, dict) else None
    if status_text != "success":
        return False, []
    outputs = entry.get("outputs")
    return True, _artifact_paths(outputs)


def _artifact_paths(value: object) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            paths.extend(_artifact_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.extend(_artifact_paths(item))
    elif isinstance(value, str):
        if value:
            paths.append(value)
    return sorted(set(paths))


def _sanitize_event_payload(value: dict[str, object]) -> dict[str, object]:
    # ComfyUI event payloads normally contain node IDs, prompt IDs, and output
    # metadata.  Preserve structure while dropping arbitrary long strings so a
    # record cannot accidentally become a prompt or image-data export.
    def clean(item: object) -> object:
        if isinstance(item, dict):
            return {str(key): clean(value) for key, value in item.items()}
        if isinstance(item, list):
            return [clean(element) for element in item]
        if isinstance(item, str):
            return item if len(item) <= 512 else f"[omitted long string; chars={len(item)}]"
        if item is None or isinstance(item, (bool, int, float)):
            return item
        return f"[omitted {type(item).__name__}]"
    return clean(value)  # type: ignore[return-value]


def _require_loopback_http_url(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise OracleConfigurationError("backend URL must be a plain http loopback URL")
    if not parsed.hostname:
        raise OracleConfigurationError("backend URL requires a hostname")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise OracleConfigurationError("backend host must be a numeric loopback address") from exc
    if not address.is_loopback:
        raise OracleConfigurationError("backend host must be loopback")


def _read_http_headers(sock: socket.socket) -> bytes:
    data = bytearray()
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(1)
        if not chunk:
            raise OracleConfigurationError("socket closed during WebSocket handshake")
        data.extend(chunk)
        if len(data) > 16 * 1024:
            raise OracleConfigurationError("oversized WebSocket handshake")
    return bytes(data)


def _read_exact(sock: socket.socket, count: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < count:
        chunk = sock.recv(count - len(chunks))
        if not chunk:
            raise OSError("socket closed while reading WebSocket frame")
        chunks.extend(chunk)
    return bytes(chunks)


def _read_server_frame(sock: socket.socket) -> tuple[int, bytes] | None:
    first = sock.recv(2)
    if not first:
        return None
    if len(first) != 2:
        first += _read_exact(sock, 2 - len(first))
    fin_opcode, length_byte = first
    if not fin_opcode & 0x80:
        raise OracleConfigurationError("fragmented WebSocket events are not supported by the pilot observer")
    opcode = fin_opcode & 0x0F
    masked = bool(length_byte & 0x80)
    if masked:
        raise OracleConfigurationError("server-to-client WebSocket frame must not be masked")
    length = length_byte & 0x7F
    if length == 126:
        length = struct.unpack("!H", _read_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(sock, 8))[0]
    if length > 4 * 1024 * 1024:
        raise OracleConfigurationError("oversized WebSocket event")
    return opcode, _read_exact(sock, length)


def _send_client_frame(sock: socket.socket, *, opcode: int, payload: bytes) -> None:
    if len(payload) > 125:
        raise OracleConfigurationError("pilot observer only sends small control frames")
    mask = os.urandom(4)
    masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
    sock.sendall(bytes([0x80 | opcode, 0x80 | len(payload)]) + mask + masked)
