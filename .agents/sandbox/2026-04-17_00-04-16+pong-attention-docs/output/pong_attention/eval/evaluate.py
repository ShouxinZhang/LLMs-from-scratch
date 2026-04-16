from __future__ import annotations

from typing import Any

import torch
from torch.utils.data import DataLoader

from pong_attention.data.dataset import ACTION_TO_INDEX
from pong_attention.data.dataset import build_window
from pong_attention.game.low_pong_env import LowPongEnv
from pong_attention.game.low_pong_env import sign


@torch.no_grad()
def evaluate_action_policy(model, dataloader: DataLoader, device: torch.device | str = "cpu") -> dict[str, float]:
    model.eval()
    device = torch.device(device)
    total = 0
    correct = 0
    intercept_mse = 0.0

    attn_last_two_mass = []
    for batch in dataloader:
        obs_window = batch["obs_window"].to(device)
        valid_mask = batch["valid_mask"].to(device)
        action_index = batch["action_index"].to(device)
        intercept_target = batch["intercept_target"].to(device)

        outputs = model(obs_window, valid_mask=valid_mask, return_attn=True)
        pred_action = outputs["action_logits"].argmax(dim=-1)

        total += action_index.numel()
        correct += (pred_action == action_index).sum().item()
        intercept_mse += torch.mean((outputs["intercept_pred"] - intercept_target) ** 2).item() * action_index.shape[0]

        attn_maps = outputs.get("attn_maps")
        if attn_maps is not None and attn_maps.numel() > 0:
            final_layer = attn_maps[:, -1]  # [B, heads, T, T]
            for batch_index in range(final_layer.shape[0]):
                valid_len = int(valid_mask[batch_index].sum().item())
                if valid_len < 2:
                    continue
                last_query = valid_len - 1
                weights = final_layer[batch_index, :, last_query, :valid_len]
                attn_last_two_mass.append(weights[:, max(valid_len - 2, 0) : valid_len].sum(dim=-1).mean().item())

    return {
        "action_accuracy": correct / max(total, 1),
        "intercept_mse": intercept_mse / max(total, 1),
        "attn_last_two_mass": sum(attn_last_two_mass) / max(len(attn_last_two_mass), 1),
    }


def one_frame_baseline_action(obs_window: torch.Tensor, valid_mask: torch.Tensor) -> torch.Tensor:
    batch_actions = []
    for obs_seq, mask in zip(obs_window, valid_mask, strict=True):
        valid_len = int(mask.sum().item())
        current = obs_seq[valid_len - 1]
        y_ball = int(round(current[1].item()))
        y_paddle = int(round(current[2].item()))
        batch_actions.append(ACTION_TO_INDEX[sign(y_ball - y_paddle)])
    return torch.tensor(batch_actions, dtype=torch.long)


@torch.no_grad()
def evaluate_one_frame_baseline(dataloader: DataLoader) -> dict[str, float]:
    total = 0
    correct = 0
    for batch in dataloader:
        pred = one_frame_baseline_action(batch["obs_window"], batch["valid_mask"])
        target = batch["action_index"]
        total += target.numel()
        correct += (pred == target).sum().item()
    return {"action_accuracy": correct / max(total, 1)}


@torch.no_grad()
def evaluate_rollout_catch_rate(
    model,
    num_episodes: int,
    window_size: int,
    width: int,
    height: int,
    seed: int,
    device: torch.device | str = "cpu",
) -> dict[str, float]:
    model.eval()
    device = torch.device(device)
    env = LowPongEnv(width=width, height=height, seed=seed)

    caught = 0
    for episode_seed in range(seed, seed + num_episodes):
        observation = env.reset(seed=episode_seed)
        history = [observation]

        # Bootstrap one step to reach the t >= 1 regime where the proof-defined policy applies.
        next_observation, _, done, info = env.step(env.oracle_warmup_action())
        history.append(next_observation)
        if done:
            caught += int(info["caught"])
            continue

        while True:
            obs_window, valid_mask = build_window(history, window_size)
            obs_window = obs_window.unsqueeze(0).to(device)
            valid_mask = valid_mask.unsqueeze(0).to(device)
            outputs = model(obs_window, valid_mask=valid_mask, return_attn=False)
            action_index = outputs["action_logits"].argmax(dim=-1).item()
            action = [-1, 0, 1][action_index]
            next_observation, _, done, info = env.step(action)
            history.append(next_observation)
            if done:
                caught += int(info["caught"])
                break

    return {"rollout_catch_rate": caught / max(num_episodes, 1)}
