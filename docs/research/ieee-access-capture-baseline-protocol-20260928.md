# IEEE Access capture and equal-information baseline protocol

Status: design only, 2026-09-28. **No new CPU/GPU run, model download, or measured result is authorized by this document.** It turns the [evidence map](ieee-access-evidence-map-20260928.md) into a reviewable next campaign design. The present DSN records must remain historical and cannot be relabeled as outcomes of this protocol.

## Research decision and units

The proposed claim is narrow: a versioned evidence contract may improve the *supportability* and cost of deciding whether an ambiguous **original run** completed. A deterministic contract cannot claim an accuracy advantage over a competent script given identical observations and the same rules. The study must separately test capture/provenance, audit effort, and operational decisions.

Freeze five distinct identities: `operation_id` (one user intent), `run_id` (one persistent product run), `call_id` (one client invocation), `product_attempt_id` (the durable attempt inside a run), and `submission_id` (one proxy-observed backend POST). `run_id` and `product_attempt_id` are established before a submission; `submission_id` is assigned only if a POST reaches the proxy. Record `request_digest`, seed, workflow digest, backend boot identity, and observer session ID. A new run or changed seed is a different treatment path even if it shares `operation_id`. Distinct proxy POST receipts are submissions; distinct start/terminal/history bindings are observed executions. No sum of cumulative snapshots is an execution count.

## Append-only capture contract (proposed)

| Record | Minimum fields | Capture owner and boundary |
|---|---|---|
| Invocation | Operation, run, call and product-attempt IDs; run state before/after, request/seed/workflow digest, monotonic and wall-clock times, exit/error classification | Product client; snapshot manifest bytes and SHA-256 before and after each call |
| Proxy receipt | Submission ID with the four parent identities, sequence, request-body SHA-256, forward status, accepted job ID in private ledger, response suppression flag, timestamps | Loopback proxy; write before telling the controller that a submission occurred |
| Observer event | Observer session, monotonic receive sequence/time, event type, prompt/job ID, relevant payload or loss marker | Backend-facing WebSocket observer; append once per frame, preserving raw and sanitized versions separately |
| History snapshot | Prompt ID, query time, full response digest, completion flag, artifact references, snapshot sequence | Read-only backend history capture; never replace an older snapshot in the research ledger |
| Product artifact | Run/attempt ownership, output path digest, byte SHA-256, read time, availability and validator version | Product plus separate read-only validator; distinguish recorded hash from fresh rehash |
| Guard decision | Guard entry point, unresolved-attempt identity, input request digest, allow/block result, reason and durable state after decision | Instrumented product entry; do not infer a guard event from absence of a POST |
| Independent answer key | Acceptance, bound execution, original-run completion, additional-submit permissibility, each with supported/unknown and evidence pointers | Frozen observer/proxy/manifest ledger reviewed independently of exporter output |

Each record needs schema version, source commit, backend/version identity, append sequence, and a content digest. Missing fields are explicit `missing` with a reason; absence is never converted to false. Keep private IDs and raw payloads locally if release constraints require it, but publish a deterministic sanitized mapping and explain what cannot be independently reconstructed. A final ledger must include scheduled, attempted, stopped, and unevaluable cases.

## Conditions to predeclare before a campaign

| Condition | Expected discriminating observation | Stop/unknown rule |
|---|---|---|
| F00 normal | One accepted POST, one bound execution, original-run completion | No binding or artifact proof => unevaluable, not successful |
| F02 accepted, response lost, same run | First response hidden; guard entry attempted on the **same** `run_id` and request; record whether it blocks and whether original run later reconciles | Do not call new-run completion original-run recovery |
| F02 accepted, response lost, new run | Separate run/seed and attempt; measures resubmission path only | Keep separate from guard efficacy denominator |
| No acceptance but client sees unknown | Independently prove zero accepted jobs while body-bearing transport error marks unknown; exercise same-run guard | If independent no-acceptance proof is missing, false-block outcome is unknown |
| Delayed/lost/duplicated observer event | Preserve raw event sequence and explicit observer gap; compare binding rules | If start/terminal/history cannot be paired uniquely, execution answer is unknown |
| Process restart | Preserve durable manifest and observer/proxy ledger identity across restart | Missing pre-restart chain => reconciliation answer is unknown |

These are proposed conditions, not completed tests. The existing `f02_campaign.py` deliberately waits for the first bindable completion before a second call and `f02_product_client.py` creates a fresh run with `seed=4100+call_index`; it cannot be reused unchanged as a same-run guard experiment. `f02_oracle.py` retains `raw_events` in memory, while `_sanitize_oracle` sums each decision's cumulative event list. A future collector must write event frames once with stable sequence IDs, preserve per-decision snapshot boundaries, and derive unique bindings from IDs. The product backend adapter marks a body-bearing transport failure `submission_outcome=unknown` even when actual acceptance may be zero, which motivates the no-acceptance condition.

## Fair comparison and outcome sheet

Create an immutable captured event set and an answer key **before** exposing results to evaluators. Three views answer the same predeclared questions: (A) product-state-only, with its intentionally smaller observation set; (B) full logs/traces plus a competent, documented audit script; (C) the evidence contract/exporter. B and C receive exactly the same admissible observations, timestamps, IDs, and missingness. Give B sufficient implementation time to reproduce sensible decision rules. Do not compare C with an intentionally weak grep or a manually blinded reviewer.

For each case and view, record four-valued answers (`supported_yes`, `supported_no`, `unknown`, `unsupported_assertion`) for acceptance, execution binding, **original-run** completion, and submit permission. Separately record audit time, manual interventions, additional submissions, distinct execution bindings, original-run completion, false blocks, and unevaluable cases. Predeclare how disagreements are resolved against the independent answer key; an `unknown` should not be scored as a wrong yes/no. Report raw counts with denominators by condition, not a natural deployment rate. A population-rate claim would require a separate sampling design.

## Pre-execution gate

1. Review the observer/proxy independence and privacy of the raw ledger, with a dry-run on invented fixtures only if separately authorized.
2. Freeze scenario schedule, seeds, request digests, expected stop rules, version identities, cost ceiling, time ceiling, and cleanup owner before resource use.
3. Review a complete source diff to ensure same-run guard calls are real product entries and that instrumentation does not change backend semantics.
4. Get a separate explicit decision for any GPU/backend campaign or model acquisition. If the equal-information full-log baseline matches contract decisions and no capture/provenance/usability advantage remains, stop Access expansion and keep the DSN Tool scope.

No publication claim or Access Results section should be drafted from this design alone.
