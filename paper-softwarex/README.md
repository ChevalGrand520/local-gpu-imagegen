# SoftwareX Original Software Publication candidate

Current files: manuscript-v0.9.md (editable content), manuscript-v0.9.docx
(official-template candidate), build_manuscript.py (deterministic package patch).
Versions 0.1 through 0.5 are retained. Nothing has been submitted.
v0.5 adds verified section-level comparisons to three related preprints,
a retained F02 walkthrough and a compact Limitations subsection. Reading
receipt and review disposition: RELATED_WORK_CHECK_20261004.md. No new results.
The v0.3 targeted review disposition is REVIEW_V03_DISPOSITION_20261004.md.
v0.4 adds a resolvable validation-material link, separates unknown submission
from retained-job recovery, clarifies derived actions and figure arrows.
The supplied model-review disposition is REVIEW_DISPOSITION_20261004.md;
current executed validation is VALIDATION_20261004.md. v0.3 pins software
snapshot dfc8378, includes one architecture figure and explicit get_run/readback
boundaries. It adds Heading1 to Impact, which the official template itself
leaves unstyled; this is a navigation improvement, not correction of a missing
section. No stable-branch merge or registry release was performed.

Official template: Version 6, March 2026, downloaded from the SoftwareX link on
https://www.elsevier.com/en-gb/researcher/author/tools-and-resources/research-elements-journals
on 2026-10-03. URL:
https://legacyfileshare.elsevier.com/promis_misc/softwarex-osp-template.docx
SHA256: 9fcf40ede96a2f188ee4ef77134e0596d01e1b65fd9db63f2874d29f2ecb916d.
Retained unmodified under templates/. The browser link download succeeded
after direct HTTP failed; the earlier download blocker is now resolved.

## Template requirements and verification

- Exactly five required main sections: Motivation and significance, Software
  description, Illustrative examples, Impact, Conclusions.
- Approximately 100-word abstract; v0.9 has 99 whitespace words.
- At most six keywords; current six. At most 4000 words; the full Markdown
  draft remains below 3300 whitespace words including metadata and references, conservatively
  below that limit. Maximum six main-body pages excluding metadata/tables/
  figures/references; v0.6 is seven pages total; page seven contains the final main sections,
  availability, declaration and references. Metadata, tables and figures are
  excluded from the template body-page limit.
- Metadata labels in the first two columns remain byte-for-byte identical to
  the official template; eight right-hand data slots are filled.
- A README.md and Licence.txt are explicitly required in the template. This
  branch and the pinned dfc8378 snapshot contain Licence.txt, byte-identical
  to the existing MIT LICENSE. No license terms changed.
- Instructions and optional empty acknowledgement removed; existing author-
  approved AI declaration preserved verbatim. No-funding statement uses the
  author's 2026-10-04 confirmation; competing interests remain pending.
- One Letter section and its full section XML unchanged; continuous line
  numbers, heading numbering and footer PAGE field preserved. Word is asked
  to refresh fields when opening; rendered page numbers correctly run 1–7.
- 26 original preserve-only DOCX parts remain byte-identical. document.xml,
  settings.xml, core.xml, image relationships and Content Types are editable;
  two image parts are added. The updated contract records this scope.
- Reference/final rendering diff completed; every page of the final revision
  was visually inspected. No clipped text, broken tables or missing glyphs.
- The paired projection checker passed again, six rows/totals; derived
  consistency only, not raw-event replay or execution authentication.

## Rebuild

Use the workspace-bundled Python with lxml:
`python paper-softwarex/build_manuscript.py`.
This writes a DOCX from the retained template and v0.9 Markdown and checks
preserve-only parts. Then run the document skill renderer and inspect every
page. Generate architecture.svg from figures/architecture.json with the ARIS
figure-spec renderer; rasterize the SVG for the DOCX image. templates/artifact.md
records the format contract; /tmp QA directories
are disposable, not deliverables or manuscript evidence.

## Remaining submission gates

The format milestone is complete. The scientific-impact argument remains
bounded: no external user study, cited downstream adoption or measured research
productivity result is available. Do not solve this by inflating claims or
adding arbitrary words. Assess whether concrete reusable functionality and the
fixed examples meet the journal's software-impact criterion.

Refresh the full Guide for Authors, source-layout expectation, administrative
declarations and current APC before submission. Select a final immutable source
snapshot that includes Licence.txt and prepare its release inventory. Keep
product source, older experiment source and source-only exporter distinct.
Private raw captures and the sanitized prototype are still not cleared for
public distribution. No GPU or new backend experiment occurred in this milestone.

The older ranking/timeline receipt remains version-labelled in paper-access/.
Current official Insights values were not refreshed through the CAPTCHA page.
The official OSP template above, however, is now directly obtained and checked.

## v0.6 recovery revision

Adds an executable known-job CPU walkthrough, its receipt, and Figure 2
(editable SVG and PNG). Engine and HTTP-adapter checks are separate; this is
not an integrated ComfyUI/GPU recovery experiment or a Windows F03 result.
The final DOCX was rebuilt and all seven rendered pages inspected on 2026-10-04.
Metadata contains the C1–C8 table; it is not an empty heading.
See KNOWN_JOB_RECOVERY_SCOPE_20261004.md for execution scope and limitations.

## v0.7 ecosystem citations

Adds the official MCP specification (2025-06-18 revision) and ComfyUI source
repository as references [7–8], verified online on 2026-10-04. Seven rendered
pages inspected; 101-word abstract and 26 preserved template parts unchanged.
Figure 2 already has editable SVG source. No new execution evidence added.

## v0.8 language revision

Humanizer prose pass: simplified repeated caveats, split the retrieval/recovery
paragraph, clarified actors and shortened repetitive closing sentences. Data
tables, 35 inline-code spans, 11 URLs, 16 citation occurrences, metadata,
references and the approved AI declaration are unchanged. No evidence added.
The abstract is 99 words; the Word manuscript remains seven pages.

## v0.9 final review

Final review and dispositions: FINAL_REVIEW_20261004.md. Fresh v0.8 claim review
and citation review are retained with their original scopes; no v0.9 independent
PASS is claimed. MCP citation now matches the declared 2024-11-05 protocol.
The same-run and paired captures are kept distinct. Misleading accepted-job and
completed-state wording was corrected. Unaccompanied Mac full-suite totals were
removed while retaining the failed-attempt and unsupported-platform limits.
Funding and absent publication/preprint/other-review history were author-confirmed.

Bounded final executor checks: 96 research tests passed; twelve synthetic CPU
operations passed; P-stop/W3 counts and original-run completion fields match;
rebuilt wheel reports seventeen tools and 2024-11-05. See
final-check-receipt-20261004.json and validation/. These are CPU/interface checks,
not new Windows, GPU or real ComfyUI recovery evidence.

Eight rendered pages inspected; 99-word abstract, two figures, eight references,
six keywords and 26 original preserve-only template parts retained. Captions
disclose Codex assistance. In the subsequent author confirmation, the diagram
model was identified as GPT-6.1 Sol; competing interests, CRediT and study-scope
statements were completed in the same v0.9 files. The author has no ORCID and
plans to apply for university APC support, with no payment commitment claimed.
Final author content approval and publisher checks in
submission/SUBMISSION_CHECKLIST_20261004.md remain open.
