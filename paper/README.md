# Standard manuscript source

`main.tex` and `references.bib` are the typeset manuscript source. The earlier
Markdown draft remains the argument/evidence working copy; it is not the
submission file. Output is `main.pdf` after compilation.

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

With TeX Live/MacTeX:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Or with Tectonic (downloads TeX dependencies on first build):

```sh
tectonic --keep-logs main.tex
```

## Scope and editorial changes

The 131-word abstract preserves the primary claim and fresh-run limitation.
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

## Build verification

Compiled with Tectonic 0.17.0: 4 pages including references, US Letter.
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

Final checks supersede the older four-page build snapshot above; see the updated
compile-report.json. ARS internal review: review/ARS_REVIEW.md. This is an inline
self-review, not independent peer review. Pending author-owned declarations:
review/AUTHOR_DECLARATIONS.md. Chinese reading abstract: review/ABSTRACT_ZH.md.

## v0.5 pre-submission recheck

Two result tables now regenerate from validated retained records. `make audit`
updates them; `make pdf` runs the audit before LaTeX. Four malformed-record
negative checks are recorded in review/AUDIT_NEGATIVE_CHECKS.json.
The checker counts historical Windows byte-match receipts, not fresh image
hashing on this machine. See review/PRE_SUBMISSION_RECHECK.md for the findings.

`make package` creates delivery/dsn-tool-description-v0.5.zip with a checksum
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
