# Reproducibility evidence note

This companion note retains audit details consolidated out of Section V in
the v0.16 narrative revision. It adds no measurement and changes no evidence.

## Materials and campaign separation

CPU records contain product revisions, harness digests and event traces.
The Windows ledger identifies source revisions and reports. Audit and figure
scripts operate offline on retained records. Live repetition requires the
pinned backend, model, workflow and private setup.

The historical four-case campaign was not rerun. The separate same-run
campaigns used existing models and the frozen product. Both the v1 masking
failure and the v2 observation are retained. Private raw captures are excluded
from delivery, so third parties analyse the included records and projections.

## Historical audit and artifact coverage

Historical JSONL contains sanitized summaries, bindings, terminal labels and
aggregate counts, rather than complete WebSocket payloads and history
snapshots. Its audit checks consistency and regenerates two tables.

The oracle's completion rule requires `executing` with `node=null` and completed
history. The exported terminal label is assigned by construction and omits the
node discriminator. Checking this label verifies the internal convention,
not completion independently. The original start-count discrepancy is discussed
in the main results; additional unbound starts remain independently unexcluded.

Report/JSONL equality and image-byte correspondence are historical inspection
receipts, not checks repeated by the offline audit. Host-side hashing matched
four generated-call artifact hashes to retained bytes, with one product-output
PNG per case. The first unresolved F02 call has no recorded product artifact
hash, so its output bytes are outside those checks. Oracle path fingerprints
hash metadata, while artifact hashes cover image content. Neither is a visual
quality or final user acceptance evaluation.

## Observer coverage

Both receiving events and binding them must occur within the capture window.
Missing events leave execution uncertain. CPU and Windows observers have
different failure boundaries; neither offers crash-complete auditability.

The fixed protocols support observations on the recorded setup. Deployment
rates, comparative performance and robustness across models need broader
evaluation. The v2 submission-blocking observation is distinct from physical
GPU work and an execution-count advantage. The cache evidence and its
implications remain in the main results.

## Offline conversion and anonymous demonstration

The converter keeps the retained product manifest and audited backend lifecycle
as separate inputs:

| Case | Execution | Evidence | Recovery | Composite verification |
|---|---|---|---|---|
| F00 | succeeded | partial | not needed | false |
| F02 | succeeded | missing | required | false |

No independent artifact validator was supplied. Four synthetic variants,
two missing-state and two job-identity-conflict, exercise unknown recovery and
mismatch evidence. They are not additional Windows experiments.

A clean-copy replay preserved all input bytes and reproduced the interpretation
summary. The anonymous demo provides whitelisted, pseudonymized projections
with the same interpretation states as the private conversion. It reproduces
semantic mapping. Auditing the raw events requires access to private captures.
