from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path

import torch

from pong_attention.expert.intercept_policy import InterceptExpert
from pong_attention.game.low_pong_env import LowPongEnv
from pong_attention.models.attention_policy import AttentionPolicy
from pong_attention.gui import theme
from pong_attention.gui.viewmodel import build_dashboard_state


class LowPongGUI:
    def __init__(
        self,
        checkpoint_path: str | None = None,
        metrics_path: str | None = None,
        width: int = 6,
        height: int = 9,
        window_size: int = 3,
        d_model: int = 48,
        num_heads: int = 2,
        num_layers: int = 2,
        seed: int = 7,
    ) -> None:
        self.width = width
        self.height = height
        self.window_size = window_size
        self.seed = seed
        self.metrics_path = metrics_path
        self.env = LowPongEnv(width=width, height=height, seed=seed)
        self.expert = InterceptExpert()
        self.device = torch.device("cpu")
        self.model = AttentionPolicy(
            window_size=window_size,
            d_model=d_model,
            num_heads=num_heads,
            num_layers=num_layers,
        ).to(self.device)
        self.model.eval()
        self.checkpoint_path = checkpoint_path
        self.model_loaded = False
        self._load_checkpoint()

        self.history = []
        self.last_step_source = "none"
        self.last_reward = 0.0
        self.last_done = False
        self.last_info = {"caught": False}
        self.autoplay_job: str | None = None
        self.autoplay_source = "model"
        self.dashboard = None

        self.root = tk.Tk()
        self.root.title("Low-Pong Attention Studio")
        self.root.geometry("1440x920")
        self.root.configure(bg=theme.WINDOW_BG)
        self._configure_styles()

        self.seed_var = tk.StringVar(value=str(seed))
        self.speed_var = tk.IntVar(value=260)

        self._build_layout()
        self.reset_episode()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.configure("Panel.TFrame", background=theme.PANEL_BG)
        style.configure("PanelAlt.TFrame", background=theme.PANEL_ALT)
        style.configure("Panel.TLabelframe", background=theme.PANEL_BG)
        style.configure("Panel.TLabelframe.Label", background=theme.PANEL_BG, foreground=theme.TEXT, font=theme.SECTION_FONT)
        style.configure("PanelAlt.TLabelframe", background=theme.PANEL_ALT)
        style.configure("PanelAlt.TLabelframe.Label", background=theme.PANEL_ALT, foreground=theme.TEXT, font=theme.SECTION_FONT)
        style.configure("Body.TLabel", background=theme.PANEL_BG, foreground=theme.TEXT, font=theme.BODY_FONT)
        style.configure("Muted.TLabel", background=theme.PANEL_BG, foreground=theme.MUTED, font=theme.BODY_FONT)
        style.configure("Card.TLabel", background=theme.PANEL_ALT, foreground=theme.TEXT, font=theme.BODY_FONT)

    def _load_checkpoint(self) -> None:
        if not self.checkpoint_path:
            return
        checkpoint = Path(self.checkpoint_path)
        if not checkpoint.exists():
            return
        state_dict = torch.load(checkpoint, map_location="cpu")
        self.model.load_state_dict(state_dict)
        self.model_loaded = True

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="Panel.TFrame", padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            container,
            text="Low-Pong Attention Studio",
            bg=theme.WINDOW_BG,
            fg=theme.TEXT,
            font=theme.TITLE_FONT,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            container,
            text="Observe the state, derive the proof rule, compare expert vs model, then inspect which frames attention reads.",
            bg=theme.WINDOW_BG,
            fg=theme.MUTED,
            font=theme.BODY_FONT,
        )
        subtitle.pack(anchor="w", pady=(2, 12))

        content = ttk.Frame(container, style="Panel.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(content, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = ttk.Frame(content, style="Panel.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0))

        controls = ttk.LabelFrame(left, text="Controls", style="Panel.TLabelframe", padding=10)
        controls.pack(fill=tk.X)
        ttk.Label(controls, text="Seed", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.seed_var, width=8).grid(row=0, column=1, padx=(8, 18))
        ttk.Label(controls, text="Auto ms", style="Body.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Scale(controls, variable=self.speed_var, from_=80, to=800, orient=tk.HORIZONTAL).grid(row=0, column=3, padx=(8, 0), sticky="ew")
        controls.columnconfigure(3, weight=1)

        button_row = ttk.Frame(controls, style="Panel.TFrame")
        button_row.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")
        for label, command in [
            ("Reset", self.reset_episode),
            ("Step Model", lambda: self.step_episode("model")),
            ("Step Expert", lambda: self.step_episode("expert")),
            ("Auto Model", lambda: self.start_autoplay("model")),
            ("Auto Expert", lambda: self.start_autoplay("expert")),
            ("Stop", self.stop_autoplay),
        ]:
            ttk.Button(button_row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 8))

        board_frame = ttk.LabelFrame(left, text="Game Board", style="Panel.TLabelframe", padding=10)
        board_frame.pack(fill=tk.BOTH, expand=False, pady=(14, 0))
        self.board_canvas = tk.Canvas(
            board_frame,
            width=theme.BOARD_WIDTH,
            height=theme.BOARD_HEIGHT,
            bg=theme.PANEL_BG,
            highlightthickness=0,
        )
        self.board_canvas.pack()

        history_frame = ttk.LabelFrame(left, text="History Strip", style="Panel.TLabelframe", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=False, pady=(14, 0))
        self.history_canvas = tk.Canvas(
            history_frame,
            width=theme.BOARD_WIDTH,
            height=theme.HISTORY_HEIGHT,
            bg=theme.PANEL_BG,
            highlightthickness=0,
        )
        self.history_canvas.pack()

        top_right = ttk.Frame(right, style="Panel.TFrame")
        top_right.pack(fill=tk.X)

        self.summary_text = tk.Text(top_right, height=7, bg=theme.PANEL_BG, fg=theme.TEXT, bd=0, highlightthickness=0, font=theme.MONO_FONT)
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.metrics_text = tk.Text(top_right, height=7, bg=theme.PANEL_ALT, fg=theme.TEXT, bd=0, highlightthickness=0, font=theme.MONO_FONT)
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        compare_row = ttk.Frame(right, style="Panel.TFrame")
        compare_row.pack(fill=tk.X, pady=(14, 0))

        self.expert_card = self._build_text_card(compare_row, "Expert Decision", style="Panel.TLabelframe")
        self.expert_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.model_card = self._build_text_card(compare_row, "Model Decision", style="PanelAlt.TLabelframe")
        self.model_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        formula_frame = ttk.LabelFrame(right, text="Proof Trace", style="Panel.TLabelframe", padding=10)
        formula_frame.pack(fill=tk.X, pady=(14, 0))
        self.formula_text = tk.Text(formula_frame, height=5, bg=theme.PANEL_BG, fg=theme.TEXT, bd=0, highlightthickness=0, font=theme.MONO_FONT)
        self.formula_text.pack(fill=tk.BOTH, expand=True)

        attn_frame = ttk.LabelFrame(right, text="Attention Heat", style="Panel.TLabelframe", padding=10)
        attn_frame.pack(fill=tk.BOTH, expand=False, pady=(14, 0))
        self.attn_canvas = tk.Canvas(attn_frame, width=760, height=theme.ATTN_HEIGHT, bg=theme.PANEL_BG, highlightthickness=0)
        self.attn_canvas.pack(fill=tk.BOTH, expand=True)

        logits_frame = ttk.LabelFrame(right, text="Action Logits", style="Panel.TLabelframe", padding=10)
        logits_frame.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        self.logits_canvas = tk.Canvas(logits_frame, width=760, height=theme.LOGITS_HEIGHT, bg=theme.PANEL_BG, highlightthickness=0)
        self.logits_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_text_card(self, parent, title: str, style: str):
        frame = ttk.LabelFrame(parent, text=title, style=style, padding=10)
        text = tk.Text(frame, height=8, bg=theme.PANEL_BG if style == "Panel.TLabelframe" else theme.PANEL_ALT, fg=theme.TEXT, bd=0, highlightthickness=0, font=theme.MONO_FONT)
        text.pack(fill=tk.BOTH, expand=True)
        frame.text_widget = text  # type: ignore[attr-defined]
        return frame

    def reset_episode(self) -> None:
        self.stop_autoplay()
        try:
            seed = int(self.seed_var.get())
        except ValueError:
            seed = self.seed
            self.seed_var.set(str(seed))
        observation = self.env.reset(seed=seed)
        self.history = [observation]
        self.last_step_source = "reset"
        self.last_reward = 0.0
        self.last_done = False
        self.last_info = {"caught": False}
        self._refresh()

    def start_autoplay(self, source: str) -> None:
        self.stop_autoplay()
        self.autoplay_source = source
        self._autoplay_once()

    def _autoplay_once(self) -> None:
        if self.last_done:
            return
        self.step_episode(self.autoplay_source)
        if not self.last_done:
            self.autoplay_job = self.root.after(max(self.speed_var.get(), 40), self._autoplay_once)

    def stop_autoplay(self) -> None:
        if self.autoplay_job is not None:
            self.root.after_cancel(self.autoplay_job)
            self.autoplay_job = None

    def step_episode(self, source: str) -> None:
        if self.last_done:
            return
        if len(self.history) < 2:
            action = self.env.oracle_warmup_action()
            self.last_step_source = f"{source} (warmup)"
        elif source == "expert":
            action = self.expert.act(self.history)
            self.last_step_source = "expert"
        else:
            self.last_step_source = "model"
            action = build_dashboard_state(
                env=self.env,
                expert=self.expert,
                model=self.model,
                history=self.history,
                window_size=self.window_size,
                device=self.device,
                metrics_path=self.metrics_path,
                model_loaded=self.model_loaded,
                last_step_source=self.last_step_source,
                last_reward=self.last_reward,
                done=self.last_done,
                info=self.last_info,
            ).model.action
        next_observation, reward, done, info = self.env.step(action)
        self.history.append(next_observation)
        self.last_reward = reward
        self.last_done = done
        self.last_info = info
        self._refresh()

    def _refresh(self) -> None:
        self.dashboard = build_dashboard_state(
            env=self.env,
            expert=self.expert,
            model=self.model,
            history=self.history,
            window_size=self.window_size,
            device=self.device,
            metrics_path=self.metrics_path,
            model_loaded=self.model_loaded,
            last_step_source=self.last_step_source,
            last_reward=self.last_reward,
            done=self.last_done,
            info=self.last_info,
        )
        self._draw_board()
        self._draw_history_strip()
        self._update_text_panels()
        self._draw_attention_heat()
        self._draw_logits()

    def _draw_board(self) -> None:
        self.board_canvas.delete("all")
        rows = self.height
        cols = self.width + 1
        cell = min(theme.BOARD_WIDTH // cols, theme.BOARD_HEIGHT // rows)
        x_offset = 34
        y_offset = 24

        for col in range(cols):
            for row in range(rows):
                x0 = x_offset + col * cell
                y0 = y_offset + row * cell
                x1 = x0 + cell
                y1 = y0 + cell
                fill = theme.PANEL_ALT if col == 0 else theme.PANEL_BG
                self.board_canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=theme.GRID, width=1)

        state = self.env.state
        if state is None:
            return

        for col in range(cols):
            self.board_canvas.create_text(x_offset + col * cell + cell / 2, 12, text=f"x={col}", fill=theme.MUTED, font=theme.BODY_FONT)
        for row in range(rows):
            self.board_canvas.create_text(14, y_offset + row * cell + cell / 2, text=f"y={row}", fill=theme.MUTED, font=theme.BODY_FONT)

        paddle_x0 = x_offset
        paddle_y0 = y_offset + state.y_paddle * cell
        self.board_canvas.create_rectangle(
            paddle_x0 + 7,
            paddle_y0 + 7,
            paddle_x0 + cell - 7,
            paddle_y0 + cell - 7,
            fill=theme.PADDLE,
            outline="",
        )

        ball_x0 = x_offset + state.x_ball * cell
        ball_y0 = y_offset + state.y_ball * cell
        self.board_canvas.create_oval(
            ball_x0 + 10,
            ball_y0 + 10,
            ball_x0 + cell - 10,
            ball_y0 + cell - 10,
            fill=theme.BALL,
            outline="",
        )

        status_color = theme.GOOD if self.dashboard.caught else (theme.BAD if self.dashboard.done else theme.MUTED)
        self.board_canvas.create_text(
            x_offset,
            y_offset + rows * cell + 20,
            text=f"state: t={state.t}  ball=({state.x_ball},{state.y_ball})  paddle={state.y_paddle}",
            anchor="w",
            fill=theme.TEXT,
            font=theme.MONO_FONT,
        )
        self.board_canvas.create_text(
            x_offset,
            y_offset + rows * cell + 42,
            text=f"episode_status: done={self.dashboard.done}  caught={self.dashboard.caught}",
            anchor="w",
            fill=status_color,
            font=theme.MONO_FONT,
        )

    def _draw_history_strip(self) -> None:
        self.history_canvas.delete("all")
        recent = self.history[-self.window_size :]
        if not recent:
            return
        margin_x = 18
        margin_y = 18
        card_w = 130
        card_h = 96
        gap = 16

        self.history_canvas.create_text(margin_x, 8, text="The policy should only need the last two frames.", anchor="w", fill=theme.MUTED)
        for idx, obs in enumerate(recent):
            x0 = margin_x + idx * (card_w + gap)
            y0 = margin_y
            x1 = x0 + card_w
            y1 = y0 + card_h
            fill = theme.ACCENT_SOFT if idx >= len(recent) - 2 else "#f6f7fb"
            self.history_canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=theme.BORDER, width=1)
            self.history_canvas.create_text(x0 + 10, y0 + 14, text=f"t={obs.t}", anchor="w", fill=theme.TEXT, font=theme.SECTION_FONT)
            self.history_canvas.create_text(x0 + 10, y0 + 38, text=f"x={obs.x_ball}", anchor="w", fill=theme.TEXT, font=theme.MONO_FONT)
            self.history_canvas.create_text(x0 + 10, y0 + 56, text=f"y={obs.y_ball}", anchor="w", fill=theme.TEXT, font=theme.MONO_FONT)
            self.history_canvas.create_text(x0 + 10, y0 + 74, text=f"p={obs.y_paddle}", anchor="w", fill=theme.TEXT, font=theme.MONO_FONT)

    def _update_text_panels(self) -> None:
        self._set_text(
            self.summary_text,
            "\n".join(self.dashboard.summary_lines + [""] + self.dashboard.history_lines),
        )
        self._set_text(self.metrics_text, "\n".join(self.dashboard.metrics_lines))

        expert_lines = [
            f"action = {self.dashboard.expert.action_name} ({self.dashboard.expert.action})",
            f"intercept = {self.dashboard.expert.intercept}",
            "",
            "This is the proof-defined policy.",
        ]
        self._set_text(self.expert_card.text_widget, "\n".join(expert_lines))  # type: ignore[attr-defined]

        model_lines = [
            f"action = {self.dashboard.model.action_name} ({self.dashboard.model.action})",
            f"intercept_pred = {self.dashboard.model.intercept}",
            f"logits = {[round(x, 3) for x in self.dashboard.model.logits]}",
            "",
            "This is the trained policy network.",
        ]
        self._set_text(self.model_card.text_widget, "\n".join(model_lines))  # type: ignore[attr-defined]

        self._set_text(self.formula_text, "\n".join(self.dashboard.formula_lines))

    def _draw_attention_heat(self) -> None:
        self.attn_canvas.delete("all")
        weights = self.dashboard.model.attn_weights
        if not weights:
            self.attn_canvas.create_text(20, 20, text="Attention becomes available after the warmup step.", anchor="w", fill=theme.MUTED)
            return

        width = int(self.attn_canvas.winfo_width() or 760)
        height = int(self.attn_canvas.winfo_height() or theme.ATTN_HEIGHT)
        left = 40
        top = 36
        cell_w = max((width - left - 40) // len(weights), 80)
        bar_h = 110

        self.attn_canvas.create_text(left, 14, text="Mean attention over heads for the last query", anchor="w", fill=theme.TEXT, font=theme.SECTION_FONT)
        self.attn_canvas.create_text(left, height - 18, text="Dark cells mean the model reads that history frame more strongly.", anchor="w", fill=theme.MUTED)

        recent = self.history[-len(weights) :]
        for idx, weight in enumerate(weights):
            x0 = left + idx * cell_w
            x1 = x0 + cell_w - 12
            y0 = top
            y1 = y0 + bar_h
            color = self._blend_heat(weight)
            self.attn_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=theme.BORDER, width=1)
            self.attn_canvas.create_text((x0 + x1) / 2, y0 + 22, text=f"t={recent[idx].t}", fill=theme.TEXT, font=theme.SECTION_FONT)
            self.attn_canvas.create_text((x0 + x1) / 2, y0 + 48, text=f"x={recent[idx].x_ball}", fill=theme.TEXT, font=theme.MONO_FONT)
            self.attn_canvas.create_text((x0 + x1) / 2, y0 + 66, text=f"y={recent[idx].y_ball}", fill=theme.TEXT, font=theme.MONO_FONT)
            self.attn_canvas.create_text((x0 + x1) / 2, y0 + 84, text=f"p={recent[idx].y_paddle}", fill=theme.TEXT, font=theme.MONO_FONT)
            self.attn_canvas.create_text((x0 + x1) / 2, y1 + 18, text=f"{weight:.3f}", fill=theme.MUTED, font=theme.MONO_FONT)

        if len(weights) >= 2:
            last_two_mass = sum(weights[-2:])
            self.attn_canvas.create_text(left, top + bar_h + 48, text=f"last_two_mass = {last_two_mass:.3f}", anchor="w", fill=theme.ACCENT, font=theme.SECTION_FONT)

    def _draw_logits(self) -> None:
        self.logits_canvas.delete("all")
        logits = self.dashboard.model.logits
        if not logits:
            return
        width = int(self.logits_canvas.winfo_width() or 760)
        height = int(self.logits_canvas.winfo_height() or theme.LOGITS_HEIGHT)
        origin_x = 120
        origin_y = height - 28
        bar_gap = 46
        bar_h = 26
        scale = 56

        self.logits_canvas.create_text(20, 20, text="The model action comes from the largest logit.", anchor="w", fill=theme.TEXT, font=theme.SECTION_FONT)

        labels = [("up", logits[0]), ("stay", logits[1]), ("down", logits[2])]
        max_value = max(abs(v) for _, v in labels) or 1.0
        for idx, (label, value) in enumerate(labels):
            y = 52 + idx * bar_gap
            self.logits_canvas.create_text(40, y + bar_h / 2, text=label, anchor="w", fill=theme.TEXT, font=theme.MONO_FONT)
            bar_len = (value / max_value) * (width - origin_x - 70)
            x0 = origin_x
            x1 = origin_x + bar_len
            color = theme.MODEL if label == self.dashboard.model.action_name else theme.ACCENT
            if bar_len >= 0:
                self.logits_canvas.create_rectangle(x0, y, x1, y + bar_h, fill=color, outline="")
            else:
                self.logits_canvas.create_rectangle(x1, y, x0, y + bar_h, fill=color, outline="")
            self.logits_canvas.create_text(origin_x + (bar_len if bar_len >= 0 else 0) + 10, y + bar_h / 2, text=f"{value:.3f}", anchor="w", fill=theme.TEXT, font=theme.MONO_FONT)

    @staticmethod
    def _set_text(widget: tk.Text, value: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", value)
        widget.configure(state=tk.DISABLED)

    @staticmethod
    def _blend_heat(value: float) -> str:
        value = max(0.0, min(1.0, value))
        low = (219, 228, 255)
        high = (39, 75, 219)
        rgb = tuple(int(low[i] + (high[i] - low[i]) * value) for i in range(3))
        return "#%02x%02x%02x" % rgb

    def run(self) -> None:
        self.root.mainloop()
