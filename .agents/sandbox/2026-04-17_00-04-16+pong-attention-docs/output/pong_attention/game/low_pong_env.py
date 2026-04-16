from __future__ import annotations

from dataclasses import dataclass
import random


def sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


@dataclass(frozen=True)
class State:
    x_ball: int
    y_ball: int
    v_ball: int
    y_paddle: int
    t: int


@dataclass(frozen=True)
class Observation:
    x_ball: int
    y_ball: int
    y_paddle: int
    t: int

    def as_vector(self) -> list[float]:
        return [float(self.x_ball), float(self.y_ball), float(self.y_paddle)]


class LowPongEnv:
    """A deterministic, no-bounce Pong variant aligned with the proof doc."""

    def __init__(self, width: int = 6, height: int = 9, seed: int | None = None) -> None:
        if width < 2:
            raise ValueError("width must be at least 2")
        if height < width + 1:
            raise ValueError("height must be at least width + 1 to support no-bounce trajectories")
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.state: State | None = None

    def reset(self, seed: int | None = None, state: State | None = None) -> Observation:
        if seed is not None:
            self._rng.seed(seed)
        self.state = state or self._sample_initial_state()
        return self.observe()

    def observe(self) -> Observation:
        if self.state is None:
            raise RuntimeError("env must be reset before use")
        return Observation(
            x_ball=self.state.x_ball,
            y_ball=self.state.y_ball,
            y_paddle=self.state.y_paddle,
            t=self.state.t,
        )

    def step(self, action: int) -> tuple[Observation, float, bool, dict]:
        if self.state is None:
            raise RuntimeError("env must be reset before stepping")
        if action not in (-1, 0, 1):
            raise ValueError("action must be one of -1, 0, +1")
        if self.state.x_ball <= 0:
            raise RuntimeError("episode already finished")

        next_paddle = min(max(self.state.y_paddle + action, 0), self.height - 1)
        next_x = self.state.x_ball - 1
        next_y = self.state.y_ball + self.state.v_ball

        next_state = State(
            x_ball=next_x,
            y_ball=next_y,
            v_ball=self.state.v_ball,
            y_paddle=next_paddle,
            t=self.state.t + 1,
        )
        self.state = next_state

        done = next_x == 0
        caught = done and next_paddle == next_y
        reward = 1.0 if caught else (-1.0 if done else 0.0)
        info = {"caught": caught}
        return self.observe(), reward, done, info

    def oracle_warmup_action(self) -> int:
        """Use hidden state once at t=0 so later supervised samples stay on-track."""
        if self.state is None:
            raise RuntimeError("env must be reset before use")
        intercept_y = self.compute_intercept_from_state(self.state)
        return sign(intercept_y - self.state.y_paddle)

    def compute_intercept_from_state(self, state: State | None = None) -> int:
        state = state or self.state
        if state is None:
            raise RuntimeError("env must be reset before use")
        return state.y_ball + state.x_ball * state.v_ball

    def _sample_initial_state(self) -> State:
        x_ball = self.width
        v_ball = self._rng.choice([-1, 1])
        if v_ball == 1:
            y_ball = self._rng.randint(0, self.height - 1 - self.width)
        else:
            y_ball = self._rng.randint(self.width, self.height - 1)

        intercept_y = y_ball + x_ball * v_ball
        low = max(0, intercept_y - x_ball)
        high = min(self.height - 1, intercept_y + x_ball)
        y_paddle = self._rng.randint(low, high)
        return State(x_ball=x_ball, y_ball=y_ball, v_ball=v_ball, y_paddle=y_paddle, t=0)
