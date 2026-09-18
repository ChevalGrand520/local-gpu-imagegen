# DSN 初稿声明与证据对应表

## Material Passport

- Origin: academic-research-suite / experiment-agent, bounded evidence validation.
- Date: 2026-09-18.
- Status: PARTIALLY_VERIFIED. E1 exporter semantics corrected with a regression test; no live backend rerun.
- Product/evidence input: `17e0bbaa8866f46fdbda6eac48763779ac07047b`.
- W3 client: `d45173af75d404ad79dc14568edd4c45f654abd2`.
- W2 correction: `a7482fedda8c98a3d31df916638fc241473316dc`.
- Frozen B2: `da65d57047b5a59e3403b49adf4605a1c0497c58`.
- Trusted ledger: `d8ef0bccc84269b7d4a627adce5f6025a17ab024`; guard PASS, 14 protected files.
- Draft reviewed: `dsn-tool-description-draft.md` v0.1, SHA-256 `8e05523bc4f641915f372437f067bb20f7730962c253590141db3721e514c00a` (external working draft, not part of this commit).
- Scope: claim tracing, exporter interpretation correction, and CPU checks. No new research design, product fix, GPU experiment, or manuscript revision.

## 实际状态修正

项目目录迁移后，旧路径仅有后来创建的两份稿件；实际研究仓库仍存在于已登记的 DSN 项目目录。W3 worktree 的双向 Git 路径因迁移失效，本轮用 `git worktree repair` 修复，未改产品文件。W3 原工作区干净，HEAD 为 d45173a。

正常 fetch 后，PR #4 实际已合并到研究分支，merge SHA 为 17e0bba；不应继续称它未合并。该合并只新增 Windows pilot 两份证据文档；`git diff --exit-code d45173a 17e0bba -- scripts tests` 返回 0。本轮没有执行合并。

专用文档分支：`paper/dsn-evidence-map`，从 17e0bba 创建。原 W2 工作树保持 a7482fe。两份旧路径稿件保留不动，后续修订应在正式文档分支接入并核验字节。

## 声明—实现—验证—允许结论

下列源码定位基于 17e0bba，符号名优先。测试通过仅覆盖相应 fixture；它不消除未覆盖条件。

| ID / 初稿位置 | 代码与提交 | 本轮或历史证据 | 允许结论 / 缺口 |
| --- | --- | --- | --- |
| C1 摘要、§2.1：reported / interpreted / oracle 分离 | a7482fe `scripts/research/export_records.py::export_record`；本分支 E1 修正；`research-normalization-v2` | exporter 11 tests 通过；新增 unresolved + exact oracle binding 回归，另检查输入保持、未知、错配、路径与覆盖拒绝 | 已有只读规范化功能；unresolved 不再升级为 execution verified。仍不能据此推断部署故障率 |
| C2 摘要、贡献 2：执行 oracle | a7482fe `execution_oracle.py::ExecutionOracle`；`run_fault_matrix.py::CpuFakeBackendWorker._run_worker` | 本轮 oracle 5 tests 通过；W2 matrix 3 tests 通过 | 独立于产品返回状态的内存事件计数，观察 CPU delegate 入口；不是独立进程、耐崩溃日志或真实 GPU 执行观察 |
| C3 摘要、贡献 3：阻止未知提交后的重发 | b3689e0、1f31bd0；`backends/base.py:255`、`engine.py:403,1487`、`run_store.py:559,1177` | 本轮 base/store 114 tests 与 engine 定向 4 tests 通过 | 对显式 `submission_outcome=unknown` 的异常，在同一 run 入口阻止相同或不同 key 再提交；不保证绕过入口或新建 run 时不重复 |
| C4 §1、§2.3：恢复未知 job | `engine.py::recoverable_next_actions` 返回 get_run；store 拒绝新提交 | W3 历史文档明确没有新增 reconciliation；本轮同 run 阻止重发测试通过 | 这是保守阻塞；未知 job 自动恢复未实现。不能写成已解决恢复完成问题 |
| C5 §4：已知 job two-stage 恢复 | B2 已有逻辑；`test_two_stage_timeout_recovers_exact_job_without_resubmission` | 本轮测试通过；W2 F03-two-stage 已有 same-job 路径 | 属于既有能力，不归为 W3 新贡献 |
| C6 §4：六个 case 的故障覆盖 | a7482fe `run_fault_matrix.py`、`tests/research/test_run_fault_matrix.py` | 在 a7482fe 实跑 3 tests，setUpClass 执行六个 cases；断言 barrier、job、submission/execution、恢复状态 | 六个预设 CPU fixture 的条件覆盖；不是实际 ComfyUI adapter HTTP 端到端实验，也不是部署概率 |
| C7 W3 相比 B2 改变重复执行 | paired-v2 common runner；B2 `da65d57`；W3 `d45173a` | 相同 localhost POST 响应丢失、相同 harness hash、独立 worker-entry oracle；12 个产品 case 全部 oracle-evaluable | F02 single-stage 中 W3 比 B2 少 1 次提交和 1 次合成执行，但从 B2 的窗口内完成变为 W3 unresolved。只能报告这一配对收益—代价，不能写部署率或净可靠性提升 |
| C8 摘要、§4：Windows 集成示例 | a7d3e36 evidence；6a74046 reservation；客户端 d45173a | 本轮读取版本化摘要，PR #4 GitHub 状态 MERGED；没有读取本地 PNG/manifest 或现场重跑 | 可引用已记录的一次 generated/unreviewed pilot；摘要来源已追溯，原始图像及日志本轮未独立验证 |
| C9 摘要、贡献 4：reproducible integration path | CPU 命令可重跑；Windows 文档只有一次运行记录与哈希 | CPU 定向测试本轮复现；Windows 无第二次复现材料 | CPU 可复跑和单次 Windows 示例分别陈述，不合并为跨环境完整复现 |
| C10 贡献 1–4：独创性 | 初稿仅列功能；参考文献尚为待补主题 | 本轮未进行新的文献综述或外部 baseline 测试 | 技术存在不等于新颖；保留 novelty pending，不赋予录用概率 |

