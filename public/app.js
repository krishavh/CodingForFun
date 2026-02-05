const startBtn = document.getElementById("startBtn");
const submitBtn = document.getElementById("submitBtn");
const answerInput = document.getElementById("answerInput");
const playerNameInput = document.getElementById("playerName");
const modeSelect = document.getElementById("modeSelect");
const statusEl = document.getElementById("status");
const roundLabel = document.getElementById("roundLabel");
const timerLabel = document.getElementById("timerLabel");
const scoreLabel = document.getElementById("scoreLabel");
const challengeType = document.getElementById("challengeType");
const challengeContent = document.getElementById("challengeContent");
const hint = document.getElementById("hint");
const leaderboard = document.getElementById("leaderboard");
const streakCount = document.getElementById("streakCount");
const bestStreak = document.getElementById("bestStreak");
const planList = document.getElementById("planList");
const planDate = document.getElementById("planDate");

let gameActive = false;
let timeLeft = 60;
let round = 1;
let score = 0;
let streak = 0;
let expectedAnswer = "";
let challengeIndex = 0;
let timerId = null;

let modes = [];
let activeMode = null;

function updateLabels() {
  roundLabel.textContent = `Round ${round}`;
  timerLabel.textContent = `${timeLeft}s`;
  scoreLabel.textContent = `Score ${score}`;
}

function setStatus(message) {
  statusEl.textContent = message;
}

function setChallenge(type, content) {
  challengeType.textContent = type;
  challengeContent.textContent = content;
}

function generateMath() {
  const level = Math.min(4, Math.floor(round / 4));
  const modeMax = activeMode ? activeMode.mathMax : 30;
  const max = Math.min(modeMax, 12 + level * 6);
  const a = Math.floor(Math.random() * max) + 2;
  const b = Math.floor(Math.random() * max) + 2;
  const ops = ["+", "-", "×"];
  const op = ops[Math.floor(Math.random() * ops.length)];
  let answer = 0;
  if (op === "+") answer = a + b;
  if (op === "-") answer = a - b;
  if (op === "×") answer = a * b;
  return { prompt: `${a} ${op} ${b}`, answer: `${answer}` };
}

function generateMemory() {
  const base = activeMode ? activeMode.memoryBase : 4;
  const max = activeMode ? activeMode.memoryMax : 8;
  const length = Math.min(max, base + Math.floor(round / 3));
  let seq = "";
  for (let i = 0; i < length; i += 1) {
    seq += Math.floor(Math.random() * 10).toString();
  }
  return seq;
}

function nextChallenge() {
  if (!gameActive) return;

  answerInput.value = "";
  answerInput.disabled = false;
  submitBtn.disabled = false;

  if (challengeIndex % 2 === 0) {
    const { prompt, answer } = generateMath();
    expectedAnswer = answer;
    setChallenge("Math Sprint", prompt);
    hint.textContent = "Solve fast, but stay accurate.";
  } else {
    const seq = generateMemory();
    expectedAnswer = seq;
    setChallenge("Memory Flash", seq.split("").join(" "));
    const flashMs = activeMode ? activeMode.flashMs : 2000;
    hint.textContent = "Memorize the digits. You'll get a short moment.";
    answerInput.disabled = true;
    submitBtn.disabled = true;

    setTimeout(() => {
      if (!gameActive) return;
      setChallenge("Memory Flash", "Type the sequence");
      answerInput.disabled = false;
      submitBtn.disabled = false;
      answerInput.focus();
    }, flashMs);
  }

  challengeIndex += 1;
  answerInput.focus();
}

function evaluateAnswer() {
  if (!gameActive) return;
  const response = answerInput.value.trim();
  const correct = response === expectedAnswer;

  if (correct) {
    streak += 1;
    const base = challengeIndex % 2 === 1 ? 10 : 14;
    const bonus = Math.min(20, streak * 2);
    score += base + bonus;
    setStatus(`Nice! Streak ${streak}. +${base + bonus} points.`);
  } else {
    streak = 0;
    setStatus("Reset. Accuracy first, then speed.");
  }

  round += 1;
  updateLabels();
  nextChallenge();
}

function endGame() {
  gameActive = false;
  clearInterval(timerId);
  answerInput.disabled = true;
  submitBtn.disabled = true;
  setChallenge("Session Complete", `Final score: ${score}`);
  hint.textContent = "Submitting your score to the community board.";
  setStatus("Run complete.");
  postScore();
}

function tick() {
  timeLeft -= 1;
  updateLabels();
  if (timeLeft <= 0) {
    endGame();
  }
}

