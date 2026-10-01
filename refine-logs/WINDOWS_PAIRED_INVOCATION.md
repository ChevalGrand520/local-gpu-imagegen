# Windows paired invocation

Controller owns the reserved GPU and every backend it starts. Source sync uses
Git in a fresh detached worktree. Product B2/W3, model and ComfyUI identities
come from the retained private config and must pass the native checks again.
No environment rebuild, package installation or model download is required.
The retained preflight ledger is the provider record; its historical success
does not certify this invocation. F00 is the real workload control witness.

The explicit reservation-preparation entry accepts the human authorization,
owner and current window as required arguments. It never launches a backend;
the expired historical template supplies paths/identities only. It creates an
advisory lock and retains a reviewed WDDM process baseline in private config.
Unknown executable names stop preparation. Only the controller releases its
own lock after checking cleanup. Do not create or replace another reservation.

Offline invocation on the existing Windows interpreter, no GPU or network:

```text
python -B D:\CodexWorkspace\scratch\paired-research-20261001\scripts\research\run_reserved_windows_paired.py D:\CodexWorkspace\scratch\paired-research-20261001\docs\research\paired-windows-config.example.json
```

Expected: exit 0, PLAN_ONLY, execution_performed=false, launch_enabled=false,
training_state=busy. This command does not declare the environment ready or
reserve it. Fresh reviewer is restricted to this invocation, source identity
and documented-CLI checks; no execute switch, GPU query, backend or file writes.

Execution uses the same entry with a fresh private configuration, --execute
and --private-root naming a nonexistent private campaign parent. Six operations
maximum; preserve all STOPPED reports. No implicit replacement batch.
