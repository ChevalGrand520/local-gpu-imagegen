# Same-run paper claim audit — 2026-10-01

**Overall verdict: WARN. New same-run empirical claims: PASS.**
**Review independence: same-family. Acceptance: provisional.**

WARN for the whole-manuscript evidence coverage; PASS for the new same-run empirical claims and retained-byte consistency. No numerical mismatch found. Historical/source-only claims lack declared direct evidence.

Audited 37 declared files and 66 claim groups: 45 exact matches, 19 missing-evidence groups, 2 ambiguous mappings. The full claim quotes and every declared-input SHA256 are in the sibling JSON. Current manuscript SHA256: `sha256:1185fca24a268b79bdae3505705da819cd362995bcf8d9846d3e1d8083c81c74`.

## Verified new evidence

| Case | Calls | POSTs | Bindings | WebSocket payloads | History bodies | Starts / null terminals | Cache / progress |
|---|---:|---:|---:|---:|---:|---:|---:|
| W3 F00 | 1 | 1 | 1 | 90 | 1 | 1 / 1 | 1 / 30 |
| W3 F02 | 2 | 1 | 1 | 10 | 1 | 1 / 1 | 1 / 0 |

All 100 WebSocket payload hashes, both history hashes, all 23 published per-case capture-file hashes, and the published preflight/configuration hashes match. Each channel is contiguous from sequence 1. Snapshot and final transport agree. Decoded events match the normalized snapshots. Start, terminal, receipt and successful history share the same correlation identity; timestamps and published binding identifiers agree. Artifact-path fingerprints match their metadata strings, not image bytes.

The F02 saved full generation-argument digest was independently recomputed with canonical JSON and matches both results. Run identity, operation key and seed agree across retained records. The first after-manifest and both retry manifests are byte-identical. The retry returns `model_identity_drifted` at `generate_round`; the controller records `submission_guard_observed=false`. Consequently the absence of another POST does not validate the ambiguity guard. The cache event and zero progress events do not establish fresh physical GPU computation.

These are checks of received, retained bytes and internal binding consistency. They do not authenticate origin, prove capture completeness, rehash model/image bytes, or create independent third-party access to private capture. The execution identifier's source algorithm was not independently rederived because oracle source was not an input.

## Corrected wording

- The revised manuscript separates a **potential** pre-acceptance false positive from the observed incomplete client operation in an accepted-response-loss CPU fixture.
- It attributes same-run completion ordering to the controller and expressly notes that the retained capture does not independently timestamp the retry.

## Remaining bounded uncertainties

- Historical 40-test/7.110-second, Windows Python 3.15.0a8, and 7-test/0.003-second receipts are absent from the declared inputs. Attach original command outputs or retain them as explicitly not reverified by this audit.
- The two-record offline demo and all-twelve-unverified normalization output are not present; only the twelve CPU source records are verified. Include the actual normalization outputs; do not infer the result from source-manifest count.
- Historical fresh-run/seed formula, environment details, cumulative-decision implementation, and old-summary zero count require historical source/receipts beyond the derived extract. Keep report-level attribution distinct from independent reconstruction and supply those sources for wider assurance.
- Implementation properties, external related-work facts, detached checkout state, no-download history and final package declarations are outside the declared raw-result set. Use separate source/citation/package checks; this bounded audit does not certify them.

Historical totals do reconcile: 4 cases, 6 calls, 6 proxy submissions, 6 distinct retained bindings, resolved-any-call sum 4 and unresolved-any-call sum 2. Four image-byte matches and report/JSONL equality remain historical inspection receipts, not checks repeated against original files here. All 12 CPU traces have unique start identifiers paired with finish identifiers and submission totals matching request events. The new two-case capture does not reconstruct the historical raw-event gap.

## Per-claim ledger

