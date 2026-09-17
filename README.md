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

- **2026-09-11** — Obsidian Echo: Signal Chase — `terminal/daily/2026_09_11_obsidian_echo.py`
- **2026-09-10** — Hollow Compass: Tide Ledger — `terminal/daily/2026_09_10_hollow_compass_tide_ledger.py`
- **2026-09-09** — Cinder Orchard: Graft Alchemist — `terminal/daily/2026_09_09_cinder_orchard_graft_alchemist.py`
- **2026-09-08** — Lantern Vale: Rune Cartographer — `terminal/daily/2026_09_08_lantern_vale_rune_cartographer.py`
- **2026-09-07** — Tide Atlas: Ford the drowned road before the second breath — `terminal/daily/2026_09_07_tide_atlas_ford_the_drowned_road_before_the_second_breath.py`
- **2026-09-06** — The Moultering Deep: Shed Your Skin or Be Shed — `terminal/daily/2026_09_06_the_moultering_deep_shed_your_skin_or_be_shed.py`
- **2026-09-04** — Lantern Lines: Chain-burst the lamp grid before your matches run out — `terminal/daily/2026_09_04_lantern_lines_chain_burst_the_lamp_grid_before_your_matches_run_out.py`
- **2026-09-03** — The Light of Saint Verra: Smoke & Signal: guide the fleet home through fog with the shutter lamp — `terminal/daily/2026_09_03_the_light_of_saint_verra_smoke_signal_guide_the_fleet_home_through_fog_with_the_shutter_lamp.py`
- **2026-09-02** — The Glasshouse: Frost & Harvest — `terminal/daily/2026_09_02_the_glasshouse_frost_harvest.py`
- **2026-08-31** — The Windmill: Ballast & Grain — `terminal/daily/2026_08_31_the_windmill_ballast_grain.py`
- **2026-08-30** — Meridian Hall: The Gear-Spirit's Toll — `terminal/daily/2026_08_30_meridian_hall_the_gear_spirit_s_toll.py`
- **2026-08-28** — Ember Watch: The Lantern-Keeper's Night — `terminal/daily/2026_08_28_ember_watch_the_lantern_keeper_s_night.py`


## Latest drop

**Belltower Siege: Wave Defense** — 2026-09-14 — `terminal/daily/2026_09_14_belltower_siege_wave_defense.py`

Updated today's drop: **Glasslight Sextant: Bearing & Shoals** — 2026-09-16 — `terminal/daily/2026_09_16_glasslight_sextant_bearing_shoals.py`

Updated today's drop: **High Tide Heist: Tide Surge Heist** — 2026-09-16 — `terminal/daily/2026_09_16_high_tide_heist_tide_surge_heist.py`

Updated today's drop: **Cellar of Nine Faucets: Dice on Draft** — 2026-09-17 — `terminal/daily/2026_09_17_cellar_of_nine_faucets_dice_on_draft.py`
