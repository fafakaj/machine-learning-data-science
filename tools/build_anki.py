"""Build app/data/anki.json: the Anki cards the site shows in its own review (no Anki app needed).

Source: tools/content/anki_w1.py, the same list anki/make_week1_deck.py turns into the .apkg.
A card id is a hash of its front, so an edit of the back keeps the card's review history.
Cloze cards become a front with a gap and a back with the gap filled in.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from content.anki_w1 import CARDS  # noqa: E402

CLOZE = re.compile(r"\{\{c\d+::(.*?)(?:::(.*?))?\}\}")


def deck_name(full):
    # "ML::1 Python" -> "1 Python": plan.json names decks without the parent.
    return full.split("::", 1)[1] if "::" in full else full


def card(deck, kind, front, back):
    cid = hashlib.sha1(front.encode()).hexdigest()[:10]
    if kind == "cloze":
        gap = lambda m: f'<span class="cloze">[{m.group(2) or "…"}]</span>'  # noqa: E731
        fill = lambda m: f'<span class="cloze on">{m.group(1)}</span>'  # noqa: E731
        return {"id": cid, "deck": deck_name(deck), "front": CLOZE.sub(gap, front), "back": CLOZE.sub(fill, front)}
    return {"id": cid, "deck": deck_name(deck), "front": front, "back": back}


def main():
    cards = [card(deck, kind, front, back) for deck, kind, front, back, *_ in CARDS]
    ids = [c["id"] for c in cards]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"Одинаковые лицевые стороны у карточек: {sorted(dup)}")
    plan = json.loads((ROOT / "data" / "plan.json").read_text())
    decks = {c["deck"] for c in cards}
    wanted = {s["deck"] for w in plan["weeks"] for d in w["days"] for s in d["steps"] if s["type"] == "anki"}
    missing = wanted - decks - {"ML"}
    if missing:
        sys.exit(f"План ссылается на колоды, которых нет: {sorted(missing)}")
    out = ROOT / "data" / "anki.json"
    out.write_text(json.dumps({"cards": cards}, ensure_ascii=False, indent=1) + "\n")
    counts = {d: sum(c["deck"] == d for c in cards) for d in sorted(decks)}
    print(f"anki.json: {len(cards)} карточек {counts}")


if __name__ == "__main__":
    main()
