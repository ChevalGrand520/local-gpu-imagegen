# Paired Windows capture: minimized, pseudonymized candidate

Release status: author approved public distribution on 2026-10-04.
Prepared and published on the dedicated manuscript work branch.
This is a transformed subset of retained observations, not a newly run
experiment, the original raw archive, or independently authenticated execution.

## Verify without a GPU

Requires Python 3.10+; standard library only. No install, network, backend or
model is needed. From this directory:

```sh
python verify.py audit .
```

The verifier computes proxy POSTs, upstream-send starts, accepted-job counts,
observed job-bound lifecycle counts, client completion, guard observations
and event-type counts from capture.json, then compares them with projection.json.
It does not calculate these counts from the projection. It checks event and
call sequence continuity, request-sequence uniqueness and send membership,
job/history associations, ordered lifecycle start/terminal events and equality
of the transformed paired request semantics. POST receipt sequence continuity
and cross-stream timing are not checked by this verifier.

| Case | Proxy POSTs | Upstream sends | Accepted jobs | Bound lifecycles | Client completed |
|---|---:|---:|---:|---:|---|
| F00 B2 | 1 | 1 | 1 | 1 | Yes |
| F00 W3 | 1 | 1 | 1 | 1 | Yes |
| F02 B2 | 2 | 2 | 2 | 2 | Yes |
| F02 W3 | 1 | 1 | 1 | 1 | No |
| FPRE B2 | 2 | 1 | 1 | 1 | Yes |
| FPRE W3 | 1 | 0 | 0 | 0 | No |

Six operations; ten product calls, eight proxy POSTs, six upstream sends.
These are fixed observations for one workload, not rates or a randomized study.
The synthetic stop control and known-job CPU fixtures are separate evidence.

## Files and provenance

- capture.json: pseudonymized per-operation observations, schema paired-sanitized-v2.
- projection.json: the previously published derived record used for comparison.
- verify.py: transformation and standalone checking code. The build command
  requires the private original archive and creates a separate private HMAC key;
  readers only need the audit command. No key is distributed.
- manifest.json: SHA256 of those three files and commitment to the original
  archive. A matching hash checks identity/integrity, not truth of an experiment.
- LICENSE: the existing repository MIT license, retained for the code.

Release packaging uses an explicit file whitelist. Python bytecode caches,
the private pseudonym key, original extraction and private review traces must
never be included.

Execution source revision: 08539d5. Original archive SHA256:
141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3.
Product snapshot and subsequent paper revisions are different revisions.

## Transformation

The builder reads the original TAR's six operation records in memory. Before
parsing WebSocket/history payloads it verifies each retained payload byte hash.
It selects the following fields and discards the remaining original bytes:

- POST receipt sequence, request sequence, HTTP acceptance status and anonymous job;
- upstream-send-start request sequences;
- WebSocket sequence, event type, anonymous job/node, and numeric cached node IDs;
- history response job, HTTP status and success flag;
- ordered product call index, anonymous run, retained state, error code and
  unknown-submission outcome;
- an opaque request tree for within-condition paired equality.

Jobs, runs, nodes and request-tree keys/scalars use HMAC-SHA256 pseudonyms
(96-bit truncation), consistent within this packet. The private random key is
kept outside the packet. Request-tree shape/equality remain visible; prompt
text, values and field names are opaque. The equality tree excludes run ID,
idempotency key, change summary, route token and endpoint identity as in the
retained prototype. It does not reveal the original workload's semantics.

The packet omits prompt text, personal paths, account/host/backend identifiers,
authorization/configuration, wall-clock and monotonic timestamps, source/backend
snapshots, payload bodies, images and process/cleanup records. Per-stream order
is retained; the packet cannot reconstruct cross-stream timing. Numeric cached
node IDs remain visible to inspect the reported caching observation.

## What these records establish

Readers can recompute the six reported rows from the transformed event/manifest
subset and inspect task associations, completion outcomes and cached-node events.
The author-side local preparation also replayed the original retained records:
1561 consistency checks passed, and its rows matched this packet. That local
result is not an independent proof that the described execution occurred.

This verifier is narrower than the original ComfyUI event oracle: it checks
start/terminal/history associations, not the entire original oracle's causal
binding and source identity contract. Original source-snapshot hashes, raw
payload hashes, manifest hashes, PNG byte hashes and process/cleanup checks
cannot be independently repeated from this minimized packet. Neither GPU
savings, general reliability nor policy superiority is established. The
original unmodified archive remains private. The old v0.8 audit is historical
and is not relabelled PASS by preparing or releasing this packet.
