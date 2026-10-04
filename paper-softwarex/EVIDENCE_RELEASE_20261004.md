# Author-approved minimized Windows evidence distribution

Date: 2026-10-04. The author explicitly approved public distribution of the
reviewed seven-file packet and corresponding manuscript-availability updates.
Evidence revision: 345da1f44ad6d67a5cc637c31edb2db607a37480.
Directory: evidence/paired-windows-minimized-v2/.

Files: capture.json, projection.json, verify.py, manifest.json, README.md,
LICENSE and SHA256SUMS. The core capture/verifier/projection/manifest match the
approved local candidate. README release status was updated after approval;
SHA256SUMS was refreshed to cover that wording change. No original TAR,
pseudonym key, private extraction, bytecode cache, images or private trace is
distributed. Original archive identity is committed by SHA256 in the manifest.

## Verification and limits

Local preparation replayed the original retained records: 1561 checks passed,
without a backend call or new execution. A fresh transformation reproduced the
candidate fields. Six rows match both the original replay and public projection;
totals are six operations, ten product calls, eight proxy POSTs and six upstream
sends. Missing history, terminal-before-start and changed-run negative cases
were rejected. Clean extraction and the copied public standalone verifier
passed; the seven-file whitelist and SHA256SUMS passed.

Public data contain 459 event records and six history observations, with
consistent identifier pseudonyms. The field selection and omissions are
documented in the packet README. The reader can recompute the six transformed
rows. Full original payload/source/manifest/image byte checks, cross-stream
timing and the complete original oracle causal-binding contract remain omitted.
These checks do not independently authenticate execution or establish general
reliability, GPU savings or policy superiority.

## Independent-review status

One fresh gpt-6-astra/ultra reviewer was invoked through aris:experiment-audit,
same-family/provisional. It returned intermediate raw replay, mapping and
privacy findings. It identified a Python cache containing an absolute source
filename and overbroad sequence-continuity wording; the cache was excluded,
and the wording was narrowed before approved packaging. The reviewer exhausted
its usage allowance before producing a final A–F report. Audit status is ERROR
(reviewer_usage_limit_before_final_report), not a new independent PASS.
Private trace is retained outside the public repository. Historical v0.8
PAPER_CLAIM_AUDIT files retain their original verdict/input scope.

## Manuscript

v0.12 cites the immutable packet revision and distinguishes subset recomputation
from raw replay/authentication. Abstract 98 words; Markdown 3636 words; nine
rendered pages, all inspected. Tables, references and author declarations remain
unchanged. Bundled build preserves 26 original template parts. The letter and
declaration/checklist drafts reflect the approved data distribution.

This approval does not authorize stable-branch merge, journal submission or
APC payment. Final author content review and current publisher/portal checks
remain separate outstanding steps.
