# External review synthesis — DS round 2

Claude review was aborted before reading any material and contributes no
substantive judgement. The DS round 2 review read the common package and compared
selected checkout source. It is an external AI review, not human peer review or
an editorial decision.

## Consensus with the retained evidence

- **Venue:** DSN Tool Description remains BORDERLINE but plausible. Continue
  after revision; do not lower venue merely to hide evidence or packaging gaps.
- **R1:** the Windows campaign creates a new run for every F02 second call, so
  it does not exercise the same-run guard. The manuscript now says this in the
  abstract and method, and distinguishes CPU blocking in F02 fixtures from the execution-count
  difference observed in the single-stage fixture.
- **R2:** each F02 retained export has cumulative `execution_start=3` versus two
  bindings. This is now named in the manuscript. The exporter sums cumulative snapshots and can count prior events again.
  This is not evidence of a third execution; original snapshots are unavailable.
- **R3:** the review package now includes exporter and guard implementation files
  through the package builder, plus the evidence addendum. It still does not
  include private models, raw Windows payloads or a complete campaign rerun.
- **R4:** an operator decision scenario and false-positive blocking cost are now
  stated. No usability or deployment impact is claimed.
- **R5:** terminal label limitations and figure/prose scope are explicit. A
  full payload-level terminal predicate remains unavailable in the retained
  package.

## Review disagreement / correction

The reported first-completion-before-second-receipt ordering is expected: the
controller gates the second call on first-call completion. It is not a timing
contradiction.

The DS review correctly identified the cumulative-count mismatch and package
limits. It recommended no longer treating the Windows campaign as guard
validation. It did not establish a third execution, cache reuse, or a terminal
predicate failure. Those remain unresolved or unsupported inferences. The
review's lack of visual rendering is retained as its own limitation.

## Decision

Proceed with DSN Tool Description only after author review of the revised scope,
actual target edition and artifact/anonymity rules. Keep lower-venue options as a
separate fallback decision; do not submit to a lower venue solely because the
current Windows campaign does not demonstrate guard efficacy. A future stronger
version would require a campaign that keeps the second call inside the unresolved
run and retains per-snapshot terminal payloads and per-call run/seed identity.
