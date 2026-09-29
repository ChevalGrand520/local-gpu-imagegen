# DSN writing findings — 2026-09-27

Evidence source: 5cd100f2b4a4a7aaeac1fd707fc248bae46f239c.
ARIS judgment: partial / same-family / provisional.

The new Windows report supports observing executions despite first-call
ambiguity. It does not show W3 reducing executions: both F02 cases are 2/2.
The harness starts a new run and changes seed for the second call. Original-run
reconciliation is unestablished. The any-call aggregation and the report's final
case table use conflicting unresolved semantics; preserve the source and flag it.

Nature-writing was used for argument-first drafting, terminology consistency,
result allocation and explicit evidence gaps with generic DSN framing. ARIS
result-to-claim supplied a bounded secondary judgment and deterministic source
existence checks. No changes to product, experiments or historical run records.

Next work: resolve existing-evidence provenance/aggregation, complete nearest-tool
literature comparison, verify target-year DSN format, then remove only closed
internal annotations. New experiments remain outside this writing task.

## v0.3

Windows retained report inspection resolves G01 at field level: overlapping
resolved=4 and unresolved=2. Test log provenance distinguishes early Windows
40 tests from later macOS 7 targeted tests. Source hashes at historical test time
remain unverified. Related work adds Temporal, OpenTelemetry and Toxiproxy from
official documentation; no experimental comparison or exhaustive novelty claim.
This revision was locally checked, not re-reviewed by the v0.2 secondary agent.
