# W0 Reuse Map

Date: 2026-09-16

This is a bounded CPU package record for `local-gpu-imagegen`. It does not
change the product contract, B2 behavior, or the research ledger.

## Anchors And Scope

| Item | Fact | Evidence level |
| --- | --- | --- |
| Target checkout at W2 correction start | `ad1ca0257036120f68df0f1a750aedf09f146b31` | Git checkout |
| Fixed B2 | `da65d57047b5a59e3403b49adf4605a1c0497c58` | Research design / Git |
| Research ledger | `d8ef0bccc84269b7d4a627adce5f6025a17ab024` | Trusted anchor |
| Work branch | `research/w2-corrections` | Git |
| Allowed writes | `docs/research/**`, `scripts/research/**`, `tests/research/**` | Execution contract |
| Protected files | Research design, terminal review, contract, ledger governance and project guide | Not modified |

The initial W0 branch was created from the fixed B2 SHA and produced the bounded
CPU evidence package in `ad1ca0257036120f68df0f1a750aedf09f146b31`. This
correction branch starts from that evidence commit; B2 remains the unchanged
product reference and no product source, existing B2 test, model, output root,
or backend service was changed.

## Existing Capabilities

### Durable run path

- `scripts/local_gpu_imagegen/run_store.py:163` defines `RunStore`, the
  filesystem fact source for one output root.
- `RunStore.begin_attempt()` normalizes the request, computes the existing
  `request_hash`, acquires the per-run lock, and records an active attempt.
  Completed idempotent attempts can be returned without invoking a backend.
- `RunStore.mark_attempt_image()` validates and records a single-stage image.
- `RunStore.mark_attempt_artifacts()` validates base/mask/final artifacts and is
  restricted to the reviewed two-stage workflow.
- `RunStore.mark_attempt_backend_job()` persists a ComfyUI job only for the
  reviewed two-stage workflow. `mark_attempt_unresolved()` requires that exact
  job identity, so it is not a solution for an unknown job ID.
- `RunStore.get()` invokes stale-attempt recovery. A dead active attempt with a
  job identity becomes `unresolved`; a dead active attempt without one becomes
  `interrupted` and returns to its last stable state. It does not infer backend
  execution from a client attempt.

### Engine and adapter entrances

- `scripts/local_gpu_imagegen/engine.py:52` defines `AssetRunEngine`.
- `AssetRunEngine.start_run()` is the product run creation entrance.
- `AssetRunEngine.generate_round()` is the product generation entrance. It
  builds the attempt request, calls `RunStore.begin_attempt()`, invokes the
  configured backend runner, validates the result, publishes the PNG through a
  pending path, creates a preview, and calls `RunStore.complete_attempt()`.
- Ordinary single-stage requests pass one `output_path` to the backend runner.
  Backend errors are recorded by `fail_attempt`; an error is not independently
  equivalent to backend execution failure.
- Two-stage requests pass stage paths and install a
  `backend_job_callback`. On a timeout, the known ComfyUI job is persisted as
  unresolved and can be reconciled by calling the same request with
  `recovery_job_id`; the recovery path does not POST a new job.
- `scripts/local_gpu_imagegen/backends/comfyui.py:203` defines
  `ComfyUIAdapter.generate()`. The normal entrance POSTs `/prompt`, extracts
  `prompt_id`, invokes the callback if present, then polls `/history/<job_id>`
  and `/queue` before downloading owned outputs. A recovery request validates
  the known job ID and skips the POST.
- `scripts/local_gpu_imagegen/backends/comfyui.py:299` defines the polling
  entrance. A timeout retains the job ID in error details, but that detail is
  not the same as durable product `backend_job` state on the ordinary route.

### Existing recovery tests and reusable fixtures

- `tests/test_run_store.py` covers stale active-attempt recovery, missing or
  malformed locks, completed idempotent reuse, and the two-stage unresolved
  job path.
- `tests/test_asset_run_engine.py` covers
  `test_two_stage_timeout_recovers_exact_job_without_resubmission`, crash after
  image publication, completed retry preview rebuilding, and backend failure
  recording.
