# Paired B2/W3 CPU fault run log

## Material Passport

- Date: 2026-09-18.
- Protocol: `paired-ambiguous-submit-v2`.
- Status: COMPLETE / DETERMINISTIC_CPU_SYNTHETIC_WORKER_ONLY.
- Trusted ledger: `d8ef0bccc84269b7d4a627adce5f6025a17ab024`; guard PASS.
- Frozen B2 product: `da65d57047b5a59e3403b49adf4605a1c0497c58`.
- W3 product fix: `d45173af75d404ad79dc14568edd4c45f654abd2`.
- B2 research checkout: `10e6d5c7d9e0b0950bdfaba3f6062e5cad86417e` on `research/paired-b2`.
- W3 research checkout at execution: `7b585d2e7310f18c3582d2a63a55b098c86f9ea8` on `paper/dsn-paired-protocol`.
- Python: 3.12.14; dependency environment from the existing offline uv cache.
- Active work: approximately 20 minutes for implementation, diagnosis, execution, and recording; no GPU/network/model wait counted.

## Harness identity

The B2 and W3 bytes matched before v2 execution:

| File | SHA-256 |
| --- | --- |
| `scripts/research/run_paired_fault_matrix.py` | `dead74d91c72c3bce107a16941ffcd45f852054f9aa1d58aaf16a29c3aa1ffc4` |
| `tests/research/test_paired_fault_matrix.py` | `1a391562f89b9e203035850fe8116ceaa527d5489c19fdc90b5b8fd95dc7311c` |
| `scripts/research/execution_oracle.py` | `ad763f7f35f9ec0024eb24cea9e9c76f1c430c907af57bf92f48eb64dfe3ffaa` |

Product-subtree `git diff --exit-code` checks against B2 and W3 anchors both exited 0. The research harness and tests were the only executable additions to the B2 research branch.

## TDD and validation commands

All commands used `uv run --offline --no-project --python 3.12 --with 'Pillow>=10'` unless shown otherwise.

| Command | Exit | Result |
| --- | ---: | --- |
| `python -m unittest tests.research.test_paired_fault_matrix` before implementation | 1 | import error for the intentionally absent runner; RED |
| same command after first implementation | 0 | 5 tests passed on W3 |
| research suite: execution oracle + exporter + historical matrix + paired matrix | 0 | 24 tests passed |
| paired tests on initial B2 cherry-pick | 1 | 1 failure: F02 two-stage had one execution, exposing an incorrect cross-path expectation |
| direct B2 diagnostic without `PYTHONPATH` | 1 | environment import error; no case started |
| same diagnostic with `PYTHONPATH=scripts:.` | 0 | B2 F02 two-stage was `partial/outcome_unknown`, 1 submission, 1 execution |
| paired tests after preserving that B2 behavior | 0 | 5 tests passed on B2 and W3 |
| runtime-identity regression before implementation | 1 | `runtime_identity` missing; RED |
| paired tests after runtime identity implementation | 0 | 5 tests passed on B2 and W3 |
| F00 healthy-control regression against v1 harness | 1 | single-stage `invalid_backend_result`; RED and stop condition triggered |
| paired tests after removing the two-stage-only field from single-stage results | 0 | 6 tests passed on B2 and W3 |
| `python -m compileall -q scripts/research tests/research` | 0 | passed before formal execution |
| `git diff --check` | 0 | passed before formal execution |
| final W3 research suite: execution oracle + exporter + historical matrix + paired matrix | 0 | 25 tests passed; 0 failures/errors/skips |
| final B2 research suite: execution oracle + exporter + historical matrix + paired matrix | 0 | 24 tests passed; 0 failures/errors/skips |

No test was skipped. The historical full product suite was not rerun because product code was unchanged; prior full-suite limitations remain applicable.

## Invalid v1 run retained

The first formal commands used the same hard-timeout wrapper and exited 0:

```text
perl -e 'alarm shift; exec @ARGV' 120 uv run ... run --system-label B2 --source-sha da65d57047b5a59e3403b49adf4605a1c0497c58 --output <w3-root>/docs/research/runs/paired-v1-b2.json
perl -e 'alarm shift; exec @ARGV' 120 uv run ... run --system-label W3 --source-sha d45173af75d404ad79dc14568edd4c45f654abd2 --output docs/research/runs/paired-v1-w3.json
perl -e 'alarm shift; exec @ARGV' 120 uv run ... compare --b2 docs/research/runs/paired-v1-b2.json --w3 docs/research/runs/paired-v1-w3.json --output docs/research/runs/paired-v1-comparison.json
```

