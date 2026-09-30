# Windows same-run campaign: retained negative result

- Date: 2026-10-01, Asia/Shanghai.
- Source: `6c2219e`, branch `codex/f02-same-run-capture`.
- Frozen B2/W3 identities unchanged. Only W3 was invoked.
- User explicitly authorized unattended execution, current desktop-memory baseline
  and resource acquisition. New 30-minute reservation: 2026-09-30 16:59:48 UTC.
- Run ended at 17:01:55 UTC, within the reservation; campaign process exit 2.
- Preflight PASS. CPU preparation: 61 Windows tests passed.
- Scope: two fixed protocol cases; no rate, significance, comparative efficacy,
  output-quality or physical GPU execution claim.

| Case | Calls | POSTs | Raw starts / null-node terminals | Bindings | Client states | Decision |
|---|---:|---:|---:|---:|---|---|
| W3 F00 | 1 | 1 | 1 / 1 | 1 | resolved | Control completed |
| W3 F02 | 2 | 1 | 1 / 1 | 1 | unresolved / unresolved | STOPPED: model_identity_drifted |

## What happened

F02 suppressed the first accepted response. The original durable manifest
remained unresolved with unknown submission and no backend job. The observer
bound one start, a terminal `executing` event with `node=null`, and successful
history. The second invocation reused the original run and complete argument
digest, including seed and operation key. It produced no second POST, but
returned `model_identity_drifted` at `generate_round`, rather than the required
`submission_outcome_unknown`. Before and after manifests were byte-identical.
The controller correctly stopped and set `submission_guard_observed=false`.

This is **not** evidence that the intended guard blocked a duplicate. A
different pre-submission rejection masks that mechanism. The exact cause of
model-identity disagreement remains unverified; do not claim actual model bytes
changed, or assume the caller simply needs to repeat discovery.

The F02 transport includes one `execution_cached` event and zero `progress`
events. Backend logs report a zero-second prompt. These observations delimit a
backend lifecycle binding, not proof of a second physical GPU computation.
F00 includes 30 progress messages. No hardware profiler was used.

## Capture and audit

The public report is `paper/evidence/windows-same-run-20261001.json`; SHA-256
`29315ed3915a3199a5eb6a8ebe1981baa88937d0a74348ae127cb2d9fdd7d112`.
Private capture remains outside Git/reviewer packages in owner-restricted
Windows storage and an ignored, owner-restricted local delivery directory.
It includes 90 F00 and 10 F02 exact WebSocket text payloads and one exact
history response per case, plus session, manifests and receipt captures.

`paper/scripts/audit_same_run_capture.py` passed offline: public-to-private
capture hashes, payload base64/SHA-256, per-channel sequence, prompt-bound
start/terminal/history, reconstructed execution binding, same run/argument
identity, one POST per case and persistent F02 ambiguity agree. The public
audit receipt is `paper/evidence/windows-same-run-audit-20261001.json`.
PASS denotes retained-byte consistency, not event completeness, origin
authentication or experimental success. This capture does not recover the
missing raw payloads of the historical September 27 campaign.

The operational runner used the legacy four-case namespace validation while
recording its actual two-case schedule; the unused B2 namespaces were fresh
declarations, not scheduled cases. This inherited schema should be specialized
before a future experiment. No failures were relabelled as successful cases.

## Cleanup and next decision

The run-owned ComfyUI process was terminated; subsequent inventory found no
Python process or port 8202 listener. No third call, new-run fallback, model
download, product change or second campaign was performed. Existing outputs
and the negative result are preserved.

Next major decision: diagnose the frozen product's model-identity gate across
fresh MCP processes, then decide whether a research-client initialization fix
can reach the intended guard without changing the frozen product or arguments.
An amended protocol must retain this failed campaign and receive a fresh
reservation. The manuscript may report this negative scope test now; guard
efficacy and observer-to-exporter conversion remain open.
