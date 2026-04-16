# Task Log

## 用户原始 query

> 我已经用rust desktop，可以用IPad操控我的Ubuntu电脑
> 但是我如果想反过来，对吧，比如说我在Ipad上写Good notes, 那么我当然也会想就是说，反过来real time share到我的比基本上
>
> 全屏实时镜像
> Help me do this!

## 你的精简理解

用户要把 `iPad` 上的 `Goodnotes` 书写内容以全屏、实时镜像的方式显示到当前 `Ubuntu` 桌面上；优先采用可落地方案直接配通，而不是停留在方案讨论。

## 你实际做了什么

1. 先查了 `RustDesk` 和 `Goodnotes` 的官方资料，确认 `RustDesk` 当前不支持 `iOS` 被控或屏幕共享，因此不能用于 `iPad -> Ubuntu` 反向实时投屏。
2. 结合官方资料，确定改用 `AirPlay` 接收端方案，并在本机检查了桌面环境与系统信息：当前是 `Ubuntu 24.04.4 LTS`、`X11` 会话，适合运行 `UxPlay`。
3. 由于当前环境无法直接通过 `sudo apt install` 安装软件，改为下载 `.deb` 包并在用户目录解包运行，不改系统级安装。
4. 下载并解包了 `uxplay` 到用户目录；首次运行发现缺少 `libdns_sd.so.1`，随后下载并解包 `libavahi-compat-libdnssd1`，补齐运行时库。
5. 再次运行 `UxPlay` 时发现缺少 `GStreamer` 的 `videoparsersbad` 插件，于是下载并解包 `gstreamer1.0-plugins-bad`，并把对应插件目录注入 `GST_PLUGIN_PATH`。
6. 新建了本地启动脚本、默认配置和桌面启动器，统一封装 `LD_LIBRARY_PATH`、`GST_PLUGIN_PATH`、`DISPLAY`、`XAUTHORITY` 等运行参数，避免用户以后手工拼命令。
7. 用 `timeout` 验证了接收端可以正常初始化并通过 `mDNS/DNS-SD` 广播 AirPlay 服务；随后正式在后台启动 `UxPlay`，服务名设为 `iPad-Goodnotes`。
8. 向用户说明了在 `iPad` 上通过“屏幕镜像 / Screen Mirroring”连接 `iPad-Goodnotes` 的操作路径，并补充了局域网发现失败时的常见排查项。
9. 用户反馈“似乎窗口卡住了”后，读取了运行中 `UxPlay` 会话输出，确认 iPad 端 `192.168.1.5` 已成功连接，并且服务端持续收到 `POST /feedback` 和视频性能回报包，说明网络连接与 AirPlay 会话本身是正常的。
10. 继续检查了当前 `GStreamer` 视频 sink 能力，发现 `autovideosink` 实际选中了 `fake-video-sink`，这意味着虽然流已到达，但没有真正的可视输出窗口，因此表现为“窗口卡住/不刷新”。
11. 针对这个问题，修改了 `UxPlay` 配置，显式指定 `vs ximagesink` 强制走 `X11` 视频输出，并增加 `avdec` 强制软件解码，避免自动选择错误的视频 sink 或不稳定的解码链路。
12. 同时去掉了 `d` 调试选项，避免终端被大量 `feedback` 日志刷满，降低“程序像卡死”的误判。
13. 杀掉旧的 `UxPlay` 进程后，按新配置重启接收端，并要求用户在 `iPad` 上重新断开再连接 `iPad-Goodnotes`，以便让新的渲染链路生效。

## 改动了哪些文件

仓库源码文件无改动。

本次新增/生成的主要路径：

- `.agents/logs/time20260416/time221845+ipad_goodnotes_airplay.md`
- `/home/wudizhe001/.local/bin/uxplay-local`
- `/home/wudizhe001/.config/uxplayrc`
- `/home/wudizhe001/.local/share/applications/uxplay-local.desktop`
- `/home/wudizhe001/.local/opt/uxplay/`
- `/home/wudizhe001/.local/opt/uxplay-libs/`
- `/home/wudizhe001/.local/opt/gstreamer-bad/`

## 结果

`UxPlay` 已在本机成功启动并广播 AirPlay 服务名 `iPad-Goodnotes`。用户后续只需保证 `iPad` 与本机处于同一局域网，并在 `iPad` 控制中心选择该设备，即可把 `Goodnotes` 全屏实时镜像到当前 `Ubuntu` 桌面。

## 补充记录

`2026-04-16 22:28:58 CST` 追加了一次故障排查记录：问题不是 AirPlay 连接失败，而是默认 `autovideosink` 退化成了 `fake-video-sink`，导致流到达但窗口不出图。已改为显式 `ximagesink + avdec` 配置，并重启接收端等待用户重新连接验证。
