from __future__ import annotations

import unittest
from types import SimpleNamespace

from scripts.research.f02_transport_shim import install_prompt_proxy


class _FakeClient:
    _f02_prompt_proxy_installed = False

    def __init__(self, base_url: str, **kwargs: object) -> None:
        self.base_url = base_url
        self.timeout = float(kwargs.get("timeout", 5.0))
        self.max_bytes = int(kwargs.get("max_bytes", 100))
        self.max_request_bytes = int(kwargs.get("max_request_bytes", 100))

    def _request(self, path: str, body: bytes | None, limit: int) -> bytes:
        return f"direct:{self.base_url}:{path}".encode()


class TransportShimTests(unittest.TestCase):
    def setUp(self) -> None:
        _FakeClient._f02_prompt_proxy_installed = False

    def test_only_prompt_uses_proxy_and_identity_client_stays_real(self) -> None:
        module = SimpleNamespace(BoundedJsonClient=_FakeClient)
        install_prompt_proxy(module, "http://127.0.0.1:39191")
        client = _FakeClient("http://127.0.0.1:8202")

        prompt = client._request("/prompt", b"{}", 100)
        history = client._request("/history", None, 100)

        self.assertTrue(prompt.startswith(b"direct:http://127.0.0.1:39191"))
        self.assertEqual(history, b"direct:http://127.0.0.1:8202:/history")
        self.assertEqual(client.base_url, "http://127.0.0.1:8202")
