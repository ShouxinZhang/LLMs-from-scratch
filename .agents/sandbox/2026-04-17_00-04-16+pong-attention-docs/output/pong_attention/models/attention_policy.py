from __future__ import annotations

import torch
from torch import nn

from pong_attention.models.causal_attention import AttentionBlock


class AttentionPolicy(nn.Module):
    def __init__(
        self,
        obs_dim: int = 3,
        window_size: int = 6,
        d_model: int = 48,
        num_heads: int = 2,
        num_layers: int = 2,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        self.window_size = window_size
        self.obs_proj = nn.Linear(obs_dim, d_model)
        self.pos_embed = nn.Parameter(torch.zeros(1, window_size, d_model))
        self.blocks = nn.ModuleList(
            [AttentionBlock(d_model=d_model, num_heads=num_heads, dropout=dropout) for _ in range(num_layers)]
        )
        self.final_norm = nn.LayerNorm(d_model)
        self.action_head = nn.Linear(2 * d_model, 3)
        self.intercept_head = nn.Sequential(
            nn.Linear(2 * d_model, d_model),
            nn.GELU(),
            nn.Linear(d_model, 1),
        )

    def forward(
        self,
        obs_window: torch.Tensor,
        valid_mask: torch.Tensor | None = None,
        return_attn: bool = False,
    ) -> dict[str, torch.Tensor]:
        batch_size, num_tokens, _ = obs_window.shape
        if num_tokens > self.window_size:
            raise ValueError(f"expected at most {self.window_size} tokens, got {num_tokens}")

        x = self.obs_proj(obs_window) + self.pos_embed[:, :num_tokens]
        attn_maps = []
        for block in self.blocks:
            x, attn = block(x, valid_mask=valid_mask, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_maps.append(attn)

        x = self.final_norm(x)
        last_indices = self._last_valid_indices(valid_mask=valid_mask, num_tokens=num_tokens, device=x.device, batch_size=batch_size)
        prev_indices = (last_indices - 1).clamp_min(0)

        batch_indices = torch.arange(batch_size, device=x.device)
        last_token = x[batch_indices, last_indices]
        prev_token = x[batch_indices, prev_indices]
        readout = torch.cat([prev_token, last_token], dim=-1)

        action_logits = self.action_head(readout)
        intercept_pred = self.intercept_head(readout).squeeze(-1)

        outputs = {
            "action_logits": action_logits,
            "intercept_pred": intercept_pred,
        }
        if return_attn:
            outputs["attn_maps"] = torch.stack(attn_maps, dim=1) if attn_maps else torch.empty(0)
        return outputs

    @staticmethod
    def _last_valid_indices(
        valid_mask: torch.Tensor | None,
        num_tokens: int,
        device: torch.device,
        batch_size: int,
    ) -> torch.Tensor:
        if valid_mask is None:
            return torch.full((batch_size,), num_tokens - 1, dtype=torch.long, device=device)
        positions = torch.arange(num_tokens, device=device).unsqueeze(0).expand(batch_size, -1)
        masked_positions = positions.masked_fill(~valid_mask, -1)
        return masked_positions.max(dim=1).values.clamp_min(0)
