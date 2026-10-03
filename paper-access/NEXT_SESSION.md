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

The subsequent contribution gate is recorded in CONTRIBUTION_GATE_20261002.md.
The B0 CPU receipt actually includes P-stop and matches W3 for F00/F02/FPRE
count and completion outcomes, so rerunning E1 unchanged has no value. The
private C TAR still matches its recorded hash, but its broad contents require
a selective privacy review before any release. Li full text was unreachable in
this pass; the novelty gate remains open. Current recommendation is to pause
Access expansion and assess a bounded tool/software route, without changing
the author's submission choice or starting experiments.

SoftwareX route readiness is assessed in SOFTWAREX_READINESS_20261002.md.
The existing GitHub repository is public and MIT licensed. An offline wheel
build plus isolated `verify` command passed, and the v0.6 anonymous demo passed
four clean-extraction checks. The wheel contains product guard code but not the
research exporter; the demo is not the whole product. The private raw TAR is
not publication-ready. No SoftwareX manuscript, new release or submission was
made. The user has since confirmed that `ChevalGrand520` is their own GitHub
account. The user then clarified that `Capricorn` is only a computer account
name and should not be the software/publication byline. `LICENSE` and
`pyproject.toml` now use the approved byline `Zhen Cheng`; historical
account-name records remain unchanged. The author subsequently authorized
the institutional website affiliation wording, recorded below.

Release-candidate inventory is recorded in
SOFTWAREX_RELEASE_CANDIDATE_INVENTORY_20261002.md. The offline wheel/sdist build
passed; the wheel omits the research exporter. A clean v0.6 demo passed four
offline commands; the focused Python 3.12 research suite passed 96 tests.
The bare Mac Python 3.13 full suite failed (23 failures, 29 errors, 32 skips
of 1,173 tests), so no full release gate is claimed. No candidate archive was
published, and the private paired raw TAR remains outside the repository.

The private paired-capture release design is recorded in
PAIRED_CAPTURE_RELEASE_DESIGN_20261003.md. A read-only inventory script under
paper-access/ scanned all 1,273 regular TAR files and 465 decoded WebSocket/
history payloads without printing values. Original audit on an owner-only
temporary extraction returned PASS, 1,561 checks; this is not independent
execution authentication. A reduced public candidate needs a separate
transformed-byte audit, because the original audit checks 1,038 source files
and raw byte hashes. No sanitized archive was built or published.

The local `paired-sanitized-v1` prototype now preserves the six derived rows
and paired semantic equality in a clean directory; its verifier passed and a
tampered send-sequence negative failed. It remains private and omits original
source/raw/image/process checks. No candidate archive or pseudonym map was
published.

The 2026-10-03 ARIS-assisted follow-up is in
`AUTONOMOUS_RESEARCH_GATE_20261003.md`. Official arXiv HTML for Li v1 was
read: its tested guard and recovery results overlap the Access contribution
more directly than the earlier abstract-only check established. Stop Access
lengthening and GPU case accumulation until a decision-changing comparator
and evidence path are designed. An offline macOS/Python 3.12 full model-free
run ended exit 1: 1,274 tests, 30 failures, 5 errors, 40 skips; this is not a
supported Windows/Ubuntu CI result. The current SoftwareX guide fetch was
blocked, and that route is still only a candidate. University pages name the
Chinese school differently from the author-provided wording; the author then
authorized use of the institutional website wording.

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
ChengZhen0105@outlook.com. The author confirmed `Zhen Cheng` as the formal
Romanized name. On 2026-10-03 the author instructed use of the institutional
website wording. The draft now uses "School of Computer Science and Technology
(School of Artificial Intelligence), Zhejiang Sci-Tech University", matching
the university journal's English affiliation. No street address has been
supplied. Do not add a supervisor for fees.
Access official average4 weeks
to accept/reject, not guarantee; APC2160USD plus taxes after acceptance.

The author subsequently instructed continuation with SoftwareX. A first
English OSP content draft now resides in ../paper-softwarex/manuscript-v0.1.md;
its claim matrix, format blocker, timeline provenance and remaining gates are
in ../paper-softwarex/DRAFT_STATUS_20261003.md. The official DOCX download
returned HTTP 403 and the publisher Insights browser page showed human
verification, so the draft is Markdown rather than official-template formatted.
No submission or new experiment occurred. Next: obtain the mandatory template
and map the drafted content to its actual slots, then review software impact
and immutable release selection.
Li full-text retrieval is closed, but its overlap currently argues against
expanding the present Access study. Yu survey remains abstract-level checked.
No new GPU run, model
download, public raw release, external reviewer message or actual submission
implied by this handoff.
Windows SSH must use verified numeric tailnet IP, never MagicDNS; no GPU access
without live resource/reservation checks.

Preserve unrelated untracked DS reviews, .review-* directories and .DS_Store.
Private author ZIPs/raw captures remain off GitHub. Keep source/evidence/workload
boundaries explicit; author-declaration and manuscript claims require human review.
