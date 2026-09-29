# Response to independent review v0.5

The independent review was read after the v0.5 package was prepared. It was
unattributed DeepSeek-harness output with explicit file coverage and a temporary
script replay. It was not treated as independent human review or as an editor
decision.

## Accepted corrections

- The retained export reports cumulative `execution_start=3` in each F02 case,
  while two execution bindings are retained. The manuscript now reports both
  fields and calls the latter **retained execution bindings**. It does not use
  cumulative snapshots as execution totals. The source explains the aggregation: cumulative snapshots recount earlier
  events. Original snapshot payloads remain unavailable for re-audit.
- The terminal discriminator is not retained. The audit's `terminal_event ==
  "executing"` check is a self-consistency check on the derived record, not an
  independent payload-level completion proof. The manuscript now says this
  explicitly and downgrades the oracle claim.
- F02 unresolved calls have no artifact hash. The manuscript retains the
  coverage limitation and does not imply artifact verification for those calls.
- Fresh-run and changed-seed details are implementation/report claims, not
  independently verifiable from the review packet. They remain qualified and
  are not presented as evidence of identical-request non-duplication.
- Historical 40/7 test outputs are provenance records, not reproducible from the
  external packet. This remains an explicit limitation.

## Findings not adopted as demonstrated errors

- `execution_start=3` does not prove a third distinct execution. The retained
  export lacks per-snapshot boundaries and payloads. The source-level aggregation explains why the count can exceed bindings;
  it is not converted into a third execution count.
- Two of six calls, not three, lack product artifact hashes: the first unresolved
  call in each F02 case. Four byte-match receipts cover two distinct hashes.
- Identical F02 output hashes do not prove cache reuse or same-seed execution.
  The package does not retain enough preimage data to make that inference.
- Absence of original host files from the external review packet is a package
  boundary, not evidence that the original campaign files never existed.

## Result

The paper's claim is narrowed to the evidence that survives this review:
versioned state separation, scoped same-run blocking, and a retained observation
channel with unresolved binding limitations. The review does not authorize a
new experiment. A future campaign would need payload-level terminal evidence,
per-call run/seed identity, and complete artifact coverage before stronger
Windows claims could be made.
