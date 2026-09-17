# W3 Windows ComfyUI Pilot Evidence

**Status:** generated / unreviewed. This record describes one real, bounded
Windows/ComfyUI two-stage pilot. It is not a visual acceptance, final artifact,
deployment result, reliability measurement, latency benchmark, or a
failure-rate / duplicate-execution-rate estimate.

## Reservation classification

The owner-recorded interruption revision is in
[`w3-windows-pilot-reservation-revision.yaml`](w3-windows-pilot-reservation-revision.yaml).
Its `revised_at` (`2026-09-17T05:07:59.0143506Z`) is before the pilot start
(`2026-09-17T06:42:35Z`); its revised end (`2026-09-17T07:07:59.0143506Z`) is
after completion. This pilot is therefore one **valid scheduled run** under
the recorded revised reservation.

## Identity and execution record

| Field | Retained value |
| --- | --- |
| Client SHA | `d45173af75d404ad79dc14568edd4c45f654abd2` |
| ComfyUI | `0.30.0` at `b1693ecba9f5b65f8c80ab36b195ab963ec92413` |
| Endpoint | loopback `http://127.0.0.1:8202` |
| Endpoint identity | `endpoint:9d0964454c0a063092a4cb95d8307912e42956e305e7266c3f9e31385f1cae56` |
| Run ID | `20260917T064132Z-4a275588bfbc` |
| ComfyUI job ID | `9ce8586b-918d-435c-b8bb-793fdb8d0499` |
| Started / completed | `2026-09-17T06:42:35Z` / `2026-09-17T06:43:19Z` |
| Model | `sd_xl_base_1.0.safetensors` |
| Model SHA-256 | `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` |
| Workflow | `sdxl-two-stage-copy-subject@1` |
| Workflow SHA-256 | `d54ecb21aa1c7981d22da2156fc40bacee304fb68a0b08a9c2b3d21fb4d79d10` |
| Component-bundle SHA-256 | `43bd2073db7675e2a1565deafc69ac904970b831be62849222a418d60d3e63e4` |
| Control SHA-256 | `521d025e89773118c91d2aa914436d8253581fed15a90ab0b95c6ec943921e02` |
| Dimensions / settings | `1280x720`; seed `4173`; subject seed `4174`; 30 steps; guidance 7.0; `dpmpp_2m` / `karras` |
| Idempotency key | `w3-windows-pilot-7dea3269-initial-01` |
| Stage budget | one two-stage round; 2 of 2 stage units consumed |

## Retained technical checks

- One ComfyUI backend job and one initial attempt were retained; `retry=0`.
  The retained result records the confirmed ComfyUI backend, checkpoint, route,
  and idempotency key; no CPU fallback, model switch, ordinary-route fallback,
  or alternate idempotency key is recorded.
- Generated round PNG SHA-256:
  `2dece226e1bc93ce0fd57bd381271c1a1e9faeb896d3aa4bfa942bd1bb92ca4f`.
  Base-stage SHA-256: `5241cecf89ddc857390d726082cb307930369dda77e2647bdc2295cd4ca65544`.
  Mask SHA-256: `551157f0599b747c53e01b86e7e1d80791a4bfacb9b4321066629b3981fa580b`.
- Protected-pixel verification checked 577,536 pixels and reported zero
  mismatches. The soft-mask record reported zero nonzero pixels in copy and
  outside regions, 341,696 positive interior pixels, and monotonic feathering.
- Preview was unavailable because the serving Python environment lacked Pillow
  (`preview_unavailable:pillow_missing`). No visual review was recorded, and
  `local_gpu_finalize_run` was not called.

## Scope and denominator

| Quantity | Value |
| --- | ---: |
| Valid scheduled cases | 1 |
| Started cases | 1 |
| Generated cases | 1 |
| Retries | 0 |
| Visual reviews | 0 |
| Finalized artifacts | 0 |

The PNG, base image, mask, model, and local output directory remain local and
are intentionally not included in this repository. This one generated,
unreviewed run does not support claims about visual quality, production
readiness, concurrency, deployment reliability, general latency, or population
failure/duplicate-execution rates.
