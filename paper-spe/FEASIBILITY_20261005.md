# SPE 可行性验证：本地阶段

最新 2026-10-06 R1：[真实结果与判断](NARRATIVE_REPORT_20261006_R1.md)。
已取得真实 known-ID 产物与 Windows 重入拒绝证据；P1 同样取回该 PNG，
人工比较任务全缓存命中，不比较 GPU 性能。作者 review/finalize 与操作者
价值仍缺；建议停止扩大 SPE 投入、不撤回 SoftwareX。下文为 10-05 本地
阶段及早期预检历史，不把其“未验证”条目冒充最新状态。

日期：2026-10-05（Asia/Shanghai）。结论：**允许一个有上限的真实后端验证阶段；目前不满足 SPE 经验报告证据门槛，不建议撤回 SoftwareX。** 本文是开发与验证记录，不是 SPE 稿件。

更新 22:30：作者已经批准 Windows/GPU 窗口；连接预检失败，GPU 阶段 **NOT_RUN**。无新的生成请求、Windows 执行或 GPU 结果。授权保留，具体记录见 `PREFLIGHT_20261005.md`。

更新 2026-10-06 00:00：Tailscale/SSH 恢复，取得 Windows 原生 CPU 负向
证据并补齐 owner-liveness 检查；随后 Windows GitHub fetch 两次失败，
exact-source 门槛未闭合。GPU 阶段仍 NOT_RUN。最新 targeted 回归为 255 tests、
2 skipped、27.982 s；修复后的 Windows 原生测试尚未执行。
见 `NARRATIVE_REPORT_20261006.md` 和 preflight 末尾，不能把此前连接失败
当作当前状态，也不能把 SSH 成功当作真实恢复成功。

## 实际状态与冻结边界

作者报告 SoftwareX 于 2026-10-05 提交，正文为 `paper-softwarex/manuscript-v0.13.md`。历史状态 Submitted to Journal 没有在本阶段访问投稿系统重新核验，不作为当前状态。

- 原投稿工作树：`/Users/chevalgrand/Documents/ paper dsn/review-checkouts/local-gpu-imagegen-dsn-writing`；分支 `codex/ieee-access-adaptation-v1`；HEAD `7f76f90751e527bb8158d15169a425069c1b699b`。未跟踪的既有评审材料保留。
- 开发工作树：`/Users/chevalgrand/Documents/ paper dsn/review-checkouts/local-gpu-imagegen-spe-validation`；分支 `experiment/spe-recovery-validation`，从上述提交隔离创建。已成功 fetch origin；没有合并稳定分支。
- 稿件引用产品快照 `dfc8378cb3d891f7951786bc4544cd971bd56a11`，提交分发快照 `360c7232707199d40a4e3fd763e5031ed129b56a`，验证材料快照 `dc9720ee76375ea341a8770c4ef32c0143b3a1ff`，paired 实验源 `08539d5`。这些版本具有不同职责，不能用新分支结果替代旧实验。
- 本阶段未改 `paper-softwarex/`、`paper/evidence/`、`src/`；`src/` 仍是投稿时的历史镜像，**新开发以 `scripts/` 为安装和运行源**。在新分支上 `git diff 7f76f90 -- paper-softwarex paper/evidence src` 为空。
- 稿件 SHA-256：`509dde073f53a25dc792fdc58a4523f4b1557594efb840c8c87f0621b0d90491`；paired projection SHA-256：`9badad8948811c06f25b876e54768a02b808f9f7233527bd2ade20b4daed0891`。完整目录 Git tree IDs 见 `validation/submission-freeze.json`。

读取了用户提供的全局 AGENTS、Git 工作流 policy、REFACTOR_NODES、paper-access/NEXT_SESSION、已投稿正文及 known-job 验证材料。真实项目及父目录未发现额外 AGENTS，根目录 PROJECT_NODES/NEXT_SESSION 不存在。重构节点中的旧分支、旧测试数字没有作为现状。原节点及稿件保持原样。

## 实现审查和最小补强

原证据能支持的范围：六个固定 Windows 操作区分提交、acceptance、生命周期和客户端完成；guard 在 F02 withholding 后仍未完成原 run，FPRE 会 false block；既有 CPU P-stop 和字段解析比较表现相同。原 known-job walkthrough 分别测试 engine fixture 和真实 adapter 对 fake HTTP 的访问，两部分没有集成，更没有重启进程后完成 review/finalize。

