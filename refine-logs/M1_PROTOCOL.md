# M1 CPU protocol freeze (2026-09-28)

Approval: user approved M0/M1 implementation and CPU validation only. No GPU.
Product source: P-retry uses native B2 da65d57047b5a59e3403b49adf4605a1c0497c58; P-stop and P-guard use W3 d45173af75d404ad79dc14568edd4c45f654abd2. Each source is extracted from Git into a temporary checkout; no product files are patched. Their own test fixtures supply fake models and CPU PNG writers.

Protocol clarification before execution:
- The 3 schedules are ordered driver barriers: complete first job before recovery intent; complete after intent but before product entry; complete after the one permitted recovery call. These are deterministic order coverage, NOT concurrent race testing or three independent statistical repetitions.
- Healthy and never-accepted cases have no outstanding first job; the schedule is then a no-op and is identified as such.
- Single-stage product requests have no backend-job callback; F03 therefore distinguishes observer-known ID from product-persisted ID. Only two-stage F03 can establish actual known-job recovery.
- P-stop inspects the product manifest and skips same-run generation only when its latest attempt explicitly records submission_outcome=unknown. Otherwise it uses the same generate_round entry. New-run scope probes bypass the original run for all three strategies, explicitly outside the stop/guard scope.
- All policy decisions use manifests, never observer results. The fixed scheduler may complete a worker at a barrier regardless of policy.
- Explicit pre-acceptance failure is a synthetic reject response; unknown-before-acceptance is a dropped localhost response without invoking the CPU worker. Accepted-loss queues a worker before dropping the response.
- Executions are counted at actual CPU fake-worker entry, not at queueing or POST. Completion additionally needs retained artifact hash and terminal/history fields. This schema is a research CPU ledger, not a ComfyUI raw payload schema.
- Total 72 cases: 45 B1; 18 B3 scope; 9 B3 two-stage F03. Maximum one recovery call per operation. Health failure or invalid complete ledger stops the campaign with its partial output retained.
- B0 maximum 24 hand-constructed records; expectations are specified independently of the audit function. This is correctness checking, not an empirical false-positive-rate estimate.
- Runtime cap 30 minutes; evidence cap 1 GiB; isolated temporary roots; no external model/provider calls.

These clarifications narrow the earlier planning language. Original EXPERIMENT_PLAN timestamped version stays unchanged. All deviations and incomplete gates will be reported.
