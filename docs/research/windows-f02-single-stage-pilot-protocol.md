# Windows/ComfyUI F02 single-stage paired pilot protocol

## Material Passport

- Protocol date: 2026-09-18.
- Status: **DESIGN REVIEWED / NOT RUN**.
- Purpose: one bounded real-backend semantic check after paired-v2.
- Trusted ledger: `d8ef0bccc84269b7d4a627adce5f6025a17ab024`.
- Frozen B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`.
- W3 client: `d45173af75d404ad79dc14568edd4c45f654abd2`.
- Authorized scope: F00 and F02, single-stage only, on the frozen Windows host.
- Prohibited expansion: no F03, two-stage fault matrix, statistical repetition,
  model download, service modification, CPU fallback, ROS2, shared server, or
  product-code change.

This document is an execution protocol, not evidence that the pilot happened.
Every expected outcome below is a hypothesis, not an acceptance criterion.

## Frozen environment

| Field | Required value |
| --- | --- |
| Host | `LAPTOP-7QD7KR9F` |
| Resource owner | `Capricorn`; record actual reservation start/end at run time |
| GPU | NVIDIA GeForce RTX 5070 Ti Laptop GPU |
| GPU UUID | `GPU-25c43be6-ab43-2700-35f9-1db584b84dd8` |
| ComfyUI endpoint | backend `http://127.0.0.1:8202`; clients use the one-shot loopback fault proxy |
| ComfyUI version | `v0.30.0` |
| ComfyUI Git SHA | `b1693ecba9f5b65f8c80ab36b195ab963ec92413` |
| Model | existing `sd_xl_base_1.0.safetensors` |
| Model SHA-256 | `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` |
| Product checkouts | detached B2 and W3 anchors above, each with only reviewed research-side pilot files |
| Product output roots | separate fresh local roots for B2 and W3 under a timestamped campaign directory |
| Backend observation window | 180 seconds from each queue acceptance |
| External hard timeout | 900 seconds per case |

The 180-second backend window is more than four times the prior 44-second real
two-stage pilot duration. The 900-second hard timeout reuses the established W3
command ceiling and limits setup, collection, and teardown around a hung case;
neither value is a latency target. Do not infer a reservation from current
process ownership. Record the actual owner, start, end, boot identity, endpoint
identity, GPU UUID, free space, and competing compute processes immediately
before the run.

Any mismatch in host, GPU UUID, ComfyUI version/SHA, model hash, product SHA,
data root, or resource ownership stops the affected experiment. Do not repair,
upgrade, restart, or reconfigure ComfyUI inside this protocol.

## Frozen request

Before scheduling a case, materialize one ordinary single-stage request package
and freeze it for both clients:

- profile: `standalone-illustration`;
- backend: ComfyUI only; no alternate route or CPU fallback;
- model and hash: the values above;
- prompt: `A red ceramic cup on a plain gray table, studio lighting.`;
- negative prompt: `text, watermark`;
- width/height: `768 x 512`;
- seed: `4173`;
- steps: `20`;
- guidance: `7.0`;
- sampler/scheduler: `dpmpp_2m` / `karras`;
- maximum rounds: one;
- review/finalize: disabled for this pilot.

Record the canonical request digest, compiled prompt digest, workflow graph
digest, input digest, route identity, validator version, and output namespace.
The generation semantics and canonical request digest must match across B2 and
W3. Run-specific IDs and separate product output roots are provenance fields
and must not be included in that canonical digest. If the two clients cannot
materialize semantically identical requests, stop before F00.

Use a fresh run and output root for every scheduled case. Do not reuse an
artifact to turn an unresolved case into a success, and do not delete partial,
failed, unknown, or duplicate outputs.

## Fault boundary

A research-only loopback reverse proxy sits between the product client and
`127.0.0.1:8202`. Choose and record an unused loopback port at run time. The
proxy must preserve request bytes and must never synthesize a successful
ComfyUI response.

For F00, the proxy forwards the request and response unchanged.

For the first call in F02, the proxy must:

1. receive exactly one client `POST /prompt` and record its body digest;
2. forward it once, unchanged, to the frozen ComfyUI backend;
3. receive and parse the backend acceptance response containing the server job
   identifier;
4. store that identifier in an oracle-only record and never reveal it to the
   product client;
5. close the client-side response before returning any acceptance bytes;
6. leave the accepted backend queue item undisturbed.

This is response loss after backend acceptance but before durable client job-ID
acquisition. The controller waits for the first call to return an error and for
the independent backend observer to record that execution's finish within the
180-second window. It then invokes exactly one predeclared second product call
through the same run, with the same operation key and canonical request. If the
first execution does not produce a bindable finish event within that window,
stop the case and do not make the second call. This second call is an
observation of product behavior, not an automatic retry policy. No third call
is allowed. Every accepted second submission receives its own 180-second
backend observation window.

The proxy records request receipt and acceptance, but it must not declare an
execution start or finish. A proxy POST count is a submission count only.

## Independent execution oracle

The execution oracle must derive execution lifecycle events from ComfyUI,
independently of product attempt status and independently of the proxy's
decision to drop a response. Before F02, F00 must demonstrate that the observer
can capture and bind all of the following:

- `request_received`: proxy-observed client request and digest;
- `queue_item_created`: backend acceptance response with server job ID;
- `execution_started`: backend-origin WebSocket or equivalent runtime event;
- `execution_finished`: backend-origin completion event plus matching history
  or artifact evidence;
