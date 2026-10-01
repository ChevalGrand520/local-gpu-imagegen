# Paired-v1 CPU implementation checkpoint

Status: CPU_COMPONENT_CHECKS_PASS_WINDOWS_INTEGRATION_PENDING.
Tool v0.18 source/PDF/bundles remain byte-identical to their freeze. No Windows
connection, generation, GPU reservation, model download or manuscript change
was performed in this checkpoint.

## Implemented

- `f02_loopback.py`: one-shot FPRE after complete body reception and before
  `_forward`; per-request append-only stage journal. A response-loss exception
  after sending retains `upstream_send_started`, even if legacy `forwarded` is
  false. Client delivery failure no longer creates a second receipt.
- `f02_product_client.py`: explicit `paired_same_run` mode, identical generation
  arguments and original run identity, no W3-only unknown admission check.
  Historical v2 retains its check. Generation request/return records include
  monotonic timestamps; artifact hashing is outside the RPC latency interval.
- `paired_ambiguity.py`: shared caller-visible unknown classification, return
  +1-second retry schedule, generation semantics including seed, distinct
  proxy/send/acceptance metrics, cumulative CPU lifecycle deduplication.
- `paired_ambiguity_operation.py`: B2/W3 operation controller; native B2 extra
  POST is a result, not a W3 guard failure. Injection is checked before retry;
  oracle completion is observed afterward. It is not a resource-owning launcher.
- Isolated archived-product CPU worker/runner, and a separate same-information
  exporter/field-parser probe runner. New runners were tested with Python
  3.13.15; no claim that this new harness supports every Python >=3.10 version.

## Executed checks

`python3.13 -m unittest discover -s tests/research -q`: exit 0,
**71 tests in 8.534 seconds**. Ten new tests cover FPRE no-forward behavior,
post-send exceptions, an append-only file journal, shared scheduling, semantic seed
binding, cumulative snapshots, and the operation controller.

The final B0 batch has **12/12 constructed CPU operation checks**, against
archived native B2 `da65d57047b5a59e3403b49adf4605a1c0497c58` and W3
`d45173af75d404ad79dc14568edd4c45f654abd2`. Twenty imported product-module
hashes per operation match the relevant archived tree; pair semantics match.
The worker/model and MCP dispatch adapter are synthetic. Calls enter the public
engine and use real HTTP response loss and PNG bytes; no internal guard is
called directly and no research code rewrites product manifests. MCP stdio,
Windows inventory rebuilding and real ComfyUI execution are not measured here.

| CPU condition | B2 proxy/upstream/worker lifecycles | W3 proxy/upstream/worker lifecycles | P-stop proxy/upstream/worker lifecycles | Original run completion B2/W3/P-stop |
|---|---|---|---|---|
| F00 | 1/1/1 | 1/1/1 | 1/1/1 | yes/yes/yes |
| F02 | 2/2/2 | 1/1/1 | 1/1/1 | yes/no/no |
| FPRE | 2/1/1 | 1/0/0 | 1/0/0 | yes/no/no |

Three additional W3 scope probes: healthy same-key replay performs no extra
POST; an unknown run rejects a new key; a new run can complete while the old
run remains unresolved. FPRE first-send absence and retained artifact bytes
were checked. W3 fault retries preserve the original manifest byte hash.

B2 module: **12/12 synthetic offline probes**. Each view has 12 correct answers,
3 explicit unknowns and 0 false affirmations. Positive calibration verifies
completion; matched completed-but-unresolved records retain the recovery veto.
Input file hashes are unchanged. The ordinary parser and exporter agree on
all twelve probes: this batch provides no accuracy/information advantage.
Likewise P-stop and W3 share the fault-case submission counts. These negative
comparisons belong in the research decision; they do not invalidate Tool
integration, but cannot support superiority over the simple baselines.

Machine-readable receipt: `PAIRED_CPU_CHECKS_20261001.json`. Counts are synthetic
operation/probe counts, never deployment rates or GPU savings.

## Retained local captures and development attempts

Private local capture parent: `../../paired-cpu-captures/` from this checkout.
These directories are not included in a paper delivery bundle.

- `20261001-pilot-01`: STOPPED at first B2 F00, due to the CPU adapter failing
  to unpack `(data, preview)`. Product code was unchanged; this failure remains.
- `20261001-pilot-02`: 12-operation PASS after matching the product MCP dispatch
  unpacking. `pilot-03`: 12-operation PASS after imported-module/cross-pair
  provenance checks. `pilot-04`: 12-operation PASS after retaining PNG
  bytes across product failure cleanup and checking W3 manifest stability.
  `pilot-05`: final 12-operation PASS after capturing the UTC return timestamp
  at the RPC boundary rather than after artifact hashing. Each is a fresh
  source-frozen development batch. They are not extra research samples and were
  not pooled. In total these batches started 49 CPU operations.
- `20261001-evidence-probes-01`, `-02`, `-03`: separate 12-probe PASS batches as
  dependency snapshots and actual input-file byte hashes were added. The final
  receipt uses `-03`, not a pooled 36-probe denominator.
- The initial nonexistent-parent setup error occurred before any operation;
  the runner now creates missing parent directories without allowing overwrite.

Final commands (no implicit overwrite):

```text
python3.13 scripts/research/run_paired_ambiguity_cpu.py --output <fresh-capture-root>
python3.13 scripts/research/paired_evidence_probes.py --output <different-fresh-capture-root>
python3.13 -m unittest discover -s tests/research -q
```

All final B0/B2 report, source-freeze, input-file and Tool freeze hashes were
rechecked after execution. Successful fixture checks do not authenticate a
future Windows execution or certify runtime call-chain provenance.

## Remaining Windows launch work

The legacy reserved runner and preflight still describe the historical four
case namespace / W3-only two-case actual schedule. Do not repurpose them by
changing a label. Integrate the new controller into a six-operation reserved
runner with an owned isolated backend per operation, unchanged within its two
calls. Require source/config bytes before backend startup, live explicit
reservation, numeric-IP SSH, startup/control-calibrated deadline, 1 GiB storage
and whole-campaign limits, and cleanup of owned services only.

That integration and native MCP route/inventory preflight are still open.
Windows tasks remain NOT_RUN. The frozen protocol's GPU budget is unconsumed.
