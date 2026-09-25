# W3 Windows F00/F02 Pilot (Agent-Managed)

Status: stopped at the F00 evaluability gate. This run does not establish a
deployment failure rate or an execution rate.

## Frozen environment

- Trusted research contract: PASS at ledger anchor `d8ef0bccc84269b7d4a627adce5f6025a17ab024` (14 protected files).
- B2 client: `da65d57047b5a59e3403b49adf4605a1c0497c58`, clean detached checkout.
- W3 client: `d45173af75d404ad79dc14568edd4c45f654abd2`, clean detached checkout.
- Agent-managed ComfyUI: `v0.30.0`, SHA `b1693ecba9f5b65f8c80ab36b195ab963ec92413`, loopback endpoint `127.0.0.1:8202`.
- Model: SDXL Base, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`.
- Model approval was private to the local state store. No public-candidate approval was made.
- The research client receives the checkpoint's absolute path from a private process environment variable; the path is not embedded in the committed script.
- Reservation: `2026-09-25T06:13:50Z` to `2026-09-25T10:13:50Z`; 900-second case timeout; 180-second observer window; exactly four single-stage cases.

## Results

| Case | Scheduled | Started | Injection confirmed | Oracle evaluable | Resolved | Unresolved | Failed | Not run |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B2 F00 | 1 | 1 | N/A | 0 | 0 | 1 | 0 | 0 |
| W3 F00 | 1 | 1 | N/A | 0 | 0 | 1 | 0 | 0 |
| B2 F02 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| W3 F02 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Total | 4 | 2 | 0/2 fault cases | 0 | 0 | 2 | 0 | 2 |

For F00, `started` means the controller invoked the product client. Both calls
returned product-reported `unresolved`, but the loopback proxy observed zero
`POST /prompt` requests and zero backend acceptances. No execution event or
artifact was observed. The independent oracle therefore had no execution to
evaluate. F02 was stopped by the frozen controller rule because F00 was not
evaluable; neither F02 product call ran.

The ComfyUI queue was empty after the campaign. The agent-started ComfyUI
process was stopped and its one-run scheduled task was unregistered. All four
case output roots remained absent. No image generation, retry, model switch,
finalization, or visual review occurred.

## Limitation and next step

The sanitized campaign record retained stdout hashes but dropped the
product client's `client_error`, so the exact reason each F00 call failed
before proxy submission is unknown. Preserve these unresolved F00 observations
as-is. The next step is to add path-redacted error-code capture to the research
evidence, diagnose the client failure without submitting `/prompt`, then use a
separate reservation before any new campaign. Do not describe these observations
as backend execution failures.

The complete campaign report and JSONL evidence remain in the Windows
user-local research/output state and are not part of this repository record.
