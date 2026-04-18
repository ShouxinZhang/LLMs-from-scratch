from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import torch

from pong_attention.data.dataset import INDEX_TO_ACTION
from pong_attention.data.dataset import build_window
from pong_attention.expert.intercept_policy import InterceptExpert
from pong_attention.game.low_pong_env import LowPongEnv


@dataclass
class PolicySnapshot:
    action: int
    action_name: str
    intercept: float | None
    logits: list[float]
    attn_weights: list[float]


@dataclass
class DashboardState:
    current_t: int
    current_x: int
    current_y: int
    paddle_y: int
    prev_y: int | None
    derived_velocity: int | None
    expert: PolicySnapshot
    model: PolicySnapshot
    history_lines: list[str]
    formula_lines: list[str]
    summary_lines: list[str]
    metrics_lines: list[str]
    done: bool
    caught: bool


def action_name(action: int) -> str:
    return {-1: "up", 0: "stay", 1: "down"}.get(action, "unknown")


def evaluate_model_history(model, history, window_size: int, device: torch.device) -> PolicySnapshot:
    if len(history) < 2:
        return PolicySnapshot(
            action=0,
            action_name="warmup",
            intercept=None,
            logits=[0.0, 0.0, 0.0],
            attn_weights=[],
        )

    obs_window, valid_mask = build_window(history, window_size)
    obs_window = obs_window.unsqueeze(0).to(device)
    valid_mask = valid_mask.unsqueeze(0).to(device)
    outputs = model(obs_window, valid_mask=valid_mask, return_attn=True)

    logits = outputs["action_logits"][0].detach().cpu().tolist()
    action_index = int(outputs["action_logits"].argmax(dim=-1).item())
    action = INDEX_TO_ACTION[action_index]
    intercept = float(outputs["intercept_pred"].item())

    attn_weights: list[float] = []
    attn_maps = outputs.get("attn_maps")
    if attn_maps is not None and attn_maps.numel() > 0:
        final_layer = attn_maps[0, -1]
        valid_len = int(valid_mask[0].sum().item())
        last_query = valid_len - 1
        attn_weights = final_layer[:, last_query, :valid_len].mean(dim=0).detach().cpu().tolist()

    return PolicySnapshot(
        action=action,
        action_name=action_name(action),
        intercept=intercept,
        logits=logits,
        attn_weights=attn_weights,
    )


def evaluate_expert_history(expert: InterceptExpert, env: LowPongEnv, history) -> PolicySnapshot:
    if len(history) < 2:
        warmup_action = env.oracle_warmup_action()
        return PolicySnapshot(
            action=warmup_action,
            action_name=f"warmup/{action_name(warmup_action)}",
            intercept=None,
            logits=[],
            attn_weights=[],
        )
    action = expert.act(history)
    intercept = float(expert.predict_intercept(history))
    return PolicySnapshot(
        action=action,
        action_name=action_name(action),
        intercept=intercept,
        logits=[],
        attn_weights=[],
    )


def load_metrics_lines(metrics_path: str | None) -> list[str]:
    if not metrics_path:
        return ["metrics: none"]
    path = Path(metrics_path)
    if not path.exists():
        return [f"metrics: missing ({metrics_path})"]
    data = json.loads(path.read_text())
    ordered = [
        ("rollout_catch_rate", data.get("rollout_catch_rate")),
        ("action_accuracy", data.get("action_accuracy")),
        ("one_frame_baseline_accuracy", data.get("one_frame_baseline_accuracy")),
        ("attn_last_two_mass", data.get("attn_last_two_mass")),
    ]
    return [f"{key} = {value:.6f}" for key, value in ordered if isinstance(value, (int, float))]


def build_dashboard_state(
    env: LowPongEnv,
    expert: InterceptExpert,
    model,
    history,
    window_size: int,
    device: torch.device,
    metrics_path: str | None,
    model_loaded: bool,
    last_step_source: str,
    last_reward: float,
    done: bool,
    info: dict,
) -> DashboardState:
    state = env.state
    if state is None:
        raise RuntimeError("environment is not initialized")

    prev_y = history[-2].y_ball if len(history) >= 2 else None
    derived_velocity = state.y_ball - prev_y if prev_y is not None else None
    expert_snapshot = evaluate_expert_history(expert, env, history)
    model_snapshot = evaluate_model_history(model, history, window_size=window_size, device=device)

    if prev_y is None:
        formula_lines = [
            "Need two frames before the proof-defined policy exists.",
            "Warmup step uses oracle action once to enter the t >= 1 regime.",
        ]
    else:
        expert_intercept = expert_snapshot.intercept
        formula_lines = [
            f"v = y_t - y_(t-1) = {state.y_ball} - {prev_y} = {derived_velocity}",
            f"y_hit = y_t + x_t * v = {state.y_ball} + {state.x_ball} * {derived_velocity} = {expert_intercept:.0f}",
            f"action = sign(y_hit - p_t) = sign({expert_intercept:.0f} - {state.y_paddle}) = {expert_snapshot.action_name}",
        ]

    history_lines = [
        f"obs[t-{len(history) - 1 - idx}]  x={obs.x_ball}  y={obs.y_ball}  p={obs.y_paddle}  t={obs.t}"
        for idx, obs in enumerate(history[-window_size:])
    ]

    summary_lines = [
        f"checkpoint_loaded = {model_loaded}",
        f"last_step_source = {last_step_source}",
        f"reward = {last_reward:.1f}",
        f"done = {done}",
        f"caught = {info.get('caught', False)}",
        f"window_size = {window_size}",
    ]

    return DashboardState(
        current_t=state.t,
        current_x=state.x_ball,
        current_y=state.y_ball,
        paddle_y=state.y_paddle,
        prev_y=prev_y,
        derived_velocity=derived_velocity,
        expert=expert_snapshot,
        model=model_snapshot,
        history_lines=history_lines,
        formula_lines=formula_lines,
        summary_lines=summary_lines,
        metrics_lines=load_metrics_lines(metrics_path),
        done=done,
        caught=bool(info.get("caught", False)),
    )
