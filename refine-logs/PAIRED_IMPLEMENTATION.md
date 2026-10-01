# Paired ambiguity v1 implementation

Status: WINDOWS_RUNNER_CPU_CHECKS_PASS_WAIT_TRAINING_AND_LIVE_PREFLIGHT.
CPU fixtures only; Windows NOT_RUN. See `PAIRED_CPU_CHECKS_20261001.md` and JSON.

Decisions recorded before implementation:
- Preserve historical same-run v2. Add an explicit `paired_same_run` caller mode
  whose retry validates identity/arguments but leaves recovery-state admission
  to the native product, equally for B2 and W3.
- Proxy stages identify each received request, not each completed receipt.
  `upstream_send_started` means the HTTP send function is entered; it does not
  certify delivery or acceptance. A forwarding exception retains that stage.
- FPRE closes the connection after complete body reception, before `_forward`.
  Its first prompt request consumes the one-shot fault even without acceptance.
- CPU checks import the two pinned Git product trees in isolated subprocesses;
  public engine entry points and real HTTP transport are exercised. The model,
  backend worker and MCP dispatch adapter are synthetic. This is not a Windows
  MCP/ComfyUI measurement or a claim of physical GPU execution.
- P-stop uses only the first caller-visible `backend_request_failed` response
  (ambiguous transport outcome), equally available on B2/W3. It does not read
  proxy receipts or independently constructed worker truth to decide to stop.
- No new Windows generation before M0 passes and M1 is verified. Preserve
  failed CPU receipts, exact source bytes and execution command/runtime context.

Implementation and validation receipts will be appended below.

The shared caller/proxy/schedule and per-operation controller are implemented.
Final source-frozen CPU matrix: 12/12; same-information offline probes: 12/12;
research regression tests: 71 PASS. Native B2 reaches same-run retry. W3 and
P-stop have equal submission counts on these faults; exporter and the ordinary
parser agree on all probes. No superiority conclusion is supported.

At the preceding checkpoint, remaining integration was the six-operation Windows resource-owning runner,
per-operation backend restart/cache policy, whole-campaign limits and live M1
preflight. The operation controller deliberately does not acquire a reservation
or manage a backend. No existing reservation/authorization was rewritten.

## Six-operation runner decisions, before implementation

- Windows is currently training; this implementation turn uses only local CPU
  tests. No SSH, remote preflight, GPU query or backend action is authorized for
  the busy host in this turn.
- CLI defaults to plan-only. Execution requires an explicit execute switch,
  an existing current reservation and launch permission in the supplied local
  configuration. Never manufacture owner, window, exclusivity or idle state.
- Source and configuration bytes are retained before the first backend start.
  Each operation starts a new owned backend process. Both calls within that
  operation share it; no cache intervention between calls.
- Before acquiring a backend, query compute processes for the frozen GPU.
  Busy/unsupported/unavailable results stop; operator idle declaration alone
  is insufficient. Existing backend/listening-port ownership is never taken.
- Enforce the fixed operation/call/submission budgets at each boundary and
  monitor wall time/storage in the Windows supervisor. Storage is a sampled
  stop condition, not an OS-enforced filesystem quota; excess is reported and
  retained. No result is called complete after a budget violation.
- Cleanup targets only tracked processes and their owned child trees. Never
  kill a process by executable name. Allow cleanup time inside the window.
- F00 controls calibrate T=max(60s,3*max(control RPC completion)); if T>300s,
  stop rather than clamp. Fresh backend startup and cleanup are separate from
  this completion metric.

## 2026-10-01 14:21 Asia/Shanghai checkpoint

The six-operation runner, Windows owned-process adapter and bounded supervisor
are now implemented. The disabled example configuration reports PLAN_ONLY.
Twenty-one runner tests use CPU substitutes and mocked native commands; the
complete research suite passes 92 tests (9.117 seconds, Python 3.13).
No Windows connection, GPU query, backend launch or training change occurred.
Real Windows APIs, MCP subprocess execution and M1 remain unverified. Training
completion alone does not authorize startup: a live preflight and an existing
valid exclusive reservation are still required. See
`PAIRED_WINDOWS_RUNNER_CPU_20261001.md` for command receipts and scope.
