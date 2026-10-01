# paired-ambiguity-v1 执行跟踪

日期：2026-10-01，Asia/Shanghai。协议设计已冻结；新增 CPU 自检，Windows/GPU 仍未运行。
此前 R000–R006 属于 2026-09-28 计划，状态保留在旧 timestamped tracker，不在此补写结果。
本计划使用新的 run ID，防止复用历史记录。GPU 任务全部等待实现与现场资源门槛。

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| PA1-R000 | M0 | 入口与记录能力静态审查 | 当前 v2 caller/controller/proxy | 源码 | 路径、发送阶段、条件限制 | MUST | STATIC_REVIEW_COMPLETE | W3-only、unknown 前置条件、完成后重试、forwarded=false 歧义；没有执行证据 |
| PA1-R001 | M0 | 同输入产品入口与故障自检 | B2/W3/P-stop | CPU 9 主操作+3 scope probe | POST、工作入口、完成、阻塞分类 | MUST | CPU_COMPONENT_PASS | final pilot-05 12/12；完整 engine 公开入口+合成 MCP adapter，非真实 stdio；新增 runner CPU 检查单独归档 |
| PA1-R002 | M0 | 同信息解释与 recovery veto | exporter/普通解析脚本 | CPU 12探针 | 错误肯定、unknown、理由、字节不变 | MUST | CPU_PASS | final probes-03 12/12；两视图结果相同，没有准确率优势 |
| PA1-R003 | M1 | Windows 现场冻结 | pinned B2/W3、caller、backend | 无生成 | source/config、预约、numeric-IP、目录 | MUST | WAIT_TRAINING_AND_LIVE_PREFLIGHT | 六操作 runner 已实现并通过本机替身检查；Windows 正在训练，本轮未连接；现场预约、源码和原生接口尚未验证；沿用公钥，不用 MagicDNS |
| PA1-R004 | M2 | 正常控制及 deadline 校准 | B2/W3 | F00，seed4101 | 完成、artifact、时延 | MUST | NOT_RUN | 两操作；每操作硬截止300秒；T超上限则停止 |
| PA1-R005 | M3 | 接受后回执丢失配对 | W3/B2 | F02，seed4101 | additional_POST、E_bound、原run完成 | MUST | NOT_RUN | 两操作；调用结束后1秒重试；不等待oracle完成 |
| PA1-R006 | M3 | 已证明未发送的保守阻塞 | B2/W3 | FPRE，seed4101 | 零发送真值、阻塞数、原run完成 | MUST | NOT_RUN | 两操作；客户端须为unknown才能进入该分母 |
| PA1-R007 | M4 | 保留负结果并裁决升级 | 三pair与离线记录 | 固定全部计划操作 | 差异、删失、coverage、P-stop等价性 | MUST | WAIT_RECORDS | 不按结果加seed；没有新GPU任务 |

首批 GPU 总上限：6 操作、10 调用、10 代理 POST、8 上游发送尝试、60 分钟、1 GiB。
历史 CPU 回执见 `PAIRED_CPU_CHECKS_20261001.md` / JSON；当次71项 PASS。
2026-10-01 14:21新增 runner 回执见 `PAIRED_WINDOWS_RUNNER_CPU_20261001.md`；全套92项 PASS，均为本机检查。
CPU 的停止策略等价性、保守阻塞代价与普通解析脚本等价性均保留。
最新现场检查与部分采集见 `WINDOWS_PAIRED_PARTIAL_20261001.md`。
M1 attempt A 端口检查停止，0调用；attempt B 两个F00完成，W3/F02在生命周期不可绑定时停止。
B2/F02、两个FPRE未运行。当前预约已过期；下一步只读分析停止原因，修订协议后再安排新预约。
停止原因已定位为观察器遇1秒静默提前退出，而非完整deadline耗尽。
修正与96项本机回归通过；见 `ORACLE_QUIET_WINDOW_DIAGNOSIS_20261001.md`。
修正版Windows实测仍NOT_RUN，需要新预约、新采集编号，T公式保持不变。
PA1-R004 未启动；不能把 CPU 通过视作 Windows 现场门槛已满足。