| ID | Location | Claim | Status | Evidence / limit |
|---|---|---|---|---|
| C001 | main.tex:13-13 | Abstract empirical totals and guarded negative interpretation | exact_match | Historical controls 1 binding each; historical response-loss cases 2 each; new campaign 2 cases; no added F02 submission; target guard not observed. |
| C002 | main.tex:33-48 | Implementation comprises export, run guard and separate observation boundaries | missing_evidence | Implementation source is not in the declared input set. |
| C003 | main.tex:52-64 | Product calls, submissions and execution observations are distinct; F00/F02/F03 scope | exact_match | Same-run F02 has 2 calls, 1 POST and 1 retained lifecycle; CPU matrix has F00/F02/F03, Windows records have F00/F02. |
| C004 | main.tex:66-72 | Research-client resolved/unresolved labels and durable-state distinction | exact_match | New F00 resolved/generated; new F02 unresolved/unresolved; old F02 unresolved then resolved. |
| C005 | main.tex:78-104 | Versioned exporter policy, provenance limits and exclusive non-mutating output | missing_evidence | No exporter source or normalized outputs were declared. |
| C006 | main.tex:108-124 | Read-only exporter command and separate observer/normalizer interfaces | missing_evidence | No command output or exporter code in the declared set. |
| C007 | main.tex:125-126 | Offline demonstration supplies two synthetic records | missing_evidence | Requested optional examples/expected-summary.json is absent. |
| C008 | main.tex:126-130 | Twelve retained CPU manifests normalize to twelve unverified outputs | missing_evidence | Twelve source manifests exist; normalized outputs and normalizer execution receipt are absent. |
| C009 | main.tex:132-151 | Unresolved backend completion can coexist with blocked same-run recovery; no automatic reconciliation | exact_match | W3 F02 cases retain completed synthetic lifecycles, unresolved product state and outcome_unknown_blocked. |
| C010 | main.tex:143-144 | Same-run guard includes a different idempotency key | missing_evidence | No explicit distinct-key counterfactual or relevant source in the declared set. |
| C011 | main.tex:153-160 | Potential pre-acceptance false positive separated from observed accepted-response-loss completion cost | exact_match | The CPU accepted-response-loss fixture has an incomplete W3 client operation; a pre-acceptance false positive is explicitly described as potential. |
| C012 | main.tex:165-179 | Shim endpoint preservation, observer connection ordering and identifier construction | missing_evidence | New captures support event/history binding; shim implementation, connection-before-invocation proof and identifier derivation source are absent. |
| C013 | main.tex:181-189 | Historical second calls create fresh runs, use seed 4100 + call_index, and digest excludes seed/plan | missing_evidence | Historical extract has calls, receipts and bindings, but no run IDs, seed arguments or digest implementation. |
| C014 | main.tex:181-182 | Historical first completion precedes second receipt | exact_match | Both F02 first-binding finish timestamps are earlier than the second proxy receipt. |
| C015 | main.tex:186-187 | CPU F02 single-stage W3 one versus B2 two executions, W3 incomplete | exact_match | B2 S/E 2/2 complete; W3 S/E 1/1 incomplete. |
| C016 | main.tex:196-210 | Figure scope/caption claims | ambiguous_mapping | Historical 2-submission ordering is supported; figure artwork and source-based new-run/changed-seed proof were not declared. |
| C017 | main.tex:218-224 | CPU normal/response-loss coverage and oracle self-checks | exact_match | Each system has 6 fixed F00/F02/F03 by single/two-stage cases; 4 self-checks include 2 submissions/0 executions, 2/1, and shared-prompt 2 executions. |
| C018 | main.tex:226-227 | 40 tests in 7.110 seconds with OK and exit code 0 | missing_evidence | No such retained test output appears in declared command-output blocks. |
| C019 | main.tex:227-228 | Windows Python 3.15.0a8 historical runtime | missing_evidence | CPU matrix identifies Python 3.12.14 for its own stage; the stated Windows test-stage receipt is absent. |
| C020 | main.tex:228-233 | Seven macOS tests in 0.003 seconds and successful compile/whitespace checks | missing_evidence | No corresponding command result was declared. |
| C021 | main.tex:235-240 | Twelve unique and finished CPU traces with matching request totals | exact_match | 12/12 cases: execution-start IDs unique within case, exactly matching finish IDs; request_received totals equal stored submissions. |
| C022 | main.tex:239-240 | Earlier control failure caused by harness result-field mismatch | missing_evidence | Only command blocks were consulted; no v1 raw result was declared. |
| C023 | main.tex:243-248 | CPU table F00 Single stage | exact_match | {"b2_se":"1/1","w3_se":"1/1","complete":"yes/yes","recovery":"Not needed / Not needed"} |
| C024 | main.tex:243-248 | CPU table F00 Two stage | exact_match | {"b2_se":"1/1","w3_se":"1/1","complete":"yes/yes","recovery":"Not needed / Not needed"} |
| C025 | main.tex:243-248 | CPU table F02 Single stage | exact_match | {"b2_se":"2/2","w3_se":"1/1","complete":"yes/no","recovery":"New submission / Unknown; blocked"} |
| C026 | main.tex:243-248 | CPU table F02 Two stage | exact_match | {"b2_se":"1/1","w3_se":"1/1","complete":"no/no","recovery":"Unknown / Unknown; blocked"} |
| C027 | main.tex:243-248 | CPU table F03 Single stage | exact_match | {"b2_se":"2/2","w3_se":"2/2","complete":"yes/yes","recovery":"New submission / New submission"} |
| C028 | main.tex:243-248 | CPU table F03 Two stage | exact_match | {"b2_se":"1/1","w3_se":"1/1","complete":"yes/yes","recovery":"Same job reconciled / Same job reconciled"} |
| C029 | main.tex:251-259 | F02 single-stage successful synthetic artifact but incomplete W3 operation; F03 two-stage unchanged | exact_match | W3 F02 has one start/finish plus artifact and valid_completion=false; B2 has two and true. F03 two-stage both have 1/1, true and same_job_reconciled. |
| C030 | main.tex:263-271 | Four fixed historical cases, two controls/two injected, all oracle-evaluable | exact_match | 4 cases; F00=2, F02=2; oracle_evaluable sum=4; both F02 injection_confirmed=1. |
| C031 | main.tex:269-274 | Historical Windows table B2_F00 | exact_match | {"calls":1,"se":"1/1","sequence":"R"} |
| C032 | main.tex:269-274 | Historical Windows table W3_F00 | exact_match | {"calls":1,"se":"1/1","sequence":"R"} |
| C033 | main.tex:269-274 | Historical Windows table B2_F02 | exact_match | {"calls":2,"se":"2/2","sequence":"U then R"} |
| C034 | main.tex:269-274 | Historical Windows table W3_F02 | exact_match | {"calls":2,"se":"2/2","sequence":"U then R"} |
| C035 | main.tex:277-281 | Historical six calls/submissions/bindings and six distinct completed binding IDs | exact_match | Calls=6, receipts=6, retained bindings=6; all IDs distinct, history_completed=true, terminal_event=executing. |
| C036 | main.tex:279-279 | Four report records matched JSONL cases | exact_match | 4 report_equals_jsonl_case=true receipts. |
| C037 | main.tex:281-297 | Historical F02 aggregate execution_start=3 despite two bindings; example 1+2=3 | exact_match | Each F02 event_counts.execution_start=3, submissions=2, bindings=2. Arithmetic 1+2=3 is correct. |
| C038 | main.tex:283-292 | Two historical cumulative observer decisions cause recounting opportunity | missing_evidence | Historical extract omits individual decisions and raw lists. |
| C039 | main.tex:299-302 | Historical RTX 5070 Ti Laptop GPU, ComfyUI v0.30.0 and pinned model/workflow checks | missing_evidence | The historical extract lacks environment fields; the new private configuration records environment for a different campaign. |
| C040 | main.tex:304-311 | Historical F02 has no demonstrated W3 count advantage or identical-request duplicate proof | exact_match | Both historical F02 records have 2 retained bindings; request identity is not established by the declared historical evidence. |
| C041 | main.tex:315-321 | New protocol, frozen W3 revision, saved same run and complete arguments | exact_match | Protocol same-run-guard-v1; configured W3 source matches CPU W3 source; canonical full arguments hash matches both results; same run IDs, seed and key match internally. |
| C042 | main.tex:317-321 | Controller-reported completion ordering with explicit missing retry timestamp | exact_match | The retained first completion and second call are present; no independent retry timestamp is retained. |
| C043 | main.tex:323-337 | Same-run table W3 F00 C/S/E 1/1/1 resolved | exact_match | 1 call result, 1 accepted POST receipt, 1 start/terminal/history binding; resolved and durable generated state. |
| C044 | main.tex:323-337 | Same-run table W3 F02 C/S/E 2/1/1 unresolved/unresolved | exact_match | 2 call results, 1 accepted POST receipt, 1 start/terminal/history binding; both unresolved. |
| C045 | main.tex:339-340 | F00 completed; F02 accepted response was dropped; original manifest unresolved/unknown/no job | exact_match | F00 generated/completed. F02 forwarded HTTP 200 receipt has response_dropped=true; manifest state and attempt unresolved, submission_outcome unknown; no durable job binding. |
| C046 | main.tex:341-345 | Retry error model_identity_drifted, not submission_outcome_unknown; guard_observed=false | exact_match | Second result client_error_code=model_identity_drifted at generate_round; campaign STOPPED with guard_rejection_not_observed and submission_guard_observed=false. |
| C047 | main.tex:342-343 | No added POST and byte-identical manifest after retry | exact_match | Only one proxy receipt retained; first after, second before and second after manifest bytes are identical. |
| C048 | main.tex:346-347 | Identity error does not prove changed model bytes | exact_match | No model before/after byte comparison tied to the failure is present. |
| C049 | main.tex:349-350 | 90 F00 and 10 F02 WebSocket payloads; one history response each | exact_match | Decoded 90 and 10 UTF-8 JSON payloads; 1 HTTP 200 history body per case. |
| C050 | main.tex:349-352 | Payload byte hashes and per-channel sequences checked | exact_match | 100/100 WebSocket body SHA256 values and 2/2 history SHA256 values match decoded bytes; sequences contiguous from 1 in each channel; final transport equals snapshot transport. |
| C051 | main.tex:351-353 | One start and one executing node=null terminal per case, successful history and published binding IDs | exact_match | Each decoded start/terminal pair has matching prompt correlation with the receipt/history; history completed=true and status_str=success; binding timestamps and IDs agree with public record. |
| C052 | main.tex:353-357 | Retained consistency is not authenticity/completeness; cache boundary and historical gap | exact_match | F02 execution_cached=1, progress=0, while retained lifecycle=1; no raw historical lists are present. |
| C053 | main.tex:357-357 | No third call or fresh-run fallback | exact_match | F02 retained invocation/result set contains calls 1 and 2 only; both use the same retained run; campaign stopped. |
| C054 | main.tex:361-369 | Historical overlapping resolved/unresolved flags sum to four and two | exact_match | Each F02 has resolved=1 and unresolved=1; sums across four cases are resolved=4, unresolved=2. |
| C055 | main.tex:366-369 | Earlier Markdown summary had zero unresolved cases | missing_evidence | That Markdown summary is excluded from declared inputs. |
| C056 | main.tex:371-375 | Execution count uses distinct bindings rather than cumulative aggregate event counts | exact_match | Historical F02 totals equal 2 distinct retained bindings while execution_start aggregates equal 3. |
| C057 | main.tex:379-385 | CPU revisions, harness digests and traces preserved; no fresh historical reproduction claim | exact_match | Both records contain product source revision, runtime checkout identity, three harness hashes and event traces; protocols explicitly synthetic. |
| C058 | main.tex:381-384 | Audit/figure scripts are read-only and reproducibility from derived records | missing_evidence | No script source or execution output is in the declared set. |
| C059 | main.tex:386-387 | Same-run used separate detached research checkout preserving frozen revisions | ambiguous_mapping | Configuration records expected frozen W3 SHA and preflight client check passed; no detached-HEAD Git receipt is retained here. |
| C060 | main.tex:389-401 | Historical retained extract lacks raw events and only records consistency receipts | exact_match | Oracle fields are bindings/event_counts/reason/status; no raw WebSocket/history bodies. Equality/image-match fields are retained booleans. |
| C061 | main.tex:403-406 | Four generated-call artifact hashes matched host image bytes; one PNG per case; first F02 has no artifact hash | exact_match | 4 artifact_checks records with matches_current_output_bytes=true; output_png_count=1 per case; first F02 calls have empty artifact_checks. |
| C062 | main.tex:407-421 | Metadata fingerprints, missing-event limits, no rates/performance/GPU/quality inference | exact_match | New artifact metadata hashes match retained path strings, not image bytes; fixed finite cases contain no deployment sample or physical GPU trace. |
| C063 | main.tex:417-421 | New controlled two-case test made no model download; raw bytes excluded from reviewer package | missing_evidence | Two-case scope is verified; no-download history and final reviewer-package contents are not declared inputs. |
| C064 | main.tex:426-497 | Related-work contracts and documentation-based scope comparison | missing_evidence | Cited publications/documentation and bibliography were not declared audit inputs. |
| C065 | main.tex:501-511 | Conclusion distinguishes historical visibility, masked same-run guard and unsupported general guarantees | exact_match | Historical retained visibility is supported; new retry is model_identity_drifted with guard false; no automatic recovery/rate/physical-GPU evidence. |
| C066 | main.tex:513-527 | Package redistribution, human-subject and AI-usage statements | missing_evidence | Package inventory, author declarations and drafting history are outside the declared evidence set. |

## Audit protocol

Fresh delegated reviewer; only the declared manuscript, table, result, capture and allowed command-output inputs were consulted. No executor narratives, source edits, generation backend calls or further experiments were used. The optional expected-summary file was absent and is not assigned a fabricated hash. For in-paper inputs, JSON hash keys are relative to the paper directory; the three external CPU records and allowed command-output document use absolute repository paths. Embedded private host paths, run identifiers, prompts and payload text are excluded from this report.

Trace metadata: `.aris/traces/paper-claim-audit/20261001_run01/`. Model settings were inherited and not independently exposed to this reviewer; no unverified model-name claim is made. This result remains same-family provisional and is not submission acceptance.

