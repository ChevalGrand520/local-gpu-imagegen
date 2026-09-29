# DSN Tool: next evidence gates (2026-09-29)

This is an execution plan, not a report of new Windows observations. The
current manuscript is `paper/main.tex`; the current exporter mapping is
`research-normalization-v3`. Historical W2 records and earlier demo archives
retain their original v2 meaning.

## Completed without a new backend campaign

1. `tests/research/test_export_records.py` checks that deleting the reported
   run state cannot promote an unresolved record to composite verification and
   that manifest job/artifact identities conflicting with selected top-level
   fields yield `evidence_state=mismatch`.
2. `paper/scripts/verify_reviewer_demo.py` normalizes the twelve retained B2/W3
   CPU product manifests with their existing fixture oracle records. No new
   artifact validator is supplied, so all twelve remain
   `execution_verified=false`. This checks the exporter against actual retained
   product-control-path records, but the CPU backend is synthetic and the
   original events are not replayed.
3. The new anonymous offline demo candidate includes these checks. It is not
   a Windows experiment or a certified anonymous submission artifact.

## Gate W: same-run guard observation on Windows

The existing F02 research client calls `local_gpu_start_run` on every invocation
and uses `seed=4100+call_index`. Its second invocation therefore cannot measure
the old run's guard. Before a new campaign, add an explicitly named same-run
mode that retains the first private `run_id` inside the Windows research harness
and sends the second `local_gpu_generate_round` through that exact run. Use the
same pinned endpoint, model, request plan, seed and idempotency key for both
attempts. Do not substitute a new run or change the request while measuring the
guard.

The first accepted `POST /prompt` must have its response suppressed by the
reviewed F02 shim. Before the second call, persist the original run manifest
and confirm an unresolved attempt with
`submission_outcome=unknown` and no durable backend job ID. Stop the case if
this state is absent, if the first proxy acceptance is not unique, or if the
observer cannot bind the first execution. After the second call, retain the
stable product error code, manifest revision, proxy receipts and observer
decision. Guard-block evidence requires the same private run ID, a product
`submission_outcome_unknown` rejection and **zero additional proxy-observed
POSTs**. A bound first execution does not by itself prove the original run was
reconciled or that the operation will eventually complete.

Keep raw WebSocket messages and history snapshots, or a replayable sanitized
equivalent with hashes and redaction rules, alongside derived event counts and
unique execution-instance bindings. This is needed to investigate the prior
`execution_start=3` versus two-binding discrepancy. Preserve each event's
backend boot identity, prompt/job identity, timestamps and snapshot index;
record cached-node messages separately from execution-start bindings. Do not
infer physical GPU work from a lifecycle event alone.

This gate is one controlled scope check. It yields no deployment failure rate,
natural duplicate-execution rate or model-general result. Any B2 comparison
must use an explicitly matched same-run protocol and state its completion cost.

## Gate X: Windows observer to exporter

The present Windows audit contains derived bindings but no complete original
product manifest plus raw observer stream for the exporter. Once Gate W captures
those inputs, define a versioned conversion that retains raw source fields,
selected job/artifact identities, independent validator provenance and mapping
reasons. Include a case with a deliberately missing field and one with an
identity conflict. Re-run the exporter and the retained-evidence audit offline
from a clean extraction. Report any remaining `partial`, `missing` or `unknown`
state explicitly; do not add an independent validator assertion merely to
obtain `execution_verified=true`.

Only after Gates W and X are checked should the manuscript claim a live
same-run guard observation or a Windows end-to-end evidence export. Until then,
the current bounded CPU and Windows results remain the paper's empirical scope.
