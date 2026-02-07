#!/usr/bin/env python3
import json
import os
import random
import re
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DAILY_DIR = os.path.join(ROOT, "terminal", "daily")
LOG_PATH = os.path.join(DAILY_DIR, "LOG.md")
LATEST_PATH = os.path.join(DAILY_DIR, ".latest.json")
PUBLIC_DAILY_PATH = os.path.join(ROOT, "public", "daily.json")
README_PATH = os.path.join(ROOT, "README.md")
INDEX_PATH = os.path.join(ROOT, "public", "index.html")
PUBLIC_DAILY_DIR = os.path.join(ROOT, "public", "daily")

ADJECTIVES = [
    "Amber",
    "Silent",
    "Crimson",
    "Velvet",
    "Neon",
    "Iron",
    "Arc",
    "Lunar",
    "Solar",
    "Obsidian",
    "Azure",
    "Golden",
]

NOUNS = [
    "Circuit",
    "Glyph",
    "Maze",
    "Beacon",
    "Vault",
    "Echo",
    "Harbor",
    "Cipher",
    "Prism",
    "Lantern",
    "Anvil",
    "Signal",
]

GAME_VARIANTS = ["signal_chase", "vault_code", "word_forge"]

SIGNAL_CHASE = """#!/usr/bin/env python3
import random

WIDTH = 9
HEIGHT = 7
PLAYER = "@"
TARGET = "*"
TRAP = "^"
EMPTY = "."


def clamp(val, low, high):
    return max(low, min(high, val))


def draw(px, py, tx, ty, traps, moves_left):
    print(f"Moves left: {moves_left}")
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if x == px and y == py:
                row.append(PLAYER)
            elif x == tx and y == ty:
                row.append(TARGET)
            elif (x, y) in traps:
                row.append(TRAP)
            else:
                row.append(EMPTY)
        print(" ".join(row))


def main():
    rng = random.Random(__SEED__)
    px, py = 0, HEIGHT - 1
    tx, ty = WIDTH - 1, 0
    traps = set()
    while len(traps) < 8:
        x = rng.randint(1, WIDTH - 2)
        y = rng.randint(1, HEIGHT - 2)
        if (x, y) in ((px, py), (tx, ty)):
            continue
        traps.add((x, y))

    moves_left = 18
    while moves_left > 0:
        draw(px, py, tx, ty, traps, moves_left)
        cmd = input("Move (W/A/S/D) or Q: ").strip().lower()
        if not cmd:
            continue
        if cmd[0] == "q":
            print("Signal lost.")
            return
        dx = dy = 0
        if cmd[0] == "w":
            dy = -1
        elif cmd[0] == "s":
            dy = 1
        elif cmd[0] == "a":
            dx = -1
        elif cmd[0] == "d":
            dx = 1
        else:
            print("Unknown command.")
            continue

        px = clamp(px + dx, 0, WIDTH - 1)
        py = clamp(py + dy, 0, HEIGHT - 1)
        moves_left -= 1

        if (px, py) in traps:
            print("You hit a trap. Signal lost.")
            return
        if px == tx and py == ty:
            print("Signal captured. You win.")
            return

    print("Out of moves. Signal fades.")


if __name__ == "__main__":
    main()
"""

VAULT_CODE = """#!/usr/bin/env python3
import random


def score_guess(secret, guess):
    exact = sum(1 for a, b in zip(secret, guess) if a == b)
    shared = sum(min(secret.count(d), guess.count(d)) for d in set(guess))
    return exact, shared - exact


def main():
    rng = random.Random(__SEED__)
    digits = [str(rng.randint(0, 9)) for _ in range(4)]
    secret = "".join(digits)
    tries = 8
    print("Vault Code")
    print("Guess the 4-digit code. Duplicates allowed.")

    while tries > 0:
        guess = input(f"[{tries} tries] > ").strip()
        if guess.lower() == "q":
            print("Vault sealed.")
            return
        if not (len(guess) == 4 and guess.isdigit()):
            print("Enter exactly 4 digits.")
            continue

        exact, near = score_guess(secret, guess)
        if exact == 4:
            print("Vault opened.")
            return
        print(f"Exact: {exact} | Near: {near}")
        tries -= 1

    print(f"Lockdown. Code was {secret}.")


if __name__ == "__main__":
    main()
"""

