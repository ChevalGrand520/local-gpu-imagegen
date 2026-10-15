# ComfyUI MCP integration milestone — 2026-10-15

Branch: experiment/comfyui-mcp-durable-bridge, based on 054e7b6 (SPE validation).

Implemented: experimental Python stdio MCP client, SQLite intent/binding journal,
three caller policies (native/stop/full), exact-ID read_history and local inspect.
No upstream code vendored or patched. Frozen SoftwareX manuscript untouched.

Validation:
- Python CLI help / py_compile passed.
- 9 boundary tests passed: cross-process retained-ID replay, explicit stop history,
  native deliberate re-entry, crash/error/missing-ID uncertainty, request/target
  conflict, history-read retry, competing clients, pre-send false block, bad JSON
  numbers / canonical order.
- Existing tests.test_spe_recovery: 8 passed.
- Pinned upstream npm ci --ignore-scripts completed (233 packages, about 7 minutes);
  npm run build passed. Temporary checkout /tmp/artokun-comfyui-mcp-review-20261015.
- Real upstream MCP tool handlers + SDK stdio harness + fake HTTP passed. See
  cpu-upstream-receipt.json. Successful enqueue starts a watcher upstream; the
  client closes its owned child after the tool reply, then starts a fresh child
  for exact-ID history. No full upstream boot side effects are required.
- Initial smoke counter ignored the upstream-added clientId query string and
  reported zero exact reads. Strengthened checks require a fake output filename
  in history replies and normalize only /api prefix and query for path counting;
  the final run passes and retains raw HTTP paths. No earlier run is claimed as
  valid exact-history evidence.

Outcome: native deliberate second call = 2 POSTs; stop+explicit history = 1 POST,
1 exact history read; full same-key re-entry = 1 POST, 1 exact history read.
No demonstrated outcome advantage over the fair simple baseline. Uncertain
upstream reply blocks re-entry. No missing-ID recovery claim.

Limits / next gate:
- This is a client-side experimental adaptation, not integration into the Python
  product RunStore or automatic interception of all upstream tools.
- Full server boot, installed desktop/LLM registration, real ComfyUI execution,
  artifact downloads, crash-after-ID BEFORE disk binding, Windows SQLite and
  power-loss behavior have not been validated here.
- Existing October 6 real history-recovery equality remains negative evidence.
- Before more development: choose a concrete operator task and compare measured
  errors/interventions against stop+explicit history. Do not add a GPU campaign
  or claim SQJ readiness merely because protocol checks passed.
- No independent agent review or research-integrity verdict was obtained.
