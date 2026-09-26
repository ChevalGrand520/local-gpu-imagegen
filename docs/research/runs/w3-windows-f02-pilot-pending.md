# Windows F02 Pilot Pending Record

**Status:** pending / not run

This record stops the requested real pilot before reservation-first preflight
hardware/backend checks because this Windows thread has no mounted
`local_gpu_*` MCP tool and no confirmed legal product-client entry point. No
ordinary HTTP request, `/prompt` request, GPU task, model operation, service
operation, or ROS2 operation was performed.

## Reservation

| Field | Value |
| --- | --- |
| Actor / owner | `Capricorn` |
| Host | `LAPTOP-7QD7KR9F` |
| GPU UUID | `GPU-25c43be6-ab43-2700-35f9-1db584b84dd8` (frozen target; live use not started) |
| Reservation start | `2026-09-20T05:53:27.0769919Z` |
| Reservation end | `2026-09-20T09:53:27.0769919Z` |
| Hard timeout | `900` seconds |
| Scope | exactly four reviewed F00/F02 single-stage cases |
| Concurrent GPU work | prohibited |
| ComfyUI endpoint | `http://127.0.0.1:8202` (frozen target; no listener observed) |
| ComfyUI PID / boot identity | PID `37720` absent; boot identity pending |
| B2 client SHA | `da65d57047b5a59e3403b49adf4605a1c0497c58` (checkout not located) |
| W3 client SHA | `d45173af75d404ad79dc14568edd4c45f654abd2` required; observed candidate was `a7d3e3695718d4cb7221852b491111e7684f8719` |

The reservation timestamps were captured from the Windows PowerShell UTC
clock. The end is exactly four hours after the captured start.

## Commands and Results

| Command | Exit | Result |
| --- | ---: | --- |
| `git -C <ledger> show d8ef0bccc84269b7d4a627adce5f6025a17ab024:scripts/verify_research_contract.py \| py - --root <ledger> --anchor d8ef0bccc84269b7d4a627adce5f6025a17ab024` | 0 | Contract guard returned `PASS`; the private ledger path is intentionally redacted. |
| `Get-Date -AsUTC`; hostname/user/Python/Windows build inventory | 0 | Start `2026-09-20T05:53:27.0769919Z`; `LAPTOP-7QD7KR9F`; `Capricorn`; Python `3.15.0a8`; Windows build `10.0.26200.0`. |
| `Get-CimInstance Win32_Process -Filter 'ProcessId = 37720'` | 0 | `PID_37720=absent`. |
| `Get-NetTCPConnection -LocalPort 8202 -State Listen` | 1 | No listener returned. |
| exact current tool-registry lookup for `local_gpu_*` | 0 | Returned `[]`; no mounted `local_gpu_*` MCP tools. |
| bounded W3 checkout identity query | 0 | Candidate `<w3-candidate>` was on `codex/w3-windows-pilot-evidence` at `a7d3e369...`, not the required SHA; the private checkout path is intentionally redacted. |

No reservation-first preflight hardware/backend phase was entered after the
tool-entry gate failed. The missing legal entry point is not a product or GPU
failure.

## Denominator

The frozen plan contains four planned rows, but no row was legally scheduled
because the entry-point gate failed. Each planned row is therefore `not-run`.

| Case | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B2 F00 | 0 | 0 | N/A | 0 | 0 | 0 | 0 | 1 |
| W3 F00 | 0 | 0 | N/A | 0 | 0 | 0 | 0 | 1 |
| B2 F02 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| W3 F02 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **4** |

## Unique Blocker

No mounted `local_gpu_*` MCP tools or confirmed legal product-client entry
point exists in this thread. Stop here. Do not retry, perform ordinary HTTP,
call `/prompt`, or continue environment probing until that entry point is
available.
