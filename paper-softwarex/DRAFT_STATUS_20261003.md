# SoftwareX candidate checkpoint — 2026-10-03

Target: Original Software Publication (formal peer-reviewed software article).
Status: first English content draft; not journal-template formatted, submitted,
released or adjudicated by a new reviewer. No new experiment or GPU use.

## Claim-evidence matrix

| Claim | Evidence source | Permitted wording / limit |
|---|---|---|
| Installable local control plane with durable run state | README, pyproject.toml, product run engine and RunStore; existing wheel verification | Interface/implementation availability, not full real generation on every platform |
| Same-run guard withholds another uncertain submission | Paired projection F02 W3/B2, execution source 08539d5 | One fixed pair: 1 vs 2 accepted jobs; original W3 run incomplete |
| Guard incurs false-block cost | FPRE W3: zero upstream sends, unresolved; B2 completes | Fixed negative example, not rate |
| Simple stop matches reported guard outcomes | Existing CPU P-stop record and contribution gate | No distinct policy superiority |
| Exporter supports structured offline inspection | Source-checkout exporter; clean offline demo; twelve equal parser probes | Exporter excluded from product distribution; no audit-effort or parser-superiority claim |
| Supported matrix software checks passed | GitHub CI run 37090919543 at caaa2e0 | GitHub-hosted model-free runners, not author's PC/GPU health |

## Structure and figure plan

The draft uses motivation, software description, illustrative examples, impact
and conclusions, plus metadata and availability statements. These headings are
a content plan; exact mandatory template slots still require verification.
One results table is present. If the official template permits the intended
layout, add one architecture figure distinguishing installed product from
source-only exporter, and one submission timeline with F02 and FPRE. Neither
figure would introduce a new measurement. All three citations already exist
in the Access bibliography; Li's relevant full text was inspected previously.

## Format and publisher access blocker

The official template URL discovered on Elsevier's author resources page is:
https://legacyfileshare.elsevier.com/promis_misc/softwarex-osp-template.docx
The direct download returned HTTP 403 in this pass. The official Insights page
also failed via the web tool; the in-app browser showed a human-verification
page. No CAPTCHA was completed. A generic Word template was not substituted.
The content draft is therefore Markdown, not a verified official DOCX.

Prior official-guide receipt: docs/research/fast-journal-fit-20261001.md records
4000 words excluding stated metadata/references, up to six figures, mandatory
template and source-layout requirements. These need refreshing before filing.

## Timeline and ranking provenance

The earlier official Insights receipt records 7 days to first decision,
43 days to decision after review, 98 days to acceptance and 12 days from
acceptance to online publication. A current third-party listing at
https://www.pjip.org/journal/1020765/softwarex repeats these values. Current
publisher values could not be refreshed in this pass. Do not add stage values
as if they were sequential intervals; first decision may be editorial screening.

The author reports a recent move to category 3. Available current public
lookups identify Xinrui 2026 category 3 and JCR Q3, alongside historical CAS
2025 category 4. Keep the system/year label in administrative materials;
do not silently reinterpret a Xinrui result as CAS. Ranking does not affect
the selected Original Software Publication article type.

## Remaining manuscript gates

1. Retrieve the mandatory template and preserve its formatting; map draft
   content to its actual slots, then render and inspect all pages.
2. Select immutable product/supplement revisions and an archival release;
   current branch and experiment revision deliberately differ.
3. Resolve current guide requirements including source-layout expectations,
   declarations, repository metadata and any required ORCID. Funding and
   conflict statements have not been invented in the draft.
4. Establish a publishable evidence subset or keep the explicit private-data
   limitation. The private raw archive/prototype are not cleared for upload.
5. Review the software impact argument. This draft does not establish external
   adoption; adding length alone cannot close the contribution gap.

Preserve the DSN frozen tag, Access draft and unrelated review files. Continue
from these files; do not repeat the broad literature or GPU campaign.
