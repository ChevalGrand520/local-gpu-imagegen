# 重构接续节点（做减法）

> 本文件是 local-gpu-imagegen「做减法重构」的跨对话接续记录。恢复时先读本文件，再读 `PROJECT_NODES.md` 的相关段落，最后检查 git 状态。

## 目标

降低项目复杂度，让它在「脱离 AI」后仍可掌控。不是加功能，是做减法。

## 现状（2026-08-30 起始）

- 分支：`main`，工作区干净（仅 `.codex/` 未跟踪）。
- 版本：v0.9.0 已发布 PyPI（wheel SHA-256 `99c02f963e86d3867165bf16981f6445cb41cf9c8f208bc360578db483bcd179`）。
- 下一个待办门禁：MCP Registry 发布（暂不动）。

## 审查结论（本次要治的三个缺陷）

1. **上帝文件**：`scripts/mcp_server.py` 2052 行，其中 `tool_schema()` 单函数 603 行（359–962），协议层/schema/参数校验/业务分发/信任/绑定全挤一处。
2. **静默吞异常**：`except Exception` + `pass` 约 57 处，遍布 `run_store.py`、`engine.py`、`bootstrap_service.py` 等，错误被藏起、不可调试。
   - ⚠️ **2026-08-31 复测更正**：该数字已过时。按 `except Exception` 紧跟 `pass`/`continue`/`return None` 的口径重新扫描全部已跟踪 `scripts/*.py`，**真正静默的只剩 1 处**（`engine.py`），广义 `except Exception` 共 25 处且多数有真实处理或重抛。原始结论保留作为历史记录，不删除。
3. **过度工程**：一个生图 MCP 做了 15000 行源码 + 20000 行测试（`run_store.py` 2037 行、`engine.py` 1652 行），`identity_strength`/trust registry/evidence 留存等机制超配。

## 修复计划（2026-08-30 修订：只拆上帝文件）

用户确认「可审计、证据留存」是生产级定位，保留；只做「拆 `mcp_server.py`」，不砍 except、不砍机制。

1. ✅ 建接续节点（本文件）
2. ✅ 建分支 `refactor/trim-except`
3. ✅ 装测试依赖 + 跑 baseline（1163 测试；本地 13 errors + 1 failure 全是环境问题：git 不在 PATH、claude/codex 契约）
4. ✅ 拆 `_constants.py`（13 行，共享常量）
5. ✅ 拆 `_protocol.py`（121 行，stdio/JSON-RPC/脚本执行）
6. ✅ 拆 `_schema.py`（666 行，tool_schema + 注册表查询）
7. ✅ 拆 `_validation.py`（364 行，参数校验）
8. ✅ `mcp_server.py` 2052 → 937 行（dispatcher + 入口），re-export 保持测试兼容
9. ✅ 最终完整测试验证：1163 tests，failures=1 / errors=13 / skipped=13，与 baseline 完全一致（剩余全是环境问题：git 不在 PATH、本机 claude/codex 契约），拆分未引入任何新失败

## 拆分后布局

- `mcp_server.py`：入口 + dispatcher（handle_tool_call + 业务函数）
- `_constants.py`：ROOT/SCRIPTS/PYTHON/超时/SERVER_VERSION 等共享常量
- `_protocol.py`：send/tool_error/jsonrpc_error/run_script 等协议与脚本执行
- `_schema.py`：tool_schema 及 _registered_* 注册表查询
- `_validation.py`：validate_tool_arguments 及 schema 类型校验
- `pyproject.toml`：py-modules 增补 4 个新模块（否则 wheel 缺模块，installed_wheel 测试会失败）

## 关键路径 / 命令

- 项目根：仓库根目录（本文件所在目录）
- git：`git`（任意可用的 git 可执行文件）
- venv python：`.venv\Scripts\python.exe`（Python 3.12.12）
- 测试命令：`.venv\Scripts\python.exe -m unittest discover -s tests -v`
- 契约验证：`.venv\Scripts\python.exe scripts\verify_mcp.py` 和 `scripts\verify_client_configs.py`
- 测试依赖（CI 用）：`setuptools>=68`、`Pillow>=10`、`uv==0.11.16`、`py7zr==1.1.3`

## 止损条件

- 任何一步测试变红且无法在当步修复 → 停下，记录，回滚到上一步 commit。
- 不碰 `main` 分支、不碰发布门禁、不改 PyPI 已发版本。
- 只做「做减法」，不顺手加功能。
