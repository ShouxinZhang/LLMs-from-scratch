# UI Debug Simulation

这个参考文档定义了“前后端分离模拟”的使用方式，用于快速判断 GUI 问题属于哪一层。

实现约定：

1. 通用技能只负责调度，不承载具体游戏逻辑。
2. 每个游戏模块把自己的 UI 调试脚本放在 `<game_module>/skills/scripts/` 下。
3. 调试输出默认写入 `.agent_cache/python-frontend-dev/<game_module>/artifacts/`。

## 后端模拟

后端模拟直接调用 `GameBackend`：

1. 切换最优路径显示。
2. 执行移动。
3. 触发收集。
4. 执行重开。

输出产物：

1. 后端状态快照 JSON。
2. 基于后端状态直接渲染的 GIF 和 PNG 帧。

## 前端模拟

前端模拟驱动真实 Tk 组件：

1. 鼠标点击路径按钮。
2. 方向键移动。
3. `WASD` 键位别名测试。
4. `R` 键重开测试。

输出产物：

1. 前端状态快照 JSON。
2. 基于真实 Canvas 项目树镜像的 GIF 和 PNG 帧。

## 推荐入口

```bash
python3 .agents/skills/python-frontend-dev/scripts/ui_debug_runner.py --module pixel_coin_game --mode both --gif-fps 48
```

也可以直接运行模块内脚本：

```bash
python3 -m pixel_coin_game.skills.scripts.ui_debug_runner --mode both --gif-fps 48
```

## 建议排障顺序

1. 后端快照异常，前端快照也异常：优先查 `core/` 或状态机。
2. 后端快照正常，前端快照异常：优先查按键映射、按钮事件、Tk 绘制。
3. 两者状态都正常但图像不对：优先查渲染层或样式层。