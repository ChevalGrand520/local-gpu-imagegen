# Official SoftwareX template contract

Reference: /Users/chevalgrand/Documents/ paper dsn/review-checkouts/local-gpu-imagegen-dsn-writing/paper-softwarex/templates/softwarex-osp-template-v6.docx
SHA256: 9fcf40ede96a2f188ee4ef77134e0596d01e1b65fd9db63f2874d29f2ecb916d
Version 6, March 2026; obtained from Elsevier's author resources link.
Reference render: /tmp/softwarex-template-qa/reference, 4 pages, all inspected.
Section/style evidence captured with packaged audits.

One portrait Letter section: 12240 by 15840 twips, margins 1440 on all sides;
header/footer distances 720; one column, continuous line numbering.
Arial 11-point body, single line spacing. Clone existing paragraph/run
properties. Title and author instruction paragraphs use Heading1 but their
instruction italics must be removed. Main headings use existing automatic
numbering and bold 11-point Arial. Subheadings clone 2.1/2.2 numbering patterns.
Preserve styles, numbering, theme, font table and section XML unchanged.

Editable slots are word/document.xml body child indices in the retained file:
16 title; 18 author; 21/22 abstract heading/content; 25/26 keywords;
29 metadata heading; 33 metadata table (only right-hand data cells editable);
35 motivation; 44 software description; 46 architecture; 48 functionalities;
53 examples; 56 impact; 68 conclusions; 76/77 references.
Clone normal non-bullet body paragraphs from 23 for prose, removing only
instruction text/links, and heading pattern 76 for unnumbered declarations.
Clone these patterns for expanded prose. Mandatory five sections retained.
Delete instructions, their bookmarks/hyperlinks, reminder and optional empty
acknowledgements. No linked body references or content controls exist.

Metadata grid is 567/3554/5357 twips. Preserve the original left two columns
byte-for-byte, table properties and grid; replace right-hand instruction
paragraphs with regular 11-point text. Allow repeating header and prevent
row splitting. Add result table by cloning the table component, with six
columns within the same text width and source cell typography/borders.

All remaining package parts are preserve-only except word/settings.xml
(updateFields=true for PAGE refresh) and docProps/core.xml (actual author and
title). Existing footer PAGE field and all header/footer parts remain unchanged.
No drawings, SDTs or embedded media. Footnotes/endnotes are template separators,
not manuscript notes, and remain unchanged. Package part hashes/inventory are
saved by builder into template-part-inventory.json before writing output.

Fidelity gate: original reference hash unchanged; only the three declared
parts may differ; metadata labels and section geometry identical; retain
automatic heading numbers and footer page field. All final pages must be
rendered and inspected. New pagination due to filled content is expected.

## v0.3 revision scope

Reviewer-requested architecture picture adds one inline image under 2.1;
word/media/image1.png is new, and document relationships and Content Types
are editable for the image only. Other relationships are semantically preserved.
Impact gains Heading1 navigation style, an intentional change from the source
template's unstyled Impact heading. The five-section numbering is preserved.
No section geometry, styles.xml, numbering.xml or footer change is permitted.
All other original package parts remain byte-identical (26 parts).

## v0.6 through v0.9 revision scope

Two inline explanatory images are embedded under architecture and known-job
recovery. word/media/image1.png and image2.png are new; image relationships and
Content Types remain the only additional mutable parts. Caption disclosure and
author-confirmed funding use normal body paragraphs. The five required sections,
metadata label cells, section geometry, styles, numbering and footer remain
preserve-only. Eight total pages in v0.9 are expected after filling these slots;
all pages must still pass visual inspection. The total-page count is distinct
from the template's main-body allowance excluding metadata, tables, figures and
references.
