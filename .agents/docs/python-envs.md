# Python Envs

原始问题：

> 在这个仓库里，除了公共 Python 环境之外，还需要安装哪些 `.venv`？

把这个问题拆开后，实际是在回答下面几个选择题。

## Q1. 主仓库根目录要不要有自己的 `.venv`？

答案：要。

推荐：

- `./.venv`

安装口径：

- 主仓库共享环境之外的全部依赖，一次性装完

## Q2. `reasoning-from-scratch/` 要不要单独有自己的 `.venv`？

答案：要。

推荐：

- `./reasoning-from-scratch/.venv`

安装口径：

- 子项目共享环境之外的全部依赖，一次性装完

## Q3. 其他章节目录要不要各自再建一个 `.venv`？

答案：不要。

默认不需要为这些目录单独建环境：

- `ch02/*`
- `ch03/*`
- `ch04/*`
- `ch05/*`
- `ch06/*`
- `ch07/*`
- `appendix-*`
- `pkg/llms_from_scratch`

它们默认复用根目录 `./.venv`。

## Q4. 公共环境要直接用默认的 `py314` 吗？

答案：不要。

推荐改用兼容这个仓库的共享环境，例如：

- `py313-torch-cu130`

## Q5. 什么情况下才值得再多建一个 `.venv`？

答案：只有两种常见情况。

1. 你明确想把 UI 工作流隔离出去
2. 你真的遇到了版本冲突

最可能涉及额外拆分的依赖：

- `chainlit`
- `transformers`
- `tokenizers`
- `safetensors`

## Q6. `.venv` 里的包是按需装，还是一次性装完？

答案：一次性装完。

这里不做“按需安装”策略。  
每个项目级 `.venv` 都直接安装“共享环境之外，这个项目需要的全部包”。

## Q7. 如果我不想继续想了，最简单的结论是什么？

答案：

1. 准备一个兼容的共享环境，例如 `py313-torch-cu130`
2. 创建 `./.venv`
3. 创建 `./reasoning-from-scratch/.venv`
4. `./.venv` 一次性安装主仓库全部非共享包
5. `./reasoning-from-scratch/.venv` 一次性安装子项目全部非共享包
6. 其他目录先不要再建新的 `.venv`

## 最终结论

除了公共 Python 环境之外，这个仓库默认只需要 2 个 `.venv`：

1. `./.venv`
2. `./reasoning-from-scratch/.venv`
