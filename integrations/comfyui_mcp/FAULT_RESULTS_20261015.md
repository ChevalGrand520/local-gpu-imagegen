# MCP 故障与进程重启：自动化 CPU 结果

日期：2026-10-15，Asia/Shanghai。实验代码使用固定上游 6996d06ff511dd7b3b05adf89716e7667df2c1b9。

## 实际完成

24 条固定轨迹（8 个场景 × 3 种调用策略），wall time 20.507 s。每个步骤启动新的 Python 客户端；每次 MCP 调用启动新的 Node SDK stdio harness，执行固定上游的原始 enqueue_workflow / get_history 工具处理器。后端为 controller 持有的本地假 HTTP 服务，不是 ComfyUI；没有 GPU、模型执行、图像下载或人工实验。

`fault_worker.py` 在预先指定的位置用 os._exit 真实终止客户端进程，不用返回错误冒充进程退出。退出之前已关闭该次调用拥有的 Node 子进程；这里未验证 Python 在 Node 正运行时被强杀的子进程清理。发送前、MCP 返回后但绑定前、绑定后但返回调用者前，退出码分别为 71、72、73。controller 的模拟后端记录不用于向恢复客户端补充遗失 ID。

## 固定场景结果

以下为同一逻辑 run 的初次动作及后续重入期间累计 POST 数。原始组的再次提交由实验调用者显式发起，**不是上游自动重试行为**。

| 场景 | 原始调用 | 持久 stop＋显式恢复 | 完整适配 | 两种持久策略的结果 |
|---|---:|---:|---:|---|
| 正常提交后重入 | 2 | 1 | 1 | 均可读到原任务的模拟产物引用 |
| 写 intent 后、发送前退出 | 1 | 0 | 0 | 均误阻塞；没有后端任务 |
| 假后端接受后关闭响应连接 | 2 | 1 | 1 | 均 unknown，无 ID，不自动再次提交 |
| 收到 MCP 回复、ID 落盘前退出 | 2 | 1 | 1 | 均 unknown，无 ID，不自动再次提交 |
| ID 落盘、调用者收到结果前退出 | 2 | 1 | 1 | 均用保存的原 ID 读取历史 |
| 一次历史 JSON 损坏后重试 | 1 | 1 | 1 | 三组均可按先前成功回执的 ID 重试读取 |
| 改 key 重入 | 2 | 1 | 1 | 两种持久策略均拒绝变更 |
| 改 seed 重入 | 2 | 1 | 1 | 两种持久策略均拒绝变更 |

正常/ID 落盘后退出两场景中，stop 组需要显式 read_history，full 组同键 submit 自动转历史。调用形式不同，不构成人类时间或错误率证据。历史失败组的两次历史请求均保留在 trace 中，未把失败读取当作空历史或再次提交理由。

## 可复核材料

- `FAULT_PLAN.md`：运行前固定的问题、对照、预算和停止条件。
- `cpu-fault-receipt-20261015.json`：全部 24 行、worker exit/reply、本地 journal 状态、HTTP 轨迹和模拟后端 job IDs。
- `cpu-fault-audit-20261015.json`：从 HTTP trace 重新计算 POST/历史请求并检查退出码、状态与对照一致性。
- 审计输出 `RECEIPT_CONSISTENCY_PASS`，不是独立认证、独立 reviewer verdict 或真实后端证据。
- 原有 17 项 boundary/recovery 回归测试通过；固定上游 smoke 在重构共用 harness 后再次运行。

复算：

```sh
python3 integrations/comfyui_mcp/audit_fault_campaign.py integrations/comfyui_mcp/cpu-fault-receipt-20261015.json
```

重跑（需已编译的固定上游本地 checkout；CPU，不启动真实 ComfyUI）：

```sh
python3 integrations/comfyui_mcp/fault_campaign.py /absolute/pinned-upstream --receipt /private/local/fault-receipt.json
```

## 判断与下一步

跨进程意图/ID 保持、未知提交约束和负向代价在这组模拟边界上成立。**完整适配与公平的简单持久化对照在所比较结果字段中全部相同。** 两组共享持久 journal/绑定实现，这是为了隔离自动恢复路由的作用，不能用来证明该 journal 优于独立实现的简单方案。

这轮回答了“实验是否可以自动推进”：可以，人工操作不是这些正确性实验的必要条件。但扩大自动化覆盖不自动产生研究新颖性。既有 10 月 6 日真实 Windows 实验中，显式 history/view 同样能取回产物的结果继续有效。

遵守预设停止条件：本轮不追加 GPU 来重复同样的相等结果，不生成 SQJ 稿件或录用判断。后续若继续，优先在 CPU 上评估原始 upstream Panel 的已有恢复能力与独立实现的最小 durable journal；只有发现具体、可复现的新增缺口，再为真实后端验证申请有界预算。
