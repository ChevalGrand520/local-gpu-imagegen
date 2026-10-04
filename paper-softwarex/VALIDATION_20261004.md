# SoftwareX revision validation receipt

v0.12 (2026-10-04): author-approved minimized Windows packet released at
345da1f44ad6d67a5cc637c31edb2db607a37480; see EVIDENCE_RELEASE_20261004.md.
The standalone seven-file packet verifier passed after copying and checksum
verification; six rows match. No new Windows/GPU execution. Original byte
replay and independent execution authentication remain distinct from public
subset recomputation. Reviewer final report was unavailable due to usage limits;
no new independent audit PASS and no change to the frozen v0.8 audit.
Bundled build/render passed; all nine pages inspected, 98-word abstract,
3636 Markdown words, 26 identical preserve-only parts, tables/references unchanged.
DOCX SHA256: 4eac128033c9967f9ce493f0ee0c68879e5b2531a8068b923b2521dab63fad73.

v0.11 (2026-10-04): restored the retained macOS full-suite summary with its
immutable source link, local qualification and absent-public-full-log boundary.
No unified failure cause asserted. Recovery wording now names retrieval,
re-entry and recovery_job_id forwarding through the adapter history path.
Bundled build/render passed; all eight pages visually inspected, 98-word
abstract, 3516 Markdown words and 26 identical preserve-only parts. Tables
and references match v0.10. No experiment or test rerun. See
REVIEW_V10_DISPOSITION_20261004.md; final submission gates remain open.

v0.10 (2026-10-04): same-run guard and operator-use clarification; see
REVIEW_V09_DISPOSITION_20261004.md. Bundled build/render passed; all eight
pages inspected, 98-word abstract, 3441 Markdown words, 367-word Impact and
26 identical original preserve-only parts. Metadata/result rows and references
match v0.9 exactly. Figure 2 PNG is 7000×1600; SVG retained, stop connector
dashed without arrowhead. Validation/supplement links pin dc9720e; all six
cited supplement paths exist there. No new tests, Windows/GPU experiment or
independent claim audit. Original v0.9 DOCX hash remains unchanged below.
v0.10 DOCX SHA256:
3af76fe63848df0a90bf574751293eaa9e99a40893c09f6144c60d7123dee6b0.
Final author content approval and current publisher/form/APC checks remain open.

Same-day author-declaration update to v0.9: completed competing interests,
CRediT and factual ethics/consent scope; diagram captions disclose the
author-confirmed GPT-6.1 Sol model. Original approved AI paragraph, result and
metadata rows, abstract and reviewed references remain intact. No experiment
rerun. Bundled build/render passed; 26 original preserve-only parts identical,
99-word abstract, 3211 Markdown words and eight pages. Changed pages 3/6/7/8
visually inspected; pages 1/2/4/5 byte-identical to the inspected prior renders.
Final updated DOCX SHA256:
0d1f4e7b45c9e2af0c05d32afb3f4e13d995295a925c6e0ad4a65534c2aa8e1d.
Final human content approval and publisher/form/APC checks remain outstanding.

v0.9 (2026-10-04): final review corrections and bounded verification.
See FINAL_REVIEW_20261004.md and final-check-receipt-20261004.json.
96 research tests passed again in 9.934 s; twelve synthetic CPU operations
passed; an isolated rebuilt wheel exposed seventeen tools and 2024-11-05.
CPU variants are B2 da65d57/W3 d45173a, separate from paired Windows 08539d5.
No new Windows, GPU or real ComfyUI recovery result. Historical CI refresh
returned 502; no current refresh claimed. Eight rendered pages inspected;
99-word abstract, 3163 Markdown words, two figures and 26 preserved template
parts. Figure/model-version and author/publisher gates remain open.

