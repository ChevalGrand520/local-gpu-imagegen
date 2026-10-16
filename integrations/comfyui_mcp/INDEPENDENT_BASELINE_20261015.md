# Independent baseline follow-up

The earlier stop/full campaign shares journal code and therefore isolates only
implicit versus explicit history routing. Add minimal_baseline.py as an
independent durable journal and binding implementation, sharing only stdio MCP
transport and prompt_id extraction. This is an experimental comparator, not a
product replacement. Its raw local database may contain secrets; do not upload it.

Validation executed: `python3 -m unittest tests.test_comfyui_mcp_minimal tests.test_comfyui_mcp_bridge tests.test_spe_recovery -q`.
23 tests passed in 6.849 s. Six new baseline tests use a synthetic stdio MCP
process: retained-ID fresh-process re-entry + explicit history, three actual
client exit windows, unknown reply, changed key/seed rejection, history failure
and retry, and three concurrent fresh clients. The command's passing tests do
not imply real backend generation or independent review.

The minimum baseline currently achieves the same checked protections and known-ID
retrieval contract. No superiority of the larger adaptation is established.
The native model is still a defined explicit retry caller, not measured upstream
or LLM retry behavior.

The 32-case real-upstream-tool-handler campaign is prepared, NOT RUN. The prior
/tmp upstream checkout has disappeared; attempts to restore GitHub source and
read pinned Panel files encountered network/SSL timeouts. No substitute fixture
is presented as upstream code. Pinned Panel recovery inspection remains pending.
The existing frozen 24-case result is unchanged and can still be audited.

Next bounded step: restore exactly 6996d06, npm ci with scripts disabled and
build, run fault_campaign.py for all four groups, audit the new receipt. Do not
extend models/fault types/GPU until a concrete distinct capability is found.

## Follow-up status — 2026-10-16

The source-restoration block was resolved. The four-group campaign and pinned
Panel component checks have run; see RECHECK_20261016.md. The original pending
status above describes the 2026-10-15 checkpoint, not the current state.
