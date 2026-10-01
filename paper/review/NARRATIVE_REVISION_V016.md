# Narrative revision, v0.16

The author requested a less mechanical abstract, an operational Section III.B,
a shorter limitations section and a conclusion expressing the design choice.
This is an editing record, not an independent review or detector evaluation.

- Abstract: describes the response-loss problem and the observed retry path;
  per-case binding counts remain in the results instead of being repeated here.
- Section III.B: follows inspection, evidence association, export and reading
  the record. Necessary conditions are integrated into those actions.
- Section V: consolidates overlapping scope statements. Its whitespace-delimited
  source word count falls from 396 in v0.15 to 195, a reduction of about 51%.
- Conclusion: explains why we keep the recovery decision attached to the
  original run, using the revised Windows case as the concrete example.

Detailed historical audit coverage, observer boundaries and converted-state
outcomes are retained in `evidence/REPRODUCIBILITY_SCOPE.md`. The main text still
states the historical raw-event gap, constructed terminal label, incomplete
artifact coverage, synthetic variants and false composite verification.
The cached-node evidence and the possibility of an unbound historical start
remain in the main results. No adverse experimental finding was removed.

Citation occurrences, figure/table blocks and inline technical identifiers are
unchanged. Code, retained measurements, source snapshots and the anonymous
v0.5 demo are unchanged. Current compilation checks are in `compile-report.json`.
The author archive remains private. This revision does not change submission
readiness or establish an AI-detector score.
