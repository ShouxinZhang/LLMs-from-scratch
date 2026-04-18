const episodeSelect = document.getElementById("episodeSelect");
const stepSlider = document.getElementById("stepSlider");
const prevBtn = document.getElementById("prevBtn");
const playBtn = document.getElementById("playBtn");
const nextBtn = document.getElementById("nextBtn");

const heroMetrics = document.getElementById("heroMetrics");
const modelOutcome = document.getElementById("modelOutcome");
const expertOutcome = document.getElementById("expertOutcome");
const modelInfo = document.getElementById("modelInfo");
const expertInfo = document.getElementById("expertInfo");
const attentionNote = document.getElementById("attentionNote");
const historyCards = document.getElementById("historyCards");

const modelBoard = document.getElementById("modelBoard");
const expertBoard = document.getElementById("expertBoard");
const attentionCanvas = document.getElementById("attentionCanvas");

let demoData = null;
let currentEpisodeIndex = 0;
let currentStepIndex = 0;
let autoplayTimer = null;

const metricConfig = [
  ["action_accuracy", "Offline Action Acc"],
  ["rollout_catch_rate", "Rollout Catch Rate"],
  ["one_frame_baseline_accuracy", "One-Frame Baseline"],
  ["attn_last_two_mass", "Attn Last-Two Mass"],
];

const stateLabels = {
  x_ball: "Ball X",
  y_ball: "Ball Y",
  y_paddle: "Paddle Y",
  chosen_action_name: "Chosen Action",
  expert_action_name: "Expert Action",
  model_action_name: "Model Action",
  model_intercept_pred: "Pred Intercept",
  reward: "Reward",
};

function fmtNumber(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isInteger(value) ? `${value}` : value.toFixed(3);
  return String(value);
}

function createMetricCard(label, value) {
  const card = document.createElement("div");
  card.className = "metric-card";
  card.innerHTML = `<div class="label">${label}</div><div class="value">${fmtNumber(value)}</div>`;
  return card;
}

