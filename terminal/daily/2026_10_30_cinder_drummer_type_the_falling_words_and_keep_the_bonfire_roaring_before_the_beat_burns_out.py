# Daily Terminal Drop
# Date: 2026-10-30
# Title: Cinder Drummer: Type the falling words and keep the bonfire roaring before the beat burns out

#!/usr/bin/env python3
"""CINDER DRUMMER - keep the rhythm, drum the falling words before the fire dies!

The bonfire crackles in four-four time. EMBER WORDS tumble down
toward the ash pit -- TYPE each one before it lands! Every word
you drum OUT feeds the flames +8 heat. A missed word dumps ash
on the fire -12 heat. Beat 250 heat to WIN THE NIGHT!

Legend (top -> bottom):
  " word "  an ember word, falling 1 row every BEAT
  *        a spark (bonus! type SPARK fast for +15 heat)
  ~        the ash line (words land here, fire fades)
  =        your drum kit (just you and the rhythm)

THE BEAT: every beat (1.6s) words fall. You type BETWEEN
  beats -- press ENTER to send. Faster typing = more heat!
  Perfect beat (under 1s) +5 bonus! Words get longer and
  faster as the fire roars higher.

SPARKS: random '*' sparks fly -- type SPARK to catch them.
 Miss 3 sparks and the night blows cold.

COMMANDS: type words + ENTER (q alone quits)
"""
import random
import subprocess
import time

WORDS = ["ash", "burn", "coal", "drum", "ember", "flame", "glow", "heat",
         "ignite", "jazz", "kindle", "low", "match", "night", "ounce",
         "pyre", "quiet", "roast", "spark", "toast", "under", "vibe",
         "warm", "axe", "burnt", "clang", "drift", "echo", "flare"]
GOAL = 250
FLOOR = 12
START_FPS = 1.6


def clear():
    print("\033[2J\033[H", end="")


def main():
    random.seed()
    heat = 40
    words = []          # [word, row, col]
    sparks = []         # [row, col]
    beats = 0
    miss = 0
    spark_miss = 0
    score = 0
    last = time.time()
    fps = START_FPS
    won = False
    dead = False
    grid = [[" "] * 40 for _ in range(FLOOR + 2)]
    t_word = time.time()

    print("CINDER DRUMMER -- type falling words, keep the fire alive!")
    input("press ENTER to start the beat...")

    while not dead and not won:
        now = time.time()
        # spawn
        if now - t_word > fps * 2:
            t_word = now
            w = random.choice(WORDS)
            col = random.randint(1, max(1, 36 - len(w)))
            words.append([w, 1, col])
            if random.random() < 0.3:
                sparks.append([1, random.randint(1, 36)])
        # move words down every beat
        if now - last > fps:
            last = now
            beats += 1
            for s in sparks:
                s[0] += 1
            sparks[:] = [s for s in sparks if s[0] < FLOOR]
            landed = [w for w in words if w[1] + 1 >= FLOOR]
            for w in landed:
                heat -= 12
                miss += 1
            words[:] = [w for w in words if w[1] + 1 < FLOOR]
            for w in words:
                w[1] += 1
            if beats % 12 == 0 and fps > 0.7:
                fps -= 0.08  # fire roars, beat quickens
            if heat <= 0:
                dead = True
        # draw
        clear()
        grid = [[" "] * 40 for _ in range(FLOOR + 2)]
        for r in range(FLOOR + 2):
            grid[r][0] = "|"
            grid[r][39] = "|"
        for w in words:
            r, c = w[1], w[2]
            for i, ch in enumerate(w[0]):
                if c + i < 39:
                    grid[r][c + i] = ch
        for s in sparks:
            if s[0] < FLOOR:
                grid[s[0]][s[1]] = "*"
        for c in range(1, 39):
            grid[FLOOR][c] = "~"
            grid[FLOOR + 1][c] = "="
        print("CINDER DRUMMER  heat:%d  goal:%d  beat: %.2fs  misses:%d  sparks missed:%d" %
              (heat, GOAL, fps, miss, spark_miss))
        for row in grid:
            print("".join(row))
        # input with timeout (poll Enter for 0.3s chunks so beat keeps rolling)
        deadline = time.time() + min(0.3, fps / 3)
        typed = ""
        while time.time() < deadline:
            # crude non-blocking check: use select on stdin
            import select
            import sys as _s
            r, _, _ = select.select([_s.stdin], [], [], 0.05)
            if r:
                ch = _s.stdin.readline()
                typed += ch.strip()
                break
        if typed:
            if typed == "q":
                print("you lay down the sticks. fire fades.")
                return
            t0 = time.time()
            hit = False
            for w in list(words):
                if w[0] == typed:
                    words.remove(w)
                    heat += 8
                    score += 10 * len(w[0])
                    if time.time() - t_word < 1.0:
                        heat += 5  # on the beat!
                        score += 25
                    hit = True
                    break
            if typed == "spark" and sparks:
                sparks.pop(0)
                heat += 15
                score += 50
                hit = True
            if not hit:
                heat -= 2  # wrong word, skins your knuckles
            # bonus speed check
            del t0
        if heat >= GOAL:
            won = True
        if miss >= 8:
            dead = True
    clear()
    for row in grid:
        print("".join(row))
    if won:
        print("\nTHE BONFIRE ROARS! night saved with %d pts! (%d beats, %d misses)" %
              (score, beats, miss))
    elif miss >= 8:
        print("\nburied in ash! %d pts, %d words missed." % (score, miss))
    else:
        print("\nfire died cold. %d pts, %d beats played." % (score, beats))


if __name__ == "__main__":
    subprocess.run(["stty", "sane"], capture_output=True)
    try:
        main()
    except KeyboardInterrupt:
        print("\n[drums silenced]")
