from __future__ import annotations

import argparse
from pathlib import Path

from pong_attention.gui.app import LowPongGUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Low-Pong attention GUI.")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=".agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/tmp/round1_run/attention_policy.pt",
    )
    parser.add_argument(
        "--metrics",
        type=str,
        default=".agents/sandbox/2026-04-17_00-04-16+pong-attention-docs/tmp/round1_run/metrics.json",
    )
    parser.add_argument("--width", type=int, default=6)
    parser.add_argument("--height", type=int, default=9)
    parser.add_argument("--window-size", type=int, default=3)
    parser.add_argument("--d-model", type=int, default=48)
    parser.add_argument("--num-heads", type=int, default=2)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    checkpoint = args.checkpoint
    if checkpoint and not Path(checkpoint).exists():
        print(f"warning: checkpoint not found, GUI will use random weights: {checkpoint}")
        checkpoint = None

    app = LowPongGUI(
        checkpoint_path=checkpoint,
        metrics_path=args.metrics,
        width=args.width,
        height=args.height,
        window_size=args.window_size,
        d_model=args.d_model,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        seed=args.seed,
    )
    app.run()


if __name__ == "__main__":
    main()
