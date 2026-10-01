Requires Python >=3.10 for offline scripts; tested with Python 3.13.15.
System Python 3.9 is unsupported. The manuscript author ZIP is PRIVATE and contains host/account identifiers
and audit paths. Only the separately sanitized anonymous demo is an external
candidate; never distribute the full delivery directory.

# v0.18 current revision

The current pass clarifies the local recovery contribution, consolidates
repeated qualifiers, places limitations after related work, moves Table I
definitions to a table note and shortens AI disclosure. The supplied review's
proposed unsupported metrics and human-verification assertion were not adopted.
See `review/RESPONSE_TO_DOUBAO_V018.md`. Detailed audit coverage remains in
`evidence/REPRODUCIBILITY_SCOPE.md`; the main results retain adverse findings.
The preceding narrative rewrite is recorded in `review/NARRATIVE_REVISION_V016.md`. The preceding
Humanizer pass is recorded in `review/HUMANIZER_PASS_V015.md`, and bounded
OPEN-item rechecks in `review/POLISH_AND_OPEN_ITEM_RECHECK_V014.md`.

The manuscript now reports the offline Windows conversion and its conservative
verification result. The anonymous demo v0.5 adds semantic projections and a
standard-library replay command, tested after clean extraction. It excludes
private raw captures and does not reproduce the live experiment. The v3 DS
review prompt and pending author declarations are under `review/`.

A separate v2 Windows campaign observes the same-run submission guard after
restoring pinned process-local inventory in both calls. F02 returns
`submission_outcome_unknown` and adds no POST; original run remains unresolved.
The v1 negative result remains in the manuscript and evidence. Physical GPU
savings and eventual completion are unestablished. See v2 report/audit under
`evidence/`. The offline converter retains lifecycle/recovery separation without an artifact
validator assertion; all composite verifications remain false. Full converted
records remain private. Submission readiness remains false; author and public
artifact reproducibility decisions remain open.

# Historical v0.9 note (superseded by the current revision above)

The v0.9 revision retains the October 1 Windows same-run campaign as a negative
result: F02 made two product calls but one POST and one bound lifecycle. The
retry returned `model_identity_drifted`, so the target ambiguity guard was not
observed. Backend cache reuse also prevents a physical GPU-work claim. The
campaign stopped and its owned backend was terminated. The public report and
offline consistency receipt are under `evidence/windows-same-run-*20261001.json`;
raw captures remain private and are excluded from the author-review package.
The same-run evidence gate remains open. This draft is not submission-ready.

`main.tex` and `references.bib` are the typeset manuscript source. The earlier
Markdown draft remains the argument/evidence working copy; it is not the
submission file. Output is `main.pdf` after compilation.

The active manuscript now describes `research-normalization-v4`. Missing or
null reported run state leaves recovery unknown, and a durable-manifest job or
artifact identity conflicting with the selected top-level identity is an
evidence mismatch. The offline checker normalizes twelve retained CPU product
manifests without adding artifact-validator assertions; none passes composite
verification. This is read-only reanalysis, not backend replay or a Windows
observer-to-exporter conversion. Earlier v0.2 demo archives and W2 records
remain historical v2 outputs; the v0.3 anonymous demo candidate carries the
current rules. The Windows same-run and observer-conversion capture criteria are
recorded in `../docs/research/dsn-next-evidence-gates-20260929.md`.

## Current working manuscript: v0.20

The paired Windows results are integrated in `main.tex` and `main.pdf`.
Historical narrative was condensed without changing retained measurements.
The current PDF is six US Letter pages with a 128-word abstract; all nine font
entries are embedded. Compile/visual details are in `compile-report.json`.
Original v0.18 delivery archives and their freeze remain historical baselines.
The v0.20 private author package and anonymous demo v0.6 add a derived paired
projection and offline checker. Full paired raw captures are excluded from both.
Old review statements below do not certify the new working manuscript.

## Verified format baseline

DSN 2026 Research Track CFP, accessed 2026-09-27:
https://dsn2026.github.io/cfpapers.html

- Tool descriptions/demonstrations: 7 pages excluding references.
- Reference-only pages are exempt; pages with technical text/figures count.
- IEEE Computer Society two-column US Letter, 10pt, 12pt leading.
- First page states paper type; abstract no more than 150 words.
- Single PDF with embedded fonts, double-blind anonymization; under 15 MB recommended.

The official DSN 2027 CFP is now available at
https://dsn2027-berlin.github.io/call-for-contributions/ . It retains the Tool
seven-page limit, 150-word abstract maximum and reference exemption. Abstracts
are due November 25, 2026 and full papers December 2, 2026 (AoE). The HotCRP
site displayed "Submissions are currently closed" on September 28. The generic
ARS IEEE references-in-limit default is overridden by the explicit DSN rule.

Rechecked 2026-10-01 against the official DSN 2027 CFP: Tool descriptions are
seven pages; reference-only pages are exempt. Thus v0.19's seventh reference-only
page was not a page-limit violation. The v0.20 reduction improves concision.

