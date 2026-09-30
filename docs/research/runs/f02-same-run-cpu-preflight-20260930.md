# Same-run capture: CPU software preflight

## Material Passport

- Date: 2026-09-30 (Asia/Shanghai).
- Verification status: VERIFIED for the bounded CPU software checks below.
- Branch: `codex/f02-same-run-capture`; base `8a7cd6f`.
- Runtime: macOS, Python 3.13.15.
- Scientific boundary: regression/integration tests with synthetic backend and
  observer fixtures, not new Windows measurements or independent samples.
- No GPU job, real ComfyUI campaign, model download, manuscript result change,
  backend restart or external reviewer contact.

## Executed checks

| Command | Result |
| --- | --- |
| `python3 -B -m unittest tests.research.test_f02_same_run -q` | 15 tests passed |
| `python3 -B -m unittest discover -s tests/research -q` | 61 tests passed |
| `python3 -B -m scripts.research.f02_same_run_campaign --help` | Exit 0; entrypoint imports and CLI parse successfully |
| `git diff --check` | No whitespace errors |

## Product-control-path check

`SameRunEngineIntegrationTests` uses the actual `AssetRunEngine` and `RunStore`
with the existing `PairedCpuBackend` localhost response-loss fixture. A test
facade substitutes discovery/MCP transport. It executes the new client's first
and second same-run invocations, rather than setting a guard-result label.
Assertions pass for:

| Quantity or state | Asserted result |
| --- | --- |
| Started product runs | 1 |
| Complete generation arguments across calls | Equal, including run ID, key and seed |
| Localhost backend submissions | 1 |
| Synthetic worker execution starts | 1 |
| Original manifest after response loss | Unknown submission / unresolved |
| Second product error | `submission_outcome_unknown` at `generate_round` |
| Original manifest after blocked retry | Unresolved |
| Repeat invocation or third call | Refused before opening a product process |

The test also changes session arguments while recomputing their digest. The
client detects disagreement with the first result and refuses the changed
session before another product process opens. An output-context change is
likewise refused. These are software checks, not a claim that arbitrary edits
to all private evidence can be authenticated.

## Controller and capture checks

The synthetic controller checks require the retained manifest, same run and
argument hashes, the specific guard error, and zero additional proxy POSTs.
They also require the old fresh-run controller to reject a same-run
configuration before preflight, preventing an accidental protocol substitution.
They reject a changed run, a different error with zero POSTs, an extra POST,
missing manifest capture, a non-unknown original state, an unbindable first
execution and a failed control. A failed or newly expired preflight creates no
capture directory and invokes no product client. The public report is checked
for absence of private run IDs, boot identity and host paths.

The raw-capture checks reproduce exact text-payload and history-response bytes
from base64 and verify their SHA-256. They preserve terminal `node=null` and
content longer than the existing sanitized event view's limit. Raw retention
remains disabled by default. These tests use constructed messages and mocked
history HTTP responses, not independent ComfyUI observations.

## Remaining gates

The code is prepared for an explicitly reserved Windows run against the pinned
product/environment identities. Live stdio routing, real ComfyUI event ordering,
backend caching behavior, the actual manifest after response loss, and the
submission guard's Windows effect remain unmeasured by this preparation.

No original-run reconciliation, eventual completion, deployment rate or natural
duplicate-execution rate is established. The Windows observer-to-exporter
conversion remains pending. Run instructions and capture roles are in
`../f02-same-run-capture-implementation-20260930.md`.
