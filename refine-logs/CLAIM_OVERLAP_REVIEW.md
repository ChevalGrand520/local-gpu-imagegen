# 贡献逐项对照：本工具与 arXiv:2609.29095v1

日期：2026-09-28。作者侧、同上下文的有界分析，不是独立同行评审或完整查新。
范围：原始 claim、历史实现、Git 元数据，与指定预印本的机制和评估对照。无新实验。

## 结论先行

**PROCEED WITH CAUTION：保留 Tool 的具体贡献；Regular 的充分差异尚未建立，不判 ABANDON。**
上一轮“M0 创新性门槛未通过”仅能解释为“暂时不足以支持按原方案扩大 Regular 实验”，不能解释为已证明整个项目不新颖。
当前最可辩护的贡献对象是可检查的证据导出及解释流程与本地管线集成。它的研究增量需要单独验证，不能由场景不同或规则更保守自动推出。

## 一、原始主张并非刚刚改写出来

下列 Git author/committer 日期均为 +08:00；完整 SHA 与两类日期保存在 `CONTRIBUTION_TIMELINE.json`。

| 时间 | 提交 | 已存在的内容 | 可支持什么 |
|---|---|---|---|
| 09-16 14:01 | ad1ca025 | exporter 的 reported/interpreted/oracle 分离及版本化输出 | 三层证据设计的内部实现记录 |
| 09-16 17:13 | b3689e0 | unknown 提交状态保存、同 run 阻塞、对应测试 | 守卫有实际历史实现，不是看到新论文后提出 |
| 09-18 22:47 | 50c190d | claim-evidence map；C10 已标 novelty pending | 当时没有完成“全球首次”论证 |
| 09-18 22:53 | eb8df81 | unresolved 即使匹配 oracle 也不能升级综合 verified | 保留 oracle 成功与产品未和解的具体解释规则 |
| 09-20 13:05 | cba9deb | loopback fault oracle controller | Windows 观测工具的内部开发记录 |
| 09-27 10:51 | 5cd100f | endpoint-preserving Windows pilot 报告 | 这部分记录晚于对方 v1 提交日期，不倒推为更早证据 |

对方官方 [arXiv 摘要页](https://arxiv.org/abs/2609.29095) 标注 v1 于 2026-09-24 提交。

**时间界限：**上述是当前仓库可核查的历史内容及可修改的 Git 元数据，尚非独立第三方时间戳或公开披露日期。未核实当时仓库可见性、首次 push 时间、对方更早稿件或其开发记录。不能推出学术优先权，更不能推出任何借用关系。

## 二、同名 guard 不等于相同机制

对方论文 §5 的 recovery conditions 将 guard 描述为：在 verify-before-retry 上组合可用的幂等键、按可见性延迟回查、对无法验证的非幂等重复写入阻塞，以及 unknown 提示；§4 的评估读取模拟服务的效果账本与最终状态。其 §7 承认服务为模拟。来源：[固定 v1 HTML](https://arxiv.org/html/2609.29095v1)。这里只归纳作者陈述，未运行或审计对方实现。

我们的 `RunStore._require_unresolved_recovery` 在同 run 的最新 attempt 为 explicit unknown 时拒绝再提交；不主动回查、不自动添加后端幂等键，也不自动和解。`get_run` 是检查接口。它比“有条件恢复”的机制更窄，不应以两边都叫 guard 就认定完全相同，也不应以更窄就认定更先进。

## 三、逐项裁决

| 我们的 claim | 现有证据 | 相对指定论文的关系 | 允许的结论与剩余缺口 |
|---|---|---|---|
| C03：同 run unknown 阻止重发 | store/engine 实现，历史 CPU 配对 | 保守阻止重复的原则重叠；控制路径不同 | 支持具体实现，不能主张新的通用重试理论；P-stop 仍是必要基线 |
| C01/C02：保留 reported、另算 interpreted、保留 oracle，附版本/原因 | `export_record` 的深拷贝、mapping_version、field_reasons、独占输出 | 已读段落未展示同一套只读导出与解释版本契约；对方也区分报告与真实效果 | **可主张具体工具功能差异**；“未在这些段落看到”不等于对方代码没有，更不等于全球首次 |
| unresolved veto：后端证据成功不等于原 run 已和解 | eb8df81 修正和历史回归记录 | 不把成功报告当执行真相的原则重叠；我们的产品状态判定更具体 | 可作可审查的应用语义规则；若只是重命名复合布尔条件，不足以支撑 Regular |
| C16：backend WS/history 绑定，不从产品响应推出执行数 | Windows oracle 实现及保留 binding | 观测来源不同：真实后端接口与模拟效果账本 | 真实接口集成有工具价值；现有摘要导出丢失 payload，不能声称更可靠或更完整 |
| C15：故障注入保留 endpoint identity | prompt transport shim | 选用的技术边界不同 | 可描述具体集成工程；未证明新的通用故障注入方法 |
| C14：减少真实重复执行 | Windows 不覆盖守卫，CPU 单阶段有完成代价 | 现有自证不足，不能归因于“被对方覆盖” | **仍不支持**；应区分自身证据缺口与相关工作重叠 |
| C21：新的 evidence-bound semantics | 初始记录已明确 novelty pending | 尚有可检查的工具差异，但没有充分方法优越性证据 | Tool 可继续；Regular 需论证“契约改变了什么可证明的判定能力” |

以上并非性能 head-to-head：两者任务、故障空间和证据源不同，不能拿案例数、模型数或某项成功率作直接排名。

## 四、哪些是已知基础，不应争“首次”

通信失败与远端执行结果不等价、稳定身份与幂等重试，是早于两项工作的基础；本工具正文已引用 RPC 与幂等 API 工作。独立实现有价值，但概念不能重新归为原创。应集中介绍具体工具、明确边界和可复查证据。

## 五、现在可用的定位文字

> We present an inspectable tool for local generative pipelines that preserves reported run state alongside versioned evidence interpretation and backend observations. A conservative same-run guard keeps unknown submissions unresolved; the tool does not claim automatic reconciliation or exactly-once execution.

这段是工具描述，不含“首次”、净可靠性提升或对竞争工作的优越性。当前标题中的 recovery 应在正文明确包括恢复决策与保守阻塞，避免被读成自动完成恢复。

## 六、决定：什么值得继续，什么仍应暂停

- 继续：Tool 的最近工作补充、工件可检查性、源文件/示例与主张一致性。这些价值没有被证明失效。
- 不直接继续：用72个固定案例去证明“unknown时停止重试”足够新；完整 M1 仍未运行，本轮不恢复。
- 若要 Regular：先列出契约相对“完整日志+简单审计脚本”的具体可判定差异，证明它不只是同一信息的 JSON 包装；再考虑部分证据、关联缺失或重启的有界验证。此为研究问题，尚非已实现贡献。
- 不因内部实现较早就免除引用，也不因对方较新就自动放弃。未证明对方已包含本工具全部结果，故不存在据此判 ABANDON 的充分依据。

## 本轮核查范围与未做事项

读 Git 历史及历史文件内容、当前 exporter/store/engine 与原始 claim map；针对固定论文 v1 的 §4 grading/validity、§5 recovery conditions、§6 guard 分析、§7 局限进行了对应阅读。使用已从官方页面取得的本地文本。没有审计对方仓库，没有全面追溯其全部引用，没有跑新 CPU/GPU 实验，没有修改论文结果或宣称录用概率。
