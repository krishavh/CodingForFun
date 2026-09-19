# Daily Terminal Drop
# Date: 2026-09-19
# Title: The Empress's Taster: Blend for Honour

#!/usr/bin/env python3
"""THE EMPRESS'S TASTER - an original terminal tea-drafting game.

The Empress distrusts poison more each year, so she hires a new Court
Taster - you. Your craft is BLENDING: every dawn the palace market
offers a row of tea cards, you draft some, and at the courthouse you
steep a blend for the tasting. The closer your blend's spirit lands to
the Empress's secret desire (shown as a range on the scale), the more
honour you earn. Land outside the range and the cup is refused. Serve
one bitter cup too many and you are escorted from the palace.

THE SCALE
  A blend's SPIRIT is the sum of its leaves' points, weighted by how
  many leaves of that garden you used (a lone leaf speaks quietly; a
  pair of the same garden rings loud - you count that garden's total
  twice, a trio three times).

THE GARDENS (each card is a leaf with a fixed strength and a quirk)
  porcelain peony   2  - calm. Nothing special, always welcome.
  iron monk         3  - bitter on its own: if it is your ONLY garden
                        in the blend, the cup is refused outright.
  honey orchid      2  - sweetens: softens one point of bitterness
                        in the final cup (see below).
  river mist        1  - after drafting, lets you peek at the top
                        card of the deck (and it is drawn next dawn).
  imperial jasmine  4  - the pride of the court: worth honour
                        straight away (+1 honour the dawn you draft it).
  snake bitterleaf  0  - poison-adjacent: worth nothing steeped, but
                        while it sits in your POUCH the assassin skips
                        one midnight check (a shield you drink).
  gilded osmanthus  3  - fickle: loses 1 strength if you also steep
                        iron monk in the same cup.

THE ASSASSIN
  Each midnight the assassin strikes if your BITTERNESS reaches 3.
  Bitterness grows by 1 for every blend that was refused. A cup with
  iron monk in it carries +1 bitterness even when accepted.

THE MARKET
  5 leaves face up each dawn. Draft ONE per dawn - take a market leaf
  or draw blind from the deck - then the market slides left and the
  gap refills. Your pouch holds at most 6 leaves. When the pouch is
  full you MUST steep a blend (choose any 2 or 3 leaves from the
  pouch) before you may draft again.

THE TASTING
  Each dawn the Empress desires a different spirit, shown as a range
  like 8-11. Steep and she sips:
    inside the range .... +1 honour per point of spirit in the range
                           (a perfect blend pays more - see scoring)
    outside the range ... cup refused: bitterness +1, no honour.
  WIN: 12 honour before the eighth dawn ends the dynasty's thirst.
  LOSE: bitterness reaches 3 at midnight, or dawn nine arrives poor.
"""
import random

POUCH_MAX = 6
BLEND_MIN = 2
BLEND_MAX = 3
HONOUR_GOAL = 12
DAWNS = 8
MIDNIGHT_CHECK = 3

LEAVES = {
    "porcelain peony":  {"s": 2, "q": "calm; no quirk"},
    "iron monk":        {"s": 3, "q": "sole garden -> refusal; +1 bitterness even accepted"},
    "honey orchid":     {"s": 2, "q": "softens 1 bitterness when steeped"},
    "river mist":       {"s": 1, "q": "peek at top of deck when drafted"},
    "imperial jasmine": {"s": 4, "q": "+1 honour the dawn it is drafted"},
    "snake bitterleaf": {"s": 0, "q": "pouch shield: assassin skips one check"},
    "gilded osmanthus": {"s": 3, "q": "-1 strength if iron monk shares the cup"},
}


def spirit_of(leafnames):
    """Spirit of a blend: sum of strengths, gardens used 2+ times ring loud."""
    counts = {}
    for name in leafnames:
        counts[name] = counts.get(name, 0) + 1
    total = 0
    for name, n in counts.items():
        strength = LEAVES[name]["s"]
        if name == "gilded osmanthus" and counts.get("iron monk"):
            strength -= 1
        total += strength * n  # a pair counts twice, a trio three times
    return total


def bitterness_of(leafnames):
    b = 1 if "iron monk" in leafnames else 0
    if "honey orchid" in leafnames:
        b = max(0, b - 1)
    return b


def scoring(spirit, lo, hi):
    """Honour for a cup landing inside the range."""
    base = spirit - lo + 1
    bonus = 2 if spirit == lo or spirit == hi else 1
    return base * bonus


def desire(dawn):
    """Daily target range: opens gentle, tightens into the double digits."""
    ranges = [(4, 5), (5, 6), (5, 7), (6, 8), (7, 9), (8, 10), (9, 11),
              (10, 12)]
    return ranges[min(dawn, DAWNS) - 1]


def fmt_range(lo, hi):
    return f"{lo}-{hi}" if lo != hi else str(lo)


def show(pouch, market, dawn, honour, bitterness, shield, desire_lo, desire_hi):
    print()
    print(f"=== DAWN {dawn}/{DAWNS}   honour {honour}/{HONOUR_GOAL}   "
          f"bitterness {bitterness}/{MIDNIGHT_CHECK}   "
          f"{'SHIELD UP' if shield else 'no shield'} ===")
    print("Empress desires a spirit of " + fmt_range(desire_lo, desire_hi))
    print("Market: " + " | ".join(f"{i + 1}.{n}" for i, n in enumerate(market)))
    print("Pouch : " + (", ".join(f"{n}" for n in pouch) if pouch else "(empty)"))
    print("Steep : s <num>,<num>[,<num>]   Draft: 1-5 or d(raw)   "
          "Quit: q")


