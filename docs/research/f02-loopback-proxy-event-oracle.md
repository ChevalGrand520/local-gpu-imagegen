# F02 loopback proxy and backend-event oracle

## Scope and authority

This research-only package implements the fault boundary and the independent
backend observer required by the reviewed Windows/ComfyUI F02 single-stage
pilot.  It does **not** modify the MCP product, ComfyUI, model files, or normal
backend routing.  The accompanying protocol and gate-review documents define
frozen hypotheses and evidence limits; they are not themselves authorization to
start services, submit prompts, repeat cases, or enlarge the campaign.

## Components

- `scripts.research.f02_loopback.OneShotLoopbackFaultProxy` binds only to a
  numeric loopback address and accepts only the reviewed ComfyUI HTTP path
  allowlist.  In F00 it forwards request bodies and responses unchanged.  In
  F02 it forwards the first `POST /prompt` once, records the request digest and
  accepted `prompt_id` in proxy-only evidence, and closes the client response
  before returning any backend acceptance bytes.  It never fabricates success.
- `scripts.research.f02_oracle.ComfyUIEventOracle` uses a read-only ComfyUI
  WebSocket plus read-only `/history/<prompt_id>` queries.  An execution is
  evaluable only when it has a backend `execution_start`, a backend terminal
  `executing` event with `node: null`, and corroborating successful history.
  Prompt IDs, POST counts, history alone, and artifact counts alone are never
  promoted to execution counts.
- `scripts.research.f02_preflight` is a no-write, no-generation gate.  It checks
  an explicit reservation before hardware or backend observation, then checks
  the ledger contract, detached B2/W3 identities, host/GPU/model/backend
  identities, and future fresh output roots.  A non-active reservation stops
  preflight before `nvidia-smi` or `GET /system_stats`.

## Evidence downgrade rule

If F00 cannot bind every accepted backend job to a backend start and terminal
finish, the oracle is `not_evaluable`.  A later F02 observation may retain only
sound proxy receipts as **submission-level evidence** (duplicate submission or
blocked resubmission).  It must leave execution count `unknown`; it cannot be
reported as duplicate execution.

## Campaign controller

`scripts.research.f02_campaign` is the only orchestration entry point.  It takes
a **private, reviewed JSON configuration** and runs the immutable order `B2
F00`, `W3 F00`, `B2 F02`, `W3 F02` after `run_preflight` returns `PASS`.

The controller requires all of the following before it opens the proxy or
observer:

- exact B2/W3 frozen SHA configuration and four distinct, nonexistent output
  roots that are also supplied to preflight;
- a frozen-request object containing canonical, compiled-prompt, workflow, and
  input SHA-256 digests, route identity, and validator version;
- one product-client argv list per checkout; the controller gives each call the
  proxy URL, unmanaged-backend setting, output root, case ID, call index, and
  operation key only through process environment; and
- the reviewed `180`-second observer window and `900`-second external case
  timeout exactly.

The product command must emit a final small JSON result with the frozen request
fields and operation key.  Command stdout/stderr and prompt content are not
retained: case evidence contains only their SHA-256 digests.  Backend prompt IDs
never flow into a product invocation and are represented in sanitized evidence
only as hashed oracle references.  The evidence JSONL parent must already
exist; a preflight failure creates no file or output directory.

The controller records SHA-256 digests of the private product argv and working
directory alongside each case.  The reviewed private configuration remains the
authority for the actual invocation; no command line, absolute checkout path,
prompt, PNG, model weight, or output-root path is committed as public evidence.

F00 must be evaluable for both B2 and W3 and match the frozen request before
any F02 product call.  Otherwise the controller records the two F02 rows as
`not_run` and returns `DOWNGRADED_SUBMISSION_ONLY`.  Within an F02 case, a
missing bindable first finish produces `submission_only` evidence and prevents
the second product call.  If an F02 oracle observation itself becomes
`not_evaluable`, the controller stops the remaining F02 schedule and records
untouched rows as `not_run`.  A second call that is blocked before the proxy is
also submission-only evidence; it is never reported as an execution count.

## Current run status — 2026-09-20

No actual Windows/ComfyUI case was started by this change.  The last supplied
reservation interval was on **2026-09-17**, which is in the past on the current
local date, **2026-09-20**.  The reservation-first gate therefore blocks before
any GPU, ComfyUI, `/prompt`, model, or output-root operation.  The ten passing
focused tests are **component/synthetic evidence**, not Windows/backend evidence
and not a result for any of the four scheduled cases.

## Next admissible action

Provide a new explicit owner reservation whose current time is within its start
and end, plus a reviewed **private** pilot configuration that binds detached
B2/W3 roots, the frozen ComfyUI/model identities, a ComfyUI PID/root, four
nonexistent fresh output roots, and reviewed client invocations.  Re-run the
read-only preflight.  Only `PASS` permits the fixed order; no retry or fifth
case is allowed.
