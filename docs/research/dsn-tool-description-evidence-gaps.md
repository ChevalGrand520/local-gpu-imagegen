> v0.4 continuation: the active manuscript is `paper/main.tex` and `paper/main.pdf`.
> This document preserves the v0.3 planning/audit snapshot. Current evidence
> disposition and review are in `paper/evidence/` and `paper/review/ARS_REVIEW.md`.

# Evidence-gap annotations and revision record

Date: 2026-09-27. Applies to external v0.1 outline/draft and new v0.3.
Tags: `EVIDENCE-GAP:Gxx` unresolved source issue; `SCOPE:Cxx` bounded claim;
`CITE-GAP:G04` literature gap. Matrix IDs provide the full permitted scope.
The old working files are preserved outside this checkout.

## v0.1 statement audit

| Original location / wording | Issue | v0.3 disposition |
|---|---|---|
| Abstract: “blocks blind resubmission” | Missing same-run, marker and entry-point scope | C03, scope stated in §3.2 |
| Abstract: “binds requests ... artifacts ...” | Field presence does not establish every exact binding | Describe nullable fields and validation rules, C01–C02 |
| Abstract: “one real ... pilot ... reproducible integration path” | Old pilot differs from latest four-case protocol; no independent replay | Replace with report-backed four-case demonstration, G03/G05 |
| Introduction: “generation is expensive ... difficult to repeat” | No cost/repeatability measurement supplied | Remove empirical cost claim |
| Introduction: “recoverable ... reproducible” | Implies completion and demonstrated reproduction | Replace with inspectable observation and guarded same-run behavior |
| Contribution 3: “no new submission ... without reconciliation” | Overbroad; fresh run outside guard | C03/C04 boundary, no automatic reconciliation |
| Contribution 4: “reproducible evidence package” | Windows raw bundle remains private/local | Source and report availability only, G03/G05 |
| §2.1: missing values “remain null/unknown” | Meaning varies by field and version | Explicit mapping/schema implementation, no universal normalization claim |
| §2.3: “safe product state” | Normative safety proof not established | Conservative design choice |
| §3: contradictory observations “as unknown” | Exporter has mismatch/failure categories too | Say conflict/unknown retained, verification gated |
| §4: “real pilot ... validator outcomes” | Old pilot validators not latest F02 acceptance evidence | Do not import protected-pixel/mask results |
| §5: “prevent unsafe resubmission” | Global safety assertion | Scoped same-run guard |
| Outline §5: input/output containment protections | Historical notes not a complete current CLI security proof | Remove broad claim, retain exclusive output creation |
| Outline §7: zero retries, protected-pixel checks | Describes earlier two-stage pilot, not current F00/F02 | Relocate to historical map; exclude from main results |
| Outline §8: clean reproduction and distributable manifests | Planned deliverables, not completed evidence | G03/G05 placeholders |
| Outline §10 and contributions: novelty | No nearest-tool review | Verified conceptual references, explicit G04 |

## Historical v0.2 evidence issues (updated disposition below)

1. **G01 aggregation:** E1 final-case table says unresolved=0. `_case_record`
   uses independent any-call flags. Each F02 has an unresolved first call.
   Do not silently change E1 or label its table as raw controller output.
2. **G02 tests:** 40 passed is a historical Windows Python 3.15.0a8 statement in
   an earlier preparation report. Final-shim suite identity is not established
   by the final report. No new test result is claimed.
3. **G03 raw evidence:** report-backed counts are not a raw JSONL, prompt-ID,
   execution-ID or image-content verification performed during this revision.
4. **G04 positioning:** RPC and idempotency references support background, not
   exhaustive novelty or an experimental comparison with existing tools.
5. **G05 reproduction/venue:** exact target-year requirements and independent
   clean-checkout reproduction remain open.
6. **G06 artifacts:** backend history and hashed paths do not prove content
   validity, protected-pixel correctness, visual acceptance or finalization.

## Main-text discipline audit

- Replaced the old integration success narrative with a per-case observation table.
- Kept equal B2/W3 counts, new-run semantics, changed seed and G01 in main text.
- Kept historical synthetic comparisons in E3; did not pool them with Windows.
- Removed rate, broad safety, automatic reconciliation and reproducibility claims.
- Primary descriptive counts appear in §4.2; no secondary statistical analyses
  are introduced because the fixed cases do not estimate a population rate.
- Claim repetition: abstract introduces; §3 explains mechanism; §4 demonstrates
  and bounds; §6 interprets; §7 concludes. Full provenance stays in the matrix.
- v0.1 §4 was an evaluation plan, not a completed Results section. v0.3 §4 is a
  report-backed Results section; word-count comparison is recorded in the
  writing verification report, not used as a scientific result.

## 中文写作说明

正文主线从“恢复成功”收窄为“保留不确定性并核对执行证据”。
同 run 阻止重发是产品能力；观察完成后新建 run 是研究 harness 的流程。
两者分别陈述，避免用自然语言把不同作用域拼成未经验证的恢复闭环。
所有缺口只列为后续工作，本轮不触发实验。

## v0.3 evidence update

See [reconciliation addendum](dsn-evidence-reconciliation-20260927.md). G01 is
closed for aggregation: direct Windows report inspection confirms overlapping
any-call counts resolved=4, unresolved=2. The original Markdown 4/0 row remains
historical, not the paper’s controller aggregation. G02 is partially closed:
40-test Windows command/output and later 7-test macOS shim/controller check
are located; exact immutable test-source provenance remains open. G03 still
requires raw-event reconstruction and artifact-byte checks. G04 now includes
Temporal and OpenTelemetry responsibility comparisons, not an exhaustive survey.
This update supersedes historical open-status wording above.
