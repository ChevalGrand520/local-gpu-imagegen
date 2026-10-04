"""One-shot, loopback-only reverse proxy for research ambiguity faults.

The proxy is deliberately narrower than a general proxy.  It accepts only the
ComfyUI HTTP paths exercised by the pilot. F02 suppresses one accepted response;
FPRE closes one fully received prompt request before calling upstream transport.
It never manufactures a successful response.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import http.client
import http.server
import ipaddress
import json
from pathlib import Path
import socket
import threading
import time
from urllib.parse import urlsplit


class ProxyConfigurationError(ValueError):
    """Raised when a proxy configuration could leave the loopback boundary."""


@dataclass(frozen=True)
class ProxyReceipt:
    sequence: int
    received_at: float
    method: str
    path: str
    body_sha256: str
    body_bytes: int
    upstream_status: int | None
    upstream_reason: str | None
    accepted_job_id: str | None
    response_dropped: bool
    forwarded: bool
    failure: str | None
    request_sequence: int = 0


class OneShotLoopbackFaultProxy:
    """Forward a small ComfyUI allowlist and drop only the first F02 acceptance.

    ``fault_mode`` is ``"F00"`` (transparent), ``"F02"`` or ``"FPRE"``. In F02
    mode only the first successfully parsed acceptance response for ``POST
    /prompt`` is hidden from the client.  Its prompt ID remains in the
    proxy-owned receipt list so a controller can hand it only to the oracle.
    """

    _ALLOWED_EXACT = {"/system_stats", "/prompt", "/queue", "/view"}
    _ALLOWED_PREFIXES = ("/object_info/", "/history/", "/view/")
    _HOP_BY_HOP = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailer", "transfer-encoding", "upgrade",
    }

    def __init__(
        self,
        upstream_url: str,
        *,
        fault_mode: str,
        bind_host: str = "127.0.0.1",
        bind_port: int = 0,
        timeout_seconds: float = 30.0,
        stage_log_path: Path | None = None,
    ) -> None:
        if fault_mode not in {"F00", "F02", "FPRE"}:
            raise ProxyConfigurationError("fault_mode must be F00, F02 or FPRE")
        _require_loopback_url(upstream_url)
        _require_loopback_host(bind_host)
        if not isinstance(bind_port, int) or not 0 <= bind_port <= 65535:
            raise ProxyConfigurationError("bind_port must be a TCP port")
        if timeout_seconds <= 0:
            raise ProxyConfigurationError("timeout_seconds must be positive")
        parsed = urlsplit(upstream_url)
        self._upstream_host = parsed.hostname or ""
        self._upstream_port = parsed.port or 80
        self._upstream_base_path = parsed.path.rstrip("/")
        self.upstream_url = upstream_url.rstrip("/")
        self.fault_mode = fault_mode
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.timeout_seconds = float(timeout_seconds)
        self._lock = threading.Lock()
        self._receipts: list[ProxyReceipt] = []
        self._f02_consumed = False
        self._fpre_consumed = False
        self._request_sequence = 0
        self._stages: list[dict[str, object]] = []
        self._stage_log_path = stage_log_path
        self._stage_log = None
        self._server: http.server.ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def receipts(self) -> tuple[ProxyReceipt, ...]:
        with self._lock:
            return tuple(self._receipts)

    @property
    def hidden_job_id(self) -> str | None:
        with self._lock:
            for receipt in self._receipts:
                if receipt.response_dropped:
                    return receipt.accepted_job_id
        return None

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("proxy is not running")
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> "OneShotLoopbackFaultProxy":
        if self._server is not None:
            raise RuntimeError("proxy is already running")
        if self._stage_log_path is not None:
            self._stage_log = self._stage_log_path.open("x", encoding="utf-8")
        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, _format: str, *_args: object) -> None:
                return

            def do_GET(self) -> None:  # noqa: N802
                parent._handle(self)

            def do_POST(self) -> None:  # noqa: N802
                parent._handle(self)

        try:
            self._server = http.server.ThreadingHTTPServer((self.bind_host, self.bind_port), Handler)
        except Exception:
            if self._stage_log is not None:
                self._stage_log.close()
                self._stage_log = None
            raise
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, name="f02-loopback-proxy", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._server = None
        self._thread = None
        if self._stage_log is not None:
            self._stage_log.close()
            self._stage_log = None

    def __enter__(self) -> "OneShotLoopbackFaultProxy":
        return self.start()

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.close()

    def evidence(self) -> list[dict[str, object]]:
        return [asdict(receipt) for receipt in self.receipts]

    @property
    def stages(self) -> tuple[dict[str, object], ...]:
        with self._lock:
            return tuple(dict(event) for event in self._stages)

    def _stage(self, request_sequence: int, stage: str, method: str, path: str) -> None:
        with self._lock:
            event = {"event_sequence": len(self._stages) + 1,
                     "request_sequence": request_sequence, "stage": stage,
                     "method": method, "path": path,
                     "monotonic_ns": time.monotonic_ns(), "wall_time": time.time()}
            if self._stage_log is not None:
                self._stage_log.write(json.dumps(event, sort_keys=True) + "\n")
                self._stage_log.flush()
            self._stages.append(event)

    def _handle(self, handler: http.server.BaseHTTPRequestHandler) -> None:
        method = handler.command.upper()
        path = handler.path
        if method not in {"GET", "POST"} or not self._allowed_path(path):
            handler.send_error(403, "F02 proxy path is not in the reviewed allowlist")
            return
        content_length = handler.headers.get("Content-Length", "0")
        try:
            length = int(content_length)
        except ValueError:
            handler.send_error(400, "invalid Content-Length")
            return
        if length < 0 or length > 16 * 1024 * 1024:
            handler.send_error(413, "request body exceeds research proxy limit")
            return
        body = handler.rfile.read(length) if length else b""
        if len(body) != length:
            handler.send_error(400, "incomplete request body")
            return
        receipt_time = time.time()
        with self._lock:
            self._request_sequence += 1
            request_sequence = self._request_sequence
            pre_drop = (self.fault_mode == "FPRE" and not self._fpre_consumed
                        and method == "POST" and _path_only(path) == "/prompt")
            if pre_drop:
                self._fpre_consumed = True
        self._stage(request_sequence, "body_received", method, path)
        if pre_drop:
            self._stage(request_sequence, "fault_injected_before_upstream", method, path)
            self._append_receipt(received_at=receipt_time, method=method, path=path, body=body,
                upstream_status=None, upstream_reason=None, accepted_job_id=None,
                response_dropped=True, forwarded=False, failure=None,
                request_sequence=request_sequence)
            handler.close_connection = True
            try:
                handler.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass  # The client may already have closed its end.
            handler.connection.close()
            self._stage(request_sequence, "connection_closed", method, path)
            return
        try:
            status, reason, headers, upstream_body = self._forward(
                method, path, handler.headers, body, request_sequence=request_sequence)
        except Exception as exc:
            # `forwarded` alone is deliberately not a no-send oracle. The stage
            # ledger survives an exception after entering the send function.
            self._stage(request_sequence, "upstream_failure", method, path)
            self._append_receipt(received_at=receipt_time, method=method, path=path, body=body,
                upstream_status=None, upstream_reason=None, accepted_job_id=None,
                response_dropped=False, forwarded=False,
                failure=f"{type(exc).__name__}: {exc}", request_sequence=request_sequence)
            handler.send_error(502, "research proxy forwarding failure")
            return
        try:
            job_id = _accepted_prompt_id(upstream_body) if method == "POST" and _path_only(path) == "/prompt" else None
            if job_id is not None and 200 <= status < 300:
                self._stage(request_sequence, "acceptance_received", method, path)
            should_drop = self._consume_f02_once(method, path, status, job_id)
            receipt = self._append_receipt(
                received_at=receipt_time,
                method=method,
                path=path,
                body=body,
                upstream_status=status,
                upstream_reason=reason,
                accepted_job_id=job_id,
                response_dropped=should_drop,
                forwarded=True,
                failure=None,
                request_sequence=request_sequence,
            )
            if should_drop:
                # No status line or acceptance bytes are emitted.  This is a real
                # transport loss after backend acceptance, not a synthetic success.
                handler.close_connection = True
                self._stage(request_sequence, "accepted_response_suppressed", method, path)
                return
            handler.send_response(status, reason)
            for name, value in headers:
                if name.lower() not in self._HOP_BY_HOP and name.lower() != "content-length":
                    handler.send_header(name, value)
            handler.send_header("Content-Length", str(len(upstream_body)))
            handler.end_headers()
            if upstream_body:
                handler.wfile.write(upstream_body)
        except OSError:
            # Delivery failure must not erase an already observed acceptance or
            # append a second receipt for the same incoming POST.
            self._stage(request_sequence, "client_delivery_failed", method, path)
            handler.close_connection = True

    def _forward(
        self,
        method: str,
        path: str,
        headers: http.client.HTTPMessage,
        body: bytes,
        *, request_sequence: int,
    ) -> tuple[int, str, list[tuple[str, str]], bytes]:
        target = self._upstream_base_path + path
        connection = http.client.HTTPConnection(self._upstream_host, self._upstream_port, timeout=self.timeout_seconds)
        try:
            connection.putrequest(method, target, skip_host=True, skip_accept_encoding=True)
            connection.putheader("Host", f"{self._upstream_host}:{self._upstream_port}")
            for name, value in headers.items():
                lowered = name.lower()
                if lowered in self._HOP_BY_HOP or lowered in {"host", "content-length"}:
                    continue
                connection.putheader(name, value)
            connection.putheader("Content-Length", str(len(body)))
            self._stage(request_sequence, "upstream_send_started", method, path)
            connection.endheaders(body)
            self._stage(request_sequence, "request_body_sent", method, path)
            response = connection.getresponse()
            response_body = response.read()
            self._stage(request_sequence, "upstream_response_received", method, path)
            return response.status, response.reason, list(response.getheaders()), response_body
        finally:
            connection.close()

    def _consume_f02_once(self, method: str, path: str, status: int, job_id: str | None) -> bool:
        if self.fault_mode != "F02" or method != "POST" or _path_only(path) != "/prompt":
            return False
        with self._lock:
            if self._f02_consumed:
                return False
            if not 200 <= status < 300 or job_id is None:
                return False
            self._f02_consumed = True
            return True

    def _append_receipt(
        self,
        *,
        received_at: float,
        method: str,
        path: str,
        body: bytes,
        upstream_status: int | None,
        upstream_reason: str | None,
        accepted_job_id: str | None,
        response_dropped: bool,
        forwarded: bool,
        failure: str | None,
        request_sequence: int = 0,
    ) -> ProxyReceipt:
        with self._lock:
            receipt = ProxyReceipt(
                sequence=len(self._receipts) + 1,
                received_at=received_at,
                method=method,
                path=path,
                body_sha256=sha256(body).hexdigest(),
                body_bytes=len(body),
                upstream_status=upstream_status,
                upstream_reason=upstream_reason,
                accepted_job_id=accepted_job_id,
                response_dropped=response_dropped,
                forwarded=forwarded,
                failure=failure,
                request_sequence=request_sequence,
            )
            self._receipts.append(receipt)
            return receipt

    def _allowed_path(self, path: str) -> bool:
        path_only = _path_only(path)
        return path_only in self._ALLOWED_EXACT or path_only.startswith(self._ALLOWED_PREFIXES)


def _path_only(value: str) -> str:
    return urlsplit(value).path


def _accepted_prompt_id(body: bytes) -> str | None:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    prompt_id = value.get("prompt_id")
    return prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else None


def _require_loopback_url(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ProxyConfigurationError("upstream URL must be a plain http loopback URL")
    if not parsed.hostname:
        raise ProxyConfigurationError("upstream URL requires a hostname")
    _require_loopback_host(parsed.hostname)


def _require_loopback_host(value: str) -> None:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ProxyConfigurationError("host must be a numeric loopback address") from exc
    if not address.is_loopback:
        raise ProxyConfigurationError("host must be a loopback address")
