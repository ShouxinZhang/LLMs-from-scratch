from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from torch.utils.data import Dataset

from pong_attention.expert.intercept_policy import InterceptExpert
from pong_attention.game.low_pong_env import LowPongEnv, Observation


ACTION_TO_INDEX = {-1: 0, 0: 1, 1: 2}
INDEX_TO_ACTION = {value: key for key, value in ACTION_TO_INDEX.items()}


@dataclass
class LowPongSample:
    obs_window: torch.Tensor
    valid_mask: torch.Tensor
    action_index: torch.Tensor
    intercept_target: torch.Tensor


def build_window(history: list[Observation], window_size: int) -> tuple[torch.Tensor, torch.Tensor]:
    obs_dim = 3
    obs_window = torch.zeros(window_size, obs_dim, dtype=torch.float32)
    valid_mask = torch.zeros(window_size, dtype=torch.bool)

    tail = history[-window_size:]
    start = window_size - len(tail)
    for offset, obs in enumerate(tail):
        index = start + offset
        obs_window[index] = torch.tensor(obs.as_vector(), dtype=torch.float32)
        valid_mask[index] = True
    return obs_window, valid_mask


class LowPongDataset(Dataset):
    def __init__(
        self,
        num_episodes: int,
        window_size: int,
        width: int = 6,
        height: int = 9,
        seed: int = 0,
    ) -> None:
        self.window_size = window_size
        self.samples = self._generate_samples(
            num_episodes=num_episodes,
            window_size=window_size,
            width=width,
            height=height,
            seed=seed,
        )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        sample = self.samples[index]
        return {
            "obs_window": sample.obs_window,
            "valid_mask": sample.valid_mask,
            "action_index": sample.action_index,
            "intercept_target": sample.intercept_target,
        }

    @staticmethod
    def collate(batch: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        keys = batch[0].keys()
        return {key: torch.stack([item[key] for item in batch], dim=0) for key in keys}

    def _generate_samples(
        self,
        num_episodes: int,
        window_size: int,
        width: int,
        height: int,
        seed: int,
    ) -> list[LowPongSample]:
        env = LowPongEnv(width=width, height=height, seed=seed)
        expert = InterceptExpert()
        samples: list[LowPongSample] = []

        for episode_seed in range(seed, seed + num_episodes):
            observation = env.reset(seed=episode_seed)
            history = [observation]
            done = False

            while not done:
                if len(history) < 2:
                    action = env.oracle_warmup_action()
                else:
                    expert_action = expert.act(history)
                    intercept_target = expert.predict_intercept(history)
                    obs_window, valid_mask = build_window(history, window_size)
                    samples.append(
                        LowPongSample(
                            obs_window=obs_window,
                            valid_mask=valid_mask,
                            action_index=torch.tensor(ACTION_TO_INDEX[expert_action], dtype=torch.long),
                            intercept_target=torch.tensor(float(intercept_target), dtype=torch.float32),
                        )
                    )
                    action = expert_action

                next_observation, _, done, _ = env.step(action)
                history.append(next_observation)

        return samples


def decode_action(action_index: torch.Tensor | int) -> int:
    if isinstance(action_index, torch.Tensor):
        action_index = int(action_index.item())
    return INDEX_TO_ACTION[action_index]
