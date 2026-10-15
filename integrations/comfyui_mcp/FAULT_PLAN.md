# CPU process-boundary campaign — 2026-10-15

Primary question: after an interrupted MCP operation, which facts survive and
which automatic actions are allowed? This is a correctness characterization,
not a claim of a new recovery algorithm or measured human productivity.

Fixed upstream 6996d06, real SDK stdio tools and fake loopback HTTP. Fresh Python
client AND upstream Node child per action. Controller observes fake HTTP events
but never supplies lost IDs to a restarted caller. It may pass an ID only when
an earlier successful caller receipt actually exposed it.

Controls: native (defined caller retries explicitly); stop with durable binding
and explicit read_history; full with durable binding and same-key automatic
history read. Stop and full share the SAME journal and binding mechanism; this
isolates automatic history routing only. It cannot prove the journal is better
than a competent independent implementation of the journal. A stronger simple
baseline with persistent exact-ID manual retrieval is intentionally preserved.

Fixed cases (each of three policies): normal replay; pre-send process exit;
accepted HTTP response loss; reply received / before local ID binding exit;
ID persisted / before caller receipt exit; one failed history read then retry;
changed key; changed seed. Each is one fixed process trace, not a randomized
repeated campaign. A separate existing test covers competing clients.

Freeze before running:
- Primary outcomes: POST count, fake accepted IDs, exact history IDs, worker exit,
  re-entry error/state, retrieved synthetic filename; no GUI/human metrics.
- Successful known-ID recovery = exact-ID history result references a synthetic
  image; NOT actual image retrieval, completed generation or finalization.
- Intent without retained ID must remain unknown; automatic resubmission must
  remain blocked for both durable policies even if no POST happened.
- Stop+explicit history and full are expected to be equal where they have the
  same retained information. Equality is a legitimate negative result.
- Fake server events are external to worker processes but synthetic. They prove
  HTTP fixture observations, not actual ComfyUI acceptance/execution.

Budget: CPU only, <=24 cases / 120 MCP child starts, <=5 minutes of runtime,
per-worker 20s deadline. No GPU, backend launch, cloud API, model download or
human experiments. Halt on mismatched oracle, leaked child process or uncertain
outcomes; fix the harness before interpreting any results. No parameter search.

Decision: if stop+manual and full remain equal, do not launch GPU work to repeat
that equality. Report only convenience of re-entry routing; require a concrete
new hypothesis before more research development. No paper-writing gate is cleared.

## Follow-up independent baseline (declared before four-group execution)

Add `minimal`: independent SQLite implementation with explicit history recovery,
sharing only MCP transport/ID extraction. Expand maximum to 32 fixed traces
(8 × 4), <=120 child starts, <=5 minutes, still CPU-only. Old 24-case receipt
remains frozen and is not relabeled as a four-group result. Unknown-ID windows
must block; known-ID recovery is expected to match full. The revised runner is
not considered executed until the pinned upstream checkout/build is restored.
