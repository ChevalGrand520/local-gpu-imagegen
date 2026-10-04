Verdict: **WARN — numerical transcription checks pass where records are supplied, but several comparisons and validation claims lack evidence in the authorized packet.** This is a provisional review by the same model family, not independent execution authentication, editorial approval, or submission approval.

Audited immutable inputs at `0b8f272`, read-only. Manuscript locations below refer to `paper-softwarex/manuscript-v0.8.md`.

Evidence aliases:

- **P**: `paper/evidence/paired-windows-projection-20261001.json`
- **W**: `paper/evidence/windows-same-run-v2-20261001.json`
- **K**: `paper-softwarex/known-job-recovery-receipt.json`
- **Q**: `paper/evidence/v022-probe-command-receipt.json`
- **R**: `paper/evidence/revision-v012-runtime-check.json`

`exact_match` means the manuscript matches the supplied record. It does **not** mean this audit reproduced or authenticated the execution.

**Evidence character and provenance**

| Input | What it actually contains | Audit consequence |
|---|---|---|
| P | Explicitly calls itself a “derived fixed-case record,” excludes private raw evidence, and says “not execution authentication.” Six summary rows, totals, aggregate events, cached-node IDs, private archive digest. | Supports checking transcription and some arithmetic. Cannot establish original execution or recompute the complete campaign from raw captures. |
| W | Two summarized W3 records, hashed private captures/manifests, selected proxy receipts, oracle summaries and product-call summaries. | More detailed than P, but not the private raw archive. Digests without their referenced bytes cannot authenticate the underlying material. |
| K | A compact result receipt with `status: PASS`, separate engine/adapter fixture results, and scope limitations. | Supports reported fixture outputs, not inspection of the executable assertions, actual image, full trace, or source implementation. |
| Q | A synthetic offline command/result receipt; 12 probes and classification totals. | Supports the recorded comparison fields; not inspection of fixtures or parser code. |
| R | An older offline command receipt; two verification commands plus a 13-test unittest result. | Supports that recorded subset only. It does not support the newer 96-test, CI, wheel, or full-suite claims. |

W's top-level `status: COMPLETED` and per-case `status: completed` must not be interpreted as client completion: its W3_F02 product calls both report `unresolved`.

**Quantitative and comparison ledger**

Repeated claims are grouped with every relevant manuscript location.

