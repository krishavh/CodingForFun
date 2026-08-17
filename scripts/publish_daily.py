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
"""
import json
import os
import re
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


def update_log(date_str, game_name, rel_path):
    line = f"- **{date_str}** — {game_name} — `{rel_path}`\n"
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if f"- **{date_str}**" in content:
            content = re.sub(r"- \*\*%s\*\*.*" % date_str, line.rstrip("\n"), content, count=1)
        else:
            content = line + content
    else:
        content = "# Daily Terminal Drops\n\n" + line
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def update_readme(date_str, game_name, rel_path):
    if not os.path.exists(README_PATH):
        return
    with open(README_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    current = text
    pattern = re.compile(r"(Today's drop[^\n]*\n)(.*)", re.S)
    first_para = f"**{game_name}** — {date_str} — `{rel_path}`\n"
    if pattern.search(text):
        text = pattern.sub(lambda m: m.group(1) + first_para + m.group(2), text, count=1)
    elif "Today's drop" in text or "Latest" in text:
        text = text + "\nUpdated today's drop: " + first_para
    else:
        text = text + "\n## Latest drop\n\n" + first_para
    if text != current:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(text)


def update_index(date_str, game_name, public_rel_path):
    rel_path = os.path.join("daily", os.path.basename(public_rel_path))
    card = (
        "        <article class=\"card\">\n"
        "          <h3>"
        + game_name
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


def update_index_json(date_str, title, rel_path, public_rel_path):
    entry = {
        "date": date_str,
        "title": title,
        "file": rel_path,
        "public_file": public_rel_path,
    }
    data = []
    if os.path.exists(INDEX_JSON_PATH):
        try:
            with open(INDEX_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    if not any(item.get("date") == date_str for item in data):
        data.append(entry)
    data = sorted(data, key=lambda item: item.get("date", ""), reverse=True)
    with open(INDEX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.makedirs(PUBLIC_DAILY_DIR, exist_ok=True)
    with open(PUBLIC_DAILY_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src = os.path.abspath(sys.argv[1])
    title = sys.argv[2]
    subtitle = sys.argv[3] if len(sys.argv) > 3 else ""
    if not os.path.exists(src):
        print(f"ERROR: source not found: {src}")
        sys.exit(2)

    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    game_name = f"{title}: {subtitle}" if subtitle else title
    slug = slugify(f"{date_str}_{title}{'_' + slugify(subtitle) if subtitle else ''}")
    filename = f"{slug}.py"

    rel_path = os.path.join("terminal", "daily", filename)
    public_rel_path = os.path.join("daily", filename)
    abs_path = os.path.join(ROOT, rel_path)
    public_abs_path = os.path.join(PUBLIC_DAILY_DIR, filename)

    if os.path.exists(abs_path) and not os.environ.get("FORCE"):
        print(f"ERROR: {abs_path} already exists (set FORCE=1 to overwrite)")
        sys.exit(3)

    # Compile-check the authored game before publishing anything.
    with open(src, "r", encoding="utf-8") as f:
        code = f.read()
    compile(code, filename, "exec")  # raises SyntaxError on bad code

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Terminal Drop\n# Date: {date_str}\n# Title: {game_name}\n\n")
        f.write(code)
    os.makedirs(PUBLIC_DAILY_DIR, exist_ok=True)
    with open(public_abs_path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Terminal Drop\n# Date: {date_str}\n# Title: {game_name}\n\n")
        f.write(code)

    update_log(date_str, game_name, rel_path)
    update_readme(date_str, game_name, rel_path)
    update_index(date_str, game_name, public_rel_path)
    update_index_json(date_str, game_name, rel_path, public_rel_path)

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


if __name__ == "__main__":
    main()
