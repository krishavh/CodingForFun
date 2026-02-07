#!/usr/bin/env bash
set -euo pipefail

export TZ=America/Los_Angeles
export GIT_SSH_COMMAND="ssh -i /home/onikita/.ssh/id_ed25519 -o IdentitiesOnly=yes"

# Random delay between 0 and 3599 seconds to land between 6-7am LA time.
if [[ "${SKIP_SLEEP:-}" != "1" ]]; then
  SLEEP_FOR=$((RANDOM % 3600))
  sleep "$SLEEP_FOR"
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/daily_terminal_game.py

if [[ -n "$(git status --porcelain)" ]]; then
  DATE=$(python3 -c 'import json, pathlib; p=pathlib.Path("terminal/daily/.latest.json"); print(json.loads(p.read_text())["date"])')
  TITLE=$(python3 -c 'import json, pathlib; p=pathlib.Path("terminal/daily/.latest.json"); print(json.loads(p.read_text())["title"])')
  git add -A
  git commit -m "Daily terminal drop: ${DATE} - ${TITLE}"
  git push
fi