v0.8 (2026-10-04): prose-only humanizer revision. Compared against v0.7:
35 inline-code spans, 11 URLs and 16 citation occurrences unchanged in order;
all table rows, software metadata, references and approved AI declaration
unchanged. Manual meaning review retained synthetic/Windows/GPU distinctions,
unknown-ID/retained-ID separation, generated/completed distinction and every
reported result. Bundled builder/renderer exited 0, 26 preserve-only template
parts unchanged, abstract 99 words. Seven rendered pages inspected in full.
No experiment, citation refresh or claim expansion in this revision.

v0.7 (2026-10-04): added official MCP specification and ComfyUI repository
references, verified through their primary pages. Bundled builder and renderer
exited 0; seven pages inspected in full, 101-word abstract, 26 original
preserve-only parts unchanged. Metadata C1–C8 is present. Figure 2 SVG source
already exists. No additional experiment or similarity-check upload occurred.

Source snapshot: dfc8378cb3d891f7951786bc4544cd971bd56a11.
Product/research source remained unchanged during these commands. Later edits
are manuscript, figure/builder and README changes; not backend/GPU execution.

| Check | Exact invocation / artifact | Result / boundary |
|---|---|---|
| Research suite | `uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest discover -s tests/research -q` | exit 0; 96 tests in 10.416 s; model-free |
| Build | `uv build --offline --out-dir /tmp/softwarex-review-build` | exit 0; 0.9.1 wheel and sdist; not uploaded |
| Isolated wheel | `uv run --offline --no-project --python 3.12 --with /tmp/softwarex-review-build/local_gpu_imagegen-0.9.1-py3-none-any.whl local-gpu-imagegen verify` | exit 0; ok=true; version 0.9.1; 17 tools; interface only |
| Wheel inventory | ZIP member and METADATA inspection | Author Zhen Cheng; no research exporter or paired checker members |

Historical receipts, available in the same source snapshot:
- `paper/evidence/v022-probe-command-receipt.json`, introduced at 9dd0634:
  twelve synthetic offline fixture probes, Python 3.13.15, no Windows/GPU.
- `paper/evidence/revision-v012-runtime-check.json`, introduced at 01c5e33:
  thirteen-test older offline subset, Python 3.13.15; not the 96-test suite.
- CI at caaa2e0: https://github.com/ChevalGrand520/local-gpu-imagegen/actions/runs/37090919543
  GitHub-hosted Windows/Ubuntu Python 3.11/3.12; historic retained result,
  not a new real-generation validation or author-machine health check.

PyPI 0.9.1 JSON was read during this revision:
https://pypi.org/pypi/local-gpu-imagegen/0.9.1/json . It exists and retains
historical author metadata Capricorn. The above wheel was rebuilt from the
cited source, with Zhen Cheng metadata; do not conflate those artifacts.
No registry upload, package replacement or new release occurred.

v0.3 document gate: final six-page rendering inspected in full; figure and
caption are together, five numbered main headings and page numbers correct,
no clipping or table split. DOCX section XML and metadata left columns match
the retained template exactly; 26 preserve-only original parts are identical.
The six DOCX result rows match the tracked projection JSON. The projection
checker passed again; derived consistency only. Abstract remains 100 words;
the full Markdown is below 2700 words, conservatively under the template limit.

## v0.6 resumed validation (2026-10-04)

- `uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python paper-softwarex/known_job_recovery_demo.py`: exit 0; current JSON output is byte-identical to known-job-recovery-receipt.json.
- Product scripts and tests match dfc8378 (`git diff --quiet dfc8378 -- scripts tests`: exit 0).
- `python paper/scripts/verify_paired_projection.py`: exit 0, six published rows/totals; derived consistency only.
- Bundled Python rebuilt manuscript-v0.6.docx: 26 original preserve-only template parts unchanged, abstract 101 words; two embedded figures.
- Bundled document renderer produced seven pages; every page visually inspected, no clipping, overlap or broken tables. Metadata C1–C8 is populated. Markdown contains 2991 whitespace words including metadata and references.
- No full-suite rerun, model download, GPU execution, real ComfyUI recovery or journal submission occurred. Prior failures and author/publisher gates remain recorded.
