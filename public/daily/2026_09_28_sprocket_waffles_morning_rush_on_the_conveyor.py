# Daily Terminal Drop
# Date: 2026-09-28
# Title: Sprocket Waffles: Morning Rush on the Conveyor

# Daily Terminal Drop
# Date: 2026-09-28
# Title: Sprocket Waffles: Morning Rush on the Conveyor

#!/usr/bin/env python3
"""SPROCKET WAFFLES - a frantic terminal diner on a conveyor belt.

Morning rush at Sprocket Waffles! Plates of waffles ride in from the
left on a conveyor belt. Each plate holds an order:

  w  plain waffle      -> CATCH it and ship it! +cash
  s  syrup waffle      -> needs SYRUP first! +more cash
  ~  syrup bottle      -> grab it, you can hold 3
  #  gear              -> gears jam the belt! DODGE or lose time!
  @  flying fork       -> duck! (or lose 3 seconds)

YOU are the fork-lift chef (Y). Move with a/d (left/right), q/e (up/down).
Catch orders as they pass your row! Only plates in YOUR row get grabbed.

Survive the RUSH: earn $75 before the breakfast bell rings (60 sec).
Syrup waffles pay DOUBLE but ONLY if you are holding syrup.
Gears break your stance: -2 seconds. Forks: -3 seconds. Busy kitchen!

CONTROLS: a/d = left/right, q/e = up/down, x = use syrup on held plate,
          (just catch plates - syrup auto-uses when you grab one!)
"""
import random
import sys
import time

WIDTH, HEIGHT = 46, 6
GOAL = 75
CATCH_ROW_MESSAGE = True  # noqa: E501 (unused, keeps flake happy style)

# item chars
WAFFLE, SYRUP_W, SYRUP, GEAR, FORK = "w", "S", "!", "#", "@"


class Plate:
    def __init__(self, x, row, kind):
        self.x = x
        self.row = row
        self.kind = kind

    def ch(self):
        return {"w": "w", "S": "S", "!": "!", "#": "#", "@": "@"}[self.kind]


def spawn_kind(t):
    r = random.random()
    if r < 0.40:
        return WAFFLE
    if r < 0.62:
        return SYRUP_W
    if r < 0.80:
        return SYRUP
    if r < 0.92:
        return GEAR
    return FORK


def draw(px, py, items, msg, cash, syrup, tleft):
    rows = []
    for y in range(HEIGHT):
        line = ["."] * WIDTH
        for it in items:
            if it.row == y and 0 <= it.x < WIDTH:
                line[it.x] = it.ch()
        if y == py:
            line[px] = "Y"
        rows.append("|" + "".join(line) + "|")
    print("\n".join(rows))
    print(f"cash ${cash}/${GOAL}  syrup {syrup}/3  time {int(tleft)}s  {msg}")


def main():
    random.seed()
    px, py = WIDTH // 2, HEIGHT // 2
    items = []
    cash = 0
    syrup = 1
    start = time.time()
    LIMIT = 60
    spawn_timer = 0.0
    msg = "RUSH!"
    # crude non-blocking input: read single chars from stdin (terminal cooked)
    import select
    import tty

    fd = sys.stdin.fileno()
    try:
        tty.setcbreak(fd)
    except Exception:
        pass  # pipe input: falls back to line reads below
    buff = ""
    last_draw = 0.0
    print("\033[2J\033[H", end="")  # clear screen
    while True:
        now = time.time()
        tleft = LIMIT - (now - start)
        if tleft <= 0:
            break
        # spawn
        spawn_timer += 0.1
        if spawn_timer >= 0.55:
            spawn_timer = 0.0
            items.append(Plate(0, random.randrange(HEIGHT), spawn_kind(tleft)))
        # move items
        for it in items:
            it.x += 1
        # catch / collide
        msg_queue = []
        new_items = []
        for it in items:
            hit = (it.row == py and abs(it.x - px) <= 1)
            if not hit:
                if it.x < WIDTH:
                    new_items.append(it)
                continue
            if it.kind == WAFFLE:
                cash += 5
                msg_queue.append("+5 waffle!")
            elif it.kind == SYRUP_W:
                if syrup > 0:
                    syrup -= 1
                    cash += 10
                    msg_queue.append("+10 SYRUP WAFFLE!")
                else:
                    cash += 3
                    msg_queue.append("+3 dry waffle..(no syrup!)")
            elif it.kind == SYRUP:
                if syrup < 3:
                    syrup += 1
                    msg_queue.append("syrup +1")
                else:
                    msg_queue.append("syrup full!")
            elif it.kind == GEAR:
                start += 2
                msg_queue.append("GEAR! -2s")
            elif it.kind == FORK:
                start += 3
                msg_queue.append("FORK! -3s")
        items = new_items
        if msg_queue:
            msg = " ".join(msg_queue[:2])
        # draw ~10 fps
        if now - last_draw > 0.1:
            last_draw = now
            print(f"\033[{HEIGHT + 2}A", end="")
            draw(px, py, items, msg, cash, syrup, tleft)
        # input
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            ch = sys.stdin.read(1)
            if ch in ("a", "A"):
                px = max(0, px - 2)
            elif ch in ("d", "D"):
                px = min(WIDTH - 1, px + 2)
            elif ch in ("w", "W", "q", "Q"):
                py = max(0, py - 1)
            elif ch in ("s", "S", "e", "E"):
                py = min(HEIGHT - 1, py + 1)
            elif ch in ("x", "X", "\033", "m", "M", "p", "P"):
                break
        if cash >= GOAL:
            break
    try:
        tty.setnormal(fd)
    except Exception:
        pass
    elapsed = max(0, min(LIMIT, LIMIT - tleft))
    print(f"\nBell! Rush over in {int(elapsed)}s. Final cash: ${cash}")
    if cash >= GOAL:
        print("BREAKFAST SERVED! You are the Waffle Baron of Sprocket Street.")
    else:
        print("Short of the goal. The griddle remembers. Try again!")


if __name__ == "__main__":
    main()
