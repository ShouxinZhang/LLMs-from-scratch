# Pong Attention Docs

本目录只保留业务验收需要的最小文档。

文件：

- `architecture.md`
  - 未来代码最小模块边界
- `problem-set.md`
  - 需要被回答的核心问题
- `proof.md`
  - attention 可解性的严格证明

当前证明只覆盖一个最小 `Low-Pong`：

- 离散时间
- 单球、单挡板
- 水平速度固定向左
- 纵向速度只取 `-1` 或 `+1`
- 不考虑顶底反弹
- 当前动作只能看过去历史

这个版本已经足够说明三件事：

1. 当前帧不够
2. 两帧历史足够
3. causal attention 可以精确实现最优动作
