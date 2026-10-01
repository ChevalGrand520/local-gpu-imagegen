# Corrected-observer Windows paired batch C

Execution source 08539d5; paired-ambiguity-v1 with corrected quiet-window
observer. Private campaign paired-windows-20261001-c, separate from A/B.
Operator explicitly approved the rerun. Reservation 11:57--12:57 UTC;
completion and cleanup occurred before expiry. No model download or rebuild.

## Runner-retained results

| Operation | Calls | Proxy POST | Upstream sends | Accepted jobs | Bound lifecycles | Original run complete |
|---|---:|---:|---:|---:|---:|---|
| B2/F00 | 1 | 1 | 1 | 1 | 1 | yes |
| W3/F00 | 1 | 1 | 1 | 1 | 1 | yes |
| W3/F02 | 2 | 1 | 1 | 1 | 1 | no |
| B2/F02 | 2 | 2 | 2 | 2 | 2 | yes |
| B2/FPRE | 2 | 2 | 1 | 1 | 1 | yes |
| W3/FPRE | 2 | 1 | 0 | 0 | 0 | no |

Runner COMPLETED, six operations, ten calls, eight proxy POSTs, six upstream
attempts. Elapsed 374.25439250003546 seconds; final checked campaign storage
46,830,269 bytes. F00 RPC intervals 35.7722965 and 24.2037979 seconds give
T=107.3168895 seconds. This is RPC latency including product/MCP overhead,
not pure GPU compute cost. Desktop activity was present and recorded.

Both W3 fault retries returned submission_outcome_unknown after the initial
backend_request_failed. Both B2 retries returned success. These fixed cases
show the submission/availability tradeoff, not a deployment rate. A bound
backend lifecycle is not independently measured physical GPU computation.
The ordinary P-stop strategy was not measured on Windows; previous CPU
equivalence remains part of the interpretation. This batch alone does not
establish superiority over all stopping policies.

## Retention and verification

The Windows private TAR SHA-256 is
141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3.
Mac TAR SHA-256 matches exactly after SFTP resume. Two interrupted transfers
were retained or superseded before validation; no partial file was audited.
`audit_paired_windows_capture.py` returned exit 0, PASS, 1,561 checks, no failed
checks. It rehashes source snapshots and raw WebSocket/history bytes, replays
event binding rules, recomputes proxy counts, compares paired input digests,
checks manifest hashes, cleanup receipts and retained client PNG hashes.
This is retained-byte consistency and event replay, not execution authentication.
The replay uses the project's binding implementation; it is not an independent
oracle. Windows-local source origins and private authenticity are not certified.
The raw package remains private and outside manuscript delivery.
Native postrun process/port query showed no Python process or 8202 listener.
The controller's advisory lock was moved to its own released-reservation
directory; unrelated desktop applications were not terminated.

Attempts A/B remain retained infrastructure/observer stops. Their counts are
not pooled into C's fixed six-operation results. The earlier interpretation
of B as deadline exhaustion was corrected in the oracle diagnosis record.
Tool v0.18 remains frozen pending a separate claim-to-evidence revision.

## Cache and claim interpretation

B2/F02 cache messages were nodes=[] for its first lifecycle and
nodes=[3,4,5,6,7,8,9] for its second. The second lifecycle reused the full
generation graph. Its extra submission and bound lifecycle cannot be described
as a second full GPU generation or a measured GPU-time saving for W3.
W3/F02 has a corroborated backend completion but an unresolved original run.
W3/FPRE has no upstream send and no backend lifecycle, but its guard still
withholds the retry. The preserved result is a submission/availability tradeoff.

Source freeze timestamp 2026-10-01T11:59:19.271147Z precedes first backend
startup at epoch 1790855966.1258285. Windows corrected-observer socket tests:
2 PASS in 1.425s. Latest local research suite: 96 PASS in 10.846s. The retained
Tool main.tex, PDF and both delivery ZIPs still match their frozen hashes.
