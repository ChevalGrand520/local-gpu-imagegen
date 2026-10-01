## 2026-10-01 paired batch C: current research disposition

This research update follows Tool v0.18; it does not amend the frozen submission
files. Historical fresh-run, same-run v1/v2 and paired batches A/B/C stay separate.
Source: `refine-logs/WINDOWS_PAIRED_COMPLETED_20261001.md`; execution source
08539d5; complete private TAR SHA-256
141b1ea66af741f9e8cc917f7a7a33db5cb0d048989f76a25166775180f852f3.
The Mac archive matches Windows. Read-only audit replays retained bytes and
bindings (1,561 checks); it does not authenticate execution or independently
validate its own binding implementation. The semantic review remains provisional.

| New ID | Claim | Evidence / permitted statement | Status / excluded inference |
|---|---|---|---|
| P01 | Same-run submission withholding under accepted response loss | C/W3_F02: 2 calls, 1 POST, 1 accepted job, 1 bound lifecycle; call 2 returns submission_outcome_unknown | Observed fixed operation; no global at-most-once guarantee |
| P02 | Paired F02 submission difference | C/B2_F02: 2 POSTs/2 lifecycles, original run complete; C/W3_F02: 1 POST/1 lifecycle, original run unresolved; shared semantic digest | Observed pair; one additional POST/lifecycle in B2, not estimated deployment effect |
| P03 | Backend completion differs from original-run completion | C/W3_F02: terminal event + successful history; original run unresolved | Observed separation; completed observation is not automatic reconciliation |
| P04 | Conservative block under proved pre-send loss | C/W3_FPRE: 1 proxy POST, 0 upstream sends, 0 lifecycles, guard rejection and incomplete original run; B2 retries and completes | Observed pair and completion cost; not deployment false-positive rate |
| P05 | GPU compute savings from guard | B2/F02 second lifecycle cached nodes 3..9, entire graph reused | Unsupported; do not equate lifecycle counts with full generations |
| P06 | Superiority over simple stop policy | CPU P-stop matches W3 submission counts; P-stop absent from Windows matrix | Unsupported; preserve competing explanation |
| P07 | Exporter better than same-information parser | Historical local probes 12/12, equal decisions; C bytes not yet converted/exported | Unsupported accuracy advantage; C establishes state separation, not exporter validation |
| P08 | Six-operation coverage | C: 6/6 completed, 10 calls/8 POSTs/6 upstream sends; normal controls separate from four fault operations | Supported coverage; not rates or statistical replication |
| P09 | Speed advantage | F00 RPC intervals 35.7722965 / 24.2037979s; desktop baseline activity present | Descriptive calibration only; not strategy speedup or GPU cost |
| P10 | Cross-platform generalization | C is one Windows/CUDA platform with one model/workflow/seed | Unsupported; Mac/MPS not measured |

Writing gate: use submission-level tradeoff as the evaluated mechanism claim.
Execution bindings, client completion, exporter interpretation and artifact bytes
remain separate fields. Do not add GPU savings, natural duplicate rates,
exactly-once execution, automatic reconciliation or method-superiority wording.
Attempts A/B retain their stops; B's early observer exit is corrected in the
diagnosis, not promoted retrospectively to completion.

## 2026-10-01 v2 follow-up — historical same-run protocol

Separate same-run-guard-v2 campaign COMPLETED. Both fresh MCP processes now
rebuild the exact pinned model inventory; frozen product and original generation
arguments are unchanged. F02 retry returned submission_outcome_unknown,
guard_observed=true, with two calls/one POST/one lifecycle binding and original
run still unresolved. This supports fixed-case submission blocking, not GPU
savings or eventual completion. V1 masking failure remains retained. Raw byte
and binding audit PASS; observer-to-exporter conversion remains open. Details:
`runs/f02-same-run-v2-windows-20261001.md`.

> v0.4 continuation: the active manuscript is `paper/main.tex` and `paper/main.pdf`.
> This document preserves the v0.3 planning/audit snapshot. Current evidence
> disposition and review are in `paper/evidence/` and `paper/review/ARS_REVIEW.md`.
> Current correction (2026-09-29): the live exporter uses
> `research-normalization-v3`, which withholds verification for a missing
> reported run state and for manifest/top-level identity conflicts. The v2
> entries below are historical planning and W2-record claims, not a current
> correctness certificate. See `paper/main.tex` and
> `tests/research/test_export_records.py` for the current policy and checks.

