---
name: sandbox-workmode
description: 当任务要求在 `.agents/sandbox/` 下隔离工作区时使用。适用于需要先按日期分组、再在当天目录下按“时间（精确到秒）+ task_name”创建任务目录，并将脚本/中间产物/最终结果集中写入该目录、尽量不污染仓库主目录的场景。
---

# Sandbox Workmode

当用户明确要求“本次任务在 `.agents/sandbox/` 下完成”时，使用这个技能。

## 核心规则

1. 先创建任务目录：

```bash
.agents/sandbox/YYYY-MM-DD/HH-MM-SS+task_name/
```

2. 本次任务新增的脚本、中间文件、统计结果、导出物，默认都写到该目录下。
3. 除非任务本身要求修改仓库正式内容，否则不要把实验性产物散落到仓库其他位置。
4. 目录内建议按用途分层，例如：

```text
output/    # 最终结果
scripts/   # 临时或复用脚本
logs/      # 按用户 prompt 分割的日志
tmp/       # 中间文件
```

例如：

```text
.agents/sandbox/2026-04-19/01-06-22+game-studio-zh/
  output/
  scripts/
  logs/
    01-06-30+translate-game-studio.md
    01-08-12+adjust-sandbox-layout.md
  tmp/
```

5. 任务结束后，给出 sandbox 根路径，并说明关键输出文件在哪里。
6. 同一个 sandbox 工作区内允许有多个日志文件；`logs/` 下的日志默认按用户 prompt 切分，而不是整次任务只保留一份总日志。

## 推荐流程

1. 用 `date '+%Y-%m-%d'` 生成日期目录，用 `date '+%H-%M-%S'` 生成当天任务时间戳。
2. `mkdir -p` 创建 `.agents/sandbox/<date>/<time>+<task_name>/`。
3. 所有新文件优先落到该目录。
4. 如果需要记录过程日志，在 `logs/` 下按用户 prompt 创建多个日志文件，建议命名为 `<time>+<prompt_slug>.md`。
5. 如有新增或修改文件，按 `workspace-docs` 要求更新文档说明。

## 注意

- `task_name` 用简短英文或短横线命名，避免空格。
- 推荐按天集中管理；同一天的 sandbox 任务都放在对应的日期目录下。
- `logs/` 不要求只有一个文件；同一工作区内可以按多次用户 prompt 连续追加多个日志文件。
- `prompt_slug` 应概括该次用户输入的意图，使用简短英文或短横线命名，避免空格；如果用户 prompt 很长，取核心动作即可。
- 如果任务需要读取仓库正式文件，可以读；但写入时优先写回 sandbox。
- 若最终确认产物需要正式入库，再从 sandbox 中挑选并迁移。
