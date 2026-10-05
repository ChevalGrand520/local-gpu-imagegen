# Portal PDF check and submission metadata correction

The author-provided portal PDF contains an Editorial Manager cover page, nine
manuscript pages and a declaration-of-interests page. It is marked Manuscript
Draft; the manuscript-number field is blank. Its filename is not evidence of
successful submission. The page images show no obvious clipping or overlap.

Three submission metadata inconsistencies were corrected in v0.13:

- Four manuscript keywords now match the portal's four-keyword limit.
- The affiliation includes the previously verified full university postal address.
- C2/C7 and the availability paragraph identify the immutable submission
  distribution at 360c7232707199d40a4e3fd763e5031ed129b56a. The original
  product source remains dfc8378cb3d891f7951786bc4544cd971bd56a11 and the
  paired experiment remains 08539d5. The source mirror is explicitly distinguished
  from a new product or experimental result.

Checks: the abstract, illustrative examples/evidence, references and author
declarations are unchanged. The DOCX builder retained 26 unrelated template
parts byte-for-byte and two embedded images. The revised document renders to
nine pages without obvious clipping or overlap. Total Markdown whitespace word
count is 3,701, including metadata, references and author information; abstract
word count is 98. Remote branch lookup returned the exact 360c723 distribution
revision. No backend or GPU operation was performed.

v0.13 DOCX SHA256:
030044197c0799d1f6e53e1917e0d6155602c591fae60752d1c260a57572f699

Outstanding: replace the uploaded v0.12 manuscript with v0.13, supply the
separate figure images and editable SVG sources, regenerate and inspect the
portal PDF, and approve the submission. The existing interests declaration
can be retained. No actual submission receipt has yet been inspected.

The author's live publishing-options screen quoted USD 1,920 excluding taxes,
charged only on acceptance, and stated that subscription publication is
unavailable. The author chose to proceed while seeking funding, with withdrawal
before formal acceptance as the intended alternative if funding cannot be
secured. Acceptance timing cannot be predicted or used as a guaranteed deadline.