# DSN claim–evidence matrix — 2026-09-27

## Current live evidence update: 2026-10-01

This update precedes manuscript revision and supersedes current-status readings
of the historical rows below. Source: `runs/f02-same-run-windows-20261001.md`,
`paper/evidence/windows-same-run-20261001.json`, exact private transport captures,
and `paper/scripts/audit_same_run_capture.py`.

| Claim | Disposition | Permitted statement / remaining gap |
|---|---|---|
| C03/C14: real same-run guard effect | Not established | F02 reused run/arguments, but model_identity_drifted rejected call 2 before the target guard; zero new POST does not attribute a guard effect |
| New C23: two-case same-run campaign | Observed | F00 1 call/1 POST/1 binding; F02 2 calls/1 POST/1 binding, unresolved/unresolved; STOPPED |
| New C24: raw transport reconstruction | Supported for this capture only | 90/10 WS payloads and 1 history response per case, hashes/sequence/start/node-null terminal/history checked; does not repair historical raw-event absence |
| New C25: physical execution/repeated work | Unsupported | F02 has cached event and no progress event; lifecycle binding is not physical GPU work |
| New C26: persistent original ambiguity | Supported retained manifests | Same F02 run remains unresolved, unknown submission, no job; before/after retry bytes identical |
| C20: reproducibility | Partial | Offline raw-capture audit ran; private payloads are not reviewer redistribution; no successful live guard replay |

No population rate, controlled comparative improvement, model-byte drift cause,
automatic reconciliation or original-run completion is inferred.

Status: working evidence map; semantic judgment is same-family/provisional.
No submission-readiness or independent raw-data audit is claimed.

## Provenance and evidence levels

Evidence checkout: `5cd100f2b4a4a7aaeac1fd707fc248bae46f239c` from
`codex/f02-loopback-fault-oracle`. Writing branch: `docs/dsn-evidence-bound-manuscript`.
The v0.1 outline and draft were external working files, absent from that commit.
This matrix supersedes their claims, not historical experiment records.

- **S**: source/test definitions inspected here; static implementation evidence.
- **H**: historical versioned test or campaign report; not rerun here.
- **R**: raw Windows observations; remain Windows-local, not inspected here.
- **L**: externally verified literature; conceptual positioning, not tool validation.

Source keys (paths relative to repository):

| Key | Source and locator |
|---|---|
| E1 | `docs/research/runs/w3-windows-f02-endpoint-shim-20260927.md`, Outcome, Case Denominators, Verified Preparation, Interpretation |
| E2 | `docs/research/runs/w3-windows-f02-retry-20260927.md`, Preparation Evidence (40 tests; Python 3.15.0a8) |
| E3 | `docs/research/dsn-claim-evidence-map.md`, C1–C10 and Oracle/Matrix boundaries; historical map, not new verification |
| E4 | `scripts/research/export_records.py`, `export_record`, `_interpret_state`, `write_export`; `tests/research/test_export_records.py` |
| E5 | `scripts/local_gpu_imagegen/run_store.py`, `mark_attempt_submission_unknown`, `_require_unresolved_recovery`; `scripts/local_gpu_imagegen/engine.py`, `recoverable_next_actions` |
| E6 | `scripts/research/execution_oracle.py`; `scripts/research/run_fault_matrix.py`, `CpuFakeBackendWorker`; `tests/research/test_execution_oracle.py`, `test_run_fault_matrix.py`, `test_paired_fault_matrix.py` |
| E7 | `scripts/research/f02_transport_shim.py`, `install_prompt_proxy`; `tests/research/test_f02_transport_shim.py` |
| E8 | `scripts/research/f02_oracle.py`, `ComfyUIEventOracle._decision`, `_execution_instance_id`; `tests/research/test_f02_windows_pilot_components.py` |
| E9 | `scripts/research/f02_campaign.py`, `_run_case`, `_case_record`, `_invoke_subprocess` |
| E10 | `scripts/research/f02_product_client.py`, `run`, `_request_digests`, `_artifact_hashes` |

## Claim decisions

