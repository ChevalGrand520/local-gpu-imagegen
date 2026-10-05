# 已授权 Windows/GPU 验证：连接预检未通过

时间：2026-10-05 22:28–22:30，Asia/Shanghai；最后确认 22:30:52。

状态：**NOT_RUN / CONNECTION_GATE_FAILED**。这不是 backend 恢复失败，不是 GPU 测量，也不是新增 CPU 验证结果。SPE contribution gate 仍为 HOLD；不建议据此撤回 SoftwareX。

## 授权与 source

作者在看到 CPU 报告及真实后端协议后明确回复“批准”，授权原协议内 20 分钟或 3 个新的 upstream prompt sends，先到者止损。授权持续有效，满足连接条件后可再预检；不允许扩大预算、增加 Agent、撤稿、转投或联系编辑。

开发 source：`93c3318ea9a396690978cb0b3d7b948eceb465a1`，分支 `experiment/spe-recovery-validation`；本地工作树干净。Windows 尚未连接，因此其 checkout/source、环境、GPU、queue、模型和 reservation 一律 **无法验证**，不是“空闲”。本阶段只读取既有协议和 runner/oracle 的接口，没有复制配置或源码到 Windows。

## 实际观察

1. 首次本机 Tailscale JSON：BackendState=Stopped，TailscaleIPs=null，Peer=null。SSH agent 无身份。
2. `ssh-add --apple-use-keychain <existing-key> </dev/null` 成功加载既有密钥；没有创建或更换密钥，没有读取私钥正文。
3. 尝试 `tailscale up --timeout=15s` 被现有非默认 flags 检查拒绝。按工具给出的现有配置，带 `--accept-dns=false --accept-routes` 重试；没有 reset 配置。该调用超时，未进入 Running。
4. 随后的 `tailscale status` 返回 NoState，诊断：

```text
fetch control key: Get "https://controlplane.tailscale.com/key?v=142": failed to resolve "controlplane.tailscale.com": no DNS fallback candidates remain for "controlplane.tailscale.com"
```

工具同时报告 logged out，但本阶段没有据此认定用户账户失效或要求重新登录；控制面 DNS 失败已足以阻止 tailnet 验证。

5. 对 SSH config 中的历史数值 Windows 地址做了一次只读 `hostname` 探针（BatchMode、StrictHostKeyChecking、8 秒连接上限）；返回 exit 255 / `Connection closed ... port 22`。没有得到主机身份或进入认证成功状态，不能确认历史数值 IP 当前映射。
6. 回滚临时连接尝试：`tailscale down` 返回 exit 0，随后 status 报 `Tailscale is stopped.`。`scutil --nc list` 同时仍把 macOS Tailscale VPN service 显示为 Connected，故只确认 Tailscale 逻辑状态已回到 Stopped，**不宣称整个系统网络服务已断开**。未修改其他 VPN、DNS、路由或账户，也未进一步排障。

## 资源和结果

- 新 upstream `/prompt` sends：0。
- Windows product/backend/observer processes：未启动。
- Task Scheduler task、GPU reservation：未创建。
- Windows/GPU/model/queue 状态：无法验证。
- 真实 job ID、图像取回或 finalization：无新结果。
- SSH 既有密钥留在当前本地 agent 中；私钥与凭据不入 Git。
- 原 SoftwareX 工作树、稿件及 evidence 不变；没有撤稿、转投或联系编辑。

下一步依赖本机 Tailscale 控制面可达及有效 peer 映射。恢复后重新检查 Windows 主机身份、source、环境和独占资源，再决定进入实验窗口。本阶段不绕过这些门槛，不用历史环境值填成 current，也不因无法连接而扩大网络修复范围。