## E1：exporter unresolved 反例与修正

冻结设计 §5.1 要求 `execution_verified=true` 时无 unresolved。修正前 `export_records.py` 的合取条件检查 execution、job、artifact、oracle 和 approval，却没有排除 reported unresolved / recovery required。

本轮只读内存探针输入如下；所有身份为合成字段，不是真实作业：

```python
import sys, json
sys.path.insert(0, 'scripts')
from scripts.research.export_records import export_record
r = {
    'reported_state': {'state': 'unresolved'},
    'job_id': 'job-1', 'artifact_hash': 'a'*64,
    'approval_state': 'valid',
    'artifact_validation': {'status': 'verified', 'independent': True},
    'oracle_state': {
        'execution_state': 'succeeded', 'oracle_evaluable': True,
        'execution_started': 1, 'execution_finished': 1,
        'job_id': 'job-1', 'artifact_hash': 'a'*64,
    },
}
x = export_record(r)
print(json.dumps(x['interpreted_state'], sort_keys=True))
assert x['interpreted_state']['recovery_state'] == 'required'
assert x['interpreted_state']['execution_verified'] is True
```

修正前探针退出 0，输出同时包含 `recovery_state=required` 与 `execution_verified=true`。这是确认反例的退出码，不是契约通过。它说明 exporter 曾存在契约缺口，不表示 B2 产品发布了错误产物，也不能计为真实 false-verification rate。

本分支先把同一反例加入 `test_unresolved_report_cannot_be_verified_with_exact_oracle_binding`。修正前该测试退出 1，失败点为 `True is not false`；随后解释层增加恢复状态约束，只有 `not_needed` 或明确的 `resolved` 才可能满足 `execution_verified=true`。修正后仍保留 oracle 的 `execution_state=succeeded`、精确 job/artifact binding 和 `evidence_state=verified`，但 `recovery_state=required` 使 `execution_verified=false`，原因记录为 `unresolved_or_reconciling_recovery_state_prevents_execution_verification`。这修复解释语义，不回写历史导出，也不改变产品恢复逻辑。

## Oracle 与矩阵的具体边界

`ExecutionOracle._events` 是当前进程中的 list；worker 与产品 fixture 同一进程。每次 `_run_worker` 调用前记录 started，delegate 返回后记录 finished。它支持当前同步异常模拟的计数，但进程崩溃后的事件完整性未被证明。

`source_sha` 在 matrix runner 内硬编码为 B2。W2 checkout 的产品目录和 `tests/test_asset_run_engine.py` 与 B2 比较无 diff，故此处有静态版本依据；这不是任意 checkout 自动锁定 B2 的能力。在 W3 上另跑 matrix 时不能信任硬编码字段来证明实际执行版本。

## 分母与历史结果

以下 W2 数字来自版本化记录并由本轮六 case 语义测试复核；重跑不新增独立科学样本。resolved 是现有 mapping 的首次故障边界分类，不直接代替冻结设计中的 resolution_rate。

| 层 | scheduled | started | injection-confirmed | oracle-evaluable | resolved | unresolved | failed | not-run |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| W2 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| W2 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 2 | 0 |
| paired-v2 B2 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| paired-v2 B2 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 2 | 0 |
| paired-v2 W3 F00 | 2 | 2 | N/A | 2 | 2 | 0 | 0 | 0 |
| paired-v2 W3 F02/F03 | 4 | 4 | 4 | 4 | 1 | 3 | 1 | 0 |

