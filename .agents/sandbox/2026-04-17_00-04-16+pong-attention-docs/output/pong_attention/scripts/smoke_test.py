from __future__ import annotations

import json

import torch
from torch.utils.data import DataLoader

from pong_attention.data.dataset import LowPongDataset
from pong_attention.eval.evaluate import evaluate_action_policy
from pong_attention.models.attention_policy import AttentionPolicy


def main() -> None:
    dataset = LowPongDataset(num_episodes=32, window_size=3, width=6, height=9, seed=123)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True, collate_fn=LowPongDataset.collate)

    model = AttentionPolicy(window_size=3, d_model=32, num_heads=2, num_layers=2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    criterion_action = torch.nn.CrossEntropyLoss()
    criterion_intercept = torch.nn.MSELoss()

    batch = next(iter(dataloader))
    outputs = model(batch["obs_window"], valid_mask=batch["valid_mask"], return_attn=True)
    loss = criterion_action(outputs["action_logits"], batch["action_index"])
    loss = loss + 0.1 * criterion_intercept(outputs["intercept_pred"], batch["intercept_target"])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    metrics = evaluate_action_policy(model, dataloader, device="cpu")
    summary = {
        "num_samples": len(dataset),
        "batch_loss": float(loss.item()),
        **metrics,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
