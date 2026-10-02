# IEEE Access preparation handoff — 2026-10-02

Actual repository: /Users/chevalgrand/Documents/ paper dsn/review-checkouts/local-gpu-imagegen-dsn-writing
Branch: codex/ieee-access-adaptation-v1. Remote: ChevalGrand520/local-gpu-imagegen.
Find current exact SHA and upstream from Git before proceeding.

Milestone: DSN Tool evidence/manuscript cycle complete through v0.22, with five
model-assisted review rounds. DSN tag dsn-tool-v0.22-frozen points to a53bdfa.
Do not move that tag. A later user-approved AI declaration edit to paper/main.tex
and its regenerated six-page PDF is committed separately; the freeze still
identifies the earlier archive. DSN has not been submitted.

Access work resides in paper-access/, not paper/. Official May2026 template
resources are unchanged. A 175-word abstract and RQ1--RQ3 frame submission
withholding, completion cost and same-information interpretation. Evidence-bound
is defined explicitly; Temporal/outbox/service idempotency responsibilities are
compared without superiority claims. EVIDENCE_GAPS.md and literature receipt
record the current limits. Yu survey DOI10.1145/3732777 exists, but reviewer
venue/year/count were wrong; metadata/abstract checked, full text not read.

Core evidence: corrected-observer Windows batch C source08539d5, six operations,
10 calls/8 proxy POSTs/6 upstream sends. F02 B2/W3 2/1 POSTs and lifecycles;
B2 completes, W3 original run unresolved. FPRE first no-send truth: B2 retries
and completes; W3 blocks, zero upstream, unresolved. Second B2 F02 lifecycle
reports cached nodes3..9; operation aggregate progress30 does not assign GPU
work to the second lifecycle. No measured compute saving. CPU P-stop equivalent
and ordinary parser classifications equal; retain these negative comparisons.
Raw private C TAR outside repo has SHA256
141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3.
Audit1561 retained-byte checks PASS, not independent execution authentication.

Compiler blocker resolved on 2026-10-02 with a portable task-local TeX Live
2026 under /tmp/paper-access-texlive. The official ZIP SHA256 matched the
recorded value; missing IEEEtran.cls and bullet.png were restored from it.
The class is unchanged. pdfLaTeX/BibTeX via latexmk built paper-access/main.pdf
(7 pages); all seven pages were visually inspected. Tectonic/XeTeX still cannot
compile the official spot-color primitive. The local /tmp compiler may not
survive a reboot; README records the build command. Compilation does not mean
submission readiness.
For the author update, the compiler was recreated in
/Users/chevalgrand/.cache/paper-access-texlive; pdfLaTeX/BibTeX again produced
a seven-page PDF and the updated first page was visually checked.

Results now have explicit RQ1--RQ3 subsections. RQ1 records one withheld
submission in the fixed accepted-response-loss pair; RQ2 records unresolved
original runs, including the no-send FPRE block; RQ3 reports equal
same-information parser classifications. No experiment or comparison was added.
Official template publication fields are visibly pending, without invented
DOI, volume, year or history.

The 2026-10-02 model-assisted DS review was dispositioned in
DS_REVIEW_DISPOSITION_20261002.md. The manuscript now labels historical and
paired protocols more explicitly, corrects the Python requirement to 3.11+,
and states that private paired raw captures are unavailable for third-party
recalculation. The review's claim that both Access table inputs are untracked
was false: `git ls-files` confirms both. No new results were added.

AI declaration approved verbatim by user and applied to both working sources:
OpenAI Codex assisted with language refinement, experimental code prototyping,
and cross-checking of author records. The author reviewed and revised the
resulting materials and takes full responsibility for the manuscript.
No additional entirely-by-authors sentence was approved. Do not imply AI is an
author or that model-assisted checks are human peer review.

User direction: prepare Access as single submission route; never submit overlapping
DSN/Access manuscripts concurrently. User reports school reimburses papers with
Zhejiang Sci-Tech University first affiliation; this is user-provided, not a
verified reimbursement amount/procedure. Sole human author and correspondence
intended. User supplied the name Cheng Zhen in Chinese (程臻), the College of
Computer and Artificial Intelligence in Chinese, and the correspondence email
ChengZhen0105@outlook.com. The draft provisionally uses Zhen Cheng and
"School of Computer Science and Artificial Intelligence" pending confirmation
of preferred Romanized name order and official college English wording. No
street or postal address has been supplied. Do not add a supervisor for fees.
Access official average4 weeks
to accept/reject, not guarantee; APC2160USD plus taxes after acceptance.

Next: confirm Romanized name order and official college English wording, then
decide whether the bounded six-operation
contribution and available software/evidence distribution support an Access
research submission. Yu survey citation is abstract-level checked only; full
text and publisher metadata remain a literature gate. No new GPU run, model
download, public raw release, external reviewer message or actual submission
implied by this handoff.
Windows SSH must use verified numeric tailnet IP, never MagicDNS; no GPU access
without live resource/reservation checks.

Preserve unrelated untracked DS reviews, .review-* directories and .DS_Store.
Private author ZIPs/raw captures remain off GitHub. Keep source/evidence/workload
boundaries explicit; author-declaration and manuscript claims require human review.
