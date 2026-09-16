# W3 Ambiguous Submit Correction

Date: 2026-09-16

This is a bounded W3 product correction record. It is separate from the W2
negative evidence at `w2-fault-matrix.json`; that historical record is not
rewritten.

## Scope And Anchors

| Item | Value | Evidence level |
| --- | --- | --- |
| Branch | `research/w3-ambiguous-submit` | Git checkout |
| Starting commit | `a7482fedda8c98a3d31df916638fc241473316dc` | Git |
| Fixed B2 | `da65d57047b5a59e3403b49adf4605a1c0497c58` | Frozen research anchor |
| Research ledger | `d8ef0bccc84269b7d4a627adce5f6025a17ab024` | Trusted anchor |
| Prior negative evidence | `ad1ca0257036120f68df0f1a750aedf09f146b31` | Historical Git commit |
| Execution mode | CPU/model-free tests only | Actual local verification |

The correction addresses one bounded gap: ordinary single-stage POST transport
failure can leave the backend acceptance outcome unknown when no job ID was
persisted. It does not add reconciliation, B3, GPU execution, Windows
execution, or a server-side deduplication claim.

## Change

`BoundedJsonClient` adds `details.submission_outcome: "unknown"` only when a
POST transport-level exception occurs. HTTP status errors, request validation,
malformed responses, backend command errors, and artifact validation errors do
not receive this marker.

The engine persists a marked exception as an unresolved attempt without
inventing a job ID. The RunStore requires the explicit marker before accepting
this transition, rejects a known-job attempt being marked ambiguous, and blocks
all later submissions for the run until an independently implemented
reconciliation path exists. The only advertised next action is `get_run`.

The existing two-stage known-job timeout path remains unchanged: its exact job
ID can still be recovered without a new POST. A prompt/client idempotency key
is not treated as server-side deduplication.

## Verification

The following focused tests passed with `/Users/chevalgrand/.local/bin/python3.13`:

```text
python -m unittest tests.test_backend_base tests.test_run_store
Ran 114 tests ... OK

python -m unittest \
  tests.test_asset_run_engine.AssetRunEngineTests.test_ambiguous_single_stage_submit_blocks_resubmission \
  tests.test_asset_run_engine.AssetRunEngineTests.test_ambiguous_submit_persists_unknown_when_pending_cleanup_fails \
  tests.test_asset_run_engine.AssetRunEngineTests.test_backend_failure_is_recorded_without_consuming_round \
  tests.test_asset_run_engine.AssetRunEngineTests.test_two_stage_timeout_recovers_exact_job_without_resubmission \
  tests.test_backend_base.BoundedJsonClientTests.test_post_transport_failure_marks_submission_outcome_unknown \
  tests.test_backend_base.BoundedJsonClientTests.test_get_transport_failure_does_not_mark_submission_outcome_unknown \
  tests.test_run_store.RunStoreTransitionTests.test_unknown_submission_outcome_blocks_all_new_submissions
Ran 7 tests ... OK

python -m compileall -q scripts tests
exit code 0
```

The full three-file invocation was also attempted with Python 3.13. It reached
207 tests but could not provide a clean suite result because Pillow was not
installed in that interpreter: 11 existing image/mask/preview tests errored or
failed for dependency reasons. The initial system Python 3.9 invocation failed
at import because the repository requires Python 3.11 or 3.12. These are
environment facts, not converted into product or research outcomes.

The CI-style isolated dependency run used Python 3.13 before the W3.1 test was
added and completed `1187` tests with `28` failures, `6` errors, and `41`
skips. The raw historical output is retained in `w3-full-suite.log`; it is not
a post-W3.1 full-suite result. At that earlier commit, the W3 tests and all
research tests passed. The retained failures are the known macOS/POSIX
capability differences and isolated-environment release checks; they are not
W3 ambiguous-submit failures.

The terminal-review product regression command was rerun with Python 3.12.14:
the original 224-test scope plus the three W3 product tests yielded `227` passed,
`1` skipped, and zero failures. The ComfyUI stub emitted one expected
BrokenPipeError during an oversized-output test; that test passed and the
exception is not a W3 failure.

The W3.1 gate check also injects a pending-artifact cleanup failure after an
ambiguous POST. The run remains durably `unresolved`, releases its lock, and
retains a sanitized cleanup warning; the residue is not treated as execution
success or as permission to resubmit. The updated focused suite reached `209`
tests with `1` Windows-only skip and no failures; the terminal-review product
regression scope reached `227` passed with `1` skip.

The ledger contract guard, `verify_mcp.py`, and `verify_client_configs.py` all
returned exit code `0`. The guard returned `PASS` for the frozen ledger anchor;
the MCP verifier returned 17 tools and protocol `2024-11-05`.

## Denominators

No new execution experiment was scheduled by this correction. Therefore:

| Quantity | Value | Interpretation |
| --- | ---: | --- |
| scheduled | 0 | No new fault-matrix cases in W3 |
| started | 0 | No new matrix execution entrance |
| injection-confirmed | 0 | Not applicable to a new matrix |
| oracle-evaluable | 0 | No new execution-oracle run |
| resolved | 0 | No new matrix recovery case |
| unresolved | 0 | No new matrix recovery case |
| failed | 0 | No matrix denominator; test failures are environment classified |
| not-run | 0 | No scheduled W3 matrix case |

The product behavior was verified with synthetic runners and HTTP client
fixtures. The W2 deterministic CPU counts remain in their original evidence
file and are not recomputed here.

For reference, the retained W2 denominators are unchanged:

| Stratum | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F00 control | 2 | 2 | not applicable | 2 | 2 | 0 | 0 | 0 |
| F02/F03 faults | 4 | 4 | 4 | 4 | 1 | 3 | 2 | 0 |
| All retained cases | 6 | 6 | not applicable | 6 | 3 | 3 | 2 | 0 |

The `failed` values are product-reported failed attempts in the retained
synthetic matrix. They are not backend execution failures or deployment
failure rates.

## Evidence Boundaries

- Actual local verification: Python-level state transitions, structured POST
  transport marking, lock/recovery behavior, and regression tests.
- Component verification: the bounded JSON client and ComfyUI adapter contract;
  no live ComfyUI request was made.
- Synthetic verification: fake backend runners and fixture PNGs; no model
  inference or image-quality result is present.
- Not verified: target Windows host, target ComfyUI version or Git SHA, live
  queue semantics, GPU execution count, model downloads, deployment failure
  rate, duplicate-execution rate, and server-side prompt/client-ID
  deduplication.

## Remaining Gate

W3 correction is locally testable, but this record does not authorize W4,
real-GPU execution, B3, statistical inference, or paper claims. The single
next step is an independent W3 gate review of this branch and its diff.
