# Low-Pong 最小模块架构

## 1. 任务

输入过去若干帧观测：

- `x_ball`
- `y_ball`
- `y_paddle`

输出当前动作：

- `-1`
- `0`
- `+1`

注意：

- 不直接给球的纵向速度
- 策略必须 causal
- 证明版专家策略从 `t >= 1` 才有定义

## 2. 最小目录

```text
pong_attention/
├── game/
│   └── low_pong_env.py
├── expert/
│   └── intercept_policy.py
├── data/
│   └── dataset.py
├── models/
│   ├── causal_attention.py
│   └── attention_policy.py
├── train/
│   └── train_imitation.py
├── eval/
│   └── evaluate.py
└── docs/
    ├── architecture.md
    ├── problem-set.md
    └── proof.md
```

## 3. 模块职责

### `game/low_pong_env.py`

只负责环境状态转移。

最小对象：

- `State = (x_t, y_t, v, p_t)`
- `Observation = (x_t, y_t, p_t)`
- `Action ∈ {-1, 0, +1}`

### `expert/intercept_policy.py`

只负责实现证明里的最优策略：

\[
\pi^\star(h_t)=\operatorname{sgn}(y_t + x_t(y_t-y_{t-1}) - p_t).
\]

### `data/dataset.py`

把轨迹转成训练样本：

- `obs_window`
- `action`
- `target_intercept`

其中 `target_intercept` 是为了检查模型到底是在学控制，还是在恢复拦截点。

### `models/causal_attention.py`

只实现第 3 章的 attention 模块：

- Q / K / V
- causal mask
- single-head / multi-head

### `models/attention_policy.py`

顶层策略网络：

- 输入历史窗口
- 输出动作 logits
- 可选输出 attention map

### `train/train_imitation.py`

第一阶段只做 imitation learning，不做 RL。

### `eval/evaluate.py`

至少评估：

- 动作准确率
- 最终挡球成功率
- attention 是否聚焦在最后两帧

## 4. 验收重点

业务验收只看三件事：

1. 单帧 baseline 必须失败
2. 两帧或 attention 模型必须成功
3. attention 权重必须主要落在最后两帧
