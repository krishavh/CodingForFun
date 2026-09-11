# Daily Terminal Drop
# Date: 2026-09-08
# Title: Lantern Vale: Rune Cartographer

#!/usr/bin/env python3
"""Lantern Vale: Rune Cartographer - carve a map's runes before the dark closes in."""
import random, sys

W, H = 8, 6
RUNES = "ᚠᚢᚦᚨᚱᚲᚷᚹ"

def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    grid = [["." for _ in range(W)] for _ in range(H)]
    px, py = 0, H - 1
    torch = 25
    carved = set()
    # 4 hidden runes
    spots = rng.sample([(x, y) for x in range(W) for y in range(H) if (x, y) != (px, py)], 4)
    runes_at = {s: RUNES[i] for i, s in enumerate(spots)}
    print("Carve the runes! Move with WASD, press SPACE to carve your tile. Torch: %d" % torch)
    while torch > 0:
        print("-" * (W * 2 + 1))
        for y in range(H):
            row = []
            for x in range(W):
                if (x, y) == (px, py):
                    row.append("@")
                elif (x, y) in carved:
                    row.append(runes_at.get((x, y), "o"))
                else:
                    row.append(".")
            print(" ".join(row))
        cmd = input("move/carve/quit> ").strip().lower()
        if cmd == "quit":
            print("You leave the vale. Runes carved:", len(carved))
            return
        if cmd == "carve":
            if (px, py) in carved:
                print("Already carved.")
                continue
            carved.add((px, py))
            torch -= 2
            if (px, py) in runes_at:
                print("A rune glows:", runes_at[(px, py)])
                if len(carved) >= 4 and all(s in carved for s in runes_at):
                    print("ALL RUNES CARVED! The vale is mapped. Torch left:", torch)
                    return
            continue
        dx, dy = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}.get(cmd, (0, 0))
        px, py = max(0, min(W - 1, px + dx)), max(0, min(H - 1, py + dy))
        torch -= 1
    print("The dark takes you. Runes carved:", len(carved))

main()
