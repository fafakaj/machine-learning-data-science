"""Build app/data/anki.json: the Anki cards of month 1 for the site's own review (no Anki app needed).

Source: tools/content/anki_w1.py ... anki_w4.py; anki/make_month1_deck.py turns this json into an .apkg.
Each card has the plan date of its theory: the site brings it in only once the student reaches that day.
A card id is a hash of its front, so an edit of the back keeps the card's review history.
Cloze cards become a front with a gap and a back with the gap filled in.
"Output" cards are run here: the back shows what the code really prints (numpy and pandas are the
versions the site runs in Pyodide, see build_all.sh).
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from content import anki_w1, anki_w2, anki_w3, anki_w4  # noqa: E402
from content.anki_common import pre, with_days  # noqa: E402

CLOZE = re.compile(r"\{\{c\d+::(.*?)(?:::(.*?))?\}\}")


def short_deck(full):
    # "ML::1 Python" -> "1 Python": plan.json names decks without the parent.
    return full.split("::", 1)[1] if "::" in full else full


def run(code):
    r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=60)
    if r.returncode:
        sys.exit(f"Код карточки упал:\n{code}\n{r.stderr}")
    return r.stdout.rstrip("\n")


def card(day, deck, kind, front, back):
    base = {"day": day, "deck": short_deck(deck), "deck_full": deck}
    if kind == "output":
        front = "Что выведет код?" + pre(code := front)
        back = pre(run(code)) + (f" {back}" if back else "")
    cid = hashlib.sha1(front.encode()).hexdigest()[:10]
    if kind == "cloze":
        gap = lambda m: f'<span class="cloze">[{m.group(2) or "…"}]</span>'  # noqa: E731
        fill = lambda m: f'<span class="cloze on">{m.group(1)}</span>'  # noqa: E731
        return {"id": cid, **base, "kind": "cloze", "front": CLOZE.sub(gap, front), "back": CLOZE.sub(fill, front), "cloze": front}
    return {"id": cid, **base, "kind": "basic", "front": front, "back": back}


def main():
    items = [x for m in (anki_w1, anki_w2, anki_w3, anki_w4) for x in with_days(m.CARDS)]
    cards = [card(*x) for x in items]
    # New cards come in plan order: by day, then as written.
    cards.sort(key=lambda c: c["day"])

    ids = [c["id"] for c in cards]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"Одинаковые лицевые стороны у карточек: {sorted(dup)}")
    plan = json.loads((ROOT / "data" / "plan.json").read_text())
    dates = {d["date"] for w in plan["weeks"] for d in w["days"]}
    bad_days = {c["day"] for c in cards} - dates
    if bad_days:
        sys.exit(f"Дни карточек вне плана: {sorted(bad_days)}")
    unclosed = [c["front"][:60] for c in cards if c["kind"] == "basic" and not c["back"].strip()]
    if unclosed:
        sys.exit(f"Карточки без оборота: {unclosed}")
    out = ROOT / "data" / "anki.json"
    out.write_text(json.dumps({"cards": cards}, ensure_ascii=False, indent=1) + "\n")
    decks = {}
    for c in cards:
        decks[c["deck"]] = decks.get(c["deck"], 0) + 1
    print(f"anki.json: {len(cards)} карточек {decks}")


if __name__ == "__main__":
    main()
