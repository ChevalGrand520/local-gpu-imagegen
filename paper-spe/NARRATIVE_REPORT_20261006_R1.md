# SPE 可行性：真实 Windows 恢复验证结果

2026-10-06，Asia/Shanghai。此报告接替 00:00 的 R0；R0 的连接失败、
原生负向结果及预检失败均保留。不是 SPE 稿件或独立 reviewer verdict。

**真实 known-ID 恢复已到 generated；Windows 重入的 key/seed/prompt 约束
已验证。可复用的操作者收益仍未证明，建议停止扩大 SPE 开发和 GPU campaign，
保留工具修复。现在不建议撤回 SoftwareX，不生成 SPE 稿件结构。**

## 发生了什么

Windows 直连 GitHub 失败后，使用作者已授权的完整 Git bundle，经 SSH
传送 Git 对象并 fetch；随后用增量 bundle 顺序接力。未改 remote、未散拷
产品文件、未修改历史 Windows checkout。隔离 detached checkout 的实际
实验 source 为 `e846a4a4abbdf8913d128d7f27e74ca23b201337`。

普通单阶段 ComfyUI 的持久化恢复缺口已修复；另在真实 Windows 复现了
退出进程仍可打开句柄、被误判存活的问题。GetExitCodeProcess 修复在 Windows
原生测试通过，随后 Windows 255 targeted tests 全部通过（45.876 s、无
skips）。Mac 98 research tests 通过（9.921 s）；prompt/wall budget 两项测试
也在 Windows 通过。上述测试仍与真实生成结果分开。

后台执行通过唯一的按需 Task Scheduler task，由持久 supervisor 持有
worker、状态和日志，不依赖 SSH 子进程存活。任务无未来触发器；本轮结束
后已禁用，LastTaskResult=0，NumberOfMissedRuns=0。没有新 Agent。

预检 a/b 被 GPU 进程基线阻止，POST=0。b 的未知项为 Windows Terminal，
真实文件签名 Valid、签名者 Microsoft Corporation；后续只加入该精确 Store
路径，并在 runner 内再次校验签名。Python/train/CUDA 进程检查未放宽。
c 启动后端后发现隔离 registry 误放在 D:，违反产品 user-local 约束；POST=0，
自有后端已清理。改到新的 LOCALAPPDATA 私有目录，复制既有批准 registry，
没有改共享 registry；d 才完成真实验证。负向收据均保留，未把这些错误算作
恢复失败、失败率或恢复率。

从 c 首次启动的 00:27:15 固定 20 分钟截止，重试没有重置预算。d 约
00:30:54 至 00:33:38 完成，实际只发送 **2 次新 upstream POST**，没有
使用第三次额度。d 的约 164 s 是从实时 status 观察到的程序 wall time，
不是 GPU compute time；本次最终收据覆盖了 started 字段，故审计脚本不从
最终 JSON 伪造开始时间，后续 runner 已补齐该字段保存。

## 结果与边界

| 问题 | 新结果 | 尚不能说什么 |
|---|---|---|
| 真实 known-ID 恢复 | 已接受 ID 持久化后，owned MCP child 以 72 退出；新进程 inspect 为 unresolved，随后取回同一 job 图像到 generated | 未执行作者 review / finalize；不是完整人工流程完成 |
| 重启后的绑定 | 原 request hash 与 job ID 保留；改 key 返回 backend_job_unresolved，改 seed/prompt 返回 idempotency_conflict | model/endpoint drift 的实机负向变更未做，现有 CPU 检查不能替代 |
| 再次提交 | 恢复和 completed replay 期间新增 POST=0；恢复后仍一个 round，replay 保持同一 image hash | 不证明后端 client_id 幂等、未知 ID reconciliation 或一般可靠性 |
| 简单方案 | P0 持久 stop record；P1 显式 history/view 也取回同一 PNG，SHA 完全相同 | 不得把 P0 的“不动作”当作 P1 不会恢复 |
| 工程价值 | 多字段绑定、run 状态、复核/发布接口有真实集成基础；本轮验证了前三项重入拒绝 | 尚无操作者时间、实际错误、重复任务收益证据，不能声称政策优越性 |

