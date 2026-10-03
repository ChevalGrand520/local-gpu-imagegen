# Disposition of supplied SoftwareX model review

Input: user's pasted independent read-only review of v0.2 at dfc8378.
This is author-side verification/disposition, not an editor response, human
peer review or acceptance judgment. Working revision: manuscript-v0.3.

| Review item | Disposition |
|---|---|
| P0-1 missing Licence.txt in pinned 088ea61 | Valid preparation gap. All v0.3 metadata/availability links now pin dfc8378, which has README, Licence.txt, Zhen Cheng package metadata and research/evidence files. C1 is version only. The old snapshot claim was factual but not yet format-ready; not data fabrication. |
| P0-2 main/release requirement | Explicit immutable commit is retained; default main differs and is disclosed. The template requires a GitHub repository/permanent version link, not a main merge. No main merge, release/tag or public history rewrite is authorized merely by this review. Final source/package archival policy still needs the full guide. |
| P1-1 Impact Heading1 | Add Heading1 for navigation consistency. The official template itself lacks this pStyle; v0.2 faithfully inherited it. A missing Heading1 alone was not evidence of a missing mandatory section or a template departure. Original sectPr claims concern section geometry, not paragraph styles. |
| P1-2 software demonstration/impact | Add architecture figure, get_run fields and source-checkout workflow; rewrite Impact around implemented inspection/measurement capability. External adoption/research-output gap remains explicit. |
| P1-3 Li positioning | State closely related mechanism and local completion-cost examples. Clarify known-job history polling versus missing-job-ID ambiguity. Do not claim Li never measures completion costs or that its theorem proves our F02 failure unavoidable. |
| P1-4 versioned validation | Current session reran 96 research tests and isolated wheel check at dfc8378; receipt contains commands, revision and scopes. Distinguish older 13-test subset and synthetic probe receipts. |
| P2-1 synthetic probes | Explicit synthetic/offline/no Windows or GPU, fixture inputs distinct from capture bytes, Python 3.13.15 receipt and source revision. |
| P2-2 CI machine | Restore explicit GitHub-hosted/author physical machine distinction; prior sentence already labelled hosted runners. |
| P2-3 install/checker scope | README stale pre-PyPI wording corrected. Cite source install plus isolated rebuilt-wheel validation; state checker/exporter source-only. Published 0.9.1 exists but historical author metadata differs. No claim that published bytes equal source snapshot. |
| P2-4 DOI | No archive DOI invented. Version moved to C1, commit permalink C2. Template says add DOI if supplied; full guide archival mandate remains unverified. |
| P2-5 format | 100-word abstract and six keywords retained; five main sections remain. Actual v0.3 page count/render recorded after generation. |

Additional corrections to the review: 088ea61 contains paper-softwarex/v0.1
Markdown, although it does not contain v0.2 DOCX. Its C2 was already a commit
permalink, not a mutable branch link. The official template says six main-body
pages excluding named material, not the review's later five-page shorthand.
Static counting of test functions does not prove execution; this revision
uses actual exit-zero receipts for the current research suite/wheel.

No GPU experiment is needed for these descriptive changes. They do not close
the external scientific-impact evidence gap. No submission, stable merge,
private-data disclosure, PyPI update or message to an external reviewer occurs.
