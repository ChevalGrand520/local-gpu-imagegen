# 2029 届升学目标下的论文计划

更新：2026-09-28。用户已批准先提高论文完整度、再选择主投。

## 时间假设与目标

用户为 2029 届；若走常规推免，按 2028 年夏令营及秋季申请准备材料。
这只是规划假设，具体院校、申请路线、成果认定和材料日期尚未确认。
规划目标为 2027 年首投、争取 2028 年上半年前录用；不是录用承诺。

## 投稿决策

- DSN Tool 保留为主题匹配候选，不再指定为唯一主投或最高性价比方案。
- 不因换成 PER 而降低证据要求；实践经验与可推广见解需要真实支持。
- 若优先明确的 CCF 成果认定，先核实学校对具体论文类别的规定，再建设 Regular 版本。
- 不把会议整体录用率解释为单篇论文概率，不提供未经校准的概率或未经核实的分区。
- 2027 年实际征稿尚需核实；不套用上一届日期。

官方依据（2026-09-28 查阅）：
- CCF 第七版说明仅将 Full/Regular 纳入会议目录范围，不能自动把 Tool、PER 或短文按会议等级认定：https://www.ccf.org.cn/Academic_Evaluation/By_category/
- DSN 2026 Tool/PER 定义：https://dsn2026.github.io/cfpapers.html
- QRS 官方公布 2026 Regular 71/278；不能视作保底：https://qrs26.techconf.org/
- PRDC 2026 截止 9 月 17 日已过：https://prdc-symposium.org/
- APSEC 2026 SEIP 对实质 AI 生成论文内容的限制与当前写作过程存在适配问题：https://conf.researchr.org/track/apsec-2026/apsec-2026-software-engineering-in-practices

## 当前获准工作

修正论文和审阅回复中的证据解释；更新编译报告；生成可检查的 v0.6 作者审阅包。
冻结 DS 已审阅的 v0.5 输入。补齐源码摘取和来源说明，不声称完整可运行复现包。
不启动 GPU、模型下载、新实验、外部模型上传或投稿。

## Regular 版本的待讨论研究问题（不是已获准实验）

1. 同一 unresolved run 内的重试是否确实触发守卫？新 run 绕过范围必须单列。
2. 如何同时报告重复执行、最终完成、阻塞代价与误拦，而非只追求执行数减少？
3. 如何保留逐调用身份、seed、去重事件和 terminal payload，使第三方可重建证据？
4. 是否能在明确故障条件与基线下验证普遍性，而非增加相似案例数量？

先形成有明确假设、预算、指标和停止条件的实验提案，再由用户决定是否执行。
在回答上述问题前，不把当前 Tool 稿仅改标题后称为成熟 Regular 论文。

## 已形成的补证提案

见 [Regular 补证提案](../../refine-logs/EXPERIMENT_PLAN.md) 与 [执行跟踪](../../refine-logs/EXPERIMENT_TRACKER.md)。
2026-09-28 已完成规划；所有新实验仍为 NOT RUN。优先建议 M0/M1，GPU 阶段另行批准。

## M0/M1 判定（2026-09-28）

最近工作检查发现 arXiv:2609.29095v1，与候选 Regular 论点明显重叠。B0 的20条构造验证通过；72案例产品矩阵未启动，GPU未运行。详见 [门槛报告](../../refine-logs/M0_M1_GATE_REPORT.md)。下一步优先裁决贡献差异，而非扩大实验。

### 逐项对照后的修正

[贡献对照](../../refine-logs/CLAIM_OVERLAP_REVIEW.md)确认历史实现与具体工具差异。当前为 PROCEED WITH CAUTION，保留 Tool；Regular 证据与差异仍不足。不是全项目创新性被否定，也不是自动恢复矩阵执行。
