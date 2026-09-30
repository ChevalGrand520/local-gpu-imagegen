# Same-run Windows preparation, 2026-10-01

## Verified preparation

- Research source: `codex/f02-same-run-capture`, exact commit
  `8f5794cbb5daf172a1915849c0732b0e9a6f65fa`.
- Windows received the source by Git fetch and created a separate detached
  research checkout; existing product and research checkouts were preserved.
- Direct numeric Tailscale address SSH succeeded without an interactive password.
- Windows Python 3.15 ran `python -B -m unittest discover -s tests/research -q`:
  **61 tests passed**, process exit 0, unittest duration 7.695 seconds.
- These tests use CPU/local fixture or mocked transport boundaries; they do not
  establish real ComfyUI behavior or the Windows submission-guard effect.
- The initial Windows GitHub fetch failed. A temporary loopback-only remote
  SOCKS forward through the authenticated Mac SSH session allowed Git fetch;
  the forward was closed after transfer. No global Windows proxy was changed.

## Live-generation gate remains pending

- No Python/ComfyUI process was observed in the bounded inventory and the
  frozen backend port 8202 was not listening.
- GPU memory use was approximately 1.35 GiB; listed processes were desktop
  applications. This does not establish an exclusive reservation and exceeds
  the ARIS default free-GPU criterion of 500 MiB.
- The retained campaign reservation expired on 2026-09-27. It cannot authorize
  or classify a new run as scheduled within an active window.
- User confirmation of exclusive ownership, an accepted desktop-memory
  baseline and a fresh 30-minute reservation was requested and remains pending.
- No ComfyUI startup, model download, POST /prompt, fault injection or GPU
  generation was performed during this preparation.

Next: verify the accepted reservation and frozen environment, create fresh
private configuration/output/capture paths, then execute only W3 F00 and W3 F02
under the same-run protocol and its stopping rules.
