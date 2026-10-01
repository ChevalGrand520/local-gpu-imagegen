# Six-operation Windows runner: offline preparation receipt

Checkpoint: 2026-10-01 14:21 Asia/Shanghai.
Protocol: paired-ambiguity-v1. Windows status: NOT_RUN.

## Implemented scope

`paired_windows_runner.py` owns the six-operation schedule and boundary checks;
`paired_windows_ops.py` adapts owned Windows processes and native preflight;
`run_reserved_windows_paired.py` supplies a plan-only default and supervised
execution entry. Existing historical four-case preflight retains its default
scope. The operation controller now retains observed prompt metrics on an early
stop, with unknown execution bindings represented as null rather than zero.

The fixed order is B2_F00, W3_F00, W3_F02, B2_F02, B2_FPRE, W3_FPRE.
Budgets are 6 operations, 10 calls, 10 proxy POSTs, 8 upstream attempts,
3600 seconds and 1 GiB. Backend processes restart between operations; calls
within one operation share the same backend. Source/configuration bytes are
archived before backend startup. F00 RPC intervals set T=max(60,3*max(interval));
T above 300 seconds stops the campaign. Cleanup uses owned PID trees only.
Storage monitoring is sampled, not a filesystem quota; an observed excess
stops the campaign and preserves its evidence.

## Local command receipts

Working directory: the repository root. Interpreter: Homebrew python3.13.

```sh
python3.13 -m unittest tests.research.test_paired_windows_runner -q
# exit 0; Ran 21 tests in 0.052s; OK
python3.13 -m unittest discover -s tests/research -q
# exit 0; Ran 92 tests in 9.117s; OK
python3.13 scripts/research/run_reserved_windows_paired.py \
  docs/research/paired-windows-config.example.json
# exit 0; PLAN_ONLY; execution_performed=false; launch_enabled=false;
# training_state=busy; reservation_is_not_created_or_extended=true
```

Tests cover order/cleanup, busy and expired reservations, control failure,
deadline calibration, pair mismatch, sampled budget overage, source-byte drift,
offline CLI behavior and supervisor termination of its owned worker. Windows
commands are mocked. Constructed counts in these tests are fixture values,
not Windows observations. Historical CPU matrix/probe receipts were not rerun,
rewritten or pooled into a new result.

## Remaining live gate

The user reported that Windows is training. This turn made zero Windows
connections, GPU queries, backend starts or training changes. Native Windows
ACL, process-tree cleanup, GPU process query, MCP/ComfyUI execution and the M1
preflight remain unverified. A successful compute-process query is a limited
process view, not proof of global GPU exclusivity.

The example config is disabled, busy and expired; it is not a reservation.
After training ends, validate the actual frozen sources, existing authorization,
active exclusive reservation, private directory and native interfaces before
launch. Do not manufacture an owner/window/idle declaration. Keep numeric-IP
access and existing public-key authentication; do not use MagicDNS.

Tool v0.18 manuscript and delivery bundles remain frozen. This checkpoint adds
no paper experiment results and establishes no physical GPU-computation claim.
