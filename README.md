# BrainAccelerator

A research-inspired focus and memory game that mixes fast math with short recall challenges. Scores are saved to a community leaderboard.

## Quick start

```bash
npm install
npm start
```

Open `http://localhost:3000`.

One-line quickstart:

```bash
npm install && npm start
```

## Docker

```bash
docker build -t brainaccelerator .
docker run -p 3000:3000 brainaccelerator
```

## GitHub Pages (frontend-only)

GitHub Pages can host the game UI, but it cannot run the Node/SQLite backend.
In Pages mode, scores and streaks are stored locally in your browser.

## Modes

- Focus Run (60s): mixed math + memory
- Deep Focus (180s): longer paced session
- Recall Ladder (90s): heavier memory ramp

## Practice plan

Enter your name to see a daily practice plan and streak tracking. The backend updates streaks whenever you complete a run.

## Project structure

- `server.js` Express + SQLite API for scores, profiles, streaks
- `public/` Web game UI
- `data/` Local SQLite database (auto-created)
- `terminal/` Terminal game (Dungeon Dash)

## Terminal game

Dungeon Dash is a tiny turn-based roguelike you can play in the terminal.

```bash
python3 terminal/dungeon_dash.py
```

## Next ideas

- Add daily practice schedules with spaced repetition
- Add multiple modes (longer sessions, adaptive difficulty)
- Add accounts and anti-cheat validation

## Daily Terminal Drops

<!-- DAILY_DROP_START -->
Latest: 2026-02-12 — Neon Prism: Word Forge (`terminal/daily/2026_02_12_neon_prism.py`)
See `terminal/daily/LOG.md` for history.
<!-- DAILY_DROP_END -->