- `tests/fake_backend_server.py` is an HTTP request/response fixture. It
  records method, path, body, and headers and is reused by ComfyUI adapter
  tests. It does not record worker start or execution instances.
- `tests/test_asset_run_engine.py` supplies reusable model-free product fixtures
  (`FakeBackendRunner`, `TwoStageBackendRunner`, profile/catalog/router setup,
  and PNG writers). The W2 harness wraps these fixtures with an independent
  CPU lifecycle oracle; wrapper request counts are not used as execution truth.

## Environment And Dependencies

The CI contract in `.github/workflows/tests.yml` tests Ubuntu and Windows with
Python 3.11 and 3.12. It installs `setuptools>=68`, `Pillow>=10`,
`uv==0.11.16`, and `py7zr==1.1.3`, then runs `compileall`, the unittest suite,
`verify_mcp.py`, and `verify_client_configs.py`. The package itself declares
Python `>=3.11` and `py7zr==1.1.3`; Pillow is a test/runtime-optional
dependency used by mask-related paths.

Local baseline verification used the already installed Python 3.12.14 through
an isolated `uv run` environment with the CI dependency set. The three
terminal-review suites passed with 224 tests, one skip, and zero failures.

The first attempt with system Python 3.9.6 failed at import because the code
uses `dataclass(slots=True)`; the second attempt with bare Python 3.12 lacked
Pillow and produced dependency failures. Neither attempt modified the
repository or product state.

## Target ComfyUI Version

`PENDING`: this macOS checkout cannot access the target Windows host or its
online ComfyUI service within this package. The adapter fixture reports
`0.3.50` in `tests/test_comfyui_adapter.py`, but that is synthetic test data,
not the target installation version. The README's Windows acceptance history
is not a current inventory. No version is guessed, and no Windows/GPU command
was run.

## Corrected CPU Package Evidence

The research-only exporter and deterministic fault-coverage harness live under
the permitted research paths. They use the product `AssetRunEngine` entrance
and the existing model-free fixture. The corrected exporter refuses to
overwrite an existing export, confines referenced input/artifact files to the
evidence root, and requires exact oracle job/artifact/lifecycle bindings before
`execution_verified` can be true.

The CPU worker entry supplies lifecycle events to the independent oracle:

`request_received -> queue_item_created -> execution_started -> execution_finished`

Each worker start gets a fresh `execution_instance_id`, including two
executions that share a prompt ID. F00 is a separate control arm. F02 creates
distinct job identities per actual submission; F03 distinguishes a known job
whose completion response is lost from F02's pre-job-ID response loss. The
two-stage F03 arm exercises same-job recovery without a second submission.

The resulting evidence is deterministic CPU/synthetic backend evidence. It can
characterize B2 control-plane behavior and the oracle protocol; it cannot
establish ComfyUI queue semantics, GPU execution count, image quality, Windows
behavior, deployment failure rates, or a natural-world duplicate-execution
rate. Those facts remain pending.

## Gaps And Non-Generalizable Conclusions

| Classification | Record |
| --- | --- |
| Already exists | Durable attempts, idempotency hash, stale recovery, known two-stage job recovery, artifact validation, and ordinary/two-stage product entrances |
| W1/W2 added here | Read-only raw/interpreted/oracle export v2 and deterministic CPU worker lifecycle coverage with separate F00 control and F02/F03 mappings |
| Pending validation | Target Windows OS/runtime, actual ComfyUI version, real adapter-to-ComfyUI full path, GPU execution count, model and workflow inventory |
| Component evidence only | Existing HTTP stub response-loss probes and adapter tests; they do not prove backend acceptance or execution |
| Synthetic evidence only | Fake runner PNGs, CPU fault cases, and oracle self-checks; they are not real inference results |
| Cannot generalize | A prompt/client ID is not server-side deduplication; a product `failed` attempt is not backend execution failure; deterministic CPU counts are not deployment rates; a known job recovery test is not ordinary-path recovery; a component probe is not a GPU duplicate-execution observation |

Only the permitted research directories are changed by this package. Product
fixes remain outside scope and require the W3 gate.
