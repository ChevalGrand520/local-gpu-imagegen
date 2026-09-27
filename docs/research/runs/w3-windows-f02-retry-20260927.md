## Material Passport

- Origin Skill: ARIS run-experiment
- Mode: run
- Input Commit: `2f4433aa27b92cdfb124c56b5d064decc7f28376`
- Verification Status: PARTIALLY_VERIFIED
- Gate Decision: `W3_HOLD / F00 PRE-SUBMIT BOUNDARY BLOCK`

# W3 Windows F00/F02 Retry

## Outcome

The corrected module-mode controller entered the fixed campaign and completed both F00 controls. Both product calls returned a product-reported `unresolved` state before submission. The loopback proxy recorded zero `POST /prompt` requests and zero backend acceptances for both cases.

The client error was the stable code `approved_private_catalog_entry_mismatch` at stage `model_route`. The cause is a research harness boundary: when the product MCP server is pointed at the loopback fault proxy, the product computes an endpoint identity from the proxy URL, while the private catalog remains bound to the actual ComfyUI endpoint. The product correctly rejects that mismatch. This is not backend execution failure and is not a deployment failure-rate observation.

The frozen controller therefore marked both F02 cases `not_run`. No image, backend execution, retry, or artifact was produced.

## Denominators

| planned | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 2 | 0 | 0 | 0 | 2 | 0 | 2 |

The two F00 calls are case-level unresolved observations. The two F02 rows are not-run by protocol. No duplicate-execution or deployment failure rate is estimated.

## Preparation Evidence

- Trusted research contract: PASS at `d8ef0bccc84269b7d4a627adce5f6025a17ab024`.
- B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`, clean detached checkout.
- W3: `d45173af75d404ad79dc14568edd4c45f654abd2`, clean detached checkout.
- Windows/GPU/backend preflight: 10/10 checks passed.
- GPU: RTX 5070 Ti Laptop GPU, expected UUID and driver identity.
- ComfyUI: `v0.30.0`, SHA `b1693ecba9f5b65f8c80ab36b195ab963ec92413`, run-owned PID verified.
- Pinned model SHA matched.
- B2 and W3 direct route probes passed and their frozen request digests matched.
- Research component suite: 40 tests passed on Windows Python 3.15.0a8; compileall and `git diff --check` passed. This is not CI verification on Python 3.11/3.12.

## Evidence Boundary

- Real Windows evidence: reservation, identity preflight, route probes, product-client calls, and proxy observations.
- Component evidence: independent oracle connect and 40 research tests.
- Real backend execution evidence: none.
- `POST` count: 0 for both F00 cases.
- `execution_started`, `execution_finished`, execution instance IDs, artifacts: unknown/not observed.
- Image quality, duplicate execution rate, deployment failure rate: not measured.

## Cleanup

- Reservation: released early at `2026-09-27T01:42:16Z`.
- Queue was empty at cleanup.
- Run-owned ComfyUI PID was stopped.
- Run-scoped ComfyUI and campaign tasks were unregistered.
- Port 8202 was verified closed.
- Raw configs, report JSONL, stderr, and model/output paths remain Windows-local.

## Automatic Next-Stage Assessment

W3 remains on hold. The next required decision is a research-design/harness boundary review for transport interception that preserves the actual backend endpoint identity. The current proxy cannot be used to measure F02 through the product's endpoint-bound trust gate without either a separately authorized research-only transport adapter or a product/harness change under a new gate.

Do not rerun F00/F02 with the same proxy arrangement. Do not infer backend failure, duplicate execution, or a rate from this retry.
