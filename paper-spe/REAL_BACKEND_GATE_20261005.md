# 待授权的 Windows / GPU 验证窗口

这是下一阶段的可审查协议，未执行。不得仅凭该文件启动任务、使用 GPU 或联系编辑。

更新（2026-10-05 22:30 Asia/Shanghai）：作者已在对话中明确批准此协议的 Windows/GPU 窗口。授权不含撤稿、投稿、联系编辑、新 Agent 或预算扩大。首次连接预检失败，GPU 阶段未执行；见 `PREFLIGHT_20261005.md`。下一次满足连接条件后可在原授权内重新预检，无需重复索取相同批准。

## 进入条件

作者明确授权 Windows/GPU 窗口和预算；fresh numeric Tailscale IP、工作分支与 exact commit 校验；专用顺序 writer；真实 backend/version/workflow/model/endpoint 身份；已有模型与足够磁盘空间；独占 reservation、无他人队列/GPU 工作。不得下载模型或消耗云 GPU。若任何条件不满足，留下无法验证或阻塞记录并停止。

在 Windows 使用新证据目录和专用开发 checkout，保留 SoftwareX/source/campaign snapshots。Git fetch 专用分支，禁止直接替换历史实验 checkout。只用 `scripts/` 安装布局；`src/` 是投稿镜像。

## 窗口和职责

总上限：20 分钟或 3 次新的 `/prompt` upstream sends，以先达到者止损；一次预检/健康控制、一次 known-ID 恢复任务、一次显式手工取回比较。使用既有可确认单阶段 workflow 和固定 seed/参数，禁止变体搜索。预计只有本地硬件占用；运行时间不等于 GPU compute time。若 backend 排队/一个任务超过窗口，不盲目补跑。

同一执行者负责后台服务与 GPU reservation；产品 action 顺序进行，另一只读 observer 进程记录事件，不是新的 Agent。Task Scheduler detached supervisor 持有状态、receipt、audit 日志；SSH 断开不代表成功或失败。只允许停止本次拥有的 client child，不得 kill shared ComfyUI、全局 interrupt 或清他人队列。

## 顺序验证

1. **预检**：source freeze、环境版本、endpoint/workflow/model identity、queue 空、可用磁盘、Task Scheduler 持久状态、observer self-check。无独立 oracle binding 则退出。
2. **Known-ID retention**：POST 前持久化 marker；已接受 ID 落盘后，在该 owned product process 注入完成响应中断/退出。保留原 plan/key/hash、route、manifest 和 HTTP timeline。observer 用本次 `client_id` 订阅并绑定 exact prompt ID 的 start/terminal + completed history。不从 POST 或仅 history 推断 execution。
3. **新进程重入**：通过真实 runtime services 和 MCP/engine 同一原 run，inspect；分别用改变 key/seed/prompt 检查禁止、再用原 request 恢复。检查 history/view 取回的 image 与 job/output node/filename 绑定、SHA-256、dimensions；恢复期间 `/prompt` 新增必须为 0。换 model/endpoint 的负向输入仅用本地持久记录/确认边界测试，不改变共享 backend 实际加载状态。
4. **后续操作**：作者实际检查图像后记录 review，使用 exact candidate confirmation 发布；新进程再 inspect final 并核对 published bytes。没有作者实际复核时，最多记 `generated`，不虚构 accepted 质量评价。
5. **公平小方案**：另一个固定任务执行 P0 durable stop 与 P1 manual history/view retrieval（同一小方案 run 的后续步骤），相同 endpoint/model/workflow/seed。按同样 job/产物 oracle 取回与核对。允许 manual retrieval 成功；不以人为禁止恢复制造贡献。记录完整工具与 P1 的 operator actions、用时、拒绝理由、找错/丢失文件、manifest/storage、一次写入开销；一人固定操作案例只能是 observation，不能报 error/recovery rates。
6. **结束**：确认 owned clients/observer 状态、无遗留 owned queue items、释放 reservation、保留本次运行产生的文件；不全局删除 backend history。记录 Task Scheduler exit/status 和 audit，收据缺失即未完成。

独立 source-lock/receipt/row recomputation 是一致性检查，不能代替执行身份验证。`client_id` 不是服务端去重契约；不允许将不同 task 的 prompt IDs 合并成一个恢复结果。若因客户端退出 backend 事件不可观察，停止并标注 oracle gap。

## Proceed / stop

Proceed：真实 exact-ID 恢复取得原任务产物并完成真实 review/finalize；Windows 新进程保持绑定且零新 POST；至少一个作者认可的实际操作者任务显示已核验的额外集成价值，并清楚说明相较 P1 的开销。三项同时满足后才写 claim-evidence matrix 和 SPE 结构。

Stop：绑定不清、真实恢复失败、预算耗尽、source/环境不一致、oracle 缺失；或者 P1 已以更低代价解决实际需求，完整工具差异仅是更多 metadata/流程而没有可核验的使用价值。至多记录一个有解释的 harness 修复；超过预算需要重新讨论，不能把失败改称恢复成功。未知 ID reconciliation、更多故障、一般可靠性或 GPU 节省不在此窗口。
