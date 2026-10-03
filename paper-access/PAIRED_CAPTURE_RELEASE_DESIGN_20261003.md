# Paired-capture supplementary artifact design, 2026-10-03

Status: local design and private-file inventory only. No raw capture was added
to Git or published. Preserve the original TAR identified by SHA256
`141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3`.
The inventory command and its member-level JSON report remained local; the
report is not a publication clearance or an anonymized deliverable.

## Baseline and actual dependencies

The original TAR contains 1,273 regular files. A clean extraction into an
owner-only temporary directory followed by
`python3.13 scripts/research/audit_paired_windows_capture.py <campaign>`
returned exit 0: `PASS`, 1,561 checks, no failed checks, and six operations /
ten product calls / eight proxy POSTs / six upstream sends. This is byte
consistency and replay through the project's oracle implementation, not
independent authentication of the Windows execution.

`paper-access/inventory_private_capture.py` walks all regular TAR members
without extracting them, rejects link/traversal members, scans marker
categories, decodes the WebSocket/history base64 fields and verifies each
embedded SHA256 before scanning. It does not print prompt, path, account or
payload values. The private inventory found:

| File class | Count | Release assessment |
|---|---:|---|
| Backend source snapshot | 908 | Exclude from a minimal capture package; verify the pinned source commit separately. Check upstream license if any source is redistributed. |
| Other source snapshots | 184 | Exclude unless a specific source file is necessary for replay; pin the exact reviewed implementation separately. |
| Client records | 66 | Include only transformed records required for call counts, semantic pairing and before/after manifest checks. Session arguments contain prompt, model/route identities and local output/product paths. |
| Observer records | 45 | Candidate inputs include operation report, proxy receipts/stages and outcomes. Inspect all free-text/error fields before inclusion. |
| Raw transport | 6 | Candidate inputs include `oracle-raw.json`; 465 embedded messages/history bodies passed retained-hash checks. No direct marker hit was observed in these files, but that is not a privacy clearance. Inspect decoded JSON and nested metadata manually. |
| Operational logs | 14 | Exclude from the minimal package unless a specific conclusion depends on one; logs can contain host, process and path details. |
| Product outputs | 14 | Includes manifests and generated PNG/JPEG bytes. Manifests have prompt/route fields; exclude images unless redistribution rights and metadata are reviewed. |
| Campaign metadata | 36 | Keep only fields necessary for the selected audit result, with explicit source mapping. |

The heuristic scan found 28 account-name, 464 host/device, 11 macOS home-path,
1,272 private-field and 56 credential-field *marker occurrences* across the
TAR. Most hits can be field names or code literals rather than secrets; zero
hits do not establish absence of sensitive data. Never publish the member-level
report or original TAR solely on the strength of these counts.

## Minimum transformed input set

For each of the six operations, the present audit reads:

- `observer/operation-report.json`, `proxy-receipts.json`,
  `proxy-stages.jsonl`, `oracle-raw.json` and `operation-outcomes.json`;
- `client/session.json` and the before/after manifest snapshots for every
  product call;
- `cleanup.json` and output PNG bytes for its source and artifact checks.

At campaign level it reads `runner-report.json`, `source-freeze.json` and all
1,038 referenced source-snapshot files. Those source checks form a large part
of the 1,561 total. The current audit cannot simply be run on a reduced set.

The candidate should use a **new, named transformed-capture schema** and a
separate read-only audit script, rather than altering the original campaign or
calling a reduced audit an original 1,561-check replay. Required transforms:

1. Replace prompt text, local paths, host/account/device names and route/model
   identity tokens with stable scoped pseudonyms; preserve equality within and
   across the paired cases where the comparison requires it. Record the private
   source-to-pseudonym map outside any reviewer package.
2. Decode each WebSocket/history body as structured JSON, transform nested
   identities and paths, re-encode it, and record **new transformed-byte
   hashes**. The old SHA256 values must remain in the private provenance map,
   never be represented as hashes of the new bytes.
3. Transform session arguments and before/after manifests consistently.
   Recompute the transformed semantic and manifest digests under a versioned
   transform. Verify paired equality and original-run state from those new
   bytes. Do not treat an unchanged original digest as proof after redaction.
4. Replace the 1,038-file source snapshot check with a separately labeled
   source-version receipt containing reviewed Git commits, source hashes and
   implementation identity. Do not claim this independently proves which code
   ran on Windows.
5. If output images are excluded, replace the artifact-byte rehash assertion
   with an explicit `not_reproducible_from_candidate` result. A retained hash
   receipt alone is not byte validation.
6. Manifest all candidate files, normalized archive metadata and transform
   version; test from a clean extraction without private path dependencies.

## Proceed / stop gates

- **Proceed to a private candidate build** only after defining exact JSON
  field transforms and a stable-ID mapping that preserve all six derived rows.
  Compare transformed-audit output to the public projection and report every
  omitted original check by name and count.
- **Stop before any release** if prompt/model/path/host/account text survives
  nested JSON, base64, image metadata, logs or file names; if source licenses
  cannot be established; or if transformed records no longer preserve paired
  semantics and original-run completion distinctions.
- **Do not call the candidate publicly reproducible** until an independent
  clean extraction reproduces its *own* declared checks and the author approves
  the exact file list and disclosure scope. This approval has not been given.

The existing v0.6 anonymous demo remains a separate offline mapping artifact.
It cannot be silently combined with this transformed-capture candidate or
described as proof of live guard execution.

## Local transformed-capture prototype

`paper-access/paired_sanitized_candidate.py` now builds a local
`paired-sanitized-v1` candidate from the private TAR. It keeps only anonymous
event types, stable pseudonymous job/node/run IDs, proxy sequence/status data,
history completion booleans, call-level errors/states and a transformed
generation-argument tree. The tree pseudonymizes both scalar values and nested
field names, so dynamic JSON keys cannot directly expose input names. It
discards original payload bytes, prompts, paths, source snapshots, logs,
process receipts and image bytes. Builder and verifier restrict call run states
and error codes to the observed closed vocabularies, rejecting unknown strings.

After this hardening, a new owner-only local candidate was built from
the hash-pinned private TAR. A clean directory containing only the four
candidate files passed its embedded verifier and matched the six public rows:
6 operations, 10 calls, 8 proxy POSTs and 6 upstream sends. All 29 distinct
semantic-tree keys had pseudonymous `id-` form. A modified paired semantic
tree and an unknown call state were each rejected after recomputing the
candidate file hash. A heuristic marker scan found no account, home-path,
device or model marker in the candidate. The pseudonym key remains outside
the candidate with mode 600. The first local prototype predates this hardening
and must not be used as the reviewed version.

This is a **private prototype**, not a release artifact. It omits the original
source/hash, raw-byte, manifest-byte, PNG-byte, process and cleanup checks. Its
PASS means only that the transformed subset preserves the six derived rows and
declared paired semantics. It does not authenticate the original execution or
replace the 1,561-check audit. Human review of fields, licenses, archive
metadata and the exact file list remains required before any disclosure.
