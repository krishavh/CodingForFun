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
Latest: 2026-08-16 — Obsidian Cipher: Vault Code (`terminal/daily/2026_08_16_obsidian_cipher.py`)
See `terminal/daily/LOG.md` for history.
<!-- DAILY_DROP_END -->

Updated today's drop: **Violet Core: Reactor Watch** — 2026-08-16 — `terminal/daily/2026_08_16_violet_core_reactor_watch.py`

Updated today's drop: **Cinder Reach: Salvage Run** — 2026-08-17 — `terminal/daily/2026_08_17_cinder_reach_salvage_run.py`

Updated today's drop: **Salt Road Gambler: The Midnight Crossing** — 2026-08-18 — `terminal/daily/2026_08_18_salt_road_gambler_the_midnight_crossing.py`

Updated today's drop: **The Last Alchemist: Cinnabar's Rose** — 2026-08-19 — `terminal/daily/2026_08_19_the_last_alchemist_cinnabar_s_rose.py`

Updated today's drop: **Threadbound: The Loom-Keeper's Gambit** — 2026-08-20 — `terminal/daily/2026_08_20_threadbound_the_loom_keeper_s_gambit.py`

Updated today's drop: **Brine Grid: The Sunken Field** — 2026-08-21 — `terminal/daily/2026_08_21_brine_grid_the_sunken_field.py`

Updated today's drop: **Nocturne Array: Ghost Frequencies** — 2026-08-22 — `terminal/daily/2026_08_22_nocturne_array_ghost_frequencies.py`

Updated today's drop: **Stone Sibyl: The Last Light of the Courtyard** — 2026-08-23 — `terminal/daily/2026_08_23_stone_sibyl_the_last_light_of_the_courtyard.py`

Updated today's drop: **Umber Spire: Borrowed Light** — 2026-08-24 — `terminal/daily/2026_08_24_umber_spire_borrowed_light.py`

Updated today's drop: **Salt Meridian: The Lamp-Keeper's Vigil** — 2026-08-25 — `terminal/daily/2026_08_25_salt_meridian_the_lamp_keeper_s_vigil.py`

Updated today's drop: **The Ash Road: The Mule-Runner's Ledger** — 2026-08-26 — `terminal/daily/2026_08_26_the_ash_road_the_mule_runner_s_ledger.py`

Updated today's drop: **Ember Watch: The Lantern-Keeper's Night** — 2026-08-28 — `terminal/daily/2026_08_28_ember_watch_the_lantern_keeper_s_night.py`

Updated today's drop: **Tide Ledger: The Cipher of Nine Bells** — 2026-08-27 — `terminal/daily/2026_08_27_tide_ledger_the_cipher_of_nine_bells.py`
