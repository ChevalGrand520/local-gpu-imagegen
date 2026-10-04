# SoftwareX 投稿前最终复查（2026-10-04）

当前候选稿已更新为 manuscript-v0.11.md/docx。新增意见处理见
REVIEW_V09_DISPOSITION_20261004.md 与 REVIEW_V10_DISPOSITION_20261004.md；
下文保留历史审查范围，不改标为 v0.11 独立通过。
作者最终内容确认和投稿端核验仍待完成。

## 同日作者确认更新

下文“最终复查”保留 939991b 时的检查范围；其中待作者确认的项目已在
后续逐项问答中补齐：无相关利益冲突；本人负责所列 CRediT 角色；两张图
使用 OpenAI Codex / GPT-6.1 Sol；无人类参与者、可识别个人数据或动物实验；
材料由作者制作或合法使用；暂无 ORCID。作者拟向学校申请 APC 支持，
尚未获批，该计划未写入论文研究资助声明。

这些事实已写入同一 v0.9 候选稿及声明草稿。尚待更新稿的最终作者内容
确认，以及当前投稿指南/实际文件槽/APC 核验；没有取得或执行提交授权。
本次只补作者声明和图题版本，没有新增实验或改写既有审查的结论。

## 结论

可以进入投稿材料收尾。当前是 **v0.9 候选稿，尚未具备直接提交状态**：
作者声明、图示 AI 工具版本和当前投稿系统要求仍有待确认。
本次未提交期刊、支付 APC、上传查重服务或合并稳定分支。

复查对象为 v0.8（提交 `0b8f272`）；修正结果为 manuscript-v0.9.md/docx。
两个内部审查员分别核对声明与证据、引用与原文，都是同模型家族的暂定
复查，不是期刊评审。引用审查没有发现虚构文献；声明审查没有发现所提供
记录中的数值或汇总错误。审查未获得私有 Windows 原始采集，因此不能认证
真实执行或独立重算整个 Windows 实验。

## 已处理的问题

| 问题 | 处理与证据 | 范围 |
|---|---|---|
| MCP 引用版本与实现不一致 | 源码及重建 wheel 都声明 2024-11-05；正文与引用 [7] 已对齐官方该版本规范 | 版本一致，不代表完整协议合规认证 |
| 润色可能暗示 accepted job 在所有未知提交中都存在 | 改为“withholding alone neither identifies an accepted job…” | FPRE 仍允许实际没有上游发送/接受 |
| `completed` 容易被读成产品最终状态名 | walkthrough 明确结束于 `generated`，acceptance/finalization 另行操作 | 没有新增完成、finalized 或真实 F03 结果 |
| P-stop 比较缺少审查包内回执 | 重跑原脚本，保存 CPU 结果及源码冻结清单；三种条件下与 W3 的四项计数和原客户端完成字段相同 | 合成 CPU 检查，使用 B2 da65d57/W3 d45173a；不重放 Windows 08539d5 |
| 96 tests / 17 tools 的审查输入不足 | 96 项研究测试再通过；重建 wheel 的独立环境 verify 报告 17 个工具、0.9.1、2024-11-05 | 无模型、无 GPU、没有运行完整生成工作流 |
| Mac 全套失败数字没有随稿公开完整日志 | 从正文移除 1274/30/5/40 数字；保留未通过和不支持完整 macOS 的限制 | 原作者记录没有被否认；本次没有重跑全套或推断统一失败原因 |
| AI 辅助图示披露不足 | 两张图题补工具和用途；保留已批准一般声明原文，补充图示辅助说明 | 精确模型版本仍待确认，候选稿中明确标出 |
| 资助及发表历史待确认 | 根据作者答复填无专项研究资助、个人完成；无发表/预印本/其他在审投稿 | 无资助不等于无利益冲突；APC 来源尚未决定 |

