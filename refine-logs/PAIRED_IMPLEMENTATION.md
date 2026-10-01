# Paired ambiguity v1 implementation

Status: CPU_COMPONENT_CHECKS_PASS_WINDOWS_INTEGRATION_PENDING.
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

Remaining integration: the six-operation Windows resource-owning runner,
per-operation backend restart/cache policy, whole-campaign limits and live M1
preflight. The operation controller deliberately does not acquire a reservation
or manage a backend. No existing reservation/authorization was rewritten.
