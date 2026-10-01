# Paired Windows attempt B: partial result, stopped

Protocol paired-ambiguity-v1; execution source d81f667. Retained private parent
paired-windows-20261001-b. The previous attempt A remains a separate M1 stop.
Operator authorized autonomous research after reporting training released.
Explicit advisory reservation ended 2026-10-01T08:45:00Z; it was not extended.

## Measured outcomes

| Scheduled operation | Outcome | Calls | Proxy POST | Upstream sends | Accepted jobs | E_bound |
|---|---|---:|---:|---:|---:|---:|
| B2/F00 | COMPLETED | 1 | 1 | 1 | 1 | 1 |
| W3/F00 | COMPLETED | 1 | 1 | 1 | 1 | 1 |
| W3/F02 | STOPPED: accepted_lifecycle_not_bindable | 2 | 1 | 1 | 1 | unknown |
| B2/F02 | NOT_RUN | - | - | - | - | - |
| B2/FPRE | NOT_RUN | - | - | - | - | - |
| W3/FPRE | NOT_RUN | - | - | - | - | - |

F00 generation RPC intervals were 36.4948651 and 34.5189013 seconds.
The protocol therefore set the fault observation deadline to 109.4845953
seconds. These intervals include product/MCP overhead and are not pure GPU
compute cost. Total campaign elapsed time was 231.5274286000058 seconds.
Totals: 3 entered operations, 4 product calls, 3 proxy POSTs, 3 upstream sends.

## Claim-evidence disposition

W3/F02 receipts confirm an accepted job and suppressed response. The first
caller returned backend_request_failed at generate_round; the second returned
submission_outcome_unknown at generate_round. There was no second proxy POST.
This supports observed same-run submission withholding for this operation.
It does not establish a paired advantage: B2/F02 was never run.

The observer recorded execution_start once, execution_cached once, three
executing events (nodes 4, 5, 7), five progress_state events and three status
events. It retained no node-null terminal event and an empty history response.
The decision is not_evaluable/missing_execution_finish. E_bound remains unknown,
not zero or one. Start events do not prove complete lifecycle or physical GPU
computation. Backend stderr reached Requested to load SDXL in the downloaded
log. The root cause of failure to finish within the deadline remains unresolved;
do not attribute it to the guard, observer implementation or hardware yet.

The owned backend cleanup receipt records pid 280564 stopped=true, exit_code=1.
A subsequent native query returned no Python process or port-8202 listener
output (PowerShell exit 1 because no listener matched). No user application was
terminated. Desktop baseline activity is a timing confound, explicitly retained.

## Corrections and next gate

An initial commentary incorrectly guessed a runner/controller evidence-interface
problem before reading the complete report. The stopped case was W3/F02, not
B2/F00, and the evidence interface worked. No code was changed on that guess.

Local regression after the port fix: 94 tests PASS in 8.615s. The preceding
Windows revision passed 93 tests in 10.331s; do not present 94 as Windows-tested.
The fresh documented plan-only invocation independently returned exit 0 and
PLAN_ONLY. Neither check authenticates physical computation.

Preserve private raw bytes and source snapshots Windows-local. Partial Mac
copies live outside the publication checkout and are not a verified complete
archive. Tool v0.18 artifacts remain byte-identical to their freeze.
No manuscript efficacy claim is added from this partial batch.

Next: offline review of raw timing/observer records and backend loading logs,
then an explicit revised measurement protocol and new reservation if a rerun is
warranted. Do not silently extend T, pool failed samples or rerun missing pairs
under the expired window. The current protocol's stop condition was honored.

Correction from the subsequent source/raw audit: the observer exited on a
one-second socket timeout, before its fixed deadline. The missing lifecycle
therefore does not show deadline exhaustion. See
`ORACLE_QUIET_WINDOW_DIAGNOSIS_20261001.md`. Historical raw bytes and unknown
E_bound remain unchanged.
