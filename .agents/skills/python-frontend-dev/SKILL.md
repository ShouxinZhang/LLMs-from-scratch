---
name: python-frontend-dev
description: 'Python 前端开发总技能：提供通用 references + 调度 scripts，按模块加载各游戏自己的 UI 调试与质量门禁脚本，并将缓存统一写入 .agent_cache。'
---

# Python Frontend Development Skill

该技能面向 Python GUI 项目，采用“通用技能调度器 + 模块内脚本”的结构：

1. `.agents/skills/python-frontend-dev/` 只保留通用方法论文档和调度入口。
2. 具体游戏的 UI 调试 / UI 质量门禁脚本放在对应模块自己的 `skills/scripts/` 下。
3. 缓存、基线和失败产物统一落到仓库根目录 `.agent_cache/`。

## 适用场景

1. 你希望把 GUI 开发从“事件回调堆积”改造成可维护模块。
2. 你希望 agent 能自动、精准地修改 UI，而不是“碰运气改代码”。
3. 你希望在现有后端门禁之外，加入前端可回归质量门禁。
4. 你希望同时跑后端模拟和前端事件模拟，快速区分问题在状态层还是 GUI 层。
5. 你希望导出高速 GIF 与逐帧 PNG，肉眼确认异常发生在哪一步。

## References

1. `references/dev-methodology.md`
2. `references/ui-quality-gate.md`
3. `references/ui-debug-simulation.md`

## Scripts

1. `scripts/ui_quality_gate.py`
2. `scripts/ui_debug_runner.py`

原先 `subskills/` 下的兼容内容已经收敛到这里的 `references/` 和 `scripts/`，不再保留独立子技能入口。

这两个脚本现在是通用调度器，不再内置任何特定游戏逻辑。

模块脚本约定：

1. `<game_module>/skills/scripts/ui_quality_gate.py`
2. `<game_module>/skills/scripts/ui_debug_runner.py`
3. `<game_module>/skills/scripts/ui_simulation.py`（可选内部复用模块）

## 快速执行

```bash
python3 .agents/skills/python-frontend-dev/scripts/ui_quality_gate.py --module pixel_coin_game --update-baseline
python3 .agents/skills/python-frontend-dev/scripts/ui_quality_gate.py --module pixel_coin_game
python3 .agents/skills/python-frontend-dev/scripts/ui_debug_runner.py --module pixel_coin_game --mode both --gif-fps 48
```

说明：
- 第 1 条命令用于创建/更新 UI 基线快照。
- 第 2 条命令用于日常门禁校验，发现回归会返回非 0。
- 第 3 条命令用于导出前后端两套复现场景的 GIF 与逐帧图片。
- 若仓库里只有一个实现了模块内 UI 脚本的游戏模块，可以省略 `--module`；若有多个模块，必须显式指定。
- 默认缓存目录：`.agent_cache/python-frontend-dev/<game_module>/`
