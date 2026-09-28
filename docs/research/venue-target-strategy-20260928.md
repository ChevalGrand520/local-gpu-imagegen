# 四目标投稿策略

日期：2026-09-28。目标集合：DSN Tool、ISSRE Regular、IEEE Access（SCI 三区候选）、ICSA（待核实，不作为当前主投）。

## 共同底稿

所有路线共享同一事实底稿：

- Windows 固定 4 案例：F00 2 个、F02 2 个；6 次调用、6 条保留 binding。
- F02 第二次调用创建新 run；Windows campaign 不测同一 run guard 效果。
- `execution_start=3` 是累计快照聚合，不是第三次执行证据。
- 未报告部署失败率、自然 duplicate-execution rate、生成质量提升或自动 unknown-job reconciliation。
- 当前证据支持记录级观察与范围明确的保守阻塞。

不能为不同投稿目标改变这些事实。

## 目标 A：DSN Tool Description

### 版本定位

标题和摘要围绕“inspectable evidence integration for local generative pipelines”。贡献为：

1. reported state、versioned interpretation、backend observation 的分离；
2. 同一 unresolved run 的保守阻塞边界；
3. Windows/CPU 观测路径及其明确限制。

### 必须保留

- 工具架构图、证据 schema、guard 入口和失败窗口；
- 4 个 Windows 案例表及累计快照解释；
- 源码地图、离线审计脚本和包校验；
- 与 Li 2026、AWS、Temporal、OpenTelemetry、Toxiproxy、Filibuster 的边界说明。

### 不应写

- CCF B Regular 已满足；
- exactly-once、自动 reconciliation、部署可靠性提升；
- guard 已减少 Windows 重复执行；
- 工具首次解决 ambiguous writes。

### 当前状态

最接近完成。仍需作者确认匿名化、目标 DSN 年份、Tool 类别及是否公开指定工件。

## 目标 B：ISSRE Regular

### 必须改变的论文问题

不能只是把 Tool Description 改成 Regular。主问题应变成：

> 在客户端提交状态、后端执行观察和恢复证据不一致时，证据契约能否给出可验证的“允许判定／拒绝判定／unknown”边界，并减少错误肯定？

### 最低补证门槛

- 与普通日志、OpenTelemetry trace 或简单审计脚本的明确对照；
- 删除 operation/run/call/attempt/job/terminal 字段后的判定退化分析；
- 跨进程或重启后的关联边界，不能只测同进程 list；
- 同时报告 verified、unknown、错误肯定和不可判定；
- 至少一个真实 backend 受控案例，但不把 4 个 Windows 案例包装成统计结论。

若无法证明这些增量，ISSRE Regular 应暂停，继续 DSN Tool。

## 目标 C：IEEE Access

### 版本定位

按 SCI 三区候选规划，但最终分区和学校认定必须按投稿/录用年度核实。期刊稿需要完整的方法、相关工作、验证和局限，而不是会议稿扩写页数。

### 必须增加

- 明确研究问题和可重复方法；
- 完整的证据 schema 与审计算法；
- 多故障条件的系统评估；
- 统计单位、删失/unknown 处理和失败案例；
- 可复现代码与数据可用性说明。

### 适用条件

如果 ISSRE/DSN Regular 的会议时间不合适，或者证据量达到期刊要求，IEEE Access 才作为正式期刊路线。不能用期刊名掩盖 Regular 贡献不足。

## 目标 D：ICSA

当前不作为主投。只有出现以下变化才重启评估：

- 贡献中心转为架构决策、架构机制或架构评估；
- 论文明确描述组件边界、质量属性权衡和架构适用条件；
- 获得目标年度 ICSA CFP 和浙江大学目标学院的认定规则。

软件架构 ICSA、计算机体系结构 ISCA、软件架构 WICSA 必须分别记录，不能用缩写替换。

## 决策门

| 门 | 条件 | 结果 |
|---|---|---|
| V0 | 浙江大学目标学院确认 Tool/PER/Regular/SCI 的认定口径 | 选择认证可行路线 |
| V1 | DSN Tool 的工件、匿名化、格式和声明完整 | 可投 DSN Tool |
| V2 | 证据契约相对普通日志的判定增量得到实验支持 | 才可升级 ISSRE Regular |
| V3 | 期刊级方法、评估、统计和数据声明完成 | 才可转 IEEE Access |
| V4 | ICSA CFP 与架构贡献同时成立 | 才重新评估 ICSA |

## 当前推荐顺序

1. 先完成 DSN Tool 投稿包；
2. 并行维护 ISSRE Regular 的差异化问题，但不运行未经新批准的实验；
3. 将 IEEE Access 作为 SCI 三区候选的期刊扩展路线；
4. ICSA 暂停，直到架构主题和认证规则明确。

## 2026-09-28 有界可行性判定

见 [Regular 可行性报告](../../refine-logs/REGULAR_FEASIBILITY_DECISION.md)。现有 exporter 的增量判定能力尚不成立；ISSRE Regular 保持条件目标，不扩大矩阵。Tool 应补充受信输入边界。IEEE Access 的“SCI三区”未完成当年权威核验，不作为确定认证事实。