IDs are stable internal manuscript annotations. “Supported” is always scoped to
its evidence level; report-backed numbers still require raw-data reconciliation
before submission.

| ID | Proposed claim / location | Evidence | Decision and permitted wording | Missing evidence / prohibited extrapolation |
|---|---|---|---|---|
| C01 | Reported, interpreted and oracle state are separate (§3) | S:E4; H:E3 C1 | Supported implementation description; mapping `research-normalization-v2` | Not proof of all input schemas or deployed correctness |
| C02 | Export is observational (§3) | S:E4 | Deep-copy normalization and exclusive creation of output; does not invoke engine | No universal containment/security guarantee; path safety needs its own API-level review |
| C03 | Unknown submission blocks another submission (§3) | S:E5; H:E3 C3–C4 | Restrict to same run and explicit `submission_outcome=unknown` at reviewed entry points | Not a global at-most-once guarantee; fresh runs bypass this scope |
| C04 | Unknown-job automatic reconciliation exists | S:E5; H:E3 C4 | Unsupported; `get_run` is inspection guidance | Need durable same-run reconciliation and acceptance evidence; do not imply implementation |
| C05 | Known-job two-stage recovery (§3) | H:E3 C5; S:engine | Existing capability, distinct from no-job-ID branch | Not a W3 novelty claim or Windows F02 demonstration |
| C06 | CPU oracle observes worker-entry events (§4.1) | S:E6; H:E3 C2,C6 | Deterministic synthetic coverage | Same-process observer; no crash-durable or GPU-kernel oracle claim |
| C07 | 40 CPU research/component tests passed (§4.1) | H:E2 | Reported Windows Python 3.15.0a8 component-suite result | Commands/logs located in reconciliation addendum: earlier Windows 40, later macOS 7; immutable test-source binding still pending; not current Mac or supported-Python CI result |
| C08 | Windows campaign 4/4 oracle-evaluable (§4.2) | H:E1 | Four fixed cases: B2/W3 × F00/F02 | Raw event recount pending; not a reliability probability |
| C09 | Each F00: 1 submission, 1 execution (§4.2 table) | H:E1 | Separate normal controls | Not fault cases; not part of fault-injection denominator |
| C10 | Each F02: 2 submissions, 2 executions (§4.2 table) | H:E1; S:E9–E10 | Two observed execution instances per controlled case | No same-payload duplicate claim or natural duplicate-execution rate |
| C11 | First F02 call unresolved, second resolved (§4.2) | H:E1; S:E10 | Research-client classifications, second call starts new run | Does not establish first manifest resolved; client catches multiple errors as unresolved |
| C12 | Second call follows oracle-confirmed completion (§3.3) | H:E1; S:E9 | Research-controller gate | Not autonomous product reconciliation |
| C13 | Same request replayed across F02 calls | S:E10 | Unsupported: fresh run each call, seed `4100 + call_index` | Frozen request digests do not alone prove identical full prompt payloads |
| C14 | W3 reduces real repeated execution | H:E1 | Unsupported: B2 and W3 both have 2/2 in F02 | CPU paired fixture differences cannot transfer to this Windows protocol |
| C15 | Endpoint-preserving injection (§3.3) | S:E7; H:E1 | Research shim intercepts prompt transport while identity client retains endpoint | Not native ComfyUI or shipped product feature; no identity-security proof |
| C16 | Independent Windows execution oracle (§3.3) | S:E8; H:E1 | Independent of product return value, dependent on backend WS + history; matching client ID | No hardware-independent monitor, replay-proof event IDs or crash completeness |
| C17 | 4 resolved / 0 unresolved (§4.2) | H:E1 table versus S:E9 `_case_record` | **RECONCILED G01**: retained report confirms any-call resolved=4, unresolved=2 | Do not publish aggregate unresolved=0 as controller output or recovery success rate |
| C18 | Artifact identity and visual acceptance (§5) | H:E1; S:E8–E10 | Report says hashes retained; content hashes and path hashes have distinct roles | Raw images/hashes not checked here; path hash is not content integrity, history is not visual acceptance |
| C19 | ComfyUI/model scope (§4.2, §5) | H:E1 | Recorded v0.30.0 at `b1693ecba9f5b65f8c80ab36b195ab963ec92413`; pinned configuration only | No backend-version/model generalization; model/workflow hash values require approved manifest |
| C20 | Reproducible integration package (§5) | H:E1,E3; S:versioned tools | Inspectable source and historical demonstration | Clean-checkout reproduction, sanitized raw bundle and third-party Windows replay pending |
| C21 | Novel evidence-bound semantics (§1, §6) | L:RPC/idempotency sources; H:E3 C10 | Application/tool integration contribution, novelty pending | No first-ever/existing-tools-cannot claim without nearest-tool comparison |
| C22 | Reliability, speed, quality superiority | No matching study | Unsupported; excluded | No rates, significance, speedup, visual-quality or acceptance probability claims |

