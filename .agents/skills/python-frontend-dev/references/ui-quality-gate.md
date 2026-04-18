# Python Frontend UI Quality Gate

该技能用于建立前端回归门禁，目标是把 GUI 改动变为可自动验证。

## 四层门禁

1. 结构快照：检查控件与画布元素是否存在，状态是否符合预期。
2. 后端模拟：直接驱动 `GameBackend`，定位状态机或规则层问题。
3. 前端模拟：通过鼠标点击和按键事件驱动 Tk UI，定位事件链或渲染问题。
4. 布局一致性：检查关键控件尺寸与画布规格是否稳定。

## 入口脚本

1. 通用调度入口：`.agents/skills/python-frontend-dev/scripts/ui_quality_gate.py --module <game_module>`
2. 模块内实现入口：`<game_module>/skills/scripts/ui_quality_gate.py`

## 执行方式

初始化或更新基线：

```bash
python3 .agents/skills/python-frontend-dev/scripts/ui_quality_gate.py --module pixel_coin_game --update-baseline
```

日常门禁校验：

```bash
python3 .agents/skills/python-frontend-dev/scripts/ui_quality_gate.py --module pixel_coin_game
```

导出前后端调试素材：

```bash
python3 .agents/skills/python-frontend-dev/scripts/ui_debug_runner.py --module pixel_coin_game --mode both --gif-fps 48
```

## 缓存位置

所有基线和失败产物默认写入：

1. `.agent_cache/python-frontend-dev/<game_module>/baseline/`
2. `.agent_cache/python-frontend-dev/<game_module>/artifacts/`

## 失败产物

门禁失败时自动导出：

1. `backend.gif` 和逐帧 PNG。
2. `frontend.gif` 和逐帧 PNG。
3. `expected.json` 与 `current.json`，用于定位到底是后端状态还是前端事件链出现偏差。