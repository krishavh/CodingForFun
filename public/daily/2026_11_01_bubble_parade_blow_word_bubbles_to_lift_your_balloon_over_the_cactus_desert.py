# Daily Terminal Drop
# Date: 2026-11-01
# Title: Bubble Parade: Blow word-bubbles to lift your balloon over the cactus desert

#!/usr/bin/env python3
"""BUBBLE PARADE - blow word-bubbles to lift your balloon over the desert!

You float a HOT AIR BALLOON across a cactus desert. Speak WORDS to
blow BUBBLES -- each letter you type makes a bubble that LIFTS you!
But spikes wait below, and your balloon leaks. Fly 5 FLAGS to win!

Legend:
  B  your balloon (rising on bubble lift!)
  ^  cactus spike (touch = -1 bubble bag, ouch!)
  F  flag (fly into it to claim it! 5 flags = WIN)
  .  sky (nothing)
  _  ground (sand, bumpy but safe)

HOW IT WORKS:
  Your balloon FALLS 1 row each beat (leaky balloon!). Type a
  word + ENTER: each LETTER makes a bubble = +1 lift row!
  Longer words = BIGGER lift, but each word costs 1 bubble
  from your bag (start 10, +1 per flag).

  Fly UP into FLAGS. Fall to the ground? bounce, keep going!
  Fall on a CACTUS SPIKE? lose a bubble bag (-1) and bounce!

  Every 12 beats a WIND GUST shoves you -- duck or drift!

SKY RULE: rows 1-8 are sky. Row 9 is the ground. Spikes sit
  on the ground in your path. Bag empty? PUFF with 'a' (free,
  +1 lift, but tire: -1 point).

SCORE: +50 per flag, +10 per spare bubble bag at win.

COMMANDS: type word + ENTER (a = puff, q alone quits)
"""
import random
import time

W = 48
SKY_TOP = 1
GROUND = 9
START_BAG = 10
WIN_FLAGS = 5
BEAT = 0.45

WORDS = ["air", "blow", "cloud", "drift", "float", "gust", "high",
         "inflate", "jet", "kite", "lift", "mist", "noun", "puff",
         "rise", "soar", "up", "wind", "zeppelin", "balloon", "cactus"]


def make_spikes(rnd):
    return sorted(rnd.randint(6, W - 6) for _ in range(4))


def make_flags(rnd, spikes):
    flags = []
    while len(flags) < WIN_FLAGS:
        c = rnd.randint(8, W - 4)
        if all(abs(c - s) > 3 for s in spikes) and all(abs(c - f) > 5 for f in flags):
            flags.append(c)
    return flags


def draw(row, col, spikes, flags, flags_got, bag, pts, beat_no, msg):
    rows = []
    for r in range(GROUND + 1):
        line = ["."] * W
        if r == GROUND:
            line = ["_"] * W
        for s in spikes:
            if r >= GROUND - 1:
                line[s] = "^"
        for f in flags:
            if r == 2 and f not in flags_got:
                line[f] = "F"
        if r == row:
            if 0 <= col < W:
                line[col] = "B"
        rows.append(" ".join(line).rstrip())
    print("\033[2J\033[H", end="")
    print("BUBBLE PARADE - desert balloon lift!")
    print("pts:%d  bag:%d  flags:%d/%d  beat:%d" %
          (pts, bag, len(flags_got), WIN_FLAGS, beat_no))
    print("rows 1-9 (9=ground):")
    for i, line in enumerate(rows[1:], start=1):
        print("%d|%s" % (i, line))
    print(msg)
    print("type word + ENTER (a=puff, q=quit): ", end="", flush=True)


def main():
    rnd = random.Random()
    row, col = 4, 2
    bag, pts = START_BAG, 0
    flags_got = []
    spikes = make_spikes(rnd)
    flags = make_flags(rnd, spikes)
    beat_no = 0
    msg = "welcome! type words to BLOW BUBBLES and lift!"
    print("\033[2J\033[H", end="")
    print("BUBBLE PARADE!")
    print("Type words. Each letter = 1 bubble = 1 lift row.")
    print("Press ENTER between words. q alone quits.")
    input("ready? ENTER to fly! ")
    next_beat = time.time()
    word = ""
    while True:
        now = time.time()
        if now >= next_beat:
            beat_no += 1
            next_beat = now + BEAT
            if row < GROUND:
                row += 1  # leaky balloon falls
            if row >= GROUND and col in spikes:
                bag = max(0, bag - 1)
                pts = max(0, pts - 5)
                msg = "OUCH! cactus spike! -1 bag, bounce!"
            if beat_no % 12 == 0 and col < W - 1:
                col += 1  # gust shoves you
                msg = "WIND GUST! shoved 1 column!"
            if col >= W - 1:
                msg = "desert ends! fly UP to flags!"
            draw(row, col, spikes, flags, flags_got, bag, pts, beat_no, msg)
        if row <= GROUND:
            word = input()
            word = word.strip().lower()
            if word == "q":
                msg = "flew home! final:%d pts" % pts
                print("\n" + msg)
                return
            if word == "a":
                row = max(1, row - 1)
                pts = max(0, pts - 1)
                msg = "PUFF! +1 lift (tired, -1 pt)"
            elif word:
                if bag > 0:
                    lift = len(word)
                    row = max(1, row - lift)
                    bag -= 1
                    pts += lift
                    msg = "%d bubbles! +%d lift, +%d pts" % (lift, lift, lift)
                else:
                    msg = "bag empty! press a to puff"
            else:
                msg = "(air)"
            newc = min(col + 1, W - 1)
            if newc != col and row < GROUND:
                col = newc  # drift forward while flying
            for f in flags:
                if f not in flags_got and abs(col - f) <= 1 and row <= 3:
                    flags_got.append(f)
                    bag += 1
                    pts += 50
                    msg = "FLAG! +%d (total %d/%d) +1 bag!" % (
                        50, len(flags_got), WIN_FLAGS)
            if len(flags_got) >= WIN_FLAGS:
                print("\033[2J\033[H", end="")
                print("YOU WIN! 5 flags! pts:%d (+%d spare bags)" %
                      (pts, bag * 10))
                pts += bag * 10
                print("FINAL: %d pts in %d beats!" % (pts, beat_no))
                return
        else:
            time.sleep(0.05)


if __name__ == "__main__":
    main()
