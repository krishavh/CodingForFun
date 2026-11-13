#!/usr/bin/env python3
"""
publish_daily.py — Kaaval's helper to publish a human/LLM-authored game
into the CodingForFun daily-drop structure.

Usage:
    publish_daily.py <game_source.py> "<Title>" ["<Subtitle>"]
      - game_source.py : path to the authored game (must be self-contained python)
      - "Title"        : e.g. "Amber Glyph" (adjectives + nouns style)
      - ["Subtitle"]   : optional variant label, e.g. "Signal Chase"

It writes the date_stamped copies (terminal/daily + public/daily), updates
LOG.md, README.md, the index.html card, both index.json files, .latest.json
and public/daily.json — same bookkeeping as daily_terminal_game.py.

Prints the commit-ready info. Does NOT commit/push itself (the outer runner
handles git so failures don't half-publish).

Checks before anything is written (exit code):
  2  bad arguments: missing source, or a title with a line break / backslash / more than 80 characters
  3  a drop for TODAY exists already. Do NOT pick a new title: one game per day.
     To replace today's game with a fixed one, run again with REPLACE=1 in the environment.
  5  the game is empty, does not compile, crashes at start, or names /tmp or a LAN address
  6  terminal/daily/index.json is not valid JSON (for example merge-conflict markers): fix it first
"""
import glob
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DAILY_DIR = os.path.join(ROOT, "terminal", "daily")
LOG_PATH = os.path.join(DAILY_DIR, "LOG.md")
LATEST_PATH = os.path.join(DAILY_DIR, ".latest.json")
INDEX_JSON_PATH = os.path.join(DAILY_DIR, "index.json")
PUBLIC_DAILY_PATH = os.path.join(ROOT, "public", "daily.json")
PUBLIC_DAILY_INDEX_PATH = os.path.join(ROOT, "public", "daily", "index.json")
README_PATH = os.path.join(ROOT, "README.md")
INDEX_PATH = os.path.join(ROOT, "public", "index.html")
PUBLIC_DAILY_DIR = os.path.join(ROOT, "public", "daily")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def fail(code, message):
    print("ERROR: " + message)
    sys.exit(code)


