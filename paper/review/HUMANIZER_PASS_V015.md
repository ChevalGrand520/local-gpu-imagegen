# Humanizer prose pass, v0.15

This is an author-side editing pass, not an independent review, plagiarism
check or AI-detector evaluation. No experimental data, backend execution or
GPU measurement was added.

## Editing source

- Upstream: https://github.com/blader/humanizer
- Version: 3.1.0; pinned revision `225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8`.
- Installed in the current Mac user's global Codex skill directory.
- SKILL.md SHA-256: `0612f1dfb1672b0ea9b97e139bf1f06cabe98d8b27424fe8ff01e1fb4cc99cad`.
- Baseline manuscript: repository revision `d688904` (v0.14).

The installation makes the skill available for discovery in a subsequent
Codex turn/session. For this pass its installed instructions were read directly.
Upstream executable scripts were not run.

## Changes and retained distinctions

| Passage | Change |
|---|---|
| Abstract | Replaces the metaphor of exposing a guard with the caller's action and the retry result. |
| Introduction and discussion | Replaces repeated "inspectable integration" wording with the records, decisions and checks the implementation connects. |
| Evidence export | States what the record contains and what the exporter does, with fewer abstract transitions. |
| CPU fixture | Opens with W3's blocked submission, followed by the worker's completion and the incomplete client operation. |
| Historical event discrepancy | Separates observations, the cumulative-count mechanism and timing into readable paragraphs. |
| Same-run v2 | Removes repeated "unchanged" phrasing while retaining the frozen product, complete arguments and locked-route validation. |
| Limitations | Replaces a parenthetical prose dash and clarifies the meaning of missing events. |
| AI disclosure | Records use of the Humanizer editing skill. |

Informative contrasts remain: submission versus execution, fresh-run success
versus original-run reconciliation, lifecycle binding versus physical GPU work,
record consistency versus authenticity, and private author material versus the
anonymous demo. These are scientific distinctions, not rhetorical filler.
The reported/interpreted/oracle separation and real three-part lists remain.
Technical terms were not replaced with synonyms for stylistic variety.

## Verification

Compared with the baseline, citation occurrences, inline `texttt` identifiers,
numeric tokens and complete figure/table blocks are unchanged. Retained
experimental evidence and exact execution-source snapshots were not edited.
The bibliography is unchanged. These mechanical checks support the prose
review; they do not independently prove semantic equivalence.

Tectonic 0.17.0 compiled the revised source successfully: six US Letter pages,
133 abstract words, all checked fonts embedded, zero overfull boxes and zero
undefined citations/references. The log has 17 underfull notices. Current PDF
hash and the page inspection status are recorded in `compile-report.json`.

All six page renders were inspected at a longest edge of 1100 pixels, with no
obvious clipping or overlap. Final human acceptance of the PDF remains pending.

From a clean extraction of the private author ZIP, the following commands ran
with Python 3.13.15 and exit code 0:

```text
python3.13 paper/scripts/verify_reviewer_demo.py
python3.13 paper/scripts/verify_windows_projection.py
python3.13 paper/scripts/verify_execution_sources.py
```

Their working directory was the extracted archive root. All 114 manifest file
hashes matched. The final archive was rebuilt after recording these results
and was checked again. The private author bundle remains private and contains
identifiers. The separate anonymous v0.5 demo is unchanged; submission readiness
remains false.