def scoring(spirit, lo, hi):
    """Honour for a cup landing inside the range."""
    base = spirit - lo + 1
    bonus = 2 if spirit == lo or spirit == hi else 1
    return base * bonus


def midnight(honour, bitterness, shield):
    print(f"\n  ~ midnight ~")
    if bitterness >= MIDNIGHT_CHECK:
        if shield:
            print("  The assassin slips in - but the snake bitterleaf's"
                  " aftertaste turns his knife. One check skipped.")
            return honour, bitterness - 1, False
        return None, bitterness, False
    print("  The palace sleeps uneasily, but you wake.")
    return honour, bitterness, shield


def game():
    deck = [n for n in LEAVES for _ in range(3)]
    random.shuffle(deck)
    market = [deck.pop() for _ in range(5)]
    pouch, honour, bitterness, shield = [], 0, 0, False
    final_honour = 0
    for dawn in range(1, DAWNS + 1):
        dlo, dhi = desire(dawn)
        while True:
            show(pouch, market, dawn, honour, bitterness, shield, dlo, dhi)
            cmd = input("> ").strip().lower()
            if cmd == "q":
                print("You set down the strainer and walk out of the "
                      "palace, unsipped.")
                return
            if cmd == "d":
                if len(pouch) >= POUCH_MAX:
                    print("  Pouch full - steep a blend first.")
                    continue
                pouch.append(deck.pop())
                if pouch[-1] == "river mist" and deck:
                    print(f"  The mist clears: next dawn's blind draw "
                          f"is {deck[-1]}.")
            elif cmd.isdigit() and 1 <= int(cmd) <= 5:
                if len(pouch) >= POUCH_MAX:
                    print("  Pouch full - steep a blend first.")
                    continue
                pouch.append(market.pop(int(cmd) - 1))
                market.insert(4, deck.pop())
                if pouch[-1] == "imperial jasmine":
                    honour += 1
                    print("  The court notes the jasmine: +1 honour.")
                if pouch[-1] == "river mist" and deck:
                    print(f"  The mist clears: next dawn's blind draw "
                          f"is {deck[-1]}.")
            elif cmd.startswith("s"):
                picks = [p.strip() for p in cmd[1:].split(",") if p.strip()]
                if not all(p.isdigit() and 1 <= int(p) <= len(pouch) for p in picks):
                    print("  Use leaf numbers from your pouch, e.g. s 1,3")
                    continue
                if not BLEND_MIN <= len(picks) <= BLEND_MAX:
                    print(f"  A blend needs {BLEND_MIN} to {BLEND_MAX} leaves.")
                    continue
                if len(picks) != len(set(picks)):
                    print("  The same leaf twice? You only own one.")
                    continue
                names = [pouch[int(p) - 1] for p in picks]
                if "iron monk" in names and len({n for n in names}) == 1:
                    print("  A lone iron monk is pure bitterness - the cup "
                          "is refused before she sips.")
                    bitterness += 1
                    continue
                sp = spirit_of(names)
                for p in sorted(map(int, picks), reverse=True):
                    pouch.pop(p - 1)
                bit = bitterness_of(names)
                if dlo <= sp <= dhi:
                    gained = scoring(sp, dlo, dhi)
                    honour += gained
                    final_honour = honour
                    if bit:
                        print("  The iron monk's bite lingers even in a "
                              "welcomed cup (+1 bitterness).")
                    print(f"  Spirit {sp} - the Empress closes her eyes and "
                          f"nods. +{gained} honour.")
                    bitterness += bit
                    break
                bitterness += bit + 1
                final_honour = honour
                print(f"  Spirit {sp} - she sets the cup aside, "
                      f"unspoken. Bitterness rises.")
                break
            else:
                print("  1-5 draft, d draw, s x,y steep, q quit.")
        honour, bitterness, shield = midnight(honour, bitterness, shield)
        if honour is None:
            print("\n  The cup nobody drank was yours. The palace has a "
                  "new taster by morning.")
            print(f"  FINAL: {final_honour}/{HONOUR_GOAL} honour when "
                  f"the night took you.")
            return
        if honour >= HONOUR_GOAL:
            suffix = "st" if dawn == 1 else "nd" if dawn == 2 else \
                     "rd" if dawn == 3 else "th"
            print(f"\n  On the {dawn}{suffix} dawn of your service, the "
                  f"Empress pours you a cup of your own blend.")
            print(f"  YOU WIN with {honour}/{HONOUR_GOAL} honour and "
                  f"bitterness {bitterness}/{MIDNIGHT_CHECK}.")
            return
    print(f"\n  Dawn nine. The dynasty still thirsts. You served "
          f"{honour}/{HONOUR_GOAL} honour.")
    print("  The Empress thanks you coolly and hires elsewhere. "
          "So close.")


if __name__ == "__main__":
    print("THE EMPRESS'S TASTER - blend for honour, dodge the assassin.\n")
    game()