function startGame() {
  const name = playerNameInput.value.trim();
  if (!name) {
    setStatus("Add your name to start.");
    return;
  }

  const selectedMode = modeSelect.value || "focus-run";
  activeMode = modes.find((mode) => mode.key === selectedMode) || activeMode;

  gameActive = true;
  timeLeft = activeMode ? activeMode.durationSec : 60;
  round = 1;
  score = 0;
  streak = 0;
  challengeIndex = 0;
  updateLabels();
  setStatus("Focus on calm + accuracy. Go!");
  nextChallenge();

  clearInterval(timerId);
  timerId = setInterval(tick, 1000);
}

async function postScore() {
  const name = playerNameInput.value.trim();
  if (!name) return;
  try {
    const res = await fetch("/api/scores", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, score, mode: activeMode ? activeMode.key : "focus-run" })
    });

    if (res.ok) {
      const payload = await res.json();
      setStatus("Score saved to the community board.");
      if (payload && typeof payload.streak === "number") {
        streakCount.textContent = `${payload.streak} days`;
        bestStreak.textContent = `${payload.best_streak} days`;
      }
      await loadPlan();
      await loadScores();
    } else {
      setStatus("Could not save score. Try again later.");
    }
  } catch (err) {
    setStatus("Network error while saving score.");
  }
}

async function loadScores() {
  leaderboard.innerHTML = "<li>Loading...</li>";
  try {
    const modeKey = activeMode ? activeMode.key : "focus-run";
    const res = await fetch(`/api/scores?mode=${encodeURIComponent(modeKey)}&limit=10`);
    const data = await res.json();
    leaderboard.innerHTML = "";

    if (!data.scores || data.scores.length === 0) {
      leaderboard.innerHTML = "<li>No scores yet. Be the first!</li>";
      return;
    }

    data.scores.forEach((row, index) => {
      const item = document.createElement("li");
      const name = document.createElement("strong");
      const meta = document.createElement("span");

      name.textContent = `${index + 1}. ${row.name}`;
      meta.textContent = row.score;

      item.appendChild(name);
      item.appendChild(meta);
      leaderboard.appendChild(item);
    });
  } catch (err) {
    leaderboard.innerHTML = "<li>Leaderboard unavailable.</li>";
  }
}

startBtn.addEventListener("click", startGame);
submitBtn.addEventListener("click", evaluateAnswer);
answerInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    evaluateAnswer();
  }
});

modeSelect.addEventListener("change", () => {
  const selectedMode = modeSelect.value;
  activeMode = modes.find((mode) => mode.key === selectedMode) || activeMode;
  if (activeMode) {
    startBtn.textContent = `Start ${activeMode.durationSec}s Run`;
  }
  loadScores();
});

async function loadModes() {
  try {
    const res = await fetch("/api/modes");
    const data = await res.json();
    modes = data.modes || [];
    modeSelect.innerHTML = "";
    modes.forEach((mode) => {
      const option = document.createElement("option");
      option.value = mode.key;
      option.textContent = `${mode.label} (${mode.durationSec}s)`;
      modeSelect.appendChild(option);
    });
    activeMode = modes[0];
    if (activeMode) {
      modeSelect.value = activeMode.key;
      startBtn.textContent = `Start ${activeMode.durationSec}s Run`;
    }
    await loadScores();
  } catch (err) {
    setStatus("Modes unavailable. Using default.");
    activeMode = { key: "focus-run", durationSec: 60 };
  }
}

async function loadProfile() {
  const name = playerNameInput.value.trim();
  if (!name) {
    streakCount.textContent = "0 days";
    bestStreak.textContent = "0 days";
    planList.innerHTML = "<li>Add your name to see the plan.</li>";
    return;
  }
  try {
    const res = await fetch(`/api/profile?name=${encodeURIComponent(name)}`);
    const data = await res.json();
    if (data.exists) {
      streakCount.textContent = `${data.streak_count || 0} days`;
      bestStreak.textContent = `${data.best_streak || 0} days`;
    }
  } catch (err) {
    // ignore
  }
}

async function loadPlan() {
  const name = playerNameInput.value.trim();
  if (!name) return;
  try {
    const res = await fetch(`/api/plan?name=${encodeURIComponent(name)}`);
    const data = await res.json();
    planDate.textContent = data.today || "Today";
    planList.innerHTML = "";
    (data.tasks || []).forEach((task) => {
      const item = document.createElement("li");
      const left = document.createElement("span");
      const right = document.createElement("strong");
      left.textContent = `${task.label} · ${task.reason}`;
      right.textContent = task.goal;
      item.appendChild(left);
      item.appendChild(right);
      planList.appendChild(item);
    });
  } catch (err) {
    planList.innerHTML = "<li>Plan unavailable.</li>";
  }
}

playerNameInput.addEventListener("blur", loadProfile);
playerNameInput.addEventListener("change", loadProfile);
playerNameInput.addEventListener("blur", loadPlan);
playerNameInput.addEventListener("change", loadPlan);

loadModes();
updateLabels();
