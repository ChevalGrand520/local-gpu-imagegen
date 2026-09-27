# Pre-submission recheck — v0.5

Scope: same-context technical and artifact self-check, not independent peer
review. No new experiment, GPU invocation, model download or publication.
The nature-reviewer workflow was inspected but not invoked; no three blind
reviewers or Nature-fit assessment is claimed.

## Repaired

- The v0.4 audit hardcoded four artifact checks and accepted empty check lists
  through all([]). The revised audit requires the expected per-call checks,
  counts them from records and verifies hash membership in recorded host hashes.
- The prior CPU check validated counts but copied completion/recovery labels
  from the comparison file. They are now matched to both original CPU records.
- Exact case sets and uniqueness are now checked for both data layers; repeated
  finish events are rejected. Explicit ValueError checks remain active under
  Python optimization, unlike assert statements.
- The two manuscript tables are generated directly from the validated records.
  This removes independent hand-entry as a source of table drift.
- The manuscript now states explicitly that rerunning the offline audit does
  not repeat host-side image hashing or report-versus-JSONL comparison. Those
  are inspection receipts in the retained extract.
- B2 and W3 definitions were moved before their first use in CPU results.
- Added an author-review ZIP builder with input checksums and a clean-directory
  audit replay check. The ZIP is not a full tool distribution or anonymously
  certified submission artifact.

## Validation

Four temporary-copy mutations were rejected: missing Windows case, missing
artifact check, flipped CPU completion and duplicated finish event. These
are validation-script checks, not new research experiments. Original records
were unchanged. Generated CPU/Windows rows retain the published values.
PDF compiled; final font/layout results live in compile-report.json.

## Remaining scholarly and submission decisions

1. **Contribution risk:** this is a bounded tool integration and diagnostic
   workflow. Existing evidence does not establish comparative utility or a new
   recovery algorithm. More confident language or extra charts cannot fix that.
2. **Evidence limit:** Windows raw events/history are unavailable in this export;
   six retained binding IDs are not six independently reconstructed executions.
3. **Reproduction:** the package can reanalyse retained records; it cannot recreate
   the Windows campaign without the pinned private setup and models.
4. **Target year and author declarations:** unresolved. Do not submit using the
   expired 2026 deadline or invent authors, funding, conflicts or human approval.
5. **Anonymity:** PDF has anonymous author metadata; system name, source hashes,
   evidence filenames and ancillary documents can still link to a repository.
   The current ZIP is for author review, not an anonymity guarantee.

No acceptance probability or final editorial verdict is assigned. The next
scientific judgement should be a separately scoped external/independent review
of usefulness and novelty, with disclosure of its actual provenance. It has not
been performed in this continuation.
