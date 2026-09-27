## Material Passport

- Origin Skill: ARIS run-experiment
- Mode: run
- Input Commit: `9b9e034239a381e5f31f7829f8712737fa1b2d83`
- Verification Status: PARTIALLY_VERIFIED
- Gate Decision: `STOP / NO CASE EVIDENCE`

# W3 Windows F00/F02 Overnight Attempt

## Outcome

The four-case campaign did not enter its case loop. The campaign launcher invoked `f02_campaign.py` by absolute file path while the SSH PowerShell working directory was the user profile directory. The script imports `scripts.research...`, so Python exited during module import with `ModuleNotFoundError: No module named 'scripts'`. A read-only `--help` diagnostic reproduced that exact import failure before `main()`.

No per-case JSONL or campaign report was emitted. All four fresh output roots remained absent, the ComfyUI queue was empty, and no case-level result is claimed. The reservation was released early and the run-owned ComfyUI process and one-shot task were stopped/removed.

## Verified Preparation

- Trusted research contract: PASS at `d8ef0bccc84269b7d4a627adce5f6025a17ab024`.
- B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`, clean detached checkout.
- W3: `d45173af75d404ad79dc14568edd4c45f654abd2`, clean detached checkout.
- Windows/GPU/backend identity preflight: 10/10 checks passed; RTX 5070 Ti, ComfyUI `v0.30.0`, backend SHA `b1693ecba9f5b65f8c80ab36b195ab963ec92413`.
- Model SHA matched the pinned SDXL checkpoint; B2 and W3 read-only route probes passed and produced identical frozen request digests.
- Component suite: 40 tests passed on Windows Python 3.15.0a8; compileall and `git diff --check` passed. This is not CI verification on Python 3.11/3.12.

The route probe initially exposed a research-client ceiling of 10 GB against the approved model's declared 12 GB minimum. The research-only caller now uses a 12 GB ceiling, matching the host's measured total VRAM; the model and workflow were not changed. This correction is committed as `9b9e034`.

## Case Denominators

| planned | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |

These are campaign-controller outcomes, not a failure-rate sample. `controller_invocation_failed=1` is reported separately from case-level `failed=0`. No POST, backend acceptance, execution, or artifact is claimed for this attempt.

## Evidence Boundary

- Real Windows evidence: identity/health preflight, route probes, and a run-owned ComfyUI process that was cleanly stopped.
- Component evidence: the 40 research tests and the read-only oracle WebSocket-connect diagnostic.
- Real generation/execution evidence: none.
- Deployment failure rate, duplicate execution rate, and image-quality claims: not measured.

## Reservation and Cleanup

- Start: `2026-09-26T16:57:48Z`
- Planned end: `2026-09-27T00:00:00Z`
- Released early: `2026-09-26T17:55:17Z`
- At release: queue empty, output roots absent, owned ComfyUI PID stopped, run-scoped scheduled task unregistered.
- Raw configs, backend logs, and failed invocation diagnostics remain Windows-local and are not part of this public record.

## Next Step

Do not retry this reservation. For a separately authorized campaign, launch from the repository root with module mode, for example:

```powershell
Set-Location $repo
py -3.15 -B -m scripts.research.f02_campaign $campaignConfig
```

The reservation was released under the consecutive-environment-failure stop rule. A new run must first establish a fresh reservation and pass the same preflight gate.
