# 用户原始 prompt

why you not do logs?
是因为SKILL里没有明确指定吗？
理论上，logs按照用户的prompts进行分割
也就是，同一个sandbox工作区内，允许多个logs, 按照用户prompts进行分割

# 精简理解

把 `sandbox-workmode` 的日志规则补充完整，明确 `logs/` 按用户 prompt 分割，同一工作区允许有多份日志。

# 实际执行动作

- 修改 `.agents/skills/sandbox-workmode/SKILL.md` 中对 `logs/` 的说明。
- 增加“同一 sandbox 工作区允许多个日志文件”的规则。
- 增加日志命名建议 `<time>+<prompt_slug>.md`。
- 增加一个按 prompt 分割日志的目录示例。

# 相关文件

- `.agents/skills/sandbox-workmode/SKILL.md`
