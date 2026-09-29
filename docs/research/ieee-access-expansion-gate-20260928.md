# IEEE Access expansion gate

Date: 2026-09-28. Status: preparation started; no Access manuscript or new results claimed.

## Decision

Start an IEEE Access research track in parallel with the existing DSN Tool draft. Do not submit the six-page Tool text as a journal paper or inflate it with background prose. The first deliverable is a testable research question and evidence plan. A full Research Article or Applied Research manuscript follows only if the evidence gate passes.

The journal [submission guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/) accept Research Articles and Applied Research articles. They describe Research Articles as having an investigation, solution and result of value, and expect quantitative validation for Applied Research. A Methods article requires a new or improved experimental, measurement or mathematical technique; the current exporter has not established that distinction. Exposition is a theoretical interpretation article, not a shortcut for this tool report.

## Proposed journal question

When a local generative pipeline loses a submission response, which retained evidence is sufficient to say that a specific run completed, which evidence only supports backend execution, and which states must stay unknown? Can a versioned evidence contract reduce unsupported positive recovery claims at a measurable completion/blocking cost?

The question is provisional. The current exporter interprets supplied records and trusts their provenance. A full-log-plus-audit-script baseline could implement the same rule on the same data. The journal contribution must show an additional capability, lower error risk, or demonstrable operational value relative to that baseline; different JSON formatting alone is insufficient.

## Minimum evidence before writing a full journal Results section

1. Specify the unit of analysis (logical operation, run, call, backend execution), fault barriers, trust assumptions and independently collected answer key. An event count or client status is not ground truth for execution.
2. Compare at least three honest views with equal underlying observations: product status, full logs/traces plus a competent audit script, and the proposed evidence contract. State which questions each view can answer, including cases where all views must return unknown.
3. Exercise the same-run guard in a real backend campaign and include a controlled no-acceptance unknown case. Report submissions, distinct bound executions, completion of the **original** run, false blocking, and missing evidence together. New-run retries remain a separate scope condition.
4. Preserve per-call run/seed identity and raw event/history snapshot boundaries. The previous Windows F02 `execution_start=3` is a sum of cumulative snapshots; the retained two bindings are not a complete independent reconstruction of all raw events.
5. Evaluate lost/duplicated/late event records and process-restart correlation with a declared fault model. Separate deterministic correctness checks from empirical reliability rates; do not estimate natural deployment rates from injected cases.
6. Release a reviewer-inspectable artifact with source, schema example, exact commands, version identities, derived evidence and stated omissions. Private models and generated images require an explicit release decision.

These are proposed research requirements, **not** authorization for new GPU runs, model downloads or a new campaign. A campaign design should be frozen, costed and reviewed before execution. If equal-information log auditing matches every decision and operational value cannot be measured, keep the Tool paper and stop the journal expansion.

## Manuscript architecture after the gate

- Problem and failure model with explicit limits of the backend observer.
- Research questions, comparison systems and validity criteria.
- Evidence contract: capture, identity, provenance, interpretation and refusal conditions.
- Implementation: exporter, guard, observer and their ownership boundaries.
- Paired CPU and real-backend evaluation with original-run completion and costs.
- Threats to validity, reproducibility, related work and data/code availability.

The existing DSN Tool manuscript is source material, not a ready-made journal draft. Do not double-submit substantially overlapping versions. If DSN accepts the Tool paper, the Access version needs a separately demonstrable new contribution and must cite the published version under IEEE policy.

## Submission mechanics to prepare in parallel

IEEE Access accepts submissions continuously and has no conference-style annual paper deadline. Its [official homepage](https://ieeeaccess.ieee.org/) advertises a 4-6 week submission-to-publication time; this is a journal target, not an acceptance or review-time guarantee. The submission checklist requires both the journal-template source file and an exactly matching PDF, all authors and biographies, a submitting-author ORCID, 3-10 keywords, and disclosure/citation for AI-generated text in the prescribed form. It recommends under 20 pages. Current anonymous IEEE conference PDF does not meet these mechanics. APC and the relevant SCI/JCR/CAS classification year require separate authoritative verification before a final submission decision.

## Immediate preparation without new experiments

- A [claim/evidence table](ieee-access-evidence-map-20260928.md) and [code-level capture/baseline design](ieee-access-capture-baseline-protocol-20260928.md) now mark missing cells as NOT RUN, map existing records to variables, and predeclare the distinct units, future collection fields, comparison views and stop rules without reclassification.
- Prepare author-owned metadata and journal-template migration only after the scientific scope is fixed.

Decision point: evaluate whether the baseline and contract differ on a meaningful, reproducible task. Only a positive, bounded result justifies expanding to a full Research Article or Applied Research manuscript.