function drawBoard(canvas, step, env) {
  const ctx = canvas.getContext("2d");
  const cols = env.width + 1;
  const rows = env.height;
  const width = canvas.width;
  const height = canvas.height;
  const cell = Math.min((width - 40) / cols, (height - 40) / rows);
  const originX = 20;
  const originY = 20;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fffaf1";
  ctx.fillRect(0, 0, width, height);

  for (let col = 0; col < cols; col += 1) {
    for (let row = 0; row < rows; row += 1) {
      ctx.fillStyle = col === 0 ? "#efe7ff" : "#ffffff";
      ctx.strokeStyle = "rgba(0,0,0,0.08)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.rect(originX + col * cell, originY + row * cell, cell, cell);
      ctx.fill();
      ctx.stroke();
    }
  }

  const before = step.state_before;
  const after = step.state_after;
  const ballX = originX + after.x_ball * cell;
  const ballY = originY + after.y_ball * cell;
  const paddleX = originX;
  const paddleY = originY + after.y_paddle * cell;

  ctx.fillStyle = "#2759ff";
  ctx.fillRect(paddleX + 8, paddleY + 8, cell - 16, cell - 16);

  ctx.fillStyle = "#ff6b2c";
  ctx.beginPath();
  ctx.arc(ballX + cell / 2, ballY + cell / 2, Math.max(6, cell / 3.8), 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#1b1c1f";
  ctx.font = "14px sans-serif";
  ctx.fillText(`t=${after.t}`, originX, originY + rows * cell + 18);
}

function renderInfo(container, step, type) {
  const fields = type === "model"
    ? [
        ["Ball X", step.state_after.x_ball],
        ["Ball Y", step.state_after.y_ball],
        ["Paddle Y", step.state_after.y_paddle],
        ["Action", step.chosen_action_name],
        ["Pred Intercept", step.model_intercept_pred],
        ["Reward", step.reward],
      ]
    : [
        ["Ball X", step.state_after.x_ball],
        ["Ball Y", step.state_after.y_ball],
        ["Paddle Y", step.state_after.y_paddle],
        ["Action", step.chosen_action_name],
        ["Expert Intercept", step.expert_intercept],
        ["Reward", step.reward],
      ];

  container.innerHTML = "";
  for (const [label, value] of fields) {
    const item = document.createElement("div");
    item.className = "info-item";
    item.innerHTML = `<div class="label">${label}</div><div class="value">${fmtNumber(value)}</div>`;
    container.appendChild(item);
  }
}

function drawAttention(step) {
  const ctx = attentionCanvas.getContext("2d");
  const width = attentionCanvas.width;
  const height = attentionCanvas.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fffaf1";
  ctx.fillRect(0, 0, width, height);

  if (!step.attn_weights || step.attn_weights.length === 0) {
    attentionNote.textContent = "Warmup step: attention is unavailable before the model has two observations.";
    ctx.fillStyle = "#65615b";
    ctx.font = "18px sans-serif";
    ctx.fillText("No attention on warmup step", 30, 50);
    return;
  }

  attentionNote.textContent = "Mean over heads for the final query token. The last two bars are the proof-relevant frames.";

  const padding = 40;
  const baselineY = height - 40;
  const maxBarHeight = height - 90;
  const barCount = step.attn_weights.length;
  const slot = (width - padding * 2) / barCount;
  const history = step.history;

  ctx.strokeStyle = "rgba(0,0,0,0.2)";
  ctx.beginPath();
  ctx.moveTo(padding, baselineY);
  ctx.lineTo(width - padding, baselineY);
  ctx.stroke();

  step.attn_weights.forEach((weight, index) => {
    const x = padding + index * slot + slot * 0.15;
    const barWidth = slot * 0.7;
    const barHeight = weight * maxBarHeight;
    const y = baselineY - barHeight;
    const recent = index >= barCount - 2;
    ctx.fillStyle = recent ? "#2759ff" : "#94a3b8";
    ctx.fillRect(x, y, barWidth, barHeight);
    ctx.fillStyle = "#1b1c1f";
    ctx.font = "12px sans-serif";
    ctx.fillText(weight.toFixed(2), x + 6, y - 8);
    ctx.fillStyle = "#65615b";
    ctx.fillText(`t=${history[index].t}`, x + 4, baselineY + 18);
  });
}

function renderHistory(step) {
  historyCards.innerHTML = "";
  const history = step.history || [];
  history.forEach((obs, index) => {
    const card = document.createElement("div");
    const isCurrent = index === history.length - 1;
    card.className = `history-card${isCurrent ? " current" : ""}`;
    card.innerHTML = `
      <div class="title">${isCurrent ? "Current Frame" : "Context Frame"} · t=${obs.t}</div>
      <div class="coords">x=${obs.x_ball}, y=${obs.y_ball}, p=${obs.y_paddle}</div>
    `;
    historyCards.appendChild(card);
  });
}

function setOutcomePill(element, caught) {
  element.textContent = caught ? "caught" : "missed";
  element.className = `pill${caught ? "" : " fail"}`;
}

function currentEpisode() {
  return demoData.episodes[currentEpisodeIndex];
}

function currentStepPair() {
  const episode = currentEpisode();
  return {
    model: episode.model.steps[currentStepIndex],
    expert: episode.expert.steps[currentStepIndex],
  };
}

function renderEpisode() {
  const episode = currentEpisode();
  const pair = currentStepPair();

  stepSlider.max = String(episode.model.steps.length - 1);
  stepSlider.value = String(currentStepIndex);

  drawBoard(modelBoard, pair.model, demoData.metadata.env);
  drawBoard(expertBoard, pair.expert, demoData.metadata.env);
  renderInfo(modelInfo, pair.model, "model");
  renderInfo(expertInfo, pair.expert, "expert");
  drawAttention(pair.model);
  renderHistory(pair.model);

  setOutcomePill(modelOutcome, episode.model.caught);
  setOutcomePill(expertOutcome, episode.expert.caught);
}

function populateHeroMetrics() {
  heroMetrics.innerHTML = "";
  const metrics = demoData.metadata.metrics || {};
  for (const [key, label] of metricConfig) {
    heroMetrics.appendChild(createMetricCard(label, metrics[key]));
  }
  heroMetrics.appendChild(createMetricCard("Checkpoint Loaded", demoData.metadata.model_loaded));
  heroMetrics.appendChild(createMetricCard("Episodes", demoData.episodes.length));
}

function populateEpisodeSelect() {
  episodeSelect.innerHTML = "";
  demoData.episodes.forEach((episode, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `seed ${episode.seed}`;
    episodeSelect.appendChild(option);
  });
}

function playToggle() {
  if (autoplayTimer) {
    clearInterval(autoplayTimer);
    autoplayTimer = null;
    playBtn.textContent = "Play";
    return;
  }
  autoplayTimer = setInterval(() => {
    const episode = currentEpisode();
    if (currentStepIndex >= episode.model.steps.length - 1) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
      playBtn.textContent = "Play";
      return;
    }
    currentStepIndex += 1;
    renderEpisode();
  }, 600);
  playBtn.textContent = "Pause";
}

async function init() {
  const response = await fetch("./data/demo_trace.json");
  demoData = await response.json();

  populateHeroMetrics();
  populateEpisodeSelect();
  renderEpisode();

  episodeSelect.addEventListener("change", (event) => {
    currentEpisodeIndex = Number(event.target.value);
    currentStepIndex = 0;
    renderEpisode();
  });

  stepSlider.addEventListener("input", (event) => {
    currentStepIndex = Number(event.target.value);
    renderEpisode();
  });

  prevBtn.addEventListener("click", () => {
    currentStepIndex = Math.max(0, currentStepIndex - 1);
    renderEpisode();
  });

  nextBtn.addEventListener("click", () => {
    const last = currentEpisode().model.steps.length - 1;
    currentStepIndex = Math.min(last, currentStepIndex + 1);
    renderEpisode();
  });

  playBtn.addEventListener("click", playToggle);
}

init();