## Denominator ledger

| Quantity | Unit | Value | Provenance and boundary |
|---|---|---:|---|
| Planned / scheduled / started | Fixed campaign cases | 4 / 4 / 4 | E1, not independent statistical samples |
| Normal controls | F00 cases | 2 | B2 and W3, kept separate from injected cases |
| Injection-confirmed | F02 cases | 2 | E1, response dropped after acceptance |
| Oracle-evaluable | Fixed campaign cases | 4 of 4 | E1 report-backed |
| Calls / proxy submissions / execution instances | Campaign totals | 6 / 6 / 6 | E1; arithmetic 1+1+2+2, not a rate |
| Unresolved first calls | Product-client calls | 2 | E1 narrative; not final-case unresolved count |
| Resolved second calls | Product-client calls | 2 | E1 narrative; fresh runs |
| Final-case resolved / unresolved | Report table | 4 / 0 | G01: do not substitute for controller any-call flags |

## Terminology ledger

| Canonical term | Meaning | Avoid |
|---|---|---|
| submission | Proxy-observed `POST /prompt` in Windows table | treating any product call as a POST |
| execution instance | Backend-event binding; synthetic worker entry in CPU harness | GPU-kernel count, prompt-ID count |
| unresolved call | Research-client classification in Windows campaign | unqualified backend failure or durable manifest claim |
| same-run guard | W3 reviewed entry-point block on unknown submission | global deduplication |
| second product call | Fresh run after controller observation | automatic recovery of original run |
| oracle-evaluable | Required event/history binding is available | correct image, complete user task |
| case / call / attempt | Campaign unit / client invocation / durable product attempt | mixing denominators |

## Release gaps

G01: closed at retained-report field level; any-call sums are 4 resolved and
2 unresolved. Full event reconstruction remains G03. Historical evidence is unchanged.
G02: invocation/output located; exact immutable test-source provenance remains open.
G03: sanitized raw per-call/event/history manifest and hash verification.
`_sanitize_oracle` sums cumulative event snapshots; use deduplicated execution
bindings rather than its `event_counts` for published execution totals.
G04: selected Temporal/OpenTelemetry/Toxiproxy comparisons added; broader academic
nearest-work review remains open.
G05: clean-checkout artifact reproduction and actual target-year DSN formatting.
G06: visual/domain acceptance and model generalization are absent, not implied.

No new experiment is requested or authorized by this gap list.

## v0.3 evidence update

See [reconciliation addendum](dsn-evidence-reconciliation-20260927.md). G01 is
closed for aggregation: direct Windows report inspection confirms overlapping
any-call counts resolved=4, unresolved=2. The original Markdown 4/0 row remains
historical, not the paper’s controller aggregation. G02 is partially closed:
40-test Windows command/output and later 7-test macOS shim/controller check
are located; exact immutable test-source provenance remains open. G03 still
requires raw-event reconstruction and artifact-byte checks. G04 now includes
Temporal and OpenTelemetry responsibility comparisons, not an exhaustive survey.
This update supersedes historical open-status wording above.
## v0.12 independent-review corrections

Two sets of nine Windows CRLF source hashes are now delivered as reconstructed
Git snapshots; all match the original receipts. Correspondence is not runtime
attestation. Normalization v4 treats partial run recovery as unknown. Across
20 offline probes, only B2/F02-two-stage changes recovery from not_needed to
unknown; no composite verification becomes true. Raw private data remain outside
the named ZIPs. Runtime >=3.10 is explicit; clean extraction tested on 3.13.15.
See paper/review/RESPONSE_TO_INDEPENDENT_REVIEW_20261001.md and the delta receipt.
