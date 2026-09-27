# DSN Tool Description outline — v0.2

Date: 2026-09-27. Working manuscript, not submission-ready.
Evidence baseline: `5cd100f2b4a4a7aaeac1fd707fc248bae46f239c`.
Claim authority: [matrix](dsn-tool-description-claim-evidence-matrix.md).

## Argument

In local image-generation pipelines, reported submission ambiguity can coexist
with observed backend completion. The tool preserves that distinction through
versioned export, a scoped same-run guard, and controlled execution observation;
the Windows demonstration does not establish automatic reconciliation or an
execution-count advantage for W3.

## 1. Introduction: problem, established semantics, tool question

- Open with lost acceptance response and the resulting unknown job ID.
- Attribute uncertainty and idempotent retry concepts to RPC/idempotency work.
- Ask what evidence permits a statement about submission, execution, or recovery.
- Contributions: evidence representation/export; bounded recovery guard;
  instrumented fault demonstration. Novelty remains pending nearest-tool review.
- Claims C01–C06, C21. Avoid universal novelty and reliability claims.

## 2. Failure model and evidence units

- Define product call, run, submission, execution instance and artifact evidence.
- F00 is control; F02 loses acceptance response; F03 is known-ID completion loss
  in CPU fixtures only.
- Separate product manifest, research-client label and backend observation.
- Explain that matching job/request identifiers does not establish deduplication.
- Claims C06, C08–C13, C16–C18.

## 3. Tool design and workflow

### 3.1 Evidence-preserving export

Input records → preserved reported state → versioned interpretation with reasons;
separate oracle and artifact evidence. Explain unresolved verification veto.
Do not promise global path-security guarantees or automatic evidence completion.

### 3.2 Same-run recovery boundary

RunStore and AssetRunEngine mark explicitly unknown submission unresolved and
block the reviewed same-run entry points. Inspection remains possible.
Known-job two-stage recovery is existing separate functionality.

### 3.3 Research-only observation and injection

Prompt transport shim retains endpoint identity; loopback proxy drops the first
accepted response. Observer subscribes before submission using matching client
ID and requires backend events plus history. Controller gates the second call.
Show a small architecture schematic and identify research versus product parts.
Fresh run, changed seed, and lack of automated reconciliation stay in main text.

## 4. Evidence and demonstration

### 4.1 CPU component and synthetic evidence

Report historical 40-test result with Python 3.15.0a8 provenance and G02 caveat.
Describe F00/F02/F03 fixtures without converting test count to statistical n.
Keep older paired CPU differences separate from live Windows observations.

### 4.2 Controlled Windows F00/F02 cases

One table: B2/W3 × F00/F02; submissions, observed execution instances,
first/second research-client labels, oracle-evaluability.
Recorded B2/W3/backend identities go into reproducibility notes.
4/4 case evaluability and 2 injected cases are coverage counts.

### 4.3 What resolution means

Explain generated→resolved mapping, original unresolved run not reconciled,
seed changes and digest limitation. Mark G01 aggregate discrepancy visibly;
do not publish an unresolved=0 or success-rate aggregate.

## 5. Reproducibility and limitations

- Source identity, exact report provenance, intended CPU reproduction commands.
- Raw Windows JSONL/configs/images/models stay local; sanitized release pending.
- Hash/path-fingerprint distinction, backend-origin oracle trust and event loss.
- No new GPU work, downloads or experiments in this writing revision.
- Remaining gaps G01–G06; no visual, speed or model-generalization claims.

## 6. Related work and discussion

RPC uncertainty and caller-token idempotency are prior concepts. Position the
tool's evidence/export/observation workflow relative to these concepts.
Mark nearest fault-injection, workflow/reconciliation and tracing comparison as
incomplete; do not imply an exhaustive survey or superiority.
Interpret the contrast between scope-limited guard and fresh-run Windows path.

## 7. Conclusion

Evidence-preserving observation is supported within the fixed protocol.
Automatic unknown-job reconciliation and deployment-wide reliability remain
unestablished. No new numbers or promises.

## Result allocation and paragraph plan

| Evidence | Function | Placement | Paragraph job |
|---|---|---|---|
| Distinct client and backend outcomes | Core finding | Abstract, §4 table | Result |
| Export and same-run guard | Necessary support | §3 | Mechanism |
| 40 historical tests | Component support | §4.1 + provenance notes | Support with boundary |
| Windows B2/W3 equal counts | Conclusion-changing qualification | §4.2 and discussion | Comparison |
| Fresh runs, seeds, G01 discrepancy | Conclusion-changing qualification | §4.3 | Limitation |
| SHAs/runtime/harness details | Provenance | §5, matrix | Reuse |
| Old CPU paired differences / old successful pilot | Historical context | Existing evidence map only | Keep protocols separate |

Shortest evidence chain: explicit ambiguity → separate observation → controlled
case counts → fresh-run qualification → scoped tool conclusion.

## Release gates

- [ ] Reconcile G01 using existing raw evidence and explicit aggregation schema.
- [ ] Resolve G02 test invocation and final-shim provenance.
- [ ] Review a sanitized raw evidence bundle; do not equate summaries with raw audit.
- [ ] Complete nearest-tool comparison and verified references.
- [ ] Verify target DSN year, page/category rules and format.
- [ ] Complete clean-checkout reproduction when authorized; current writing adds no experiment.
- [ ] Human author reviews interpretation, attribution and availability statements.

These are manuscript gaps, not authorization to run further experiments.
