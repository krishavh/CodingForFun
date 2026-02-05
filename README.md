# BrainAccelerator

A research-inspired focus and memory game that mixes fast math with short recall challenges. Scores are saved to a community leaderboard.

## Quick start

```bash
npm install
npm start
```

Open `http://localhost:3000`.

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

## Next ideas

- Add daily practice schedules with spaced repetition
- Add multiple modes (longer sessions, adaptive difficulty)
- Add accounts and anti-cheat validation
