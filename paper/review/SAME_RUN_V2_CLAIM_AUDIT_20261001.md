# V2 same-run claim audit — 2026-10-01

**Overall: WARN. V2 empirical checks: PASS.**
**Review independence: same-family. Acceptance: provisional.**

V2 empirical counts, complete same-run argument reuse, unchanged manifests, and the observed submission_outcome_unknown guard signature PASS. Overall WARN only for bounded provenance/causal mappings; no numerical mismatch.

This is a continuation of the v1 reviewer, with independent recomputation of the v2 retained bytes. It is **not** a fresh zero-context review. No v1 report, manuscript or evidence file was modified.

## Verified result

| Case | Calls | POSTs | Bound lifecycles | WebSocket / history | Cache / progress | Retry error |
|---|---:|---:|---:|---:|---:|---|
| W3 F00 | 1 | 1 | 1 | 90 / 1 | 1 / 30 | — |
| W3 F02 | 2 | 1 | 1 | 10 / 1 | 1 / 0 | submission_outcome_unknown |

The F02 result and outcome independently retained by the caller/controller agree on `submission_outcome_unknown` at `generate_round`, exit 0, no timeout and `submission_guard_observed=true`. The caller propagates the structured MCP error code; the controller checks this code and stage in addition to equal session/run/argument digests and no additional POST. This distinguishes the recorded v2 rejection from the v1 masking error, subject to the retained-record provenance limits below.

The full generation-argument digest was recomputed using the source's canonical JSON rule. Run identity, key, seed, context and request digest match. The first after-manifest and both retry manifests are byte-identical, unresolved, and contain unknown submission with no durable job. The existing source calls normal generation with saved arguments after rebuilding inventory in each fresh MCP process; no caller-side bypass is present.

All 100 WebSocket body hashes and 2 history hashes match decoded bytes. Channel sequences are contiguous. All 23 per-case capture-file hashes, root preflight/config hashes and the retained source-hash dictionary match. Each case has one start and one `executing` event with `node=null`, correlated with its accepted receipt and successful completed history. Binding timestamps and published identifiers agree. F02 cache=1/progress=0 does not establish fresh physical GPU computation.

Both inspected source files use LF locally; converting only their line endings to CRLF reproduces their captured Windows SHA256 values exactly. The JSON records both actual local hashes and this explicit comparison; it does not falsely assert byte equality.

## Remaining limits

- The revised source explicitly limits argument equality to reuse within the same run and displays separate v1/v2 table rows; these wording/table clarifications pass.
- The stable product error and normal caller path support a bounded guard-rejection observation. Product internal source, raw MCP response bodies and source-tree immutability receipts were not declared; this is not an authenticated internal branch trace or proof of unchanged product files.
- The v1 inventory explanation remains qualified. This v2-only pass does not re-audit v1 source or certify its full causal error path.
- Retained-byte consistency does not establish authenticity, completeness, physical GPU work, image quality, eventual completion, population efficacy or third-party access to private capture. New payloads do not reconstruct the historical campaign.

## Claim ledger

| ID | Location | Claim | Status |
|---|---|---|---|
| V2-01 | main.tex:13-13 | Abstract v2 guard observation and lack of reconciliation | exact_match |
| V2-02 | main.tex:325-338 | V2 table F00 C/S/E 1/1/1 and F02 2/1/1; call labels | exact_match |
| V2-03 | main.tex:353-356 | Both fresh MCP processes rebuild pinned inventory using exact-file index, fingerprint and private-catalog checks | exact_match |
| V2-04 | main.tex:355-356 | Complete generation arguments reused unchanged within the same run | exact_match |
| V2-05 | main.tex:355-356 | Frozen product unchanged and locked-route validation not bypassed | ambiguous_mapping |
| V2-06 | main.tex:357-359 | Retry returns target error at generation and controller reports guard true | exact_match |
| V2-07 | main.tex:358-359 | One total POST and unchanged unresolved manifest | exact_match |
| V2-08 | main.tex:359-361 | One fixed response-loss case observes submission blocking, without completion | exact_match |
| V2-09 | main.tex:361-362 | Inventory change supports v1 explanation without proving full cause | ambiguous_mapping |
| V2-10 | main.tex:364-365 | V2 captures 90 F00/10 F02 WebSocket payloads and one history response each | exact_match |
| V2-11 | main.tex:365-366 | Byte hashes and channel sequences checked | exact_match |
| V2-12 | main.tex:366-368 | One start, one executing node=null and successful history per case with published binding identity | exact_match |
| V2-13 | main.tex:368-371 | No authenticity/completeness or fresh physical GPU inference | exact_match |
| V2-14 | main.tex:371-372 | New payloads do not recover historical events; no third call/fresh-run fallback | exact_match |
| V2-15 | main.tex:401-403 | Separate v2 observation preserves v1 negative result | exact_match |
| V2-16 | main.tex:433-438 | One fixed v2 case does not establish population or execution-count advantage | exact_match |

Audited 31 declared files. Manuscript SHA256: `sha256:d29ecd89bf053035dc05f21255768986d94e8e44feba521a269bb67620793e85`. All declared-input hashes, per-claim evidence, raw-check booleans and privacy-filtered forensic prompt/response metadata are in the sibling JSON. Embedded private host paths, run identifiers, prompts and raw payload text are excluded.
