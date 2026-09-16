# W3 Real Windows/ComfyUI Pilot Preflight

Date: 2026-09-16

This record documents the approved real-pilot preflight only. No generation,
model download, ComfyUI startup, server mutation, or `/prompt` request was
performed. The pilot remains pending because the target Windows host was not
reachable from this checkout.

## Scope And Anchors

| Item | Value | Evidence level |
| --- | --- | --- |
| Branch | `research/w3-ambiguous-submit` | Git checkout |
| Checkout before this record | `add98fe53658e7797920b1401c6f78e4bfc2c681` | Git |
| Fixed B2 | `da65d57047b5a59e3403b49adf4605a1c0497c58` | Frozen research anchor |
| Research ledger | `d8ef0bccc84269b7d4a627adce5f6025a17ab024` | Trusted anchor |
| Pilot mode | Read-only preflight | Actual local activity |
| Intended backend | Existing Windows ComfyUI only | Not verified |

## Candidate Connection Inventory

The local SSH configuration contains these explicit candidates:

| Candidate | Configured user | Resolved host | Result |
| --- | --- | --- | --- |
| `10.98.19.31` | `chengzhen` | `10.98.19.31:22` | Connection closed by remote host |
| `hand-data-server` | `chengzhen` | `10.98.19.31:22` | No reusable control socket; remote connection closed |
| `192.168.10.149` | `jaka` | `192.168.10.149:22` | Connection closed by remote host |

Both IPs had local known-host entries. The configuration and host keys do not
identify either candidate as the target Windows ComfyUI owner, so neither is
silently classified as GPU-A or GPU-B.

## Read-Only Commands And Results

The following loop was run for both explicit IP candidates:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=5 "$target" 'hostname'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=5 "$target" 'uname -a 2>/dev/null || ver 2>&1'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=5 "$target" 'nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader 2>/dev/null'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=5 "$target" 'ps -eo pid=,comm=,args= 2>/dev/null | grep -Ei "[c]omfy|[m]ain.py" | head -20'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=5 "$target" 'curl --max-time 3 --silent --show-error --fail http://127.0.0.1:8188/system_stats 2>/dev/null'
```

Each remote invocation reported `Connection closed by <target> port 22` and
returned no system, GPU, process, or API payload. The enclosing diagnostic
loop exited `0` because it intentionally continued after per-target failures;
the remote SSH failures are therefore not counted as pilot runs.

The local-only control-socket check was:

```sh
ssh -O check hand-data-server
```

It exited `255` with `No such file or directory` for the configured control
socket. No existing session could be reused.

## Gate Result

The two candidate hosts produced two environment failures. Under the frozen
stop condition, the affected real pilot is stopped rather than retried or
expanded. No target ComfyUI version, ComfyUI Git SHA, Windows runtime, GPU
UUID, backend boot ID, model identity, workflow identity, owner reservation,
hard timeout, output root, or disk reservation was verified.

| Quantity | Value | Interpretation |
| --- | ---: | --- |
| scheduled | 0 | No real generation case was scheduled |
| started | 0 | No backend or product generation entrance was invoked |
| injection-confirmed | 0 | No fault was injected |
| oracle-evaluable | 0 | No execution oracle run occurred |
| resolved | 0 | No pilot recovery case existed |
| unresolved | 0 | No pilot recovery case existed |
| failed | 0 | Connection failures are environment failures, not product failures |
| not-run | 0 | No case entered the schedule; pilot is separately `pending` |

## Evidence Boundary And Next Gate

This is actual local connection-preflight evidence only. It is not Windows
verification, ComfyUI component verification, GPU verification, inference
evidence, execution-count evidence, deployment-failure evidence, or a
duplicate-execution result. The existing CPU/fake and adapter records remain
unchanged and cannot be combined with this pending preflight to claim a live
end-to-end run.

The single next step is to make one explicitly identified Windows host/session
and its GPU owner available for a read-only inventory. Until that is available,
the real pilot stays pending and no generation command is authorized by this
record.