def update_log(date_str, game_name, rel_path):
    line = f"- **{date_str}** — {game_name} — `{rel_path}`\n"
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if f"- **{date_str}**" in content:
            # a function as replacement: a backslash in the title is then plain text, not a regex escape
            content = re.sub(r"- \*\*%s\*\*.*" % date_str, lambda m: line.rstrip("\n"), content, count=1)
        else:
            content = line + content
    else:
        content = "# Daily Terminal Drops\n\n" + line
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def update_readme(date_str, game_name, rel_path):
    """Rewrite only the block between the DAILY_DROP markers. (An older version appended one
    "Updated today's drop" line per day to the end of the file; those lines are removed here.)"""
    if not os.path.exists(README_PATH):
        return
    with open(README_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    current = text
    start, end = "<!-- DAILY_DROP_START -->", "<!-- DAILY_DROP_END -->"
    block = f"{start}\nLatest: {date_str} — {game_name} (`{rel_path}`)\nSee `terminal/daily/LOG.md` for history.\n{end}"
    if start in text and end in text:
        text = text[:text.index(start)] + block + text[text.index(end) + len(end):]
    else:
        text = text.rstrip("\n") + "\n\n## Latest drop\n\n" + block + "\n"
    text = re.sub(r"\n+Updated today's drop: [^\n]*", "", text).rstrip("\n") + "\n"
    if text != current:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(text)


def update_index(date_str, game_name, public_rel_path):
    rel_path = os.path.join("daily", os.path.basename(public_rel_path))
    card = (
        "        <article class=\"card\">\n"
        "          <h3>"
        + html.escape(game_name)
        + "</h3>\n"
        "          <p class=\"meta\"><time>"
        + date_str
        + "</time></p>\n"
        "          <div class=\"meta\">\n"
        "            <span>Terminal</span>\n"
        "            <span>Daily</span>\n"
        "            <span>Creative</span>\n"
        "          </div>\n"
        f"          <a class=\"cta\" href=\"{rel_path}\">View Today's Game</a>\n"
        "        </article>"
    )
    start = "<!-- DAILY_CARD_START -->"
    end = "<!-- DAILY_CARD_END -->"
    if not os.path.exists(INDEX_PATH):
        return
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    if start in text and end in text:
        before = text.split(start)[0]
        after = text.split(end)[1]
        new_text = before + start + "\n" + card + "\n" + end + after
    else:
        marker = "      <section class=\"cards\">\n"
        if marker in text:
            parts = text.split(marker)
            new_text = parts[0] + marker + start + "\n" + card + "\n" + end + "\n" + parts[1]
        else:
            new_text = text
    if new_text != text:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(new_text)


def load_index():
    """The list in terminal/daily/index.json. A broken file stops the run: an older version replaced it
    with a one-entry list and the whole history was lost at the next push."""
    if not os.path.exists(INDEX_JSON_PATH):
        return []
    try:
        with open(INDEX_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except ValueError as exc:
        fail(6, f"{INDEX_JSON_PATH} is not valid JSON ({exc}). It may hold merge-conflict markers. "
                "Repair it (git checkout the last good version or remove the markers), then run again. Nothing was written.")
    if not isinstance(data, list):
        fail(6, f"{INDEX_JSON_PATH} does not hold a list. Nothing was written.")
    return data


def update_index_json(data, date_str, title, rel_path, public_rel_path):
    entry = {
        "date": date_str,
        "title": title,
        "file": rel_path,
        "public_file": public_rel_path,
    }
    data = [item for item in data if item.get("date") != date_str] + [entry]      # one entry per day
    data = sorted(data, key=lambda item: item.get("date", ""), reverse=True)
    with open(INDEX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.makedirs(PUBLIC_DAILY_DIR, exist_ok=True)
    with open(PUBLIC_DAILY_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def check_game(src, code, filename):
    """Stop a broken game before it is published."""
    if len(code.strip()) < 400:
        fail(5, f"{src} holds {len(code.strip())} characters. That is not a game. Nothing was written.")
    try:
        compile(code, filename, "exec")
    except SyntaxError as exc:
        fail(5, f"the game does not compile: {exc}. Nothing was written.")
    for pattern, what in ((r"/tmp/", "a /tmp path"), (r"\b(192\.168|10\.\d+)\.\d+\.\d+\b", "a LAN address")):
        if re.search(pattern, code):
            fail(5, f"the game names {what}; this repo is public. Remove it. Nothing was written.")
    # Start it once with no keyboard. Waiting for input (EOFError), a full-screen library with no terminal,
    # or still running after 10 s are all fine. Any other traceback is a crash at start.
    try:
        run = subprocess.run([sys.executable, src], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return
    err = run.stderr or ""
    if "Traceback" in err and not re.search(r"EOFError|KeyboardInterrupt|curses|termios|Inappropriate ioctl|tty", err):
        last = [line for line in err.strip().splitlines() if line.strip()][-1]
        fail(5, f"the game crashes at start: {last[:200]}. Fix the game, then run publish again. Nothing was written.")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src = os.path.abspath(sys.argv[1])
    title = sys.argv[2].strip()
    subtitle = sys.argv[3].strip() if len(sys.argv) > 3 else ""
    if not os.path.exists(src):
        fail(2, f"source not found: {src}")
    for label, text in (("title", title), ("subtitle", subtitle)):
        if "\n" in text or "\\" in text or len(text) > 80 or (label == "title" and not text):
            fail(2, f"the {label} must be 1-80 characters on one line with no backslash. Got {len(text)} characters. Nothing was written.")

    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    game_name = f"{title}: {subtitle}" if subtitle else title
    slug = slugify(f"{date_str}_{title}{'_' + slugify(subtitle) if subtitle else ''}")[:80].strip("_")
    filename = f"{slug}.py"

    rel_path = os.path.join("terminal", "daily", filename)
    public_rel_path = os.path.join("daily", filename)
    abs_path = os.path.join(ROOT, rel_path)
    public_abs_path = os.path.join(PUBLIC_DAILY_DIR, filename)

    # One drop per day. The check is by DATE, not by file name: a second title for the same day made
    # two games for one date (the index kept the first one, the log showed the second).
    day_prefix = date_str.replace("-", "_") + "_"
    todays = sorted(glob.glob(os.path.join(DAILY_DIR, day_prefix + "*.py")))
    replace = bool(os.environ.get("REPLACE") or os.environ.get("FORCE"))
    if todays and not replace:
        fail(3, "today's drop exists already: " + ", ".join(os.path.relpath(p, ROOT) for p in todays)
                + ". Do NOT pick a new title: one game per day. If today's game is good, go on with the git steps. "
                  "To replace it with a fixed game, run the same command again with REPLACE=1 in front.")

    with open(src, "r", encoding="utf-8") as f:
        code = f.read()
    check_game(src, code, filename)
    index_data = load_index()

    # Files that were already changed before this run (a drop that did not finish, or stray files):
    # `git add -A` would push them with today's commit. Say so; do not hide it.
    try:
        dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"], capture_output=True, text=True, timeout=20).stdout.splitlines()
        dirty = [line for line in dirty if not line[3:].startswith("scripts/")]      # tool changes are not drop leftovers
    except (OSError, subprocess.SubprocessError):
        dirty = []

    # ---- all checks passed: write ----
    removed = []
    if replace:
        for old in todays + sorted(glob.glob(os.path.join(PUBLIC_DAILY_DIR, day_prefix + "*.py"))):
            if os.path.abspath(old) not in (abs_path, public_abs_path):
                os.remove(old)
                removed.append(os.path.relpath(old, ROOT))
    header = f"# Daily Terminal Drop\n# Date: {date_str}\n# Title: {game_name}\n\n"
    os.makedirs(PUBLIC_DAILY_DIR, exist_ok=True)
    for path in (abs_path, public_abs_path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(code)

    update_log(date_str, game_name, rel_path)
    update_readme(date_str, game_name, rel_path)
    update_index(date_str, game_name, public_rel_path)
    update_index_json(index_data, date_str, game_name, rel_path, public_rel_path)

    data = {"date": date_str, "title": game_name, "file": rel_path,
            "public_file": public_rel_path}
    with open(LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    with open(PUBLIC_DAILY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"DATE={date_str}")
    print(f"TITLE={game_name}")
    print(f"FILE={rel_path}")
    print(f"PUBLIC_FILE={public_rel_path}")
    print(f"WRITTEN={len(code)} chars")
    print(f"SLUG={slug}")
    if removed:
        print("REPLACED (old files of today removed): " + ", ".join(removed))
    if dirty:
        print(f"WARNING: {len(dirty)} file(s) were changed or new BEFORE this publish; `git add -A` will commit them too. Look at them first:")
        for line in dirty[:15]:
            print("   " + line)


if __name__ == "__main__":
    main()
