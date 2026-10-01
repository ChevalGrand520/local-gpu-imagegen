"""Research-only transport shim for endpoint-preserving F02 injection."""

from __future__ import annotations

from typing import Any


def install_prompt_proxy(base_module: Any, proxy_url: str) -> None:
    """Route only /prompt transport through a proxy while preserving identity."""
    client_type = base_module.BoundedJsonClient
    if getattr(client_type, "_f02_prompt_proxy_installed", False):
        return
    original_request = client_type._request

    def request(self: Any, path: str, body: bytes | None, limit: int) -> bytes:
        request_path = path.split("?", 1)[0].rstrip("/") or "/"
        if request_path != "/prompt":
            return original_request(self, path, body, limit)
        proxy = client_type(
            proxy_url,
            timeout=self.timeout,
            max_bytes=self.max_bytes,
            max_request_bytes=self.max_request_bytes,
        )
        return original_request(proxy, path, body, limit)

    client_type._request = request
    client_type._f02_prompt_proxy_installed = True