已知任务：`8461effe-f982-4644-9e38-264b468814d9`。人工比较任务：
`7056a405-0fde-4665-9850-0cb660f91982`。两者各有 exact prompt ID 的
WebSocket execution_start / execution_success 和 completed history；
history 内 graph、client_id、输出 node 9 与相应 payload 和观察者 ID 一致。
产物 `local-gpu-imagegen_00032_.png`，1024×1024，SHA-256：
`dfc97e42a12d2fb3d1e359be52db6270b6acec01bc4377b0549c94e9b019b04a`。
取回的 product round、replay 和 P1 文件与该 SHA 相同。

**缓存边界必须保留：**首次任务 cached nodes=[]，观察到 30 个 progress
事件；第二个任务 cached nodes=[3,4,5,6,7,8,9]，复用了同一后端输出文件。
这不是两个独立采样任务，不是冷启动公平性能比较。两段 backend event
span 约 19.937 s / 0.00176 s，不能拿来比较策略速度、GPU 耗时或节省。
本轮只比较显式取回的结果和契约。

**观察者架构偏离：**只读 WebSocket/history 观察组件运行在 controller
worker 中，与 owned MCP 产品进程不同，但没有另起纯 observer-only 进程。
它在手工阶段也承担 POST 控制。因此本轮不能标记整个原协议 PASS 或宣称
独立 observer process 审计已完成。真实后端来源、产品进程重入和文件绑定
结果仍保留；正式经验报告若继续，应补齐职责分离。没有独立 reviewer Agent。

## 可测代价

同一图像 952,925 bytes。完整工具的 run 文件：manifest 33,389 bytes、
preview 27,854 bytes、PNG 952,925 bytes，总计 1,014,168 bytes。
P0 stop record 173 bytes；P1 加同一 PNG 为 953,098 bytes。这个限定范围差
61,070 bytes，但未计双方输入配置/graph、代码、registry、observer logs、
目录和其他人工工作，不能称总存储 benchmark。write count/写入延迟未测量。

累计产品改动仍只在 3 文件：75 additions / 37 deletions。CPU recovery
tests 330 行、Windows liveness test 34 行、budget tests 28 行、真实 runner
356 行、收据审计 120 行，另有文档和 private receipts。研究 harness 的
开发/配置成本明显高于本身的产品修复；不将代码行数冒充 person-hours。
没有模型下载、云 GPU、训练、全局包安装或稳定分支 merge。只停止本次自有
backend/process tree；reservation 已释放，真实查询确认 PID267180 不存活。
结束时 GPU 1910 MiB、0% 是进程视图观察，不是全局硬件独占证明。

## SPE 判断与下一步

技术上，真实恢复和 Windows 重入已有可复核支持。贡献上，P1 可完成相同
产物取回；尚不能证明完整工具多出的契约与流程给真实操作者带来足够价值。
因此 **不值得继续增加故障种类、模型、GPU 次数或稿件篇幅**。优先保留
工具修复及证据，服务 SoftwareX 的工具贡献路线。

若作者之后指出一个真实、反复出现且小方案不能低成本解决的使用问题，
再把候选/发布集成转成固定操作者任务；作者实际检查当前图像后才能执行
review/finalize。当前没有作者复核、没有质量 accepted、没有 final artifact。
这些是明确缺口，不用自动授权或 AI 看图伪造作者验收。

已投稿工作树 HEAD 与正文 SHA 重新核验保持不变：7f76f907…；
509dde073f53a25dc792fdc58a4523f4b1557594efb840c8c87f0621b0d90491。
SoftwareX 当前审理状态未重新查询，不把历史 Submitted to Journal 当作
当前状态。不撤稿、不提交 SPE、不联系编辑；转投仍须作者决定并先取得
SoftwareX 审理终止确认。

审计命令：

```sh
uv run --offline --no-project --python 3.12 --with 'Pillow>=10' python paper-spe/audit_real_recovery.py <private-root-d>
```

输出 RECEIPT_CONSISTENCY_PASS 是同一执行者对 raw transport hashes、graph、
job/产物/请求绑定的确定性复算，不是独立 reviewer verdict。原始私有证据
不进 Git。公开概要见 `validation/real-summary-20261006.json`。
