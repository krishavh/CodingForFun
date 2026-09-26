# Daily Terminal Drop
# Date: 2026-09-26
# Title: Lanternmouth Lagoon: Night-fishing memory game

#!/usr/bin/env python3
"""LANTERNMOUTH LAGOON - an original terminal memory & push-your-luck fishing game.

You are a night-fisher on a black lagoon where one ancient fish -- the
LANTERNMOUTH -- glows beneath the surface. Six fishing spots lie in a row,
and every cast into a spot pulls up the top card of that spot's face-down
deck. Memorize what you've seen, because each spot's deck holds different
fish, and decks do NOT refill between nights.

HOW A NIGHT WORKS
  Pick a spot, draw its top card face-up, choose to KEEP it (bank its
  shine in your creel) or CAST again. Every extra cast that night wakes
  the Lanternmouth: its dread rises by 1. Each spot has a dread cap --
  push past it and the LANTERNMOUTH LUNGES, tearing every card you kept
  that night out of your creel and ending the night on the spot.

  So you want to hop between safe spots... but decks drain, and a card
  you left face-up in your hand is lost the moment you cast elsewhere.

THE SIX SPOTS (each deck has its own personality)
  Reeds      (6 cards) small honest fish; the only home of the humble
             Minnow -- and only ONE Eel hides here.
  Oyster Bed (6) three Pearls, pure shine -- but one card is a CRAB that
             snips your smallest kept fish out of the creel.
  Kelp Gate  (5) lean water: two Big Blues, two Eels, one Glass Koi.
  Sunken Pew (5) drowned chapel: shine-heavy, but the WRAITH card ends
             your night immediately (no lunge, you keep what you kept).
  Buoy 7     (4) deep water: two Big Blues, a Pearl, and one Eel.
  The Riptide(3) one colossal Lanternmouth (18 shine!), one Eel, one
             Wraith, and a dread cap of 1. Pure gamble.

NIGHTS & THE WIN
  You fish for 4 nights; decks do not refill, so the lagoon thins as you
  go. Between nights the deep cools (global dread -1). Score is the shine
  of everything in your creel at dawn. 25+ shine lights the village's
  lanterns in your honour; 12+ earns the harbourmaster's single nod.
"""
import random
import sys

CARDS = {
    # name: (shine, hooktext)  hooktext shown when drawn
    "Silver Minnow": (2, "slips into the creel easily"),
    "Brass Perch": (3, "its scales clink like coins"),
    "Glass Koi": (4, "you can see its heartbeat"),
    "Pearl": (5, "round and warm as a streetlamp"),
    "Big Blue": (6, "it fights the whole way up"),
    "Eel": (0, "it stares at you, unblinking"),
    "Crab": (-1, "snip! it takes your smallest kept fish"),
    "Wraith": (0, "the water goes cold..."),
    "The Lanternmouth": (18, "the whole lagoon glows"),
}

SPOT_ORDER = ["Reeds", "Oyster Bed", "Kelp Gate", "Sunken Pew", "Buoy 7", "The Riptide"]
DECKS = {
    "Reeds":       ["Silver Minnow", "Brass Perch", "Silver Minnow", "Glass Koi", "Eel", "Brass Perch"],
    "Oyster Bed":  ["Pearl", "Pearl", "Glass Koi", "Crab", "Silver Minnow", "Pearl"],
    "Kelp Gate":   ["Big Blue", "Eel", "Glass Koi", "Big Blue", "Eel"],
    "Sunken Pew":  ["Brass Perch", "Pearl", "Wraith", "Glass Koi", "Big Blue"],
    "Buoy 7":      ["Big Blue", "Eel", "Big Blue", "Pearl"],
    "The Riptide": ["The Lanternmouth", "Eel", "Wraith"],
}
SPOT_MAXDREAD = {"Reeds": 4, "Oyster Bed": 3, "Kelp Gate": 3, "Sunken Pew": 2, "Buoy 7": 2, "The Riptide": 1}


def new_deck(name):
    d = DECKS[name][:]
    random.shuffle(d)
    return d


def spot_report(name, deck):
    seen = {}
    for c in deck:
        seen[c] = seen.get(c, 0) + 1
    bits = [f"{c} x{n}" for c, n in seen.items()]
    return f"{name:<11} {len(deck)} unseen | " + ", ".join(bits)


