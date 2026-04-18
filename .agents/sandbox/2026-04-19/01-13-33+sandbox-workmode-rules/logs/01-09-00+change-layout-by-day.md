# 用户原始 prompt

Hmm? let me think
我觉得，sandbox技能直接按照具体的分钟来划分，不利于集中管理
对，按照天来分割储存，同一天的放在同一个文件路径下

# 精简理解

把 `sandbox-workmode` 的目录规范改成按天分组，再在当天目录下存放具体任务目录。

# 实际执行动作

- 修改 `.agents/skills/sandbox-workmode/SKILL.md`。
- 将目录格式从 `.agents/sandbox/YYYY-MM-DD_HH-MM-SS+task_name/` 改为 `.agents/sandbox/YYYY-MM-DD/HH-MM-SS+task_name/`。
- 同步更新 `description`、核心规则、推荐流程和注意事项。

# 相关文件

- `.agents/skills/sandbox-workmode/SKILL.md`