官方 [MCP 2024-11-05 规范](https://modelcontextprotocol.io/specification/2024-11-05)
于 2026-10-04 核验。其他引用的逐项来源与限制见
FINAL_CITATION_REVIEW_20261004.md。

Elsevier 当前政策允许 AI 辅助制作特定解释性示意图，要求每张图题注明工具、
版本与用途，并在一般 AI 声明中披露。两图由保留的图示规范/渲染代码绘制。
历史模型版本未核实，不能用当前应用或文档运行时版本替代。
来源：[Elsevier AI policies](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)。

## 验证结果

- `tests/research`：96 tests，9.934 s，exit 0。
- 原有合成 CPU 脚本：12/12 操作，PASS，Python 3.12.14；包括九个同 run
  操作和三个范围探针。CPU lifecycle 字段为 `E_bound_cpu`，不能当作 GPU 测量。
- 新重建 wheel：exit 0；isolated verify `ok=true`，17 tools，版本 0.9.1，
  协议 2024-11-05。wheel 没有 research exporter/paired checker 成员；没有发布。
- 已知 job 恢复 walkthrough 与派生 Windows 表 checker 在本次复查前段再运行
  通过；没有新增真实 ComfyUI、Windows F03 或 GPU 执行。
- 源码 scripts/tests 与软件快照 dfc8378 相同；元数据 Python >=3.11、
  py7zr==1.1.3、MIT LICENSE 与 Licence.txt 一致。
- DOCX 构建/渲染成功；八页逐页检查，没有裁切、重叠、损坏表格或缺图。
  26 个原模板 preserve-only 部件一致；C1–C8 填充完整。99 词摘要、六关键词、
  两图、八引用；全 Markdown 3163 个空白分隔词，包含元数据及参考文献。
  五个 highlights 长度为 80/72/77/60/57。八页总长包含元数据、图、表和引用，
  与模板排除这些内容的正文页数限制不同；提交系统最终 PDF 仍须检查。

公开 CPU 结果和冻结记录：validation/cpu-report-20261004.json、
validation/cpu-source-freeze-20261004.json。命令、环境、负面尝试及范围见
final-check-receipt-20261004.json。这些 executor 记录不是独立执行认证。

首次 CPU 调用使用相对输出路径，因脚本路径比较报错停止；未修改脚本，
换新绝对路径后通过。旧临时 wheel 已不存在，重新构建后通过。原失败记录
保留在本机，不混入成功回执。CI run 37090919543 的 API 两次返回 502，
本次没有刷新历史 CI；论文保留的是已有版本化验证记录中的历史声明。

本次两份 CPU 本地采集目录收尾移至
`/tmp/private-softwarex-final-cpu-20261004`（失败）和
`/tmp/private-softwarex-final-cpu-20261004-absolute`（成功）。公开结果中的
历史绝对路径仍指向运行时位置；没有改写原始回执字节。这些临时目录不
作为永久归档；提交的 CPU JSON 和源码冻结清单是保留的公开材料。

## 仍存在的实质局限

1. **原始 Windows 可复现性有限。** 派生六行记录支持抄录与一致性核查，
   私有原始文件未随稿提供。同 run v2 两例与 paired 六例是不同采集；
   W3 F02 的事件汇总数不同，不能拼成同一实验的认证材料。正文表只使用
   paired projection，没有借新 CPU 检查认证旧 Windows 执行。
2. **科研影响证据偏弱。** 官方模板把 Impact 视为重点；外部采用、日常工作
   改善、下游科研/商业影响尚未测量。这是 SoftwareX 编辑可能质疑的适配
   风险。不能靠增加引用数、改写为优势或虚构用户结果补足，也未证实必须
   再做用户研究才能投稿。
3. **恢复演示的范围有限。** retained-job CPU engine 与 fake HTTP adapter
   分开检查；不是集成真实后端恢复。明确 stop-only 无后续动作，可以展示
   功能差别，但不证明新策略或统计优势。未知 job ID 的 F02 仍无法自动协调。

PAPER_CLAIM_AUDIT.json 按技能的原始结果要求记录执行认证 BLOCKED；审查员
原始判断是 WARN。完整 32 个数字/比较组与 30 个范围组保留在 trace 中。
这是审查保障范围的限制，不是“已发现数据错误”，也不自动构成已核实的
期刊拒稿规则。v0.9 executor 修正没有把 v0.8 审查重新标为独立 PASS。

## 投稿前剩余事项

- 作者确认利益冲突和 CRediT；两图的 Codex 模型版本仍待事实说明。最终稿
  及补充材料需作者审阅批准。ORCID/地址仅按投稿系统实际字段补充。
- 核验当前 SoftwareX Guide for Authors、初次投稿文件槽、声明与匿名要求、
  软件快照/归档要求和实际 APC/税费。当前 guide/Insights/open-access 页被
  403/证书或 CAPTCHA 阻挡；没有越过警告，也没有拿历史 USD1920 作报价。
  保留的官方 OSP v6 模板已获得并核验，完整指南尚未刷新。
- 选择已检查的公开补充文件，查看投稿系统生成的 PDF，完成最终审核后
  才进行提交。DSN 与 Access 相关稿不能并行投稿。

外部相似度检查未执行。本次没有发现它是已核实的 SoftwareX 必交材料，
也不因为声明 Codex 就推断必须购买查重。若作者选择学校的授权服务，报告
需人工判断重合来源；相似度本身不是抄袭或作者身份结论。来源：
[iThenticate 官方说明](https://guides.ithenticate.com/hc/en-us/articles/38053179354125-iThenticate-and-Plagiarism)。