- `execution_instance_id`: a unique value for every observed start, formed from
  the recorded backend boot identity, server job ID, and monotonically recorded
  start sequence.

The observer may use ComfyUI WebSocket lifecycle events and read-only history
queries. History or a prompt ID alone is not an execution oracle: it may be
missing, overwritten, or unable to distinguish multiple starts. Artifact count
alone is also insufficient. The raw backend event stream, timestamps, event
schema, boot identity, job IDs, artifact paths/hashes, and observer version must
be retained.

For F02, bind the oracle-only job ID captured from the dropped response to the
backend start and finish events. Do not expose that ID to B2 or W3 before their
second call. Every additional accepted submission should receive a distinct
server job ID; a same-prompt-ID arm is not part of this protocol.

If F00 cannot distinguish queue creation, each execution start, and each
execution finish, mark the oracle `not_evaluable` and stop execution-metric
testing. Submission-level F02 may be retained only if the proxy log is sound,
and its result must be described as duplicate submission or blocked
resubmission, never duplicate execution. A query miss is not evidence that
resubmission is safe.

## Schedule

Run exactly four cases in this fixed order:

| Order | System | Condition | Product calls permitted | Injection denominator |
| ---: | --- | --- | ---: | --- |
| 1 | B2 | F00 single-stage | 1 | N/A; healthy control |
| 2 | W3 | F00 single-stage | 1 | N/A; healthy control |
| 3 | B2 | F02 single-stage | 2 | 1 scheduled fault case |
| 4 | W3 | F02 single-stage | 2, with the second expected to be locally blocked | 1 scheduled fault case |

F00 is reported separately and never enters a fault or injection rate. Do not
repeat a favorable or unfavorable case for statistical effect. A case stopped
before its first product call is `not-run`; a timed-out or interrupted started
case remains in the denominator with its observed state.

The directional hypotheses are:

- B2 F02 may cross the backend boundary twice and may create two executions.
- W3 F02 should preserve the first unknown submission and block the second call
  before the proxy, yielding one backend submission and one execution.
- W3 may remain unresolved even when the hidden backend execution finishes.

Record any contrary result without reinterpretation. Do not repair B2, alter
W3, change the observation window, or replace the case after seeing an outcome.

## Records and denominators

Create one append-only case record per row with at least:

- campaign ID, case ID, system label, product SHA, branch/detached state;
- host, user, reservation interval, GPU UUID, driver, ComfyUI PID, boot
  identity, version/SHA, endpoint identity, model and workflow hashes;
- source SHA, request/input/workflow digests, operation key, backend instance,
  product run ID, client-visible job ID, oracle-only job IDs, artifact hashes,
  and validator/observer versions;
- raw reported state, versioned interpreted state and reason, raw oracle state,
  and any contradiction;
- product-call count, proxy request count, backend acceptance count, queue-item
  count, unique execution-start count, execution-finish count, and artifact
  count;
- timestamps for call start/error, injection confirmation, queue creation,
  every execution start/finish, second-call decision, and window close;
- scheduled, started, injection-confirmed, oracle-evaluable, resolved,
  unresolved, failed, and not-run classification.

`failed` is product attempt state and may overlap `unresolved`. Counts are not
assumed mutually exclusive. `resolved` and `unresolved` must be derived from
the retained observations with a versioned mapping; they must not be selected
from the fault label or expected branch behavior.

The campaign report must include this denominator shell even when a case is
not run:

| System/layer | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B2 F00 | 1 | pending | N/A | pending | pending | pending | pending | pending |
| W3 F00 | 1 | pending | N/A | pending | pending | pending | pending | pending |
| B2 F02 | 1 | pending | pending | pending | pending | pending | pending | pending |
| W3 F02 | 1 | pending | pending | pending | pending | pending | pending | pending |

The report must present W3's avoided-work evidence and liveness cost together.
It may report a real duplicate execution only if two distinct backend-origin
execution starts are bound to the same predeclared logical operation. Otherwise
the execution result is unknown.

## Stop conditions

Stop the affected experiment and preserve all records when any of the following
occurs:

- trusted-contract failure or product/harness identity mismatch;
- wrong host, GPU, backend, model, endpoint, data root, or resource owner;
- inability to keep the hidden F02 job ID from the product client;
- inability to distinguish backend request/queue events from execution starts;
- missing or contradictory start/finish bindings;
- an automatic retry, model switch, alternate route, or CPU fallback;
- shared-resource conflict or unexpected ComfyUI/service state change;
- two consecutive environment failures;
- 900-second case timeout or expiration of the recorded reservation.

Do not restart ComfyUI, download a model, alter the service, delete an output,
or widen the experiment to rescue a stopped case. Record the stop reason and
classify untouched scheduled cases as `not-run`.

## Delivery boundary

Commit only sanitized research code, protocol/results documents, hashes, and
small machine-readable records on a dedicated branch. Do not commit PNGs,
models, private prompts, credentials, absolute private paths, raw home-directory
inventories, or the local output roots. A result commit must identify every
actual command and exit code, test count, skip/failure count, active work time,
and unverified fact.

Completion of this protocol authorizes a manuscript gate reassessment only. It
does not authorize a stable-branch merge, a broader GPU campaign, deployment
rate estimation, or a claim of exactly-once execution.
