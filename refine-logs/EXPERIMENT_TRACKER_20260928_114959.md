# 补证执行跟踪

本轮执行记录见 M0_M1_GATE_REPORT.md：B0 构造检查完成；Regular 扩大实验差异依据暂不足；逐项复核为 PROCEED WITH CAUTION，完整 M1 矩阵暂停。

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R000 | M0 | 创新性与入口检查 | 三策略 | 不适用 | 可达性、最近工作差异 | MUST | CAUTION_DIFFERENTIATION | 入口源码检查完成；发现强相关预印本 |
| R001 | M1 | 证据判定校准 B0 | 完整与删除字段 | 构造序列 | 错误肯定、unknown | MUST | B0_CHECKED | 20条构造序列；不是产品实验 |
| R002 | M1 | 同run机制 B1 | retry/stop/guard | 五条件三调度 | 提交、执行、完成 | MUST | HOLD_NOT_RUN | 45操作；驱动未集成验证 |
| R003 | M1 | 范围与已知ID B3 | 三策略 | 作用域与两阶段 | 阻塞、完成、执行 | MUST | HOLD_NOT_RUN | 18+9操作 |
| R004 | M2 | 健康校准 | 现有后端 | 三seed | 完成时间、证据完整性 | MUST | NOT RUN | GPU另行批准，最多3生成 |
| R005 | M3 | 真实后端 B2 | 三策略 | 三条件三seed | 追加执行与完成代价 | MUST | NOT RUN | GPU另行批准，27操作 |
| R006 | M4 | 判读增量 B4 | 三记录视图 | 已冻结记录 | 错误肯定、覆盖率 | MUST | NOT RUN | 不新增生成 |
