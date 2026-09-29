# M0/M1 执行记录与停止判定

日期：2026-09-28。阶段性结论（须结合下方复核）：Regular 扩大实验的差异依据暂不足；M1 仅完成 B0 构造验证及实现草稿，72 案例矩阵未启动。GPU、真实后端、模型下载、外部模型调用均未发生。

## 1. 改变决策的最近工作

Li, Jiapeng. *Where Does Exactly-Once Live? Model, Harness, and Tool-Contract Effects on Duplicate Side Effects in LLM Agents*. arXiv:2609.29095v1，2026-09-24。

- 官方摘要与版本：[arXiv](https://arxiv.org/abs/2609.29095)。
- 本次读取范围：官方摘要页；HTML 的相关工作、问题与命题、guard 实验/消融、讨论和局限等指定段落。未执行对方代码，未独立验证实验数字，未认定为已接收同行评审论文。
- [HTML 原文](https://arxiv.org/html/2609.29095v1)。本文仅概括与决策有关的要点，不复制原文。

| 我们的候选论点 | 对方已涉及的内容 | 本次判断 |
|---|---|---|
| 超时后无法仅凭客户端响应确定副作用 | 显式研究不确定写入及隐藏效果 | 问题本身不是新贡献 |
| 重试可能重复，放弃可能漏做 | 同时讨论重复、完成和未知结果 | 不能用小矩阵重新发现这一取舍来支持 Regular |
| 记录 unknown 并阻止无法验证的再次写入 | 包含追踪未知写入、限制重复及 guard 消融 | W3 局部 guard 必须说明额外贡献 |
| 客户端报告成功不同于真实执行情况 | 对照 agent 报告与效果账本 | 分离 reported/oracle 不能单独声称首次 |
| 本地生成工具的保留证据、导出重建和作用域检查 | 其主要环境为模拟服务与 agent 评估 | 应用场景不同；尚未证明这是独立研究创新 |

这是重叠风险判断，不是抄袭判断，也不是证明所有可能贡献都已被覆盖。对方自述结果未被我们复现。最近工作比较是有界检索，不是系统综述。

## 2. 基础工具对照

| 来源 | 已有能力/概念 | 本工具必须避免的泛化 |
|---|---|---|
| [AWS Builders Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 稳定请求身份与幂等重试 | 阻止 retry 不等于实现服务端幂等 |
| [Temporal activity definition](https://github.com/temporalio/documentation/blob/main/docs/encyclopedia/activities/activity-definition.mdx) | Activity 重试与副作用幂等责任 | 客户端完成记录不等于副作用仅执行一次 |
| [OpenTelemetry context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) | 用上下文关联跨组件信号 | 多层事件关联本身不是新方法 |
| [Toxiproxy](https://github.com/shopify/toxiproxy) | TCP 故障注入 | 丢回执故障注入本身不是新贡献 |
| [Filibuster](https://www.filibuster.cloud/) | 自动合成故障测试变体 | 固定少量 fault case 不构成新故障测试技术 |

检索词包括 exactly-once agents、ambiguous submission recovery idempotency，以及上述项目官方文档。部分批量网页请求长时间未返回后停止；关键新论文通过官方 arXiv 直接读取核实。其他新论文仅作为后续线索，不借二手引用声称读过。

## 3. 产品入口核查

- Native B2：da65d57047b5a59e3403b49adf4605a1c0497c58。
- Native W3：d45173af75d404ad79dc14568edd4c45f654abd2。
- 同一公开方法：`AssetRunEngine.generate_round`，内部使用 `RunStore.begin_attempt`。
- W3：`_require_unresolved_recovery` 对 unknown 阻止再次提交；`recoverable_next_actions` 只给出 get_run。尚无自动查回丢失 job ID 的能力。
- B2 与 W3 的相关差异经 Git diff 核对：transport unknown 标记、unknown 状态保存、守卫和恢复动作暴露。
- 两套源码已从 Git 导出至临时目录，没有更改产品源码。测试文件整体哈希不同，但本轮用到的 fixture 类/辅助方法 AST 哈希一致，记录见 `M0_FIXTURE_PARITY.json`。
- 以上是源码级可达性，不冒充已完成跨版本运行验证。

## 4. 已实现和实际执行

新增 `cpu_evidence_contract.py`：以 operation/run/call/attempt/job/execution 身份、事件顺序和闭合快照检查合成 worker 证据；拒绝缺失 terminal discriminator、身份冲突和不完整生命周期。

- B0：20 个手工构造案例全部匹配预先指定的预期状态；详见 `docs/research/runs/m1-b0-contract-20260928.json`。
- 4 个单元测试通过，包括多 POST 不推出执行、同 job 多执行、缺终止事件和错误绑定。它们与 B0 重叠，不能合计成24个独立实验。
- 两个新脚本通过 Python 编译检查；`git diff --check` 通过。
- `run_regular_cpu_gate.py`：矩阵驱动草稿已实现并通过语法检查，但**未做产品集成运行**。其正确性和72格覆盖均未验收。
- 未运行现有 research 全量测试，避免把已有实验夹具隐式运行混入本轮；既有40-test结果没有被更新。
- 未将新结果加入论文实验表；B0 不证明产品恢复正确、guard 有效或部署准确率。

## 5. 为什么暂停

原提案 M0 的继续条件是“有非平凡研究问题、三策略公平且可实现”。新文献使“unknown 停止重试+有限故障矩阵”的 Regular 差异尚未成立。因此完整 M1 campaign 暂停，而不是耗尽预算后再寻找创新性。

这不是因为需要再次获得已授予的 CPU 权限；是事先约定的科学决策条件没有满足。

## 6. 建议与下一步决策

优先保留 Tool 定位，先更新最近工作对照和收缩主张。当前不得继续把“补72个CPU案例”描述为自然升级 Regular 的路径。

若仍探索 Regular，应先裁决一个可证伪的新问题：在事件丢失、导出裁剪和跨进程恢复下，能否用明确的证据契约给出**可验证的判定充分条件及拒绝判定边界**，并相对传统完整日志/既有 tracing 加审计脚本展示额外价值？

这只是候选方向，尚未通过最近工作检查，也不授权新增方法或扩大实验。不能仅改名“evidence-bound”就认为完成差异化。若没有额外价值，则结束 Regular 升级，完成诚实可检视的 Tool 稿。

## 后续逐项复核（2026-09-28）

见 [贡献对照](CLAIM_OVERLAP_REVIEW.md)。判定校正为 PROCEED WITH CAUTION：同 run guard 与对方复合 guard 不等同；存在具体工具功能差异但不构成已证明的 Regular 创新。9月16日已存在 exporter 和守卫的 Git 记录；不是公开优先权证明。完整 M1 仍未运行，不将早先“门槛未通过”解读为项目应放弃。
