# 实验日志

## 任务

在 sandbox 内实现最小 `Low-Pong` attention 项目，并按轮次改进直到准确率通过验收阈值。

约束：

- 每轮先由 4 个无记忆 subagents 审查
- 主 agent 汇总后亲自改代码
- 禁止 reward hack
- 若主指标 `acc > 90%`，立即停止

## 初始 build 状态

最小闭环已打通：

- 环境：`game/low_pong_env.py`
- 专家策略：`expert/intercept_policy.py`
- 数据集：`data/dataset.py`
- attention 模型：`models/causal_attention.py` + `models/attention_policy.py`
- 训练入口：`train/train_imitation.py`
- 评测入口：`eval/evaluate.py`
- smoke test：`scripts/smoke_test.py`

初始小训练结果：

- `action_accuracy = 0.5125`
- `intercept_mse = 16.0076`
- `attn_last_two_mass = 0.3681`

初始 one-frame baseline：

- `action_accuracy = 0.171875`

问题：

1. 评测只看离线动作准确率，不看真实 rollout 成功率
2. 模型 readout 读取错了右对齐窗口中的 token
3. 默认窗口长度过大，和证明所需历史不匹配
4. `intercept` 辅助目标被直接加进主损失，存在 reward hack 风险
5. 环境 `info` 暴露了隐藏状态派生量

## Round 1: 4 个 subagents 审查摘要

### 审查结论

1. 模型硬 bug
   - `AttentionPolicy` 在右对齐窗口下使用 `sum(valid_mask)-1` 取最后 token，导致经常读到 padding，而不是当前帧。
2. 结构不匹配证明
   - 当前最优策略只依赖最后两帧，但模型 readout 没有显式使用这两个 token。
3. 评测不可信
   - 原评测只做 teacher-forced offline accuracy，没有 rollout catch rate。
4. 数据和默认配置不合理
   - 默认 `window_size=6` 引入过多无关 padding；
   - 该任务只需要最后两帧附近信息。
5. anti-reward-hack 风险
   - `intercept` 目标应作为诊断量，不应默认作为主损失的一部分。

### 采用的修改项

1. 修正 readout 取 token 的逻辑
2. 把 readout 改成显式拼接 `prev_token` 和 `last_token`
3. 默认 `window_size` 改为 `3`
4. 默认 `intercept_weight` 改为 `0.0`
5. 新增 rollout catch rate 评测
6. 新增 one-frame baseline 汇总进最终指标
7. 去掉环境 `info` 中的隐藏状态派生量

### 未采用项

- 没有直接把任务改成“显式监督拦截点主任务”
- 没有增加任何利用隐藏状态的 shortcut
- 没有为冲高指标而改动任务定义

## Round 1 实际修改文件

- `output/pong_attention/game/low_pong_env.py`
- `output/pong_attention/models/attention_policy.py`
- `output/pong_attention/eval/evaluate.py`
- `output/pong_attention/train/train_imitation.py`
- `output/pong_attention/scripts/smoke_test.py`

## Round 1 关键命令

### smoke test

```bash
PYTHONPATH=.agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/output \
  .agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/.venv/bin/python \
  -m pong_attention.scripts.smoke_test
```

### 训练与评测

```bash
PYTHONPATH=.agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/output \
  .agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/.venv/bin/python \
  -m pong_attention.train.train_imitation \
  --train-episodes 256 \
  --val-episodes 64 \
  --rollout-episodes 64 \
  --epochs 8 \
  --batch-size 32 \
  --window-size 3 \
  --output-dir .agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/tmp/round1_run
```

## Round 1 结果

最终指标：

- `action_accuracy = 0.984375`
- `intercept_mse = 29.383534812927245`
- `attn_last_two_mass = 0.4828485704889317`
- `rollout_catch_rate = 0.921875`
- `one_frame_baseline_accuracy = 0.015625`

解释：

- 离线动作准确率已经超过 90%
- 更重要的是 `rollout_catch_rate` 也超过 90%
- one-frame baseline 极低，说明模型确实依赖历史而不是当前帧 shortcut
- `attn_last_two_mass` 不是特别高，但主控制表现已经过验收阈值

## 停止条件

本轮已经满足：

- `action_accuracy > 90%`
- `rollout_catch_rate > 90%`

因此按规则停止，不再进入 Round 2。

## 产物位置

代码：

- `output/pong_attention/`

训练结果：

- `tmp/round1_run/attention_policy.pt`
- `tmp/round1_run/metrics.json`
