"""Shared process constants for the decomposed MCP server."""

from __future__ import annotations

import os
import sys

from local_gpu_imagegen import __version__
from local_gpu_imagegen.paths import resolve_resource_root


ROOT = resolve_resource_root()
SCRIPTS = ROOT / "scripts"
PYTHON = sys.executable
DEFAULT_COMMAND_TIMEOUT_SECONDS = int(os.environ.get("LOCAL_GPU_IMAGEGEN_COMMAND_TIMEOUT_SECONDS", "900"))
MAX_PREVIEW_BASE64_CHARS = 4 * ((1024 * 1024 + 2) // 3)
MAX_DISCOVERY_METADATA_STRING_CHARS = 4096
SERVER_VERSION = __version__
