# B2/W3 同协议配对故障实验方案

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent.
- Origin Mode: plan + bounded design review.
- Origin Date: 2026-09-18.
- Verification Status: DESIGN_REVIEWED / NOT_RUN.
- Version Label: `paired-ambiguous-submit-v2`; v1 was invalidated before interpretation because F00 single-stage failed from a research-harness-only result field.
- Trusted ledger: `d8ef0bccc84269b7d4a627adce5f6025a17ab024`; contract guard PASS before this plan.
- Frozen B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`.
- W2 research harness base: `a7482fedda8c98a3d31df916638fc241473316dc`; its product subtree must match B2.
- W3 product fix: `d45173af75d404ad79dc14568edd4c45f654abd2`.
- Scope: deterministic CPU component coverage only. This plan does not authorize live GPU, deployment-rate estimation, statistical expansion, B3 changes, or stable-branch merge.

## 1. Objective and frozen question

The experiment asks one bounded question:

> Under the same deterministic F00/F02/F03 schedule and the same independent CPU worker oracle, how do frozen B2 and W3 differ in backend submissions, true synthetic worker starts, recovery state, and valid completion?

This is the minimum fair comparison required before claiming that W3 changes the ambiguous-submit behavior. It is not a test of image quality, natural failure frequency, or general distributed exactly-once execution.

The expected trade-off from frozen H2 is directional, not an acceptance criterion: W3 may prevent an additional execution after F02 while leaving the operation unresolved. A negative result, no difference, or an unexpected completion loss remains valid evidence and must not be filtered.

## 2. Systems under test and contamination checks

| Label | Runtime checkout requirement | Product identity requirement | Research files |
| --- | --- | --- | --- |
| B2 | dedicated worktree rooted at W2 correction or a new research-only branch | `scripts/local_gpu_imagegen/**` and reused product tests byte-equivalent to frozen B2 | paired harness may differ from B2 only under `scripts/research/**`, `tests/research/**`, and `docs/research/**` |
| W3 | dedicated worktree rooted at the W3 product fix | product changes exactly traceable to `d45173a`; later docs/research-only commits allowed | paired harness must be byte-identical to the B2 paired harness |

Before any case starts, the runner must record:

1. actual checkout HEAD and branch;
2. product-subtree diff result against the designated B2 or W3 anchor;
3. SHA-256 of every paired harness, oracle, and semantic-test file;
4. protocol version, Python version, dependency versions, output root, and monotonic start time;
5. trusted-ledger checker result.

The B2 and W3 harness digests must match. Runtime labels and expected source SHAs are command inputs, not hard-coded by fault name. A product-subtree mismatch, harness mismatch, wrong data root, or contract failure stops both members of the affected pair.

## 3. Injection and observation design

### 3.1 Common product-level harness

Each case uses the real `AssetRunEngine` and `RunStore` entrance with a fresh persistent run directory. For F00/F02, the common research backend runner also uses the SUT version's real `BoundedJsonClient` against one identical localhost server fixture. The synthetic server owns the request/queue/worker boundary and emits independent events only from that boundary:

- `request_received`;
- `queue_item_created`;
- `execution_started` with a new `execution_instance_id` for every actual worker entry;
- `execution_finished` with outcome and artifact hash.

The fault controller must not predeclare execution events. It may release a response barrier only after the worker entry itself has emitted its event. Each new submission receives a distinct synthetic server job ID unless a separately named same-prompt-ID oracle self-check is running.

F02 applies the same physical condition to B2 and W3:

1. the localhost server accepts the POST;
2. it records request and queue events;
3. its worker starts and finishes once;
4. it closes the connection before returning the job-ID response.

The harness must not add, remove, or normalize `submission_outcome`. B2 and W3 each produce their own error through their checked-out `BoundedJsonClient`; raw error details are recorded before any interpretation. This exercises the actual W3 transport classification and its Engine/RunStore reaction in one CPU path. The historical W2 matrix directly raised an unmarked synthetic error and therefore cannot be reused as this comparison.

The second `generate_round` call in a fault case is a predeclared protocol observation, not an automatic experiment retry. It uses the same operation key and request bytes. If the product rejects it before the backend boundary, the oracle records no new request or execution. Crashed test processes are never silently retried.

### 3.2 Transport-origin preflight

Before the product cases, one separate preflight per system exercises that version's real `BoundedJsonClient.post_json` against the same local response-loss fixture. It records whether the real transport layer emits `submission_outcome=unknown`; it does not require a favorable value.

This preflight is kept outside the execution denominator. The integrated F02 product case, rather than an inference that stitches two separate tests together, supplies the bounded CPU path evidence. Neither check is a real ComfyUI/GPU observation because the server and worker remain synthetic.

### 3.3 Fault barriers

| Fault | First-call barrier | Second observation | Correctness property under test |
| --- | --- | --- | --- |
| F00 | none | none | normal completion remains possible; all-reject is not a success |
| F02 | localhost worker finished, POST response and job ID unavailable to product | same operation submitted once more by the protocol | product preserves ambiguity; W3 should not cross the backend boundary again without reconciliation evidence |
| F03 | job ID appears in error evidence; the two-stage arm also persists its canonical callback binding; worker finished and completion response is lost | same operation submitted once more | two-stage known-job recovery uses the same job; single-stage is characterization only |

F03 remains in the paired schedule as a specificity and regression control. W3 did not claim to add ordinary single-stage known-job reconciliation, and an unchanged result is expected to be reported as such.

## 4. Frozen schedule and denominators

There is one deterministic replay per system/path/fault tuple. Repeating identical fixtures may test stability later but does not create independent scientific samples.

| Layer | B2 | W3 | Combined scheduled |
| --- | ---: | ---: | ---: |
| F00 single-stage + two-stage | 2 | 2 | 4 |
| F02 single-stage + two-stage | 2 | 2 | 4 |
| F03 single-stage + two-stage | 2 | 2 | 4 |
| transport-origin check | 1 | 1 | 2, reported separately |
| oracle self-checks | 4 | shared identical checks | not experimental cases |

F00 is reported separately and never enters fault or injection denominators. For each system and each fault/path stratum, output all of:

- `scheduled`;
- `started`;
- `injection-confirmed`;
- `oracle-evaluable`;
- `resolved`;
- `unresolved`;
- `failed`;
- `not-run`.

`failed` means a product attempt reported failed and may overlap unresolved; it is not backend execution failure truth.

## 5. Outcomes and analysis

Primary observations are exact paired counts, not inferred deployment rates:

1. `oracle_execution_count` per case;
2. `backend_submission_count` per case;
3. recovery classification and whether the same job was reconciled;
4. valid completion and unresolved status;
5. product error code, barrier, durable job identity, and attempt statuses.

For each matched tuple, report `W3 - B2` for submission count and execution count, plus the categorical transition in recovery/completion state. Do not pool the two paths into a probability estimate. Do not compute `duplicate_execution_rate` from POSTs or from cases without a complete oracle.

The comparison is evidence-complete when all scheduled rows remain visible and every included execution comparison has:

- confirmed injection;
- complete request, queue, start, and finish events;
- unique execution-instance IDs;
- exact request digest and operation binding;
- an explicit observation-window close event;
- raw reported state and versioned interpreted mapping.

If the oracle is incomplete, retain the row and downgrade it to submission-level evidence. If W3 blocks another execution but lowers valid completion or increases unresolved, both effects must appear together; the result cannot be summarized as an unqualified reliability improvement.

## 6. Planned artifacts

| Artifact | Proposed repository path | Requirement |
| --- | --- | --- |
| protocol | `docs/research/dsn-paired-fault-protocol.md` | this reviewed plan |
| common runner | `scripts/research/run_paired_fault_matrix.py` | identical bytes in B2/W3 research worktrees |
| semantic tests | `tests/research/test_paired_fault_matrix.py` | assert barriers, identities, counts, recovery, and denominators |
| B2 raw result | `docs/research/runs/paired-v2-b2.json` | generated once; immutable after commit |
| W3 raw result | `docs/research/runs/paired-v2-w3.json` | generated once; immutable after commit |
| comparison | `docs/research/runs/paired-v2-comparison.json` | deterministic join by fault/path; no hidden row deletion |
| execution log | `docs/research/runs/paired-v2-commands.md` | exact commands, exit codes, durations, versions, and failures |

Raw result writers must refuse overwrite. The three `paired-v1-*.json` files are retained as invalid harness-run evidence and excluded from all paired conclusions. Existing W2 and Windows pilot evidence remains unchanged.

## 7. Monitoring, resource limits, and stops

- Environment: CPU only, Python 3.12 with the existing offline test dependency set.
- Hard timeout: 120 seconds per subprocess and 10 minutes for the complete paired package.
- Output roots: dedicated temporary/product-test roots only; never the Windows pilot or user output root.
- Network: localhost fixture only; no model download or remote service.
- Shared resources: no GPU, ComfyUI, ROS2, or production server ownership required.
- Retry policy: no automatic retry after process crash; one environment repair attempt may be made, and two consecutive environment failures stop the affected experiment.

Stop immediately for contract failure, product-anchor mismatch, harness-digest mismatch, oracle self-check failure, unconfirmed barrier, output-root conflict, or an oracle that cannot distinguish request receipt from execution start.

## 8. Design review disposition

### Accepted

- Same physical response loss, schedule, request bytes, worker oracle, mapping, and observation window across B2/W3.
- The SUT's real POST transport client produces its own raw error, so the harness does not silently grant W3's marker to B2.
- F00 remains outside the fault denominator.
- F03 is retained as a no-new-feature/regression control.
- Completion loss and unresolved cost are co-primary with duplicate-execution observations.

### Rejected

- Reusing the historical W2 matrix as the W3 comparison: it injects a semantic exception instead of the common physical POST response loss.
- Running only W3 and treating the old B2 summary as a pair.
- Treating two POSTs as two executions.
- Repeating deterministic cases and presenting repetitions as an estimated failure probability.
- Calling this a real ComfyUI/GPU end-to-end result.

### Gate decision

`DESIGN_REVIEWED / IMPLEMENTATION_NOT_STARTED / EXECUTION_NOT_STARTED`.

The next implementation unit is limited to the common paired runner, semantic tests, and overwrite-safe result plumbing under the proposed research paths. It must begin with failing tests for protocol identity and F02 marker semantics. No favorable outcome is required for acceptance.
