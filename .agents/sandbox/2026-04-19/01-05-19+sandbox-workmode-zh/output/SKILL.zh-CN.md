---
name: sandbox-workmode
description: 当任务要求在 `.agents/sandbox/` 下隔离工作区时使用。适用于需要按“时间（精确到秒）+ task_name”创建任务目录、将脚本、中间产物和最终结果集中写入该目录、并尽量不污染仓库主目录的场景。
---

# Sandbox 隔离工作模式

当用户明确要求“本次任务在 `.agents/sandbox/` 下完成”时，使用这个技能。

## 核心规则

1. 先创建任务目录：

```bash
.agents/sandbox/YYYY-MM-DD_HH-MM-SS+task_name/
```

2. 本次任务新增的脚本、中间文件、统计结果和导出物，默认都写到该目录下。
3. 除非任务本身要求修改仓库正式内容，否则不要把实验性产物散落到仓库其他位置。
4. 目录内建议按用途分层，例如：

```text
output/    # 最终结果
scripts/   # 临时或可复用脚本
logs/      # 日志
tmp/       # 中间文件
```

5. 任务结束后，给出 sandbox 根路径，并说明关键输出文件的位置。

## 推荐流程

1. 用 `date '+%Y-%m-%d_%H-%M-%S'` 生成时间戳。
2. 用 `mkdir -p` 创建 `.agents/sandbox/<timestamp>+<task_name>/`。
3. 所有新文件优先写入该目录。
4. 如有新增或修改文件，按 `workspace-docs` 的要求更新文档说明。

## 注意事项

- `task_name` 使用简短英文名或短横线命名，避免空格。
- 如果任务需要读取仓库正式文件，可以读取；但写入时优先写回 sandbox。
- 若最终确认产物需要正式入库，再从 sandbox 中挑选并迁移。
