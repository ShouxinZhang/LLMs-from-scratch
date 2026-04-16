from __future__ import annotations

from typing import Sequence

from pong_attention.game.low_pong_env import Observation, sign


class InterceptExpert:
    """Optimal policy for the no-bounce Low-Pong variant."""

    def act(self, history: Sequence[Observation]) -> int:
        if len(history) < 2:
            raise ValueError("expert policy requires at least two observations")
        intercept_y = self.predict_intercept(history)
        current = history[-1]
        return sign(intercept_y - current.y_paddle)

    def predict_intercept(self, history: Sequence[Observation]) -> int:
        if len(history) < 2:
            raise ValueError("expert policy requires at least two observations")
        current = history[-1]
        previous = history[-2]
        velocity = current.y_ball - previous.y_ball
        if velocity not in (-1, 1):
            raise ValueError(f"expected velocity in {{-1, +1}}, got {velocity}")
        return current.y_ball + current.x_ball * velocity
