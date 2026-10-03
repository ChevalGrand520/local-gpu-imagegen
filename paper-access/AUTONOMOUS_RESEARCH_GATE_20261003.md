# Autonomous research and release gate, 2026-10-03

Status: author-side ARIS-assisted assessment. No GPU experiment, private-capture
publication, new release, stable-branch merge, journal submission, or human peer
review occurred. This note records a stopping decision for the current claim,
not a prediction of an editor's decision.

## Nearest-work check

Li, *Where Does Exactly-Once Live?*, arXiv:2609.29095v1, was read in its
official full-text HTML, particularly Sections 3, 6.1, 6.5 and 7 and the
experiment-setup passage describing the guard conditions:
https://arxiv.org/html/2609.29095 . It defines observation-equivalent absent
and late-commit outcomes, proves a verification-only limit without a known
in-flight bound, evaluates read-back and escalation, and tests a guard that
remembers unknown writes, refuses unverifiable repeats and annotates
uncertainty. Its benchmark uses simulated services and a much broader set of
faults and agent/harness conditions. These are the paper's claims, not results
reproduced by this project.

Our product remains a distinct concrete integration: a persistent local
generation run, a same-run admission veto and an exporter that separates run
state from supplied ComfyUI observations. The six corrected Windows operations
show the accepted-response-loss withholding case and the pre-send false block.
They do not establish a novel recovery-policy class, superior duplication
rate, better completion rate, compute savings or an advantage over Li's guard.
The CPU stop-after-unknown comparator and same-information parser also match
the proposed method on their reported outcomes. The current Access draft
correctly labels Li as a simulated benchmark and does not compare counts
across studies, but its research contribution remains too narrow for an
evidence-backed recommendation to expand or submit it now.

**Decision:** stop automatic Access lengthening and GPU case accumulation.
Reopen the research route only with a preregistered, decision-changing measure
that distinguishes this integration from both a simple caller-side stop and
existing guard work, with a reviewer-inspectable evidence path. A revised
question and comparator are prerequisites to any new run.

## Supported-platform software gate

The repository CI runs its full model-free suite on Windows and Ubuntu with
Python 3.11/3.12 and test dependencies. A local macOS run used Python 3.12
with cached Pillow, setuptools and py7zr via offline `uv`. It completed
1,274 tests in 112.961 s with exit 1: 30 failures, 5 errors, 40 skips.
Observed failures include macOS-unsupported `/proc/self/fd` and atomic report
installation paths, isolated pip installation failure, and one tracked Windows
absolute workspace root caught by repository hygiene. The invocation document
now uses project-relative paths; revalidation is required. This is a failed local
full-suite gate, not a Windows or Ubuntu CI result and not proof of a single
cause for all failures. The earlier focused 96-test research suite and isolated
wheel `verify` passed, but cannot replace a supported Windows product gate.

SoftwareX remains a candidate software route, not a ready submission. The
publisher's current Research Elements page identifies SoftwareX as a venue
for detailed descriptions of research software and links its author guide and
template: https://www.elsevier.com/en-gb/researcher/author/tools-and-resources/research-elements-journals .
The live guide could not be fetched here (HTTP 403), so current word, figure,
template and fee requirements are **unverified in this pass**. The official
SoftwareX reviewer form also asks for convincing impact evidence and complete
software metadata: https://legacyfileshare.elsevier.com/promis_misc/softwarex-reviewer-form.pdf .
No external uptake or broader scientific impact is measured in this record.

## Evidence and author metadata

The private `paired-sanitized-v1` prototype passed its own clean-directory
subset verifier in the prior milestone. It omits original raw/source/image and
process checks. The original 1,561-check audit and transformed audit answer
different questions; neither independently authenticates Windows execution.
The exact candidate file list and any disclosure still need author review.

The author approved `Zhen Cheng` as the formal name. Institutional pages
currently call the Chinese school `计算机科学与技术学院（人工智能学院）`, whereas the
author-provided wording was `计算机与人工智能学院`. A university journal has used
`School of Computer Science and Technology (School of Artificial Intelligence)`:
https://xuebao.zstu.edu.cn/oa/darticle.aspx?id=20241112&type=view .
The institution's current school page is https://jsjxy.zstu.edu.cn/ .
This evidence does not establish the author's own affiliation unit or its
required English byline. Confirm the exact affiliation with the author before
changing the manuscript or filing it.

## Next decision gates

1. Resolve the formal affiliation and choose whether to pursue an improved
   Access research claim or a SoftwareX software description. No concurrent
   submission of overlapping manuscripts.
2. For SoftwareX, run the supported Windows/Python release gate and inventory
   the product, supplementary exporter and candidate data as distinct objects.
   Confirm the tracked-path correction and the full supported CI matrix before
   any release claim.
3. Review privacy and rights for the precise transformed candidate. Its PASS
   cannot be relabeled as a replay of private raw evidence.