发现并用新独立进程 probes 复现：普通单阶段 ComfyUI 没有 engine 层 job callback，timeout 后 run 回到 `created`；发送并退出、尚未持久化 ID 时，stale cleanup 也会回到 `created`。这允许后续调用绕过不确定结果约束。它是新发现的实现边界，不改写历史 Windows 记录或已投稿稿件结论。

补强只涉及三个产品文件：

1. adapter 在验证通过、POST 前调用持久化 send-intent callback。写入失败则不发送。该标记表示不确定，绝不表示后端已接受。
2. engine 为 ComfyUI 单阶段及两阶段都安装 callbacks；收到 ID 后存储 exact job binding，再次进入时转交 retained `recovery_job_id`。`/history`、`/view` 完成取回；不发新的 `/prompt`。
3. RunStore stale recovery 保留 send-intent 的 unknown 状态。已知 job 或 send-intent 后发生异常时，不清为可重新提交的 failed/created。普通 ComfyUI 也可存储 job；既有无 backend 字段的两阶段 fixture 兼容。

这是可逆且针对真实恢复问题的修复，不是新恢复策略。未经 marker 保护的旧活跃 manifest 不能倒推是否发送；没有迁移旧记录。原有 WebUI/Diffusers 没有获得本阶段的 send-intent 保障。任意新建 run、跨 run 去重、断电/文件系统损坏、所有并发 interleavings 都不在新验证范围。

## 完成的 CPU 验证

环境：macOS Apple Silicon，已有离线缓存的 CPython 3.12.14、Pillow。无下载模型、无云付费调用、无 Windows/GPU/真实 ComfyUI 执行。`tests/test_spe_recovery.py` 使用父进程持有 fake HTTP server，每个产品 action 创建全新 Python 进程、engine 和 RunStore；只有模型许可/catalog/route 及 visual review 输入使用 fixture。产品 engine、adapter、文件读写没有用假的生成 runner代替。

| Probe | 实际观察 | 限制 |
|---|---|---|
| 已知 job timeout 后重启 | 新进程保留 request hash/job ID；换 key、seed、prompt、model identity 均阻止执行 | catalog/授权为 fixture，非真实部署 |
| 恢复和后续流程 | 从 history/view 取回同一 synthetic PNG，generated → review → finalized；final bytes 与取回 bytes 相同 | review 是合成 API 输入，非人工质量验收 |
| completed replay | 新进程返回已完成 round，没有任何新增 HTTP 请求 | 固定本地 case |
| POST 后、ID 落盘前退出 | child `os._exit(71)`；新进程为 unknown/unresolved，原 key 与新 key 都 blocked；总 POST=1 | CPU fake acceptance，非真实 execution |
| ID 落盘后退出 | child `os._exit(72)`；恢复 generated；总 POST=1 | 同上 |
| marker 落盘后、发送前退出 | child `os._exit(73)`；POST=0，仍 unknown/blocked | **false block 代价明确存在** |
| send-intent callback 持久化失败 | 注入 OSError；POST=0 | callback failure injection，不是断电测试 |
| view 返回无效产物 | job ID 保留；另一进程恢复成功；总 POST=1 | fake payload |
| lifecycle 参数非法 | 非法 ID/callback 在 HTTP 前被拒绝 | adapter 边界验证 |

最终回归命令（工作树根目录）：

```sh
SPE_CPU_RECEIPT_DIR=paper-spe/validation/cpu-20261005-final uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest tests.test_run_store tests.test_asset_run_engine tests.test_comfyui_adapter tests.test_runtime_services tests.test_backend_base tests.test_spe_recovery -q
uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python -m unittest discover -s tests/research -q
uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python paper-softwarex/known_job_recovery_demo.py
uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python paper/scripts/verify_paired_projection.py
```

结果：254 tests，exit 0，1 skipped，27.757 秒；独立 research 96 tests，exit 0，8.916 秒；原 known-job walkthrough PASS；六行 projection 一致性 PASS。254 含新增 8 个 test methods。某些已有 fake HTTP timeout 测试在 server 端打印 BrokenPipe/ConnectionReset，unittest 结果通过；不解释为真实网络运行结果。没有重跑整体 1,274-test macOS suite，不宣称修复了历史 macOS 失败。

最终过程 receipts 在 `validation/cpu-20261005-final/`。`cpu-20261005/` 是中间版本：component probes 通过，但同轮总回归存在旧两阶段 fixture 兼容错误；该问题修复后才有最终回归。最早 probes 在原产品上有 3 个失败（普通已知 job、ID 前 crash、ID 后 crash 均返回 created）；初次 discovery 还加载了既有 fixture TestCase，所以那次总计 131 tests。它不是 131 个新增验证，也不提供独立审计。executor 自审，未调用独立 reviewer Agent。

