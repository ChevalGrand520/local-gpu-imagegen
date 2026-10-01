# paired-ambiguity-v1 执行跟踪

日期：2026-10-01，Asia/Shanghai。协议设计已冻结；没有新增 CPU/Windows/GPU 结果。
此前 R000–R006 属于 2026-09-28 计划，状态保留在旧 timestamped tracker，不在此补写结果。
本计划使用新的 run ID，防止复用历史记录。GPU 任务全部等待实现与现场资源门槛。

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| PA1-R000 | M0 | 入口与记录能力静态审查 | 当前 v2 caller/controller/proxy | 源码 | 路径、发送阶段、条件限制 | MUST | STATIC_REVIEW_COMPLETE | W3-only、unknown 前置条件、完成后重试、forwarded=false 歧义；没有执行证据 |
| PA1-R001 | M0 | 同输入产品入口与故障自检 | B2/W3/P-stop | CPU 9 主操作+3 scope probe | POST、工作入口、完成、阻塞分类 | MUST | TODO_IMPLEMENT | 禁止直接调用内部 guard 冒充产品路径 |
| PA1-R002 | M0 | 同信息解释与 recovery veto | exporter/普通解析脚本 | CPU 最多12探针 | 错误肯定、unknown、理由、字节不变 | MUST | TODO_IMPLEMENT | 其他条件补足后隔离 recovery veto |
| PA1-R003 | M1 | Windows 现场冻结 | pinned B2/W3、caller、backend | 无生成 | source/config、预约、numeric-IP、目录 | MUST | WAIT_M0 | exact source bytes 在执行前归档；沿用公钥，不改 MagicDNS |
| PA1-R004 | M2 | 正常控制及 deadline 校准 | B2/W3 | F00，seed4101 | 完成、artifact、时延 | MUST | NOT_RUN | 两操作；每操作硬截止300秒；T超上限则停止 |
| PA1-R005 | M3 | 接受后回执丢失配对 | W3/B2 | F02，seed4101 | additional_POST、E_bound、原run完成 | MUST | NOT_RUN | 两操作；调用结束后1秒重试；不等待oracle完成 |
| PA1-R006 | M3 | 已证明未发送的保守阻塞 | B2/W3 | FPRE，seed4101 | 零发送真值、阻塞数、原run完成 | MUST | NOT_RUN | 两操作；客户端须为unknown才能进入该分母 |
| PA1-R007 | M4 | 保留负结果并裁决升级 | 三pair与离线记录 | 固定全部计划操作 | 差异、删失、coverage、P-stop等价性 | MUST | WAIT_RECORDS | 不按结果加seed；没有新GPU任务 |

首批 GPU 总上限：6 操作、10 调用、10 代理 POST、8 上游发送尝试、60 分钟、1 GiB。
执行状态不能由本 tracker 预先改为 PASS。下一步是 PA1-R001/002 的 harness 适配与
CPU 自检；PA1-R004 不是本次已启动的任务。
