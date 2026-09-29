# Daily Terminal Drop
# Date: 2026-09-29
# Title: Mushroom Cellar: Hold the steps against the Mold Duke

#!/usr/bin/env python3
"""MUSHROOM CELLAR - a terminal deck-building fight against the Mold Duke.

You are a spore sprite defending your cellar from the MOLD DUKE.
Every night he sends a wave of molds. Fight them with MUSHROOMS!

Each night you pick 4 mushrooms from your satchel, then take turns:
  ->  PLAY a card (costs spores), or
  ->  REST (gain 2 spores), or
  ->  PREEN (heal 3 hp, once per fight), or
  ->  RUN (end the run, keep stars).

MUSHROOMS in your satchel (start with 4, buy new ones each dawn):
  puff     1: deal 2 damage
  shaggy   2: deal 5 damage
  inkcap   2: deal 3 damage and heal 1
  oyster   3: deal 4 damage and gain 1 spore back
  lion     3: deal 3 damage to EVERY mold in the wave
  slime    2: deal 2 damage and poison 2 (poison bites at turn end)
  chanter  4: deal 9 damage, big!

MOLDS get meaner each night. Beat a wave -> stars + pick a new mushroom.
Dead molds drop spores. When your hp hits 0 the cellar falls.

KEY: card numbers cost SPORES. You refill by resting. Plan the bloom!
"""
import random

FIGHTS = ["puff", "shaggy", "inkcap", "oyster", "lion", "slime", "chanter"]

CARDS = {
    "puff":    {"cost": 1, "txt": "2 dmg"},
    "shaggy":  {"cost": 2, "txt": "5 dmg"},
    "inkcap":  {"cost": 2, "txt": "3 dmg heal 1"},
    "oyster":  {"cost": 3, "txt": "4 dmg +1 spore"},
    "lion":    {"cost": 3, "txt": "3 dmg ALL molds"},
    "slime":   {"cost": 2, "txt": "2 dmg poison 2"},
    "chanter": {"cost": 4, "txt": "9 dmg"},
}

SHOP = ["shaggy", "inkcap", "oyster", "lion", "slime", "chanter"]

MOLD_NAMES = ["fuzz", "blotch", "smudge", "grody", "grubble", "mustio", " mildewking"]
MOLDS_ASCII = r"""
   __  __  _  _  ___  _  _   ___ ___  ___  ___ ___ ___
  / _||  \| || ||   \| || | / __| _ \| _ )/ __|_ _|_ _)
 | (_ | () | \/ | |) | \/ / \__ \  _/| _ \ (__ | | | |
  \__||__/|_||_||___/|_||_\ |___/_|  |___/\___|___|___|
           the molds send their duke
"""


def d6():
    return random.randint(1, 6)


class Run:
    def __init__(self):
        self.hp = 20
        self.max_hp = 20
        self.spores = 3
        self.stars = 0
        self.night = 1
        self.satchel = ["puff", "puff", "inkcap"]
        self.poison = 0
        self.preened = False
        self.molds = []
        self.pot = 0
        self.alive = True


