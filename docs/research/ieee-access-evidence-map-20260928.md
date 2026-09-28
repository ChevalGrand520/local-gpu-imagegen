# IEEE Access evidence map and fair baseline

Status: preparation, 2026-09-28. Existing records only. No new campaign is described here as completed.

## Candidate article type and question

The likely type is **Applied Research** under the [IEEE Access submission guidance](https://ieeeaccess.ieee.org/authors/submission-guidelines/). That category expects quantitative validation of a practical solution. A **Methods** article would require a new or improved measurement technique; the current exporter has not demonstrated such a method beyond a competent log audit.

Question: For an ambiguous local generation submission, can an evidence contract improve the correctness or efficiency of an operator's decision about the original run while preserving uncertainty when backend observation is incomplete?

The question is deliberately conditional. If identical evidence with a well-written audit script gives the same answers at comparable cost, the manuscript should describe a useful tool, not a superior research method.

## Frozen units and variables

| Variable | Definition | Existing evidence | Missing for journal claim |
|---|---|---|---|
| Logical operation | One user-intended generation, separate from product run | CPU fixtures use operation keys | Windows F02 second call changes run and seed; same intent cannot be assumed |
| Product run | Persistent state inspected after a call | CPU manifests and Windows client classifications | First F02 Windows run's full retained manifest is unavailable in published extract |
| Submission | Proxy-observed backend POST, not every client invocation | Windows F00: one per case; F02: two per case | Complete per-attempt request identity for fair cross-run comparison |
| Backend execution | Distinct bound observer instance or CPU worker entry | Six retained Windows binding IDs; synthetic CPU entry events | Complete raw Windows event/history snapshots and independent GPU execution witness |
| Original-run completion | Durable completion of the run that received the ambiguous submission | CPU F02 single-stage W3 remains incomplete | Controlled Windows same-run recovery/guard case |
| Artifact | Product content hash with host-side receipt | Four resolved-call byte-match receipts | First unresolved F02 calls lack product artifact hashes; visual quality unmeasured |
| False positive | Declaring original run completed without sufficient retained evidence | Exporter unit tests and two synthetic demo records show some veto cases | Independent, predeclared answer key across fault cases; original records may be incomplete |
| False block | Guard refuses a new submit when first attempt provably was not accepted | Conservatism follows source rule | Controlled no-acceptance unknown case with actual product entry and outcome proof |

No cell above is a deployment frequency or natural duplicate-execution rate. The 40 historical CPU tests and 4 Windows cases are coverage/provenance, not random samples.

## Equal-information baseline protocol

1. Freeze one raw event set per operation before any policy sees it. Include original run ID, call/attempt ID, request/seed, proxy receipts, backend event payloads/history and product manifest. If a field is missing, the missingness itself is recorded.
2. Give **product-state**, **full logs/traces plus a competent audit script**, and **versioned evidence contract** access to the same admissible observations. Only the product-state view intentionally omits backend logs; it answers a different information question. The full-log baseline must be allowed to implement the same sensible decision rules as the contract.
3. Define target questions before running: Was POST accepted? Is execution bound to the original operation? Did the original run complete? Is an additional submit permitted under the policy? Ground truth for each question comes from a separately captured observer/manifest ledger, never from the exporter being evaluated.
4. Score each answer as supported positive, supported negative, unknown, or unsupported positive/negative. Record the cost of obtaining the answer, additional submissions and incomplete operations. Unknown is a valid result, not an error to hide.
5. Compare paired operations under identical seeded workflow and fault schedule. Separate same-run behavior from deliberate new-run requests. Failures to capture the answer key stay unevaluable and in the denominator ledger.

This protocol still needs source/observer trust and an independent implementation review before use. A Python script reading the same snapshots can reproduce any deterministic mapping; potential value would have to appear in reliable capture, durable provenance, operator workflow, or lower decision cost, each with its own measurable test.

## Present result-to-claim disposition

| Candidate claim | Current disposition | Reason |
|---|---|---|
| The exporter preserves reported state and versioned interpretation | Supported as implementation | Source and unit checks; two runnable synthetic examples |
| The offline audit rechecks retained derived records | Supported within retained-record scope | Clean extracted demo passes; historical host receipts are not revalidated |
| W3 blocks a second same-run submission after explicit unknown | Supported by source and synthetic CPU fixture | Windows second F02 call creates a new run |
| W3 lowers duplicate execution in a real backend | NOT RUN in the guard's Windows scope | Both Windows F02 conditions have two submissions and two bindings |
| The contract beats an equal-information log audit | NOT RUN | No fair baseline or independent answer-key study |
| The tool lowers deployment failure rate | NOT RUN | No population or naturalistic denominator |
| The tool authenticates oracle provenance | Unsupported | Supplied oracle/validator flags are trusted inputs |

## Gate to the next work unit

The next authorized preparation is a code-level capture and baseline design with predeclared expected outcomes; execution of a new CPU or GPU campaign is a separate work unit. If the equal-information baseline reproduces all decisions and no distinct capture or usability gain emerges, stop Access expansion and retain the DSN Tool article. IEEE Access's continuous intake does not relax its evidence requirement, and simultaneous submission of substantially the same manuscript is excluded.