| ID | Manuscript claim/location | Exact evidence/value | Classification |
|---|---|---|---|
| N01 | Package/version `0.9.1`: L20, L72, L74, L147 | No package metadata or wheel/interface receipt among inputs. | `missing_evidence` |
| N02 | Cited software snapshot `dfc8378cb3d891f7951786bc4544cd971bd56a11`: L22, L147 | K.`fixtures_source = "dfc8378"` identifies fixture source only; it does not establish full product snapshot, contents, version, or distribution provenance. | `ambiguous_mapping` |
| N03 | Paired execution source `08539d5`: L23, L88, L147 | P.`execution_source = "08539d5"` | `exact_match` |
| N04 | Python requirement `>=3.11`: L26 | Not supplied. R.`minimum_runtime = "Python 3.10"` is an explicitly older offline receipt and cannot verify the current requirement. | `missing_evidence` |
| N05 | CI Python 3.11/3.12, Windows/Ubuntu pass, run `37090919543`: L26–27, L125 | No CI record among inputs. | `missing_evidence` |
| N06 | Dependency `py7zr==1.1.3`: L28 | No dependency metadata among inputs. | `missing_evidence` |
| N07 | Isolated installed/rebuilt wheel exposes **17 tools**: L72, L125 | No wheel build/install/verify receipt among inputs. | `missing_evidence` |
| N08 | **12 synthetic probes**, exporter/parser classifications equal: L80, L143 | Q.`probes=12`, `agreement_count=12`; exporter and field_baseline each `{correct:12, unknown:3, false_affirmations:0}` | `exact_match` |
| N09 | Probe interpreter **Python 3.13.15**: L80 | Q.`interpreter = "Python 3.13.15; explicit installed executable"` | `exact_match` |
| N10 | **Six operations**, two paths for each of **three conditions**: L11, L88, L111, L131 | P.`totals.operations=6`; rows contain B2/W3 × F00/F02/FPRE exactly once. | `exact_match` |
| N11 | **Ten product calls**: L90 | P.`totals.product_calls=10`. P has no per-row product-call counts, so this total can be transcribed but not independently summed from its rows. | `exact_match` |
| N12 | **Eight proxy POSTs**: L90 | P.`totals.proxy_posts=8`; sum of row `S_proxy` = `1+1+1+2+2+1=8`. | `exact_match` |
| N13 | **Six upstream sends**: L90 | P.`totals.upstream_attempts=6`; sum of row `S_upstream` = `1+1+1+2+1+0=6`. | `exact_match` |
| N14 | F00 B2: **1 / 1 / 1 / 1 / Yes**: L94 | P row `B2_F00`: `S_proxy=1`, `S_upstream=1`, `A=1`, `E_bound=1`, `client_completion=true`. | `exact_match` |
| N15 | F00 W3: **1 / 1 / 1 / 1 / Yes**: L95 | P row `W3_F00`: same values. W also reports one acceptance/start/finish and `reported_state=resolved`. | `exact_match` |
| N16 | F02 B2: **2 / 2 / 2 / 2 / Yes**: L96 | P row `B2_F02`: `2,2,2,2,true`. | `exact_match` |
| N17 | F02 W3: **1 / 1 / 1 / 1 / No**: L97 | P row `W3_F02`: `1,1,1,1,false`. W reports one acceptance/start/finish, `submission_guard_observed=true`, and both calls `reported_state=unresolved`. | `exact_match` |
| N18 | FPRE B2: **2 / 1 / 1 / 1 / Yes**: L98 | P row `B2_FPRE`: `2,1,1,1,true`. | `exact_match` |
| N19 | FPRE W3: **1 / 0 / 0 / 0 / No**: L99 | P row `W3_FPRE`: `1,0,0,0,false`. | `exact_match` |
| N20 | F02 guard retains **one** accepted job/lifecycle versus B2's **two**; W3 incomplete, B2 complete: L11, L38, L86, L105, L133, L143 | P `B2_F02` versus `W3_F02`: `A 2→1`, `E_bound 2→1`, completion `true→false`. Both record corresponding `execution_success` counts. | `exact_match` |
| N21 | Second B2 F02 lifecycle cached nodes **3 through 9**: L107 | P.`cache_second_B2_F02_nodes=["3","4","5","6","7","8","9"]` | `exact_match` |
| N22 | FPRE B2 eventually sends **one** request and completes; W3 sends **zero** and remains incomplete: L11, L64, L109, L133, L143 | P `B2_FPRE.S_upstream=1`, completion true; `W3_FPRE.S_upstream=0`, completion false, guard true. | `exact_match` |
| N23 | Synthetic CPU stop-after-unknown matches W3 across **F00, F02, FPRE counts/completion**: L11, L111, L143 | No P-stop outcome matrix, counts, or comparison receipt in any input. K's stop-only control explicitly says it is **“not P-stop Windows/CPU campaign.”** | `missing_evidence` |
| N24 | Known-job retrieval adds **zero backend calls**: L115 | K.`engine_fixture.get_run_backend_calls_added=0` | `exact_match` |
| N25 | Recovery records **one round**, an existing image, and `generated`; stop control remains `unresolved`: L115, L117, L121 | K.`rounds=1`, `image_recorded_and_exists=true`, `after_state="generated"`, `stop_only_control_state="unresolved"`. | `exact_match` |
| N26 | Retained/forwarded known identifier: L115 | K.`retained_backend_job_id` and `recovery_job_id_forwarded` both `"job-two-stage-timeout"`. | `exact_match` |
| N27 | Adapter requests `/history/prompt-1` and `/view`, with **zero `/prompt` POSTs**: L117, L121 | K.`adapter_fixture.request_paths=["/history/prompt-1","/view?filename=result.png&subfolder=&type=output"]`; `prompt_posts=0`; `workflow_job_id="prompt-1"`. | `exact_match` |
| N28 | **Two separate component checks**, without integrated backend execution: L117 | K.`scope="Separate engine fixture and real adapter against loopback fake HTTP server"`; `real_comfyui_executed=false`. | `exact_match` |
| N29 | **96 research tests**, Python **3.12**, Pillow installed, at cited snapshot: L125 | No corresponding receipt, environment, or test result among inputs. R's 13-test Python 3.13.15 result is a different subset. | `missing_evidence` |
| N30 | Older **13-test** offline subset under Python **3.13.15**: L125 | R.`runtime="Python 3.13.15"`; unittest check stderr `"Ran 13 tests in 0.002s … OK"`; `exit_code=0`. | `exact_match` |
| N31 | macOS Python **3.12** full suite: **1,274 tests, 30 failures, 5 errors, 40 skips**: L127 | No full-suite record among inputs. | `missing_evidence` |
| N32 | Validation materials revision `abb363992469c23eae354f2374af32ffc8c6b1ad`, distinct from software snapshot: L125 | URL states the revision; linked document was outside authorized inputs and was not read. | `missing_evidence` |

No manuscript numerical discrepancy, rounding problem, or incorrect aggregation was established from the supplied records.

**Scope, mechanism, and remaining comparison ledger**