## 简单方案比较与代价

新增一个明确的 CPU comparator：原子 replace 的小 JSON stop 记录、request hash、known job ID；单个顺序 owner。它收到与完整工具相同的 POST graph。

- P0 stop-only：持久化并 inspect，之后不动作，仍 unresolved。
- P1 stop + 显式 manual retrieval：两次 GET history/view，将字节写到文件，也能 finalized。P1 是补充的手工取回基线，不冒充原十二个 CPU P-stop 操作。
- 完整工具与 P1 在该已知任务 fixture 上都只有一个 POST、取回同一图像字节。比较 receipt 的 POST=2 是两个独立路径各一次，不是任何一路重试两次；不是 accepted job/execution 数。

因此“stop 没有恢复、工具有恢复”只描述 P0 的动作定义，不能证明恢复难以用小方案实现。完整工具已在 CPU 验证的差别是持久化的请求/模型绑定约束、completed replay、复核候选及确认后发布的集成契约。尚未证明它们缩短操作时间、减少人工错误或降低运维成本；不能称政策优越性。

该 fixture 代价：完整工具 finalized manifest 20,078 bytes，run 文件合计 22,650 bytes；P0 记录 129 bytes，P1 final record 206 bytes（未计输入 config/graph、synthetic 源图和人工步骤，不能当总存储 benchmark）。完整工具有额外的 marker 写入与 ID 写入，已有 engine/RunStore/adapter 共约 5,396 行，承担 profile、review、locking、artifact 等更广职责；小 comparator 的 stop_worker 为 36 行、无并发或同等校验。代码行数不是开发难度或质量测量。

开发成本：产品 diff 64 additions / 35 deletions，3 个文件；新增 330 行 CPU harness/tests 和本阶段文档、receipts；本地分析与开发约二十分钟量级，回归本身几十秒量级，没有测算人工 person-hours。没有改变包版本、发 release、合并或部署。一次有意义的代码提交及专用分支 push 用于审查和未来跨设备接力。

## 尚缺证据与继续门槛

1. **真实恢复：未验证。** Windows 真实 ComfyUI job timeout 后，retained ID 能在真实 services/catalog/route 下被新进程查询、取得正确产物、经作者实际复核并完成原 run。必须有独立 backend lifecycle 与完整 history 绑定，不能用这里的 PNG 或 job 名代替。
2. **目标平台重启：未验证。** 本地 child exit 可验证进程边界，不能替代 Windows 进程身份/锁与真实 endpoint/model 绑定检查；真实 run 的 key/hash 禁止变更和零额外 POST 需同窗 audit。
3. **可复用的工程价值：尚未证明。** 与 P1 公平比较固定操作者任务的完成状态、动作数、错误/拒绝、用时、丢失/找错产物、metadata/storage 和持久化开销。CPU 只建立可测量契约；不能从一次 case 估算错误率。先由作者确认实际 recurring 使用问题，再确定 operator 任务。

下一阶段的具体可审查方案见 `REAL_BACKEND_GATE_20261005.md`；作者已经授权，但连接预检未通过，未启动 GPU 阶段。三项都证明且差异对操作者有意义后，才制定 SPE experience-report 结构。在此之前不扩写稿件、不追加模型/训练/大范围故障 campaign。若真实 known-job 恢复不能跑通，或 P1 以很少代码/操作已满足实际需求、完整工具没有额外受验证的价值，建议停止 SPE 投入。

## 投稿决定

SPE 的官方 [Aims and Scope](https://onlinelibrary.wiley.com/page/journal/1097024x/homepage/aims.htm) 接受 completed-project/case-study/practical-tool experience reports。官方 [Overview](https://onlinelibrary.wiley.com/page/journal/1097024x/homepage/productinformation.html) 要求贡献可让其他设计/实现实践者受益，并要求稿件未在他处审理（本阶段查询 2026-10-05）。该要求不是篇幅门槛。

当前判断为 **SPE contribution gate HOLD，而非可投稿或仅待改写**。CPU 已证明一条可集成的恢复路径并修复一个真实实现缺口，值得最多一个经批准的验证窗口；它也揭示了小 manual-retrieval 基线可以完成相同任务，进一步投入需严格止损。**不建议现在撤回 SoftwareX**。保持已提交稿件的事实与版本；当前未撤稿、未提交 SPE、未联系编辑。正式转投由作者决定，并以 SoftwareX 审理终止确认作为前置条件。
