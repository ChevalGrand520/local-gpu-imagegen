# SPE 自动推进结果，2026-10-06

这是 ARIS research-pipeline 在作者限定范围内的阶段报告，非 SPE 稿件、
非独立 reviewer verdict。复用既有问题与验证协议；没有重新找题、创建
Agent、扩大 GPU 预算、撤稿、投稿、联系编辑或合并稳定分支。

结论：**SPE contribution gate HOLD；现在不值得撤回 SoftwareX。**

## 已完成与证据

- 冻结并保留 SoftwareX 稿件、source、evidence；截至 00:00 原工作树 HEAD
  仍 7f76f90751e527bb8158d15169a425069c1b699b，正文 SHA-256 仍
  509dde073f53a25dc792fdc58a4523f4b1557594efb840c8c87f0621b0d90491。
- CPU fixture 证明已知任务恢复、进程重入绑定约束和 completed replay；
  未知提交保守 stop，会产生发送前 crash 的 false block。原 254 targeted
  与 96 research tests 通过；与手工 history/view 取回的同字节结果相同。
- Tailscale 恢复至 LAN direct、15 ms，真实 SSH 身份核验成功。GPU/磁盘/
  ComfyUI 源码和模型存在性有新只读观察，非后端执行结果。
- 新发现、原生重现 owner-liveness 缺陷：Windows child 已退出但持有句柄，
  产品返回 alive=true。W3 与修复前 SPE 函数源码 SHA 完全相同。
- 最小补强 GetExitCodeProcess == STILL_ACTIVE，查询失败保守保留锁，确保
  句柄关闭。对应 Windows 旧开发修复；不是新增的论文贡献。
- 本轮 Mac 255 targeted tests：exit 0，2 skips，27.982 s；新增 native
  Windows 测试在 Mac skipped。不宣称已取得修复后的 Windows GREEN。
- Windows Git fetch 两次失败，隔离 worktree 未创建；没有在历史 checkout
  上运行新协议。实际新 prompt sends、生成/GPU任务、reservation 均为 0。

机器可读摘要见 `validation/windows-preflight-20261006.json`；详情与负向结果
见 `PREFLIGHT_20261005.md`，历史/CPU边界见 `FEASIBILITY_20261005.md`。

## 仍缺什么

1. Windows 取得专用 exact source，执行新增原生 liveness 测试和恢复重入。
2. 独占资源、模型 fingerprint、endpoint/workflow/queue/oracle 全部核验后，
   Task Scheduler 的持久 supervisor 才能开启原 20 分钟 / 3 POST 窗口。
3. 真实 known-ID 产物取回、零重提交和后续流程。作者睡眠期间不能代作
   人工 review；没有作者真实检查则最多记录 generated。
4. 对实际重复出现的操作者问题，证明请求绑定、候选复核/发布集成等能力
   的可复用价值，并与公平的 P1 手工取回比较操作、时间、错误与成本。

## 成本和止损

此前产品改动为 3 文件 64 additions / 35 deletions、330 行 CPU tests。
本轮增加 13 行级 liveness diff（11 additions / 2 deletions）和 34 行原生
回归，以及预检/交接文件。回归约 28 s；网络和原生预检为十分钟量级。
没有测量 person-hours，不把等待时间称为 GPU compute。

完整工具与小方案在已有比较字段相同；P1 可以取回相同产物。metadata、
review、finalization 的额外约束尚未证明操作者收益。当前证据无法支持
一般可靠性、恢复率、策略优越性或 GPU 节省。若一个有界真实窗口仍不能
展示可验证的集成价值，停止扩大 SPE 投入；不靠篇幅或措辞提高贡献。

本轮按 source gate 失败停止，未进行自动 reviewer loop，也没有 reviewer
PASS/accepted 结论。只保存工程结果和下一步，不生成 SPE 正文。
