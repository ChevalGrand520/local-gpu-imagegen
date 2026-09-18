# DSN paired-v2 manuscript gate review

## Material Passport

- Review date: 2026-09-18.
- Review mode: evidence-bound manuscript gate; no new experiment or
  multi-model review.
- Decision: **CONDITIONAL GO / NOT SUBMISSION-READY**.
- Draft reviewed: `dsn-tool-description-draft.md` v0.1, SHA-256
  `8e05523bc4f641915f372437f067bb20f7730962c253590141db3721e514c00a`.
- Paired protocol: `paired-ambiguous-submit-v2`.
- Trusted ledger: `d8ef0bccc84269b7d4a627adce5f6025a17ab024`; contract guard PASS.
- Frozen B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`.
- W3 product fix: `d45173af75d404ad79dc14568edd4c45f654abd2`.
- Evidence boundary: deterministic CPU synthetic-worker evidence plus one
  healthy, real Windows/ComfyUI integration pilot. No real fault injection has
  yet been observed on ComfyUI.

## Gate decision

The project remains worth preparing as a DSN tool-description or tightly
bounded case-study submission. Paired-v2 materially improves the evidence: it
compares B2 and W3 under the same physical localhost response-loss mechanism,
uses the same harness bytes, and counts worker-entry events rather than POSTs.
It identifies one concrete safety/liveness trade-off in F02 single-stage:

| Observation | B2 | W3 | W3 minus B2 |
| --- | ---: | ---: | ---: |
| Backend submissions | 2 | 1 | -1 |
| Synthetic worker executions | 2 | 1 | -1 |
| Valid completion in the fixed window | yes | no | loss of completion |
| Recovery interpretation | new submission after fault | outcome unknown, blocked | conservative containment |

This is not yet evidence for a broad reliability-improvement claim. It is one
deterministic CPU arm in which W3 avoids one additional synthetic execution by
remaining unresolved. The strongest defensible paper is therefore about
**evidence decomposition and conservative containment of ambiguous
submissions**, with the observed safety/liveness cost reported as a result.

Before treating the implementation result as the central systems claim, run
the separately frozen real Windows/ComfyUI F02 single-stage pilot. A
submission-only result would still be useful, but it would not validate a
duplicate-execution claim. No acceptance probability is assigned: empirical
coverage and novelty positioning are not strong enough to support a calibrated
probability.

## What the current evidence supports

| Claim | Gate status | Evidence-bound wording |
| --- | --- | --- |
| Reported, interpreted, and oracle states are separated | supported | The research exporter preserves the three layers and records versioned mapping reasons. |
| Unknown or contradictory oracle evidence is not promoted to verified execution | supported at component level | Exporter regression tests cover missing, unknown, mismatched, contradictory, and exactly bound evidence. |
| POST count is not used as execution count | supported in the research harness | Worker-entry events carry unique synthetic execution-instance IDs. This is not a real backend oracle. |
| W3 contains an ambiguous single-stage submission | supported at product/component level | A transport-marked unknown submission is persisted and another submission through the same run is blocked. |
| W3 reduces repeated work under F02 | supported only for one paired synthetic arm | W3 produced one fewer submission and one fewer synthetic execution than B2, while losing valid completion in the observation window. |
| Known-job two-stage completion can be reconciled | supported, but pre-existing | F03 two-stage uses the same known job with one submission and one execution in both B2 and W3. |
| The stack can complete a real ComfyUI run | supported as a single integration demonstration | One scheduled Windows/RTX 5070 Ti two-stage run generated an unreviewed artifact; no fault was injected. |

## Claims that must be narrowed

1. **Recovery is not complete.** W3 does not discover or reconcile an unknown
   backend job. It records uncertainty and blocks another submission in the
   same run. The title and conclusion should prefer “handling,” “containment,”
   or “evidence-bound ambiguity” over an unqualified “recovery” claim.
2. **The execution oracle is independent of product state, not operationally
   independent infrastructure.** The CPU oracle is an in-process research
   observer attached to the fake worker entry. Describe this scope every time
   it is used to support an execution count.
3. **The result is a trade-off, not a monotonic improvement.** The only changed
   execution-count arm also changes valid completion from true to false. Both
   outcomes belong in the abstract, result table, and discussion.
4. **One healthy Windows pilot is not cross-environment reproducibility.** It
   demonstrates compatibility with one frozen client/backend/model/workflow
   configuration. It does not establish deployment reliability, visual
   quality, performance, or fault semantics.
5. **The guard has a bounded ownership scope.** Current evidence covers another
   call through the same run. It does not prove global deduplication across new
   runs, alternate clients, process loss, or direct backend access.

The following statements are not supported and should not appear without new
evidence: exactly-once execution, server-side deduplication, automatic recovery
of unknown jobs, a deployment duplicate-execution rate, a deployment failure
rate, production readiness, or net reliability improvement.

## Draft-specific review

### Abstract and title

The draft is disciplined about synthetic versus real evidence, but its title
and final abstract sentence imply more recovery capability than implemented.
Rename the paper around ambiguous-submission evidence or containment. Replace
“reproducible integration path” with “one version-bound integration
demonstration” unless a second independent reproduction is added.

The abstract should include the paired result and its cost, rather than only
stating that fault coverage exists. A defensible result sentence is:

> In one deterministic F02 single-stage arm, W3 blocked the protocol's second
> submission and reduced synthetic worker starts from two to one, while the run
> remained unresolved instead of producing a valid completion within the fixed
> observation window.

### Contributions

Contributions 1 and 2 are supported as research-tool contributions.
Contribution 3 should say “guarded containment” rather than “recovery path” and
remove the remaining `VERIFY` marker after the exact tested SHA is cited.
Contribution 4 should separate the reproducible CPU artifact from the single
real integration demonstration.

### Evaluation

The evaluation section needs an actual paired results table, not only a plan.
F00 must remain outside fault/injection denominators. For F02/F03, report all
denominators and explain that `failed` is product-attempt status and can overlap
`unresolved`.

| System/layer | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B2 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| B2 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 2 | 0 |
| W3 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| W3 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 1 | 0 |

F02 two-stage, F03 single-stage, and F03 two-stage show no execution-count
improvement under paired-v2. State these null results explicitly. Retain the
invalid paired-v1 files as negative evidence and exclude them from every result
denominator.

### Related work and venue fit

Novelty remains unreviewed. The working reference placeholders are not enough
for submission. A bounded literature pass must distinguish this artifact from
idempotency keys, transactional outbox/workflow recovery, uncertain commit
outcomes, retry safety, and fault-injection observability. Venue/category fit
must also be checked against the official call used for the actual submission
year; this review does not infer category rules from an earlier call.

## Readiness gates

| Gate | Current state | Required evidence |
| --- | --- | --- |
| Contract and provenance | pass | Keep the ledger anchor, B2/W3 SHAs, harness hashes, and invalid-run record in the artifact. |
| Component semantics | pass for bounded scope | Preserve exporter and paired-harness regression tests. |
| Paired CPU comparison | pass | Report the safety/liveness trade-off without deployment-rate language. |
| Real F02 semantic check | pending | Run one predeclared B2/W3 single-stage F02 comparison only if an independent backend execution oracle is evaluable. |
| Manuscript claims | pending | Revise title, abstract, contributions, evaluation, and limitations to the wording above. |
| Novelty and citations | pending | Complete claim-linked literature review and verify every reference. |
| DSN submission rules | pending | Verify current official category, page limit, artifact, registration, and presentation requirements. |

## Decision after the real pilot

- If backend-origin events bind each accepted request to a distinct execution
  start and finish, and the paired behavior matches the frozen hypotheses, the
  paper gains one real case-study validation of the core F02 semantics. It may
  still claim only a version-bound case, not a rate.
- If the oracle distinguishes submissions but not execution starts, report
  duplicate submission only. Keep execution counts unknown and do not infer
  them from prompt IDs, POSTs, or artifact count.
- If W3 blocks another submission but the first execution cannot be reconciled,
  retain the liveness limitation as a first-class result.
- If B2 and W3 do not differ, preserve the negative result and refocus the paper
  on evidence correctness and ambiguity preservation.
- If the oracle or identity checks fail, stop the execution experiment. Do not
  replace the missing real evidence with additional synthetic repetitions.

The unique next empirical step is the reviewed Windows/ComfyUI F02
single-stage pilot. Broader matrices, repeated-rate estimation, F03 reruns,
visual-quality studies, and product changes are outside this gate.
