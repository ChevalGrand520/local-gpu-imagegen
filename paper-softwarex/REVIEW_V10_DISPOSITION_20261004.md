# v0.10 意见处理与 v0.11 核验

2026-10-04。保留 v0.10；本轮仅补回已记录的信息并修正措辞。

1. 已核对 paper-access/AUTONOMOUS_RESEARCH_GATE_20261003.md:44，记录为
   Python 3.12 本地 macOS 全套 1274 tests、30 failures、5 errors、40 skips、
   exit 1。§3.4 恢复这些数字及观察到的失败类别，并链接到包含该记录的
   dc9720ee76375ea341a8770c4ef32c0143b3a1ff。此前以完整日志未随稿为由删掉
   汇总数字，造成信息损失；该处置在此修正。记录支持报告本地汇总，
   不支持独立复算，也不支持把全部失败归因于一个平台问题。
2. 保留 local、非 Windows/Ubuntu CI、完整日志未公开和未统一归因四项限定。
3. §2.2 改回 is outside the scope of this guard。
4. §4 明确 get_run 暴露 generate_round:recover，再以同键/hash 重入，
   转发 recovery_job_id，通过 adapter history 路径恢复保留的任务。
5. 验证材料 revision 保持 dc9720e；稿件 revision 以 v0.11 和包含稿件的
   Git commit 标识，两者分开，不因稿件更新而移动既有验证材料链接。

bundled builder/render 成功；八页均视觉检查，无截断或重叠。摘要 98 词，
完整 Markdown 3516 词；26 个原模板保留部件相同。表格及参考文献与 v0.10
完全相同。没有重跑 macOS 门禁、其他测试或实验，也没有新独立审计通过。
作者最终确认与当前投稿指南/文件槽/APC 核验仍待完成，未执行投稿。
