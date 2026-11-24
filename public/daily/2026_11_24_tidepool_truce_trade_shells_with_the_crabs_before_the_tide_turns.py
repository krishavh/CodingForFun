# Daily Terminal Drop
# Date: 2026-11-24
# Title: Tidepool Truce: Trade shells with the crabs before the tide turns

# Daily Terminal Drop
# Date: 2026-11-24
# Title: Tidepool Truce: Trade shells with the crabs before the tide turns

#!/usr/bin/env python3
"""TIDEPOOL TRUCE - barter with crabs before the tide rolls in!

Crumby tidepool. Crabs hold shells and want snacks.
You have 12 snacks and 60 seconds.
Each crab wants a shell you have (or none) and pays crumbs.
Deal at the right crab, or walk: tide rises every 8 seconds!
Keys: number = visit crab. b = buy shell (5 crumbs). q = quit.
Sell all shells before time runs out? Winner! Drowned? Splash.
"""
import random
import sys
import time

CRAB_NAMES = ["Pinchy", "Sideways", "Clawdia", "Bubble", "Snappy"]
SHELLS = ["coil", "limpet", "mussel", "whelk"]

SHELL_ART = {
    "coil":   ["   ____   ", "  / .-. \\ ", "  \\ '-' / ", "   '----' "],
    "limpet": ["    ___   ", "   /   \\  ", "  (_____) ", "          "],
    "mussel": ["   .---.  ", "  ( o_o ) ", "   '---'  ", "          "],
    "whelk":  ["    .--.  ", "   / () \\ ", "   | || | ", "   '--'--'"],
}


class Crab:
    def __init__(self, idx):
        self.name = CRAB_NAMES[idx]
        self.idx = idx + 1
        self.shell_in = random.choice(SHELLS + [None])
        self.shell_out = random.choice(SHELLS)
        self.price = random.randint(2, 9)
        self.done = False

    def line(self):
        want = self.shell_in or "none"
        has = "*" if self.done else "-"
        return "%d. %s [%s] wants %s for shell %s (%d crumbs)" % (
            self.idx, self.name, has, want, self.shell_out, self.price)


def bar(w=42):
    print("+" + "-" * w + "+")


def draw(shells, crumbs, secs, tide):
    sys.stdout.write("\x1b[2J\x1b[H")
    bar()
    print("| TIDEPOOL TRUCE" + " " * 27 + "|")
    bar()
    for name in SHELLS:
        art = SHELL_ART[name]
        count = shells.count(name)
        print(("| %s x%d" % (name.ljust(10), count)).ljust(41) + "|")
        for row in art:
            print("| " + row.ljust(40) + "|")
    bar()
    print(("| Crumbs: %d  Snacks: %d  Tide: %d/3  Time: %ds" % (
        crumbs, 12, tide, secs)).ljust(41) + "|")
    bar()


def main():
    random.seed()
    shells = ["coil"]
    crumbs = 0
    snacks = 12
    tide = 0
    start = time.time()
    DURATION = 60
    crabs = [Crab(i) for i in range(5)]

    while time.time() - start < DURATION:
        secs = int(DURATION - (time.time() - start))
        draw(shells, crumbs, secs, tide)
        for c in crabs:
            print(" " + c.line())
        print("\n b = buy random shell (5 crumbs)  q = quit")
        print(" Tide rises every 8s! At 3 you are soaked (game ends).")
        print("\nCommand (crab #, b, q): ")
        sys.stdout.flush()
        # tiny non-blocking-ish: read with timeout via select
        import select
        r, _, _ = select.select([sys.stdin], [], [], 1.0)
        if r:
            cmd = sys.stdin.readline().strip().lower()
            if cmd == "q":
                print("\nBye! The crabs wave goodbye.")
                return
            elif cmd == "b":
                if crumbs >= 5:
                    crumbs -= 5
                    s = random.choice(SHELLS)
                    shells.append(s)
                    print(" Bought a %s shell!" % s)
                    time.sleep(0.6)
                else:
                    print(" Not enough crumbs!")
                    time.sleep(0.6)
            elif cmd.isdigit() and 1 <= int(cmd) <= 5:
                c = crabs[int(cmd) - 1]
                if c.done:
                    print(" %s already traded." % c.name)
                    time.sleep(0.6)
                else:
                    need = c.shell_in
                    if need and need not in shells:
                        print(" %s wants a %s shell first!" % (c.name, need))
                        time.sleep(0.6)
                    else:
                        if need:
                            shells.remove(need)
                        shells.append(c.shell_out)
                        crumbs += c.price
                        c.done = True
                        print(" %s trades! +%d crumbs, got %s shell" % (
                            c.name, c.price, c.shell_out))
                        time.sleep(0.6)
        # tide
        elapsed = time.time() - start
        new_tide = int(elapsed // 8)
        if new_tide != tide:
            tide = new_tide
            print("\n ~ The tide rises! Level %d ~" % (tide + 1))
            time.sleep(0.8)
        if tide >= 3:
            print("\n SPLASH! The tide soaked your shells.")
            print(" Final: %d crumbs, %d shells" % (crumbs, len(shells)))
            return
        if all(c.done for c in crabs):
            print("\n ALL CRABS TRADED! You master the tidepool!")
            print(" Final: %d crumbs, %d shells in %ds" % (
                crumbs, len(shells), int(elapsed)))
            return
    print("\n Time! Tidepool closes. Final: %d crumbs, %d shells" % (
        crumbs, len(shells)))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
