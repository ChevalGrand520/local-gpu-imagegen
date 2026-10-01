# Paired results to claim gate

Route: ARIS result-to-claim; read-only fresh subagent.
review_independence: same-family
acceptance_status: provisional
claim_supported: partial (overall); yes for narrowly scoped C1.

Deterministic ARIS precheck found COMPLETED in the private runner-report.json
(exit 0, verified). This is an evidence-existence check only. The earlier local
retained-capture audit passed 1,561 checks. The semantic reviewer inspected the
protocol, CPU receipt, runner data and decoded relevant raw events. No network,
GPU action or file mutation was delegated.

## Verdict

- C1: supported in fixed Windows batch C. F02 B2/W3 POST and lifecycle counts
  are 2/1; original completion is yes/no. FPRE upstream sends are 1/0, with
  original completion yes/no. W3 fault retries return submission_outcome_unknown.
- C2: supported only by earlier synthetic/offline probes. Exporter and ordinary
  same-information parser agreed on twelve probes; the new Windows campaign
  did not newly evaluate exporter correctness or classification superiority.
- GPU savings: unsupported; second B2/F02 lifecycle reports cached nodes 3..9.
- Superiority over P-stop: unsupported; CPU counts/completion match W3 and
  Windows P-stop was not measured.
- General reliability, deployment rates and automatic recovery: unsupported.

FPRE's no-send evidence and W3's blocked retry belong beside the positive F02
submission result. The contribution is an inspectable submission/availability
tradeoff and integrated evidence contract, not superiority over all retry policies.
Reviewer confidence was high on semantic limits and moderate on runtime causal
attribution, because provenance and binding rely on retained project records.

## Writing route

Matrix updated first with stable P01--P10 IDs; outline then separates the
research extension from frozen Tool v0.18. Unsupported claims are marked in
the matrix before prose. `docs/research/paired-study-narrative.md` is the new
working draft, covering evaluation question, protocol, both paired results,
negative baselines and a compact evidence boundary.

The review suggests bounded prose revision; this checkpoint retains the frozen
submission artifact and stages the prose separately, as required by the active
experiment plan. No new generation, external review API, model download or
manuscript build was performed. Six-operation completion alone does not pass
the gate for a full research-paper novelty claim or authorize wider experiments.

Next gate: decide which manuscript claims genuinely require new evidence and
which are already covered by this bounded Tool contribution. Do not expand
workloads solely to manufacture an advantage.