WORD_FORGE = """#!/usr/bin/env python3
import random

WORDS = __WORDS__


def scramble(word, rng):
    letters = list(word)
    rng.shuffle(letters)
    return "".join(letters)


def main():
    rng = random.Random(__SEED__)
    word = rng.choice(WORDS)
    scrambled = scramble(word, rng)
    tries = 5

    print("Word Forge")
    print("Unscramble the word. Type Q to quit.")
    print(f"Scramble: {scrambled}")

    while tries > 0:
        guess = input(f"[{tries} tries] > ").strip().lower()
        if guess == "q":
            print("Forge cools.")
            return
        if guess == word:
            print("Word reforged. You win.")
            return
        print("Not quite.")
        tries -= 1

    print(f"The word was '{word}'.")


if __name__ == "__main__":
    main()
"""

WORD_LIST = [
    "signal",
    "cipher",
    "ember",
    "shadow",
    "orbit",
    "lantern",
    "starlit",
    "vector",
    "flux",
    "prism",
    "echo",
    "ember",
]


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def ensure_block(text, start, end, new_block):
    if start in text and end in text:
        before = text.split(start)[0]
        after = text.split(end)[1]
        return before + start + "\n" + new_block + "\n" + end + after
    return text.rstrip() + "\n\n" + start + "\n" + new_block + "\n" + end + "\n"


def update_log(date_str, title, filename):
    header = "# Daily Terminal Drops\n\n"
    entry = f"- {date_str} — {title} (`{filename}`)\n"

    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(entry)
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        existing = f.readlines()

    if any(filename in line for line in existing):
        return

    if existing and existing[0].startswith("# Daily Terminal Drops"):
        existing = existing[:2] + [entry] + existing[2:]
    else:
        existing = [header, entry] + existing

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(existing)


def update_readme(date_str, title, rel_path):
    block = (
        f"Latest: {date_str} — {title} (`{rel_path}`)\n"
        f"See `terminal/daily/LOG.md` for history."
    )
    start = "<!-- DAILY_DROP_START -->"
    end = "<!-- DAILY_DROP_END -->"

    if not os.path.exists(README_PATH):
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    if "## Daily Terminal Drops" not in text:
        text = text.rstrip() + "\n\n## Daily Terminal Drops\n"

    new_text = ensure_block(text, start, end, block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)


def update_index(date_str, title, rel_path):
    card = (
        "        <article class=\"card\">\n"
        "          <h2>Daily Terminal Drop</h2>\n"
        f"          <p>{title} — {date_str}. Fresh terminal game released each morning.</p>\n"
        "          <div class=\"meta\">\n"
        "            <span>Terminal</span>\n"
        "            <span>Daily</span>\n"
        "            <span>Creative</span>\n"
        "          </div>\n"
        f"          <a class=\"cta\" href=\"{rel_path}\">View Today\'s Game</a>\n"
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

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)


def main():
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    seed = int(now.strftime("%Y%m%d"))
    rng = random.Random(seed)

    title = f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}"
    slug = slugify(f"{date_str}_{title}")
    filename = f"{slug}.py"
    rel_path = os.path.join("terminal", "daily", filename)
    abs_path = os.path.join(ROOT, rel_path)
    public_rel_path = os.path.join("daily", filename)
    public_abs_path = os.path.join(PUBLIC_DAILY_DIR, filename)

    created = not os.path.exists(abs_path)

    variant = rng.choice(GAME_VARIANTS)

    if variant == "signal_chase":
        content = SIGNAL_CHASE.replace("__SEED__", str(seed))
        game_name = f"{title}: Signal Chase"
    elif variant == "vault_code":
        content = VAULT_CODE.replace("__SEED__", str(seed))
        game_name = f"{title}: Vault Code"
    else:
        words = [w for w in WORD_LIST if len(w) >= 4]
        content = WORD_FORGE.replace("__SEED__", str(seed)).replace("__WORDS__", repr(words))
        game_name = f"{title}: Word Forge"

    if created:
        header = (
            "# Daily Terminal Drop\n"
            f"# Date: {date_str}\n"
            f"# Title: {game_name}\n\n"
        )
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(content)

    update_log(date_str, game_name, rel_path)
    update_readme(date_str, game_name, rel_path)
    update_index(date_str, game_name, public_rel_path)

    data = {"date": date_str, "title": game_name, "file": rel_path, "public_file": public_rel_path}
    with open(LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    with open(PUBLIC_DAILY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    os.makedirs(PUBLIC_DAILY_DIR, exist_ok=True)
    with open(abs_path, "r", encoding="utf-8") as src, open(public_abs_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())


if __name__ == "__main__":
    os.makedirs(DAILY_DIR, exist_ok=True)
    main()
