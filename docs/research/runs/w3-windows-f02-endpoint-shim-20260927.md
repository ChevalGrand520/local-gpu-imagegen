## Material Passport

- Origin Skill: ARIS run-experiment
- Mode: run
- Input Commit: `d62cb372898b210942fdafb4794e8b85d2cf23c2`
- Verification Status: PARTIALLY_VERIFIED
- Gate Decision: `BOUNDED W3 EVIDENCE / NO RATE CLAIM`

# W3 Windows F00/F02 Endpoint Preserving Pilot

## Outcome

The endpoint preserving research shim allowed the product MCP server to keep
the real ComfyUI endpoint identity while routing only `POST /prompt` through
the reviewed loopback fault proxy. The independent WebSocket oracle used the
same ComfyUI `client_id` as the product operation key, which is required for
ComfyUI to deliver execution events to the observer connection.

The fixed four case campaign completed:

- B2 F00: one POST, one backend acceptance, one execution start, one finish,
  completed history, oracle evaluable.
- W3 F00: one POST, one backend acceptance, one execution start, one finish,
  completed history, oracle evaluable.
- B2 F02: first response was intentionally dropped after backend acceptance;
  the product reported unresolved, then a second submission completed.
- W3 F02: the same controlled response loss and recovery sequence completed.

## Case Denominators

| planned | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 4 | 2 | 4 | 4 | 0 | 0 | 0 |

The table is case-level. At call level, the two F02 cases each had one
unresolved first product call followed by one resolved recovery call. Across
the campaign there were 6 product calls, 6 proxy submissions, and 6 observed
execution instances. Each F02 case had 2 submissions and 2 executions.

These observations describe the fixed fault cases. They do not estimate a
deployment failure probability or a natural duplicate-execution rate.

## Verified Preparation

- Trusted research contract: PASS at
  `d8ef0bccc84269b7d4a627adce5f6025a17ab024`.
- B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`, clean detached checkout.
- W3: `d45173af75d404ad79dc14568edd4c45f654abd2`, clean detached checkout.
- Windows/GPU/backend preflight: 10/10 checks passed.
- GPU: RTX 5070 Ti Laptop GPU with the frozen UUID and driver identity.
- ComfyUI: `v0.30.0`, SHA
  `b1693ecba9f5b65f8c80ab36b195ab963ec92413`.
- Pinned model and workflow hashes matched the frozen configuration.
- B2 and W3 route probes produced matching frozen request digests.

## Evidence Boundary

- Real Windows evidence: reservation, identity preflight, product calls,
  proxy receipts, backend WebSocket execution events, history completion, and
  artifact hashes.
- Component evidence: endpoint-preserving transport shim, independent oracle,
  and research tests.
- Synthetic evidence: CPU fault matrix remains deterministic fault coverage.
- Unsupported claims: deployment failure rate, population duplicate-execution
  rate, performance improvement, and visual-quality superiority.

## Cleanup

- Queue was empty at cleanup.
- Run-owned ComfyUI process was stopped.
- Run-scoped ComfyUI and campaign tasks were unregistered.
- Port 8202 was verified closed.
- Raw campaign JSONL, private configs, model files, and generated images remain
  Windows-local.

## Interpretation

The result supports a bounded claim: under the controlled F02 response-loss
barrier, the product recorded an unresolved first call, submitted a second
call after oracle-confirmed completion, and the oracle observed two distinct
execution instances for the case. The result does not support a probability
claim. The endpoint preserving shim and same-client-id observer are part of
the research harness and must be described as such.
