# Durable client for artokun/comfyui-mcp (experimental)

This is an additive stdio MCP client for one caller-supplied API graph. It uses
an unchanged upstream MCP server, preserving the existing tool and seed semantics.
It is not yet wired into the product CLI/RunStore and is not a new MCP server.

Pinned upstream: https://github.com/artokun/comfyui-mcp/tree/6996d06ff511dd7b3b05adf89716e7667df2c1b9

See ASSUMPTIONS.md before interpreting results. Existing real Windows results:
../../paper-spe/NARRATIVE_REPORT_20261006_R1.md (manual history also recovered).

Modes: `native` (no journal), `stop` (durable stop), `full` (durable known-ID
history on same-key re-entry). Explicit `read_history` is available to both
journal modes. None of the modes infer completion from a readable history reply.
The upstream original tools remain usable outside this client; there is no
system-wide deduplication or protection of bypass calls.

Example (launches the configured MCP server; submit can start real GPU work):

```sh
python integrations/comfyui_mcp/bridge.py --help
```

Use only an explicitly approved backend for real submission. A fresh run_id is
intentional new work; changing an existing run's key/graph/endpoint is rejected.
Raw workflow JSON and results may contain private data: keep all local journals
and experiment receipts private until separately reviewed.

## Run the checks

Python 3.11+; the bridge itself requires no external Python dependencies:

```sh
python3 -m unittest tests.test_comfyui_mcp_bridge -v
```

For an upstream tool-handler smoke check (CPU fake HTTP, NOT a GPU campaign),
prepare a local checkout of the exact upstream revision and run its `npm ci
--ignore-scripts --no-audit --no-fund` and `npm run build`, then:

```sh
python3 integrations/comfyui_mcp/upstream_smoke.py /absolute/upstream-checkout \
  --receipt /private/local/cpu-receipt.json
```

The smoke uses the real unmodified workflow and history tool registrations in
an SDK stdio harness. It does not run full upstream boot, which has panel
installation, update and orphan-download services. Its mock workflow/outputs
are synthetic and do not prove a valid executable ComfyUI graph.

For normal approved use, substitute the upstream server's built entry point:

```sh
COMFYUI_URL=http://127.0.0.1:8188 python3 integrations/comfyui_mcp/bridge.py \
  --database /private/local/runs.sqlite --endpoint http://127.0.0.1:8188 \
  --action inspect --run-id example-run \
  -- node /absolute/upstream-checkout/dist/index.js
```

`inspect` does not start the server or send a backend request. To submit, use
`--action submit --key <stable-key> --workflow /private/local/graph.json` with
the same remaining arguments. `--action read_history` reads the exact retained
ID. A same-key `submit` in full mode reads history after an ID is retained;
stop mode returns the journal and needs explicit `read_history`.

Upstream code/config must remain fixed. The endpoint identity argument is an
operator declaration, not independently verified routing evidence. No prompt
is resent after an unresolved intent. Disk failure, malformed reply, pre-send
failure or an upstream process crash can therefore leave a false block.

## Interpretation of the checked-in CPU receipt

`native` counts 2 POSTs because the test caller explicitly requests two
submissions. This is NOT evidence that upstream automatically retries errors.
Both `stop` + manual read and `full` have 1 POST and 1 exact-ID history read.
The fixture history includes a fabricated output reference; no PNG was rendered
or downloaded, and no completion/quality judgment is inferred from the reply.
The malformed-response case exercises upstream's real ENQUEUE_UNVERIFIED path
against a synthetic HTTP 200, not measured backend acceptance.

The frozen SoftwareX manuscript and earlier real Windows records are unchanged.

## Automated fault campaign

The next milestone is recorded in [FAULT_RESULTS_20261015.md](FAULT_RESULTS_20261015.md).
24 fixed CPU traces cover real client exits at three boundaries, HTTP response
loss, history read failure, request changes and normal re-entry. Reproduce with
`fault_campaign.py`; recompute receipts with `audit_fault_campaign.py`. These
experiments need no human participants. Stop+explicit recovery and full remain
equal in all compared outcome fields; no GPU campaign or user study was run.

The follow-up `minimal_baseline.py` independently implements durable stop and
explicit history; it does not reuse DurableClient's journal/binding code.
See INDEPENDENT_BASELINE_20261015.md for the initial baseline checks. The four-group
upstream campaign has now run: see RECHECK_20261016.md for 32 passing fixed traces,
baseline equality, and the pinned Panel capability inspection. Its database stores raw requests/config: keep it private.
