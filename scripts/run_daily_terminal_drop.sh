#!/usr/bin/env bash
set -uo pipefail

export TZ=America/Los_Angeles
export GIT_SSH_COMMAND="ssh -i /home/onikita/.ssh/id_ed25519 -o IdentitiesOnly=yes"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOG="terminal/daily/cron.log"

echo "[$(date '+%F %T %Z')] daily drop run starting" >> "$LOG"

# Sync so pushes can't be rejected for drift. Rebase local daily-drop ontop of
# live main; if that fails, abort cleanly and alert.
git fetch origin 2>>"$LOG" || { echo "FETCH FAILED" >> "$LOG"; exit 1; }
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo "[$(date '+%F %T %Z')] repo drifted; rebasing local drop onto origin/main" >> "$LOG"
  git rebase origin/main 2>>"$LOG" || { echo "REBASE CONFLICT — manual fix needed" >> "$LOG"; exit 2; }
fi

# Author a fresh game with this prompt-driven generator (the "brain").
# The daily_terminal_game.py deterministic generator is now a fallback only;
# a fresh original game is authored by the orchestrated pipeline below.

echo "[$(date '+%F %T %Z')] authoring game" >> "$LOG"
python3 scripts/daily_terminal_game.py >> "$LOG" 2>&1

if [[ -n "$(git status --porcelain)" ]]; then
  DATE=$(python3 -c 'import json; print(json.load(open("terminal/daily/.latest.json"))["date"])')
  TITLE=$(python3 -c 'import json; print(json.load(open("terminal/daily/.latest.json"))["title"])')
  git add -A
  git commit -m "Daily terminal drop: ${DATE} - ${TITLE}" >> "$LOG" 2>&1
  git push >> "$LOG" 2>&1
  echo "[$(date '+%F %T %Z')] pushed ${DATE} - ${TITLE}" >> "$LOG"
else
  echo "[$(date '+%F %T %Z')] nothing to commit (already present)" >> "$LOG"
fi

echo "[$(date '+%F %T %Z')] daily drop run complete" >> "$LOG"