Audit found `F00-single-stage` failed in both systems because the research harness added a two-stage-only `workflow_job_id` field to a single-stage result. This invalidated the healthy control. The three v1 files are retained unchanged and excluded from every conclusion:

| File | SHA-256 |
| --- | --- |
| `paired-v1-b2.json` | `088a696fbef4bf3b7e2382b92b6f12b45f5e29f9c6545634a598f0a10ea5818f` |
| `paired-v1-w3.json` | `b9e16894de7aca45d3e81bb0b46bf14217617e338f97bd394ff940a074897a01` |
| `paired-v1-comparison.json` | `dad88afa049752349b5af7703a0ce4c3f75a734dabffdfe2203da2dcc3a94f65` |

## Valid v2 execution commands

Before v2, the trusted contract, both product-anchor checks, harness digest equality, and absence of destination files all exited 0. Each run had a 120-second process alarm; observed wall time was about 3.7 seconds per matrix.

```text
perl -e 'alarm shift; exec @ARGV' 120 uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python scripts/research/run_paired_fault_matrix.py run --system-label B2 --source-sha da65d57047b5a59e3403b49adf4605a1c0497c58 --output <w3-root>/docs/research/runs/paired-v2-b2.json
perl -e 'alarm shift; exec @ARGV' 120 uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python scripts/research/run_paired_fault_matrix.py run --system-label W3 --source-sha d45173af75d404ad79dc14568edd4c45f654abd2 --output docs/research/runs/paired-v2-w3.json
perl -e 'alarm shift; exec @ARGV' 120 uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python scripts/research/run_paired_fault_matrix.py compare --b2 docs/research/runs/paired-v2-b2.json --w3 docs/research/runs/paired-v2-w3.json --output docs/research/runs/paired-v2-comparison.json
```

All three commands exited 0. Result hashes:

| File | SHA-256 |
| --- | --- |
| `paired-v2-b2.json` | `3ad68bdb1aaf3c6befc2f6518da276bd31cc1665173b0b6c507a0a15547493f8` |
| `paired-v2-w3.json` | `891bdc27cfd4f5c1e12002975519d5f4e32e8531d9be7455fdad2bf217d157ba` |
| `paired-v2-comparison.json` | `c533c40d194d92000f3f48fede638b352432253b0e6aecd549cf80fb9b8a7d5d` |

## Denominators

| System/layer | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B2 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| B2 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 2 | 0 |
| W3 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| W3 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 1 | 0 |

`failed` is a product attempt-status count and overlaps unresolved. It is not backend execution failure truth.

## Result boundary

- F02 single-stage: B2 observed 2 submissions and 2 synthetic worker executions, then valid completion. W3 observed 1 submission and 1 execution, blocked the second call, and remained unresolved.
- F02 two-stage: both observed 1 submission and 1 execution. B2 remained partial/outcome-unknown; W3 retained an explicit unresolved unknown-submission state. There is no execution-count improvement in this arm.
- F03 single-stage: both observed 2 submissions and 2 executions, then valid completion. W3 did not change this path.
- F03 two-stage: both reconciled the same known job with 1 submission and 1 execution. This is existing B2 capability.
- F00: both paths completed normally in both systems.

Therefore the deterministic schedule contains one paired arm with one fewer synthetic execution under W3, accompanied by loss of valid completion within the fixed observation window. This is a bounded CPU synthetic-worker observation, not a duplicate-execution rate, deployment failure probability, real ComfyUI execution result, or unqualified reliability improvement.

## Resource and privacy boundary

No GPU, model, remote backend, Windows service, ROS2 process, or production output root was used. Localhost HTTP and isolated temporary run roots only. The JSON contains test fixture identities and synthetic artifact metadata; no PNG, model, user input, credential, or private dataset is included.

## Delivery status

Local commits completed. The first normal pushes failed with an HTTP/2 framing error for B2 and a stalled W3 connection that was stopped after more than 90 seconds. One bounded retry used command-local `-c http.version=HTTP/1.1`; B2 then returned an empty reply and W3 could not connect to `github.com:443`. After these two network failures, no further push was attempted. No Git configuration was persisted, no history was rewritten, and PR #6 remains at its previously published protocol-only revision until network access is restored.
