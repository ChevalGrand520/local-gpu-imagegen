# Disposition of the 2026-10-02 model-assisted Access review

Scope: author-side review of the current Access draft. This is not an editorial
decision, independent execution authentication or authorization to release raw
captures or run a GPU experiment. Source review was supplied as a pasted report;
the present disposition checks its claims against the current Git worktree.

| Review point | Disposition | Basis and action |
|---|---|---|
| Historical 6/6/6 and paired 10/8/6 are contradictory | Partly accept | The counts belong to distinct protocols. The manuscript already separated fresh-run from same-run calls, but the table captions and local references were easy to miss. Both captions and the historical text now name their protocol explicitly. Do not pool the counts. |
| `execution_start=3` mixes paired and historical cases | Reject | The statement follows the historical four-case table and its two F02 rows. `paper/evidence/windows-audit.json` contains those counts and two proxy submissions per F02 row. The paired projection reports different event counts. The revised sentence explicitly names the historical export. The unresolved historical raw-event gap remains. |
| Paired results cannot be independently recomputed from distributed raw records | Accept | The derived projection and audit script exist, but the private WebSocket/history/proxy capture needed by that script is not distributed. The manuscript now states this limitation directly. A sanitized raw package needs a separate privacy and release decision; no public release is authorized here. |
| `paper-access/tables/*.tex` are untracked, preventing a clean build | Reject | `git ls-files` lists both `cpu-rows.tex` and `windows-rows.tex`, as well as `main.pdf` and `template-provenance.json`. The review's clean-clone conclusion relied on a false premise. |
| Python requirement is 3.10 | Accept wording correction | `pyproject.toml` declares `>=3.11`. The manuscript now states that requirement and retains the measured 3.13.15 test interpreter. |
| RQ3 demonstrates exporter superiority | Reject as a reading of the draft | The draft already reports equal decisions on twelve constructed probes and explicitly denies a classification-accuracy advantage. The review usefully notes that the same-author parser is not a blind third-party audit. No stronger result is inferred. |
| Recovery in the title overpromises completion | Open judgment | The product does not reconcile unknown jobs, and W3's faulted original runs remain incomplete. A title centered on submission control may fit better, but title and article-type changes depend on the author's route decision. |
| Add Li's theorem-level claim from the preprint | Defer | This review inspected only the abstract. Do not insert a precise theorem or proof characterization before reading the relevant full-text statement and assumptions. |

The seven-page length is not the demonstrated blocker. The research gap is a
defensible contribution over simple stop and an equal-information audit, plus
reproducibility of the paired Windows result. The current CPU stop policy already
matches W3 on reported submission/completion behavior; repeating those same
cases would not establish policy superiority. A blind external audit comparison
would need a frozen answer key, equal observations, an independent implementer
and predeclared cost and error measures. It is a separate study, not a minutes-
only formality.

Decision gate: before more experiments, choose whether this bounded manuscript
continues as an Access research candidate or is developed as a tool/software
paper. For the Access route, first inspect the nearest full texts and define a
falsifiable value claim beyond classification equivalence. Separately decide
whether a reviewer-inspectable, privacy-reviewed raw package is feasible.
Neither step implies publication, GPU use or a model download.