def play():
    print("\n" + "=" * 62)
    print("   L A N T E R N M O U T H   L A G O O N".center(62))
    print("   a night-fishing memory game".center(62))
    print("=" * 62)
    creel = []          # cards kept across all nights
    nights = 4
    for night in range(1, nights + 1):
        print(f"\n--- NIGHT {night} of {nights} ---")
        print("Spots (what's still UNSEEN in each deck):")
        decks = {n: new_deck(n) for n in SPOT_ORDER}
        alive = [n for n in SPOT_ORDER if decks[n]]
        if not alive:
            print("Every deck in the lagoon is fished dry. It rests.")
            break
        for n in alive:
            print("  " + spot_report(n, decks[n]))
        dread = 0          # dread earned THIS night
        night_creel = []   # cards banked this night (can be lost to a lunge)
        current = None     # card in hand, not yet kept
        fled = False
        while True:
            kept_shine = sum(CARDS[c][0] for c in night_creel)
            print(f"\nCreel shine tonight: {kept_shine} | Dread {dread} | Kept: {len(night_creel)}")
            spots_alive = [n for n in SPOT_ORDER if decks[n]]
            if not spots_alive:
                print("Every deck is fished dry. The lagoon rests.")
                break
            for n in spots_alive:
                mark = " <-" if n == current and False else ""  # (spot of hand shown below)
                hand = f"  hand: {current}" if current else ""
                print(f"  [{n}] {len(decks[n])} left{mark}")
            if current:
                print(f"  In hand: {current} (shine {CARDS[current][0]}) - (k)eep it or cast elsewhere")
            cmd = input("Cast into which spot, (k)eep hand, or (q)uit: ").strip().lower()
            if cmd == "q":
                creel.extend(night_creel)
                return finish(creel, early=True)
            if cmd == "k":
                if current is None:
                    print("Nothing in hand to keep.")
                    continue
                if current in ("Wraith", "Crab"):
                    print("That isn't for keeping. Toss it back.")
                    current = None
                    continue
                night_creel.append(current)
                print(f"Kept: {current} (+{CARDS[current][0]} shine)")
                current = None
                continue
            chosen = None
            for n in SPOT_ORDER:
                if cmd and (cmd == n.lower() or cmd == n.lower().split()[0]):
                    chosen = n
                    break
            if chosen is None or chosen not in spots_alive:
                print("That spot is empty or unknown. Try a spot name, 'k', or 'q'.")
                continue
            card = decks[chosen].pop()
            shine, hook = CARDS[card]
            print(f"\n>>> {chosen}: you draw the {card} -- {hook}" + (f". Shine {shine}." if shine else "."))
            if card == "Wraith":
                print("The wraith brushes your lantern. Your night ends HERE.")
                fled = True
                break
            if card == "Crab":
                if night_creel:
                    smallest = min(night_creel, key=lambda c: CARDS[c][0])
                    print(f"The crab snips the {smallest} out of your creel!")
                    night_creel.remove(smallest)
                else:
                    print("The crab finds an empty creel and sulks.")
                current = None
                continue
            # keep-or-skip decision: casting again (rather than keeping) wakes the deep
            if current is not None:
                dread += 1
                if dread > SPOT_MAXDREAD[chosen]:
                    print("The water shudders... the LANTERNMOUTH LUNGES!")
                    print(f"Your {len(night_creel)} kept card(s) this night tear free and vanish.")
                    night_creel = []
                    fled = True
                    break
            current = card
        if not fled:
            creel.extend(night_creel)
            print(f"Night {night} safe. Creel now holds {len(creel)} card(s) overall.")
    return finish(creel)


def finish(creel, early=False):
    total = sum(CARDS[c][0] for c in creel)
    print("\n" + "=" * 62)
    print("   DAWN".center(62))
    print("=" * 62)
    if early:
        print("(You rowed home early.)")
    if creel:
        print("Creel contents:")
        for c in sorted(creel, key=lambda c: -CARDS[c][0]):
            print(f"   {c}  ({CARDS[c][0]})")
    else:
        print("Your creel is empty. The lagoon keeps its secrets.")
    print(f"\nFINAL SHINE: {total}")
    if total >= 25:
        print("The village lights every lantern in your honour.")
    elif total >= 12:
        print("A fine catch. The harbourmaster nods once -- high praise.")
    else:
        print("The lagoon won this time.")
    print("Thanks for fishing.")


if __name__ == "__main__":
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print("\nYou slip the oars into the dark. Goodnight.")
        sys.exit(0)
