from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from pong_attention.data.dataset import LowPongDataset
from pong_attention.eval.evaluate import evaluate_action_policy
from pong_attention.eval.evaluate import evaluate_one_frame_baseline
from pong_attention.eval.evaluate import evaluate_rollout_catch_rate
from pong_attention.models.attention_policy import AttentionPolicy


def train(args: argparse.Namespace) -> dict[str, float]:
    device = torch.device(args.device)
    train_dataset = LowPongDataset(
        num_episodes=args.train_episodes,
        window_size=args.window_size,
        width=args.width,
        height=args.height,
        seed=args.seed,
    )
    val_dataset = LowPongDataset(
        num_episodes=args.val_episodes,
        window_size=args.window_size,
        width=args.width,
        height=args.height,
        seed=args.seed + 10_000,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=LowPongDataset.collate,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=LowPongDataset.collate,
    )

    model = AttentionPolicy(
        window_size=args.window_size,
        d_model=args.d_model,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        dropout=args.dropout,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    action_loss_fn = nn.CrossEntropyLoss()
    intercept_loss_fn = nn.MSELoss()
    best_metrics: dict[str, float] | None = None
    best_rollout = float("-inf")

    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0.0
        for batch in train_loader:
            obs_window = batch["obs_window"].to(device)
            valid_mask = batch["valid_mask"].to(device)
            action_index = batch["action_index"].to(device)
            intercept_target = batch["intercept_target"].to(device)

            outputs = model(obs_window, valid_mask=valid_mask, return_attn=False)
            loss_action = action_loss_fn(outputs["action_logits"], action_index)
            loss_intercept = intercept_loss_fn(outputs["intercept_pred"], intercept_target)
            loss = loss_action + args.intercept_weight * loss_intercept

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / max(len(train_loader), 1)
        print(f"epoch={epoch + 1} train_loss={avg_loss:.4f}")
        offline_metrics = evaluate_action_policy(model, val_loader, device=device)
        rollout_metrics = evaluate_rollout_catch_rate(
            model,
            num_episodes=args.rollout_episodes,
            window_size=args.window_size,
            width=args.width,
            height=args.height,
            seed=args.seed + 20_000,
            device=device,
        )
        epoch_metrics = {**offline_metrics, **rollout_metrics}
        print(json.dumps({"epoch": epoch + 1, **epoch_metrics}, indent=2))
        if epoch_metrics["rollout_catch_rate"] > best_rollout:
            best_rollout = epoch_metrics["rollout_catch_rate"]
            best_metrics = epoch_metrics

    metrics = best_metrics or evaluate_action_policy(model, val_loader, device=device)
    metrics["one_frame_baseline_accuracy"] = evaluate_one_frame_baseline(val_loader)["action_accuracy"]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_dir / "attention_policy.pt")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    return metrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-episodes", type=int, default=256)
    parser.add_argument("--val-episodes", type=int, default=64)
    parser.add_argument("--rollout-episodes", type=int, default=64)
    parser.add_argument("--window-size", type=int, default=3)
    parser.add_argument("--width", type=int, default=6)
    parser.add_argument("--height", type=int, default=9)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--d-model", type=int, default=48)
    parser.add_argument("--num-heads", type=int, default=2)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--intercept-weight", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--output-dir", type=str, default="tmp/train_run")
    return parser


if __name__ == "__main__":
    train(build_parser().parse_args())