failed 是存在 product failed attempt 的 case 数，与 unresolved 可以重叠；各列不可直接相加作为互斥分类。W2 合成重复执行观察仅 F02-single-stage、F03-single-stage 两例，不能沿用初版“三例”或 0.5。

Windows 历史摘要：scheduled=1、started=1、generated=1、retry=0、visual review=0、finalized=0。未注入故障；独立 execution oracle 可判定分母、故障 resolved/unresolved 等未由该摘要建立，保留 N/A/unknown，不拿 job 数代替 execution 数。

## 本轮验证命令与结果

Python 3.12.14，Pillow 12.3.0。裸 3.12 的 PIL 导入最初失败（退出 1）；随后使用 uv 离线缓存环境，导入退出 0。没有联网安装、模型下载或 GPU 调用。uv 创建了本地可再生环境与 uv.lock；新生成的 uv.lock 已移除，环境未提交。

1. ledger 内：`git show d8ef0bccc84269b7d4a627adce5f6025a17ab024:scripts/verify_research_contract.py | python3 - --root <actual-ledger-root> --anchor d8ef0bccc84269b7d4a627adce5f6025a17ab024`：退出 0，PASS，14 protected files。实际 root 是迁移后的账本目录。
2. 产品主仓库：`git worktree repair <actual-w3-root>`：退出 0。修复前 W3 的 `git status` 报无效 gitdir；修复后 status 干净、HEAD d45173a。
3. `git fetch origin research/w3-ambiguous-submit codex/w3-windows-pilot-evidence`：退出 0。
4. `gh pr view 4 --json state,headRefOid,baseRefName,mergeCommit,url`：成功输出 MERGED、17e0bba。其后另执行的 PIL 导入失败，不能把组合命令退出 1 归给 PR 查询。
5. `git diff --exit-code da65d57047b5a59e3403b49adf4605a1c0497c58 a7482fedda8c98a3d31df916638fc241473316dc -- scripts/local_gpu_imagegen tests/test_asset_run_engine.py`：退出 0。
6. `git diff --exit-code d45173af75d404ad79dc14568edd4c45f654abd2 17e0bbaa8866f46fdbda6eac48763779ac07047b -- scripts tests`：退出 0。
7. W3：`uv run --offline --python 3.12 --with 'Pillow>=10' python -m unittest tests.research.test_execution_oracle tests.research.test_export_records tests.test_backend_base tests.test_run_store tests.test_asset_run_engine.AssetRunEngineTests.test_ambiguous_single_stage_submit_blocks_resubmission tests.test_asset_run_engine.AssetRunEngineTests.test_ambiguous_submit_persists_unknown_when_pending_cleanup_fails tests.test_asset_run_engine.AssetRunEngineTests.test_backend_failure_is_recorded_without_consuming_round tests.test_asset_run_engine.AssetRunEngineTests.test_two_stage_timeout_recovers_exact_job_without_resubmission`：退出 0；133 tests / 0 fail / 0 error / 0 skip，5.428 s。
8. W2 a7482fe：`uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest tests.research.test_run_fault_matrix`：退出 0；3 tests / 0 fail / 0 error / 0 skip，0.558 s；包含六个 case。
9. W3：`uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -`，stdin 为 E1 探针：退出 0，反例成立。
10. 本分支 E1 回归单测（修正前）：退出 1；1 test / 1 failure，确认 `execution_verified` 错误为 true。
11. 同一回归单测（修正后）：退出 0；1 test / 0 failure。
12. `... python -m unittest tests.research.test_export_records`：退出 0；11 tests / 0 fail / 0 error / 0 skip。
13. `... python -m unittest tests.research.test_execution_oracle tests.research.test_export_records tests.research.test_run_fault_matrix`：退出 0；19 tests / 0 fail / 0 error / 0 skip，0.568 s。
14. `... python -m compileall -q scripts/research tests/research`：退出 0。

没有复跑全量 suite，历史全量失败仍保留在原日志，定向通过不能写为全仓通过。本轮活动为目录恢复、静态核验和约 6 秒的报告测试运行；未启动新的执行指标实验。

## 后续唯一工作单元

E1 和 paired-v2 CPU 对照均已完成。后续唯一工作单元是由高级模型基于 paired-v2 的收益—代价做 DSN 稿件闸门复审：决定主张应停留在工具展示/案例研究，还是还需一个真实 ComfyUI F02 语义核验。当前没有足够证据把项目描述为“已实现未知 job 自动恢复”“已证明部署失败率”或“已证明可靠性净改善”。
