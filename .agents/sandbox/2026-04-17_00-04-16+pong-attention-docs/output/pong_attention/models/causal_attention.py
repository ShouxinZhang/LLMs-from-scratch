from __future__ import annotations

import math

import torch
from torch import nn


class CausalMultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.0, qkv_bias: bool = False) -> None:
        super().__init__()
        if d_model % num_heads != 0:
            raise ValueError("d_model must be divisible by num_heads")
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.q_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
        self.k_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
        self.v_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        valid_mask: torch.Tensor | None = None,
        return_attn: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        batch_size, num_tokens, _ = x.shape

        q = self.q_proj(x).view(batch_size, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)

        attn_scores = q @ k.transpose(-2, -1)
        attn_scores = attn_scores / math.sqrt(self.head_dim)

        causal_mask = torch.triu(
            torch.ones(num_tokens, num_tokens, dtype=torch.bool, device=x.device),
            diagonal=1,
        )
        attn_scores = attn_scores.masked_fill(causal_mask, float("-inf"))

        if valid_mask is not None:
            key_padding_mask = ~valid_mask[:, None, None, :]
            attn_scores = attn_scores.masked_fill(key_padding_mask, float("-inf"))

        attn_weights = torch.softmax(attn_scores, dim=-1)
        attn_weights = torch.nan_to_num(attn_weights, nan=0.0, posinf=0.0, neginf=0.0)
        attn_weights = self.dropout(attn_weights)

        context = attn_weights @ v
        context = context.transpose(1, 2).contiguous().view(batch_size, num_tokens, self.d_model)
        context = self.out_proj(context)

        if valid_mask is not None:
            context = context * valid_mask.unsqueeze(-1)

        return context, attn_weights if return_attn else None


class AttentionBlock(nn.Module):
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.0) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.attn = CausalMultiHeadAttention(d_model=d_model, num_heads=num_heads, dropout=dropout)
        self.norm2 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model),
            nn.Dropout(dropout),
        )

    def forward(
        self,
        x: torch.Tensor,
        valid_mask: torch.Tensor | None = None,
        return_attn: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        attn_out, attn_weights = self.attn(self.norm1(x), valid_mask=valid_mask, return_attn=return_attn)
        x = x + attn_out
        x = x + self.ff(self.norm2(x))
        if valid_mask is not None:
            x = x * valid_mask.unsqueeze(-1)
        return x, attn_weights
