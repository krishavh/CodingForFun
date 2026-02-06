const timeLabel = document.getElementById("timeLabel");
const scoreLabel = document.getElementById("scoreLabel");
const streakLabel = document.getElementById("streakLabel");
const runner = document.getElementById("runner");
const zone = document.getElementById("zone");
const startBtn = document.getElementById("startBtn");
const hitBtn = document.getElementById("hitBtn");
const statusEl = document.getElementById("status");

let gameActive = false;
let timeLeft = 45;
let score = 0;
let streak = 0;
let speed = 1.4;
let direction = 1;
let pos = 0;
let animationId = null;
let timerId = null;

function setStatus(message) {
  statusEl.textContent = message;
}

function updateLabels() {
  timeLabel.textContent = `${timeLeft}s`;
  scoreLabel.textContent = score.toString();
  streakLabel.textContent = streak.toString();
}

function randomizeZone() {
  const trackWidth = runner.parentElement.clientWidth;
  const zoneWidth = trackWidth * 0.16;
  const padding = 20;
  const left = Math.floor(Math.random() * (trackWidth - zoneWidth - padding * 2)) + padding;
  zone.style.left = `${left}px`;
  zone.style.width = `${zoneWidth}px`;
}

function tick() {
  if (!gameActive) return;
  const trackWidth = runner.parentElement.clientWidth;
  const maxPos = trackWidth - 24;
  pos += speed * direction;
  if (pos <= 0) {
    pos = 0;
    direction = 1;
  }
  if (pos >= maxPos) {
    pos = maxPos;
    direction = -1;
  }
  runner.style.left = `${pos}px`;
  animationId = requestAnimationFrame(tick);
}

function hit() {
  if (!gameActive) return;
  const zoneRect = zone.getBoundingClientRect();
  const runnerRect = runner.getBoundingClientRect();
  const runnerCenter = runnerRect.left + runnerRect.width / 2;
  const inZone = runnerCenter >= zoneRect.left && runnerCenter <= zoneRect.right;

  if (inZone) {
    streak += 1;
    const bonus = Math.min(12, streak * 2);
    score += 10 + bonus;
    speed = Math.min(4.2, speed + 0.12);
    setStatus(`Hit! +${10 + bonus} points.`);
  } else {
    streak = 0;
    score = Math.max(0, score - 6);
    speed = Math.max(1.2, speed - 0.15);
    setStatus("Miss. Reset and refocus.");
  }

  updateLabels();
  randomizeZone();
}

function endGame() {
  gameActive = false;
  cancelAnimationFrame(animationId);
  clearInterval(timerId);
  hitBtn.disabled = true;
  startBtn.disabled = false;
  setStatus(`Final score: ${score}. Ready for another run?`);
}

function startGame() {
  gameActive = true;
  timeLeft = 45;
  score = 0;
  streak = 0;
  speed = 1.4;
  direction = 1;
  pos = 0;
  runner.style.left = "0px";
  updateLabels();
  randomizeZone();
  hitBtn.disabled = false;
  startBtn.disabled = true;
  setStatus("Time it. Hit the zone.");

  clearInterval(timerId);
  timerId = setInterval(() => {
    timeLeft -= 1;
    updateLabels();
    if (timeLeft <= 0) {
      endGame();
    }
  }, 1000);

  cancelAnimationFrame(animationId);
  animationId = requestAnimationFrame(tick);
}

startBtn.addEventListener("click", startGame);
hitBtn.addEventListener("click", hit);
window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    hit();
  }
});

window.addEventListener("resize", () => {
  if (gameActive) {
    randomizeZone();
  }
});

updateLabels();
