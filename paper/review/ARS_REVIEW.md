# ARS internal manuscript review — v0.4

Mode: existing-manuscript completion/revision. Inline role-guided assessment
by the same Codex context that edited the paper; not independent, not blind,
not an external review or acceptance forecast.
calibration_status: NOT_CALIBRATED
criteria_binding_unavailable: future target edition not confirmed.
Criteria: ARS field-general engineering rubric; DSN 2026 format checked separately.

## Initial findings and implemented repairs

1. **Major: evidence presentation incomplete.** Prior PDF omitted paired CPU
   results and gave only Windows summary counts. Added Table I from twelve
   retained synthetic event traces and Table II from four Windows records.
   Deterministic read-only audit checks counts, unique IDs, start/finish pairing,
   report/JSONL equality and four current output-byte matches.
2. **Major: recovery scope could be misread.** Added Fig. 1 (same-run scope) and
   Fig. 2 (fresh-run F02 sequence). Both clearly distinguish inspection from
   reconciliation and avoid claiming deployment execution reduction.
3. **Major: insufficient tool-use description.** Added exporter invocation,
   interpretation workflow and explicit separation of Windows observer schema
   from normalized exporter schema. No unimplemented automated bridge is claimed.
4. **Major: evidence strength overstated by the word raw.** Existing JSONL is a
   sanitized case export, not full raw events/history. Revised limitations to
   state precisely what can be checked and what cannot be reconstructed.
5. **Minor: layout overflow.** Wrapped exporter command rather than reducing font.
   Recompiled and inspected all pages, plus the sequence figure at page resolution.

## Final criterion judgements

| Dimension | Judgement | Anchors and rationale | Residual uncertainty |
|---|---|---|---|
| Originality | PARTLY_MEETS | Introduction and Related Work claim application integration, not new exactly-once semantics; compares RSM, Temporal, tracing and fault tooling | Comparative usefulness/novelty remains a reviewer risk; selected sources are not exhaustive |
| Methodological rigor | MEETS for narrow claims | Tables I–II distinguish synthetic same-run cases from real fresh-run protocol; no population statistics | No new-run identity equivalence, crash completeness or end-to-end reconciliation guarantee |
| Evidence sufficiency | MEETS for retained-record claims | Audit verifies twelve synthetic traces and six retained Windows binding IDs; four image hashes match current product outputs | Windows raw event/history reconstruction unavailable; first F02 output bytes not checked |
| Argument coherence | MEETS | Guard benefit/cost and Windows observation scope are explicit across method, tables and conclusion | Title's recovery wording must retain its qualified meaning |
| Writing quality | MEETS with limitations | Complete abstract, method/use, results, discussion, limits, data/code and AI-use sections; two figures and two tables | Author declarations and actual venue edition remain outside technical drafting |

## Decision

Technical manuscript package completed for author review. Not submission-ready.
No unresolved evidence inflation identified in the checked claim set; this is
not a correctness certificate. Main submission risks are novelty/usefulness,
restricted artifact reproducibility, unknown final author declarations and
unconfirmed target-year rules. Extra GPU experiments are not launched to hide
these limitations. An independent human/reviewer assessment is still useful.

## Compliance and authorship

Primary software research; PRISMA-trAIce systematic-review reporting is not
applicable. RAISE principles-only advisory: evidence provenance and actual AI
assistance are disclosed; human oversight/final accountability cannot be attested
by Codex. No human-read marks or author CRediT/funding/COI statements were invented.
See AUTHOR_DECLARATIONS.md. No messages or manuscript were sent to external
review models or other people.