| ID | Claim/location | Evidence and limit | Classification |
|---|---|---|---|
| S01 | Open-source Python/MCP control plane, named commands/tools, architecture and adapters: L11, L25, L29–31, L40, L50, L54, L72, L143 | Receipt command names partially support Python/source tooling. Source, metadata, README, interface schemas and figures are excluded. Full implementation claims cannot be verified here. | `missing_evidence` |
| S02 | Windows product support; Ubuntu CI is not retained GPU evidence; only ComfyUI evaluated: L27, L50, L127 | W names a same-run scope but contains no full backend/environment configuration. P names a derived fixed-case record. Current product-platform and backend-coverage declarations require source/configuration evidence. | `ambiguous_mapping` |
| S03 | MIT license, identical `Licence.txt`, repo/PyPI availability and historical artifact distinction: L21, L24, L74, L147 | License, package and public availability evidence absent. | `missing_evidence` |
| S04 | Exporter/checker are excluded from wheel/sdist and require source checkout: L31, L54, L74, L147 | No distribution file listing or packaging metadata. | `missing_evidence` |
| S05 | Durable/frozen routes, immutable child runs, route-change rejection, endpoint/model/compiler identity: L56, L78 | W has `request_matches_frozen=true` and request/route digests. It contains no raw manifests or route-mutation test. | `ambiguous_mapping` |
| S06 | Backend/model supplied separately; no bundled weights/cloud API; LAN/loopback traffic, trust and explicit download behavior: L28, L54, L58 | Requires configuration/source/distribution inspection, all excluded. | `missing_evidence` |
| S07 | In tested same-run unknown branch, repeat call returns unresolved and withholds further submission: L62, L76, L86 | W `W3_F02`: two calls, same `run_id_sha256`, second `client_error_code="submission_outcome_unknown"`, unchanged before/after manifest hashes, one proxy request, guard true. | `exact_match` |
| S08 | Arbitrary new runs/processes are outside demonstrated guard scope: L62 | W.`retry_scope="same_run"` and top-level scope expressly limit inference. | `exact_match` |
| S09 | Backend acceptance, lifecycle completion and client completion differ: L11, L36, L90, L105, L131, L133 | P `W3_F02`: `A=1`, `E_bound=1`, `execution_success=1`, client completion false. W: `history_completed=true` while calls remain unresolved. | `exact_match` |
| S10 | F02 causes response loss after acceptance: L86, L88 | W F02 proxy receipt has `forwarded=true`, `upstream_status=200`, `response_dropped=true`; it records one backend acceptance. P labels F02 but lacks comparable detailed receipt. | `exact_match` for W's recorded event; `ambiguous_mapping` to P's particular six-operation capture |
| S11 | Product never retained the returned identifier; retrieval cannot discover it; no automatic history reconciliation/in-flight detection: L66, L86 | Raw manifests, product implementation and unknown-branch retrieval trace absent. W records hashed manifests, not their contents. | `missing_evidence` |
| S12 | `local_gpu_get_run` local-state contract, exact response fields and unknown-attempt field values: L66, L76 | K supports recovery next-actions and zero backend calls for its **known-job fixture**; W supports unresolved call results and the second-call error. Neither exposes the full claimed unknown-branch retrieval response. | `ambiguous_mapping` |
| S13 | Idempotency key binds request hash and is sent as `client_id`; no verified server deduplication contract: L68 | No request bodies, binding source, backend contract or deduplication test supplied. Absence of a guarantee is a prudent limitation, not a verified contract finding. | `missing_evidence` |
| S14 | Recovery requires same key/hash; changed key is rejected before runner entry; two-stage route forwards recovery identifier: L78, L115 | K confirms forwarded ID and `changed_key_error="backend_job_unresolved"`. It does not expose hash inputs, mismatch tests, or runner-call count for changed-key rejection. | `exact_match` for ID/error; `missing_evidence` for hash rule and rejection ordering |
| S15 | Fake backend reports ID via callback then raises timeout; engine retains exact manifest field: L115 | K reports before-state and retained ID but no callback/exception trace or raw manifest. The word “timeout” in the identifier is not an execution trace. | `missing_evidence` |
| S16 | Recovery actions `get_run`, `generate_round:recover`: L115, L121 | K.`engine_fixture.next_actions` contains those exact strings. | `exact_match` |
| S17 | Stop-only control takes no action on same manifest and remains unresolved: L115, L121 | K.`control_scope` explicitly defines that policy; `stop_only_control_state="unresolved"`. This is a stipulated control, not evidence of policy superiority. | `exact_match` |
| S18 | Recovery checks use synthetic/known-ID fixtures, no GPU/real ComfyUI/missing-ID reconciliation/F03 Windows; finalization remains outside result: L117 | K.`gpu_executed=false`, `real_comfyui_executed=false`, scope/limits; `after_state="generated"`. | `exact_match` |
| S19 | Probe fixtures separate from Windows bytes; no Windows/GPU execution; equal parser classifications: L80 | Q scope states synthetic offline fixtures, not historical Windows data; execution flags false; agreement 12. | `exact_match` |
| S20 | Field parser written by same author; parser superiority or audit-effort benefit unestablished: L80 | Authorship not in Q. Q supports equality only and contains no superiority/audit-effort measurement. | `missing_evidence` for authorship; `exact_match` for bounded interpretation |
| S21 | Source checker verifies paired derived rows/totals without model/backend execution: L74, L101, L131 | P is explicitly derived. The checker is excluded; R names `verify_windows_projection.py`, **not** `verify_paired_projection.py`. | `exact_match` for P's derived status; `missing_evidence` for the named checker's behavior |
| S22 | Cached second accepted job does not prove twice the computation or GPU savings: L107, L133, L137 | P supplies aggregate events/cache-node IDs, no GPU-work metric; W expressly excludes physical GPU execution claims. | `exact_match` as limitation of supplied evidence |
| S23 | Six fixed examples do not provide randomized repetition, population rates, general reliability or improvements in quality/performance/resources: L111, L137 | P contains only six fixed rows and no repetition/rate/performance study. | `exact_match` as limitation of supplied evidence |
| S24 | No later client session/recovery measured; adoption, daily-practice and downstream impact unmeasured: L44, L86, L137 | No such results in inputs. The entire absence of other studies cannot be established from this restricted packet. | `ambiguous_mapping` |
| S25 | New validation checks used no models/separate environments; Mac failures include particular filesystem/install causes without one universal attribution: L125–127 | New validation records and failure logs excluded. R/Q/K are limited offline receipts and cannot establish the new validation environment or failure causes. | `missing_evidence` |
| S26 | Raw capture is private; derived checker does not authenticate it; limited reproduction: L11, L101, L139, L147 | P explicitly states raw exclusion/no authentication; W references private-capture hashes rather than providing those bytes. | `exact_match` for availability within packet and authentication limit |
| S27 | Private raw archive contains stated configuration/source/log/image material; sanitized prototype preserves rows/relations but is unreleased/incomplete: L139, L147 | P gives archive digest; W lists selected hashes. Raw archive and sanitized prototype are absent. Contents and prototype preservation cannot be checked. | `missing_evidence` |
| S28 | Li, effect-history, verification-aware wrappers, ToolPro comparisons; novelty and contract conclusions: L38, L40, L42, L68 | Cited papers/sites and underlying implementation were not authorized inputs. | `missing_evidence` |
| S29 | Permanent archive not selected/no DOI; reference years, identifiers, MCP revision and access dates: L32, L147, L155–169 | No archive/source/reference verification permitted. These are metadata assertions, not audited experimental results. | `missing_evidence` |
| S30 | Integration contribution, limited characterization, no superiority/general impossibility claim: L40, L66, L111, L115, L143 | Consistent with limited supplied records. Any assertion that P-stop specifically matches remains N23's unsupported-in-packet comparison. | `exact_match` for stated limits; N23 remains `missing_evidence` |

