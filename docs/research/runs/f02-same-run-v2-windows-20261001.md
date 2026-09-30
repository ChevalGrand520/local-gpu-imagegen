# Windows same-run v2 follow-up — 2026-10-01

The user explicitly requested continued autonomous work after the v1 stopped
result. Source inspection found that every product call starts a fresh MCP
process, but v1 rebuilt the pinned portable-model inventory only on call one.
Discovery inventory is process-local. ModelCatalog.verify_locked_route runs
before the submission guard. This is a supported masking explanation, not
proof that model bytes changed or a complete reconstruction of the old error.

The research caller now repeats the existing exact-file index/fingerprint and
private catalog checks on both calls. Frozen W3 code, original run, seed,
operation key and complete generation arguments are unchanged. Product locked
route validation remains active; no bypass or product repair was added.
Protocol identity is same-run-guard-v2. CPU research tests: 61 passed on Mac
and 61 on Windows. Runner source a8e58eb. New private roots keep old captures.

The first v2 launcher attempt (root suffix b) returned CONFIG_ERROR because its
runner still emitted v1; it finished in about eight seconds without a campaign
capture. The runner was corrected and a fresh root suffix c launched. Both
attempt receipts and logs are preserved; this is not a successful experiment.

Cache behavior remains observable rather than controlled. A lifecycle binding
must not be promoted to physical GPU computation or natural duplication rates.

## Actual result

Campaign c COMPLETED, exit 0; reservation start 2026-09-30T17:52:08Z
(2026-10-01 01:52:08 Asia/Shanghai), finish 17:53:48Z. Preflight PASS.
F00: C/S/E=1/1/1, resolved. F02: 2/1/1, unresolved/unresolved; retry error
submission_outcome_unknown, guard_observed=true. Complete arguments and run ID
match. Original manifest remained unresolved, submission unknown, with no job;
retry before/after bytes match. No third call or fresh-run fallback.

Offline retained-byte audit PASS: raw WebSocket counts 90/10, history 1/1,
start 1/1, node-null terminal 1/1, bindings 1/1. F02 cached event 1, progress 0.
This establishes one fixed-case guard rejection and no additional proxy POST,
not physical GPU savings, eventual completion, or deployment frequency.
Post-run live check: Python processes 0 and port 8202 listeners 0.
Public report SHA256 5e29a4c0d9c9b592aa648c4ad50430e1225d09eb0676abbeee412595e40f0506.

## Offline exporter bridge

Version windows-capture-conversion-v1 first requires the raw audit, then maps
the retained manifest separately from the bound lifecycle decision. Full source
fields and source hashes remain in a private export; public output contains
interpretation and mapping reasons only. No independent artifact hash or
validator assertion was added. F00 is succeeded/partial/not_needed; F02 is
succeeded/missing/recovery_required. Both execution_verified=false. Two missing-
state and two selected-job-conflict variants are synthetic stress checks, not
Windows experiments; conflicts map to mismatch. Clean-copy reproduction and
input-byte immutability passed. Gate X has an offline prototype and retained
result, not a public raw-data reproducibility or fully verified execution claim.
