# 已授权 Windows/GPU 验证：连接恢复，源码同步门槛未通过

00:00 检查时：SSH 已认证成功；真实 GPU
恢复实验仍为 **NOT_RUN / SOURCE_SYNC_GATE_FAILED**。以下 22:30、23:32 的
连接失败保留为历史观察，不代表最新连通状态。最新详情见本文末尾。

最新更新 00:10 后：作者要求全自动继续并授权必要后续操作。Windows
直连 GitHub 再次 40 s 超时后，改用完整 Git bundle 经已认证 SSH 传送，
不改 remote、不散拷源码。Windows bundle verify 成功，隔离 detached
checkout 的 exact SHA 为 5e0983e0662ceb31fca1773e1e8b7053151079c5。
**SOURCE_SYNC_GATE 已闭合**。新 Windows native liveness 回归 1 项通过、
0.028 s；255 targeted tests 全部通过、45.876 s、无 skips。此前 pending
GREEN 和同步阻塞已解除。正在准备 Task Scheduler 有界 runner；尚无新 POST。

时间：2026-10-05 22:28–22:30，Asia/Shanghai；最后确认 22:30:52。

状态：**NOT_RUN / CONNECTION_GATE_FAILED**。这不是 backend 恢复失败，不是 GPU 测量，也不是新增 CPU 验证结果。SPE contribution gate 仍为 HOLD；不建议据此撤回 SoftwareX。

## 授权与 source

作者在看到 CPU 报告及真实后端协议后明确回复“批准”，授权原协议内 20 分钟或 3 个新的 upstream prompt sends，先到者止损。授权持续有效，满足连接条件后可再预检；不允许扩大预算、增加 Agent、撤稿、转投或联系编辑。

22:30 时的开发 source：`93c3318ea9a396690978cb0b3d7b948eceb465a1`，分支 `experiment/spe-recovery-validation`；当时本地工作树干净、Windows 尚未连接，因此其 checkout/source、环境、GPU、queue、模型和 reservation 均无法验证。该段是首次预检记录。

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

## 作者请求后的再次检查（23:27–23:32）

当前系统层的 DNS 已恢复：系统 resolver 和直接向 8.8.8.8、1.1.1.1 的 UDP DNS 查询均取得 controlplane.tailscale.com 地址。Python 默认 opener 和无代理 opener 的 HTTPS HEAD 都返回 200。这纠正了“系统网络一直无法解析”的推断；没有证明 Tailscale extension 自身可达。

保留既有 accept-dns=false / accept-routes 配置重启 Tailscale，再重新启用其 macOS connection service，均未得到 Running/peer mapping；extension 仍报 NoState 和控制面 DNS 错误。没有改 DNS、其他代理、账户或密钥。

新 SSH verbose 检查显示 TCP 建立后，对历史数值地址的 22 端口返回 `HTTP/1.1 404 Not Found` 而不是 SSH banner，随后关闭。`route -n get` 证明该地址及控制面 IP 都通过 utun5，gateway 100.64.164.1；utun5 local address 为 100.64.164.2。这只能证明当前连接路径异常，不能确认 Windows SSH 服务故障或识别拦截者。没有越过 host-key 验证、没有发送登录凭据。

只读检查了 Watt Toolkit UI，显示 Hosts 模式和“一键加速”，没有据此认定它就是 utun5 的持有者；未停止它或更改其设置。已向作者询问“数据线连接手机与 Mac，还是 Mac 与 Windows”，尚待设备信息，不能把普通数据线等同于可用网络链路。

本次仍为 CONNECTION_GATE_FAILED：没有 Windows 身份核验、Task Scheduler、reservation、生成请求或 GPU 执行。检查结束将 Tailscale 逻辑状态恢复为 Stopped。下一步应确认备用连接的设备与网络类型，并同时复核到 tailnet 数值地址的路由，不能只凭 HTTPS 成功启动实验。

## 第三次检查：SSH 恢复与 Windows 原生负向证据

2026-10-05 23:49 至 2026-10-06 00:00。数值 tailnet 地址的 SSH 公钥认证
成功，hostname 为 LAPTOP-7QD7KR9F；随后 Tailscale ping 显示 LAN direct，
15 ms。没有使用数据线或更改其他 VPN。最新 Tailscale 仍提示无法同步
coordination server，因此 peer 可达可能退化；不能宣称网络问题彻底解决。

只读 Windows 检查：GPU UUID 与冻结环境匹配，RTX 5070 Ti Laptop GPU，
12,227 MiB，总占用 1,642 MiB、利用率 4%。compute-app 查询列出 WDDM
桌面进程而非 Python；这不证明资源独占。现有 ComfyUI 和 SDXL 文件存在，
ComfyUI Git HEAD b1693ecba9f5b65f8c80ab36b195ab963ec92413；E: 可用
86,387,380,224 bytes；系统 Python 3.14 可导入 Pillow 12.2.0。
本次未重新 fingerprint 模型；两端口的连接检查没有确认服务可用，未得到
backend queue。因此 endpoint/model/queue/reservation 门槛仍未闭合。

历史 W3 checkout 为 clean detached d45173af75d404ad79dc14568edd4c45f654abd2。
Windows primary 的旧节点另有 2026-09-02 liveness 修复（3595fe0），不在
当前 SPE source 中；没有修改这些 checkout 或把旧节点当成新实验结果。

原生无 GPU 检查在 W3 运行真实产品函数：owned child 活着时 true；退出码
0 后仍持有 Popen handle，产品仍返回 true（预期 false）。该函数源码
SHA-256 d43140824a3dda86414ae23182e0d53120a9ee8d05c2052e1371aa0c7366ba9f
与修复前 SPE 分支完全相同。该结果证明 owner-liveness 缺陷，**不证明**
真实后端恢复。SPE 分支加入 GetExitCodeProcess / STILL_ACTIVE 检查；查询
失败仍保守视为存活，finally 关闭句柄。此修复对应已知旧修复，不包装成新
研究贡献。新增 Windows-only retained-handle 回归；Mac 255 targeted tests
通过、2 skipped、27.982 s，其中原生 Windows 测试被跳过，修复后的 Windows
GREEN 尚未取得。fake HTTP 线程打印 ConnectionResetError，但 suite exit 0。

尝试经 Git fetch 专用分支，再创建隔离 Windows worktree；首次 GitHub HTTPS
Recv failure / connection reset，单次禁用 Git HTTP proxy 的有界重试在
21,110 ms 后仍无法连接 github.com:443。两次均 exit 128，worktree add 未执行。
没有通过 SSH 复制产品源码或改变 remote，没有在未核验版本上执行 GPU 任务。

结尾状态：**SOURCE_SYNC_GATE_FAILED**。新 upstream POST=0；backend/client
生成进程、GPU reservation、Task Scheduler 实验 task 均未创建。只有已完成并
退出的原生 CPU probe child。未消耗已授权 GPU 实验窗口；授权和预算保留。
Tailscale 保留用户当前连接，未执行 down。下一步先让 Windows Git 正常取得
专用 exact commit，运行原生 liveness 回归，再检查真实 backend/oracle；不扩大
网络修复或 GPU campaign。SPE 仍 HOLD，不建议撤回 SoftwareX。