def spawn_wave(run):
    n = min(2 + run.night // 2, 5)
    molds = []
    hp = 3 + run.night
    dmg = 1 + run.night // 3
    for i in range(n):
        name = random.choice(MOLD_NAMES).strip()
        molds.append({"name": f"{name} mold", "hp": hp, "dmg": dmg})
    return molds


def show(run):
    print()
    print(f"  NIGHT {run.night}  hp {run.hp}/{run.max_hp}  spores {run.spores}"
          f"  stars {run.stars}  poison {run.poison}")
    print("  ---")
    for i, m in enumerate(run.molds):
        print(f"  [{i}] {m['name']:14} hp {m['hp']:2}  (hits {m['dmg']})")
    if not run.molds:
        print("  (no molds left - the cellar breathes)")
    print("  ---")
    for i, c in enumerate(run.hand):
        print(f"  [{i}] {c:9} cost {CARDS[c]['cost']}  {CARDS[c]['txt']}")
    print("  commands: play <n> | rest | preen | run | status")


def draw_hand(run):
    run.hand = random.sample(run.satchel, min(4, len(run.satchel)))


def molds_turn(run):
    total = sum(m["dmg"] for m in run.molds)
    if total:
        print(f"\n  the molds surge! {total} damage.")
        run.hp -= total
    if run.poison:
        print(f"  poison bites the molds! {run.poison} damage.")
        for m in run.molds:
            m["hp"] -= run.poison
    dead = []
    i = 0
    while i < len(run.molds):
        m = run.molds[i]
        if m["hp"] <= 0:
            drop = 1 + (1 if d6() > 3 else 0)
            print(f"  {m['name']} burst! +{drop} spores")
            run.spores += drop
            dead.append(i)
            del run.molds[i]
        else:
            i += 1
    return dead


def play_card(run, i):
    if i < 0 or i >= len(run.hand):
        print("  no such card.")
        return False
    c = run.hand[i]
    cost = CARDS[c]["cost"]
    if run.spores < cost:
        print(f"  not enough spores for {c} (need {cost}).")
        return False
    run.spores -= cost
    run.hand.pop(i)
    dmg = {"puff": 2, "shaggy": 5, "inkcap": 3, "oyster": 4, "lion": 3, "slime": 2, "chanter": 9}[c]
    if c == "lion":
        for m in run.molds:
            m["hp"] -= dmg
        print(f"  lion's mane spores dust EVERY mold for {dmg}!")
    elif c == "slime":
        run.poison += 2
        if run.molds:
            run.molds[0]["hp"] -= dmg
        print(f"  slime mold creeps. poison {run.poison}. {dmg} to lead mold.")
    else:
        if run.molds:
            run.molds[0]["hp"] -= dmg
            print(f"  {c} pops! {dmg} to {run.molds[0]['name']}.")
        else:
            print(f"  {c} pops into empty air.")
    if c == "inkcap" and run.hp < run.max_hp:
        run.hp = min(run.max_hp, run.hp + 1)
        print("  you heal 1.")
    if c == "oyster":
        run.spores += 1
        print("  oyster glisters: +1 spore.")
    molds_turn_drops = []
    i = 0
    while i < len(run.molds):
        if run.molds[i]["hp"] <= 0:
            drop = 1
            print(f"  {run.molds[i]['name']} burst! +{drop} spore")
            run.spores += drop
            molds_turn_drops.append(i)
            del run.molds[i]
        else:
            i += 1
    return True


def wave_clear(run):
    if run.molds:
        return False
    print(f"\n  NIGHT {run.night} CLEARED. molds flee the cellar!")
    gain = 2 + run.night
    run.stars += gain
    print(f"  +{gain} stars!")
    return True


def shop_phase(run):
    print("\n  DAWN. pick a new mushroom for your satchel (or skip):")
    picks = random.sample(SHOP, 3)
    for i, c in enumerate(picks):
        print(f"  [{i}] {c:9} {CARDS[c]['txt']}")
    print("  [s] skip (heal 2)")
    while True:
        raw = input("  pick> ").strip().lower()
        if raw == "s":
            run.hp = min(run.max_hp, run.hp + 2)
            print("  rested among the moss. +2 hp")
            return
        if raw.isdigit() and int(raw) < 3:
            c = picks[int(raw)]
            run.satchel.append(c)
            print(f"  {c} joins the satchel!")
            return
        print("  ?")


def fight(run):
    run.molds = spawn_wave(run)
    run.poison = 0
    run.preened = False
    print(MOLDS_ASCII)
    print(f"  NIGHT {run.night}: {len(run.molds)} molds creep up the steps!")
    while True:
        if not run.molds:
            if wave_clear(run):
                return True
        draw_hand(run)
        while True:
            show(run)
            if run.hp <= 0:
                return False
            raw = input("  > ").strip().lower()
            if raw.startswith("play"):
                parts = raw.split()
                if len(parts) < 2 or not parts[1].isdigit():
                    print("  play <n>")
                    continue
                if play_card(run, int(parts[1])):
                    break
            elif raw == "rest":
                run.spores += 2
                print("  you rest among the spores. +2 spores.")
                break
            elif raw == "preen":
                if run.preened:
                    print("  already preened this fight!")
                    continue
                run.preened = True
                heal = 3
                run.hp = min(run.max_hp, run.hp + heal)
                print(f"  you preen your cap. +{heal} hp")
                break
            elif raw == "run":
                print("  you flee into the dark. run ends.")
                return False
            elif raw == "status":
                continue
            else:
                print("  play <n> | rest | preen | run | status")
        molds_turn(run)
        if run.hp <= 0:
            print("\n  the cellar falls silent... molds everywhere.")
            return False


def main():
    print(MOLDS_ASCII)
    print("  MOLD DUKE sends molds up the cellar steps each night.")
    print("  Build your mushroom satchel. Hold the steps!")
    run = Run()
    while run.alive:
        if not fight(run):
            break
        run.night += 1
        shop_phase(run)
    print(f"\n  RUN END  nights {run.night - 1}  stars {run.stars}")
    print(f"  satchel: {', '.join(sorted(set(run.satchel)))}")
    print("  the molds settle in... for now.")


if __name__ == "__main__":
    main()
