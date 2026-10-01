"""Launch the product MCP server with research-only F02 transport injection."""

from __future__ import annotations

import os
from pathlib import Path
import runpy
import sys

from f02_transport_shim import install_prompt_proxy


def main() -> None:
    server = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(server.parent))
    proxy_url = os.environ.get("LOCAL_GPU_IMAGEGEN_RESEARCH_PROMPT_PROXY_URL")
    if proxy_url:
        import local_gpu_imagegen.backends.base as base

        install_prompt_proxy(base, proxy_url)
    sys.argv = [str(server), *sys.argv[2:]]
    runpy.run_path(str(server), run_name="__main__")


if __name__ == "__main__":
    main()