**Material findings**

1. **P-stop equivalence is not supported by this evidence packet** — L11, L111, L143. None of P/W/Q/R contains the control result, and K expressly excludes the P-stop campaign. A dedicated control result is needed before this comparison can receive `exact_match`.

2. **The newer software validation numbers are not auditable here** — L72, L125–127. The absent records concern 17 tools, 96 tests/Python 3.12/Pillow, CI run 37090919543 and its platform/runtime matrix, and the macOS 1,274/30/5/40 totals and failure analysis. R verifies only the older 13-test Python 3.13.15 subset.

3. **P and W must not silently be combined as one capture.** For W3_F02, P records `executing=8`, `progress_state=44`, `progress=30`; W records `executing=1`, `progress_state=1`, with no `progress` entry. W contains only W3 F00/F02; P contains six paired cases. This is an **`ambiguous_mapping` risk**, not a demonstrated manuscript number error: the records may describe distinct captures. Their matching high-level outcomes do not establish shared execution provenance.

4. **Some implementation details exceed what the supplied receipts expose** — notably L66, L68, L76, L78 and the callback/hash/rejection-order clauses of L115. The core K outcomes match, but its `PASS` field cannot substitute for reading the executable assertions or trace.

Audit limits: no source-code inspection, linked validation document, private captures, sanitized prototype, figure inspection, reference verification, network access, rerunning checks, backend execution or GPU execution. No files were written. No `number_mismatch`, `aggregation_mismatch`, or demonstrated current `config_mismatch` was found; missing evidence must not be relabeled as proof that a claim is false.
