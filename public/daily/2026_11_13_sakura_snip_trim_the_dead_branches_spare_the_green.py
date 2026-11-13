# Daily Terminal Drop
# Date: 2026-11-13
# Title: Sakura Snip: Trim the dead branches, spare the green

# Daily Terminal Drop
# Date: 2026-11-13
#!/usr/bin/env python3
"""SAKURA SNIP - trim the bonsai, but only the dead branches!

You are a bonsai master. Branches grow on the tree.
GREEN branches are alive: LEAVE THEM!
BROWN branches are dead: SNIP THEM!
But young shoots (y) will turn green -- wait for them!

Each round branches pop up. Press the number of a DEAD
branch to snip it. Snip a GREEN branch? Ouch! Tree loses
health. Miss a dead branch? It rots the tree too!

Survive 12 rounds. Keep the tree alive!

COMMANDS: 1-9 snip branch   q quit
"""
import random
import sys
import time
import os
import tty
import termios
import select

TREE = r"""
        {4}
       {3}|
      {2}|   {5}
       {1} {0}
    ____|____
   \_________/  <- soil
"""

class Branch:
    def __init__(self, num, pos):
        self.num = num
        self.pos = pos
        self.state = "brown"  # brown, green, shoot
        self.age = 0

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def draw(branchies, health, round_no, msg):
    clear()
    spots = {b.num: "###" for b in branchies}
    chars = {}
    for b in branchies:
        if b.state == "green":
            chars[b.num] = "###"
        elif b.state == "shoot":
            chars[b.num] = "yyy"
        else:
            chars[b.num] = "###"
    tree = TREE
    for i in range(6):
        tree = tree.replace("{%d}" % i, chars.get(i, "   "))
    print(tree)
    print()
    for b in sorted(branchies, key=lambda x: x.num):
        tag = {"brown": "DEAD", "green": "GREEN", "shoot": "SHOOT"}[b.state]
        print("  [%d] %s branch" % (b.num, tag))
    print()
    print("  Tree health: %d  |  Round %d/12" % (health, round_no))
    print()
    if msg:
        print("  >> %s" % msg)
    print()
    print("  Snip a DEAD branch number (1-9), q to quit:")

def main():
    random.seed()
    health = 10
    msg = ""
    for rnd in range(1, 13):
        branchies = []
        count = random.randint(3, 5)
        nums = random.sample(range(6), count)
        for i, n in enumerate(nums):
            b = Branch(i, n)
            roll = random.random()
            if roll < 0.4:
                b.state = "brown"
            elif roll < 0.7:
                b.state = "green"
            else:
                b.state = "shoot"
            branchies.append(b)
        # shoot may turn green mid-round
        deadline = time.time() + 4.0
        answer = None
        while time.time() < deadline:
            draw(branchies, health, rnd, msg)
            print("  (%d sec left)" % max(0, int(deadline - time.time())))
            sys.stdout.flush()
            ready = []
            import select
            dr, _, _ = select.select([sys.stdin], [], [], 0.25)
            if dr:
                ch = sys.stdin.read(1)
                if ch and ch in "12345":
                    n = int(ch)
                    match = [b for b in branchies if b.num == n]
                    if match:
                        answer = n
                        break
                elif ch == "q":
                    print("Bye!")
                    return
        if answer is None:
            dead = [b for b in branchies if b.state == "brown"]
            if dead:
                health -= 1
                msg = "Too slow! A dead branch rots the tree. -1"
            else:
                msg = "Nice patience! All green this round."
        else:
            b = [x for x in branchies if x.num == answer][0]
            if b.state == "brown":
                msg = "SNIP! Dead branch gone. Clean cut!"
                branchies.remove(b)
                health = min(10, health + 1)
            elif b.state == "green":
                health -= 2
                msg = "OUCH! That branch was ALIVE! -2 health"
            else:
                b.state = "green"
                msg = "Shoot trimmed... it was turning green. -1 health"
                health -= 1
        if health <= 0:
            draw(branchies, 0, rnd, msg)
            print("  THE TREE DIED! Bonsai funeral at round %d." % rnd)
            time.sleep(2)
            return
        time.sleep(1.2)
    print()
    print("  SEASON COMPLETE! Tree health: %d" % health)
    if health >= 8:
        print("  MASTER GARDENER! The bonsai blooms!")
    elif health >= 4:
        print("  Healthy tree. Well trimmed.")
    else:
        print("  Barely alive... practice more.")
    time.sleep(2)

if __name__ == "__main__":
    try:
        tty.setcbreak(sys.stdin.fileno())
        main()
    except termios.error:
        main()
    finally:
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN,
                               termios.tcgetattr(sys.stdin.fileno()))
        except termios.error:
            pass