IEEEtran.cls is the unmodified CTAN class:
https://mirrors.ctan.org/macros/latex/contrib/IEEEtran/IEEEtran.cls
IEEEtran.bst is likewise the unmodified CTAN BibTeX style; hashes and source
URLs are recorded in template-provenance.json. See embedded licenses. The IEEE ZIP endpoint returned non-ZIP content;
CTAN supplied the class instead. Fonts/margins are not manually reduced.

## Build

The small local reviewer demonstration is built with
`python3 paper/scripts/package_reviewer_demo.py` from the repository root. Its
`paper/examples/README.md` gives a single offline command that runs in a clean
extraction. It contains synthetic exporter inputs and retained derived records;
it is not a full backend distribution, an anonymous submission artifact, or a
new experiment.

The separately sanitized candidate is built with
`python3 paper/scripts/package_anonymous_demo.py`. It normalizes archive
timestamps and source-module names, records an author-side source/delivery hash
map outside the ZIP, and runs the same offline checker after extraction. It is
still an internal candidate: publicly indexed source or data may be recognizable.
DSN 2027's artifact-evaluation track is separate from research-paper review
and does not require the artifact at initial paper submission.

With TeX Live/MacTeX:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Or with Tectonic (downloads TeX dependencies on first build):

```sh
tectonic --keep-logs main.tex
```

## Scope and editorial changes

The current abstract preserves the primary claim and fresh-run limitation.
The result table is made column-width; the architecture is a vector LaTeX
figure. Internal claim tags and private provenance paths are not printed;
scientific limitations remain in the text. Administrative evidence references
are kept in ../docs/research/dsn-evidence-reconciliation-20260927.md.
The wide responsibility comparison is expressed in related-work prose.

No author identity or affiliation was invented. Anonymous formatting is not a
completed anonymity audit; source/repository identifiers need final review.
This is a typeset working draft, not submission-ready: raw-event reconstruction,
artifact-byte verification, broader academic positioning and target-year rules
remain open. No experiments were run to produce this document.

## Historical build verification

The earlier four-page draft compiled with Tectonic 0.17.0, US Letter.
All seven font subsets are embedded. No undefined citations/references or
overfull boxes. Five underfull hbox notices remain (loose spacing); rendered
pages were inspected without clipping or overlap. The PDF is about 47 KB;
its small size reflects text and vector content, not an empty/corrupt file.
The generic skill's 100 KB heuristic is not a PDF validity requirement.
Machine-readable results and PDF hash: compile-report.json. Full compile log
and rendered pages are retained locally in ignored build/.

Tectonic used T1 font encoding to avoid XeTeX TU/ptm font substitution.
No global LaTeX installation was made; the temporary compiler is outside Git.

Vendored CTAN class/style files retain upstream trailing whitespace byte-for-byte;
local .gitattributes exempts only these two files from whitespace linting.

## v0.4 completed technical manuscript package

The active manuscript is main.tex/main.pdf; docs/research/dsn-tool-description-draft.md
is the archived v0.3 planning draft, not the latest typeset text. This revision
adds two vector diagrams, a paired CPU coverage table, a Windows case table,
read-only retained-evidence audit, current artifact-byte matching and expanded
related work. No experiment was rerun.

Regenerate derived evidence: `python3 paper/scripts/audit_retained_evidence.py`
from repository root. Regenerate diagrams with a Python environment containing
reportlab: `python3 paper/scripts/build_figures.py`. Run the LaTeX build in paper/.

Final checks supersede the older four-page build snapshot above. The current
six-page draft and 135-word abstract are recorded in compile-report.json. ARS
internal review: review/ARS_REVIEW.md. This is an inline
self-review, not independent peer review. Pending author-owned declarations:
review/AUTHOR_DECLARATIONS.md. Chinese reading abstract: review/ABSTRACT_ZH.md.

## v0.5 pre-submission recheck

Two result tables now regenerate from validated retained records. `make audit`
updates them; `make pdf` runs the audit before LaTeX. Four malformed-record
negative checks are recorded in review/AUDIT_NEGATIVE_CHECKS.json.
The checker counts historical Windows byte-match receipts, not fresh image
hashing on this machine. See review/PRE_SUBMISSION_RECHECK.md for the findings.

`make package` creates delivery/dsn-tool-description-v0.8.zip with a checksum
manifest. This is an author-review package, not a complete tool distribution
or a certified anonymous submission artifact. It preserves scientific limits.


## Independent review disposition

The external DeepSeek-harness review is stored outside the common input as an
author-supplied review record, and its disposition is in review/INDEPENDENT_REVIEW_RESPONSE.md.
It found a real cumulative event-count versus binding-count discrepancy and a
missing terminal-payload discriminator. The manuscript now reports these as
limitations and uses retained bindings as a narrow count. This response is not
authoritative independent verification and does not claim the missing payloads
were recovered.

## v0.12 review corrections

Eighteen Windows execution-source hashes can be checked using
`python3.13 paper/scripts/verify_execution_sources.py`. These are CRLF byte
snapshots reconstructed from Git history, not runtime attestation. Historical
unsupported test-count/runtime claims were removed. Normalization v4 preserves
unknown recovery for partial runs. See `review/RESPONSE_TO_INDEPENDENT_REVIEW_20261001.md`.
