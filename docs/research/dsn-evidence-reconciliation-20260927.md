# Evidence reconciliation — 2026-09-27

Scope: read-only follow-up; no experiment, service launch or model download.
This addendum corrects manuscript interpretation; historical reports stay intact.

## Retained Windows campaign report

File: `w3-f02-full-shim-20260927T024140Z-campaign-report.json`.
SHA-256: `5c946b67f840876fa4a6a44bf39c7cdf4604d655fdc0197123acd675cebc55f2`.
Read directly on Windows via authenticated SSH; command exit 0.
Private host paths and raw campaign payloads are not copied into the repository.

| Case | Calls | Proxy submissions | Execution count field | Binding count | Call labels | resolved flag | unresolved flag |
|---|---:|---:|---:|---:|---|---:|---:|
| B2 F00 | 1 | 1 | 1 | 1 | resolved | 1 | 0 |
| W3 F00 | 1 | 1 | 1 | 1 | resolved | 1 | 0 |
| B2 F02 | 2 | 2 | 2 | 2 | unresolved; resolved | 1 | 1 |
| W3 F02 | 2 | 2 | 2 | 2 | unresolved; resolved | 1 | 1 |

All four oracle_evaluable flags are 1. F02 injection_confirmed flags are 1;
F00 has N/A. Controller any-call sums are resolved=4 and unresolved=2.
The Markdown summary's unresolved=0 is not this aggregation; no exclusive
final-case interpretation should silently replace the controller definition.
G01 is resolved at report-field/aggregation level. Original-run reconciliation
is not established. This is not a full raw-event reconstruction or artifact audit.

## Historical tests located

Source task: `01a0a869-dc10-7842-92f8-bbeea86d2a78`, “执行 bounded CPU研究实验”.
The separately referenced ACT R001 task is not the evidence source for DSN.

1. Windows command: `py -3.15 -B -m unittest discover -s tests\research -v`.
   Retained output: `Ran 40 tests in 7.110s`, `OK`, `exit=0`.
   Command/output call ID: `call_J6dExP2sKhM4ntwqxKBTJaLc`.
   Preparation report identifies Python 3.15.0a8. The worktree contained edits;
   do not infer an immutable final-shim source identity from this invocation.
2. Later macOS command: `python3 -m unittest tests.research.test_f02_transport_shim tests.research.test_f02_campaign_controller -v`.
   Retained output: `Ran 7 tests in 0.003s`, `OK`, `exit=0`.
   Same command chain completed compileall and `git diff --check`.
   Command/output call ID: `call` identifier not transcribed; located by exact
   command and output in the source task's retained tool records.

These results are stage-specific, not 47 distinct tests and not a final-shim
40-test full-suite result. Earlier failed intermediate checks also remain in
the source history; the later successful targeted check does not erase them.
G02 is partially closed: commands, outputs, runtime description and stages
are located; exact source-file hashes at test execution remain open.

## Remaining boundaries

G03: full event-to-history binding reconstruction and distributable sanitized
raw evidence are pending. Artifact bytes have not been rehashed here.
G04: related work is expanded with official workflow/tracing documentation;
nearest fault-injection comparison and broader novelty assessment remain open.
No changed scientific denominator, new experiment or probability estimate.
