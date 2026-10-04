# SoftwareX Original Software Publication candidate

Current files: manuscript-v0.4.md (editable content), manuscript-v0.4.docx
(official-template candidate), build_manuscript.py (deterministic package patch).
Versions 0.1 through 0.3 are retained. Nothing has been submitted.
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
- Approximately 100-word abstract; v0.2 abstract is exactly 100 whitespace words.
- At most six keywords; current six. At most 4000 words; the full Markdown
  draft remains below 2700 whitespace words including metadata and references, conservatively
  below that limit. Maximum six main-body pages excluding metadata/tables/
  figures/references; the entire v0.3 rendering is six pages.
- Metadata labels in the first two columns remain byte-for-byte identical to
  the official template; eight right-hand data slots are filled.
- A README.md and Licence.txt are explicitly required in the template. This
  branch and the pinned dfc8378 snapshot contain Licence.txt, byte-identical
  to the existing MIT LICENSE. No license terms changed.
- Instructions and optional empty acknowledgement removed; existing author-
  approved AI declaration preserved. No funding/conflict statement invented.
- One Letter section and its full section XML unchanged; continuous line
  numbers, heading numbering and footer PAGE field preserved. Word is asked
  to refresh fields when opening; rendered page numbers correctly run 1–6.
- 26 original preserve-only DOCX parts remain byte-identical. document.xml,
  settings.xml, core.xml, image relationships and Content Types are editable;
  one image part is added. The updated contract records this scope.
- Reference/final rendering diff completed; every page of the final revision
  was visually inspected. No clipped text, broken tables or missing glyphs.
- The paired projection checker passed again, six rows/totals; derived
  consistency only, not raw-event replay or execution authentication.

## Rebuild

Use the workspace-bundled Python with lxml:
`python paper-softwarex/build_manuscript.py`.
This writes a DOCX from the retained template and v0.4 Markdown and checks
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
