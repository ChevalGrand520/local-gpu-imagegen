# Same-run F02 capture implementation

## Material Passport

- Date: 2026-09-30.
- Stage: research harness implementation and CPU software preflight.
- Branch: `codex/f02-same-run-capture`, based on `8a7cd6f`.
- Scope: W3 F00 control plus W3 F02 same-run submission guard. No B2 product
  calls, live Windows measurement, model download or GPU work in this preparation.
- Historical four-case pilot records and the manuscript's empirical claims
  remain unchanged. This is not an independent peer review.

## Entry point and frozen product

From the **new research checkout**, run only when a reviewed private
configuration and an explicit active Windows reservation are available:

```text
python -m scripts.research.f02_same_run_campaign PRIVATE_CONFIG.json
```

This new command has protocol `same-run-guard-v1`. The original
`f02_campaign` command retains its fresh-run behavior. The new controller
rejects an unspecified protocol; the old controller rejects a same-run
configuration before preflight rather than silently executing fresh runs. It
reuses the frozen-client and environment preflight; it still verifies both
detached B2 and W3 checkouts and the four distinct fresh output-root entries,
but invokes only `W3_F00` and `W3_F02`. The product W3 checkout stays at
`d45173af75d404ad79dc14568edd4c45f654abd2`; the new research wrapper is outside
that checkout. Its exact source-file hashes are retained with every run.

Copy the existing reviewed private configuration, select fresh output and
evidence paths, and add these campaign fields:

```json
{
  "protocol_version": "same-run-guard-v1",
  "same_run_capture_root": "ABSOLUTE_PRIVATE_CAPTURE_DIRECTORY"
}
```

`same_run_capture_root` and `campaign.evidence_file` must be new paths with
existing parents. Captures must be separate from product outputs.
`campaign.client_commands.W3` must invoke the **new checkout's**
`scripts/research/f02_product_client.py` using the intended Python interpreter.
`preflight.clients.W3.root` remains the frozen product checkout. The controller
sets `LOCAL_GPU_IMAGEGEN_CLIENT_ROOT` to that verified root, rather than inheriting
an unrelated ambient client-root variable. Do not copy research files into or
modify either frozen product checkout. Other configuration fields, pinned
model/endpoint identities and reservation requirements remain mandatory.

## Same-run state and stopping rules

Call 1 saves a private session before generation: run ID, complete generation
arguments, request digest, product root, endpoint, proxy, output root and operation
key. The seed is 4101. Call 2 reads this session and uses the exact same generation
arguments, including seed, idempotency key and change summary. It performs no
second `start_run` or route selection. Session drift is checked against the
first call's result. A third call and a repeated invocation of either call index
are refused before launching a product process.

The controller first requires a completed/bindable F00 control with a captured
manifest. In F02 it requires one accepted POST with its response suppressed,
a bindable first execution, frozen-request agreement and an original captured
manifest whose latest attempt is unresolved, has `submission_outcome=unknown`,
has no backend job object and matches the operation key. Only then can it issue
the second product call. The client rechecks that manifest before generation.

The public field `submission_guard_observed=true` requires all of:

- Exact agreement of both run-ID hashes and complete generation-argument hashes.
- Valid before/after manifest capture hashes and an unchanged saved session.
- Product error `submission_outcome_unknown` at stage `generate_round`.
- No timeout, successful client transport exit, and zero additional proxy POSTs.
- The original run remains unresolved with the matching unknown/no-job attempt.

A zero-POST result with another error, a changed run, an unbindable first
execution or a missing capture stops the case without claiming a guard effect.
The remaining reservation time bounds the product and observer deadlines; an
expired reservation prevents new calls. No failure authorizes a third call,
fresh-run fallback, backend restart or reconciliation.

## Private capture and public summary

The private directory includes the reviewed configuration and preflight, harness
source hashes, immutable session, each call's before/after manifests and results,
proxy receipts, oracle-decision snapshots and final raw transport capture.
Raw WebSocket **text-message payload bytes** and history-response bytes are
retained as base64 with SHA-256, sequence and receive time. This is not a complete
network/frame capture. Transport errors are recorded when bytes are unavailable.
The opt-in raw capture preserves `node=null`, cached-node payloads and long
strings that the old sanitized event view omits.

Files are created exclusively; existing evidence is never overwritten.
POSIX files use owner-only permissions; Windows private-directory ACLs remain
the author's responsibility. Raw captures may contain paths, prompts and route
identities and must not be included in reviewer packages. The public summary
contains stable error codes, state labels, bindings, counts and hashes. It
contains no private run/prompt IDs, host paths or raw payloads.

The first bound lifecycle execution does not prove physical GPU work, exhaustive
event completeness, original-run reconciliation or eventual completion. This
protocol tests submission rejection in the same run and estimates no natural
duplicate or deployment failure rate. A live observer-to-exporter conversion
remains a separate evidence gate.

## CPU preflight

```text
python -B -m unittest tests.research.test_f02_same_run -q
python -B -m unittest discover -s tests/research -q
```

The focused tests include a real product-engine control path with a localhost
CPU backend whose accepted response is lost. Discovery/MCP boundaries are test
facades; this does not exercise a real Windows stdio process or ComfyUI backend.
See `runs/f02-same-run-cpu-preflight-20260930.md` for the verified preparation.
