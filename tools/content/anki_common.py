"""Helpers for the Anki card lists (anki_w1.py ... anki_w4.py).

A list holds DAY(...) markers and cards. A card belongs to the last DAY above it: the plan date of
the theory it repeats. The site brings a card in only once the student has reached that day.
Card: (deck, kind, front, back); kind is "basic", "cloze" (front only) or "output" (front is code,
back is a comment; tools/build_anki.py runs the code and puts its real output on the back).
A card may end with KEEP("<id>"): the id of its old front. An edit of the front then keeps the card's
review history (the id is a hash of the front).
"""

import html


def c(s: str) -> str:
    """Встроенный код."""
    return f"<code>{html.escape(s)}</code>"


def pre(s: str) -> str:
    """Блок кода."""
    return f"<pre><code>{html.escape(s.strip())}</code></pre>"


def DAY(iso: str):
    return ("DAY", iso)


def KEEP(card_id: str):
    return {"id": card_id}


def with_days(items):
    """[DAY, card, card, DAY, ...] -> [(day, deck, kind, front, back, keep_id), ...]."""
    out, day = [], None
    for it in items:
        if it[0] == "DAY":
            day = it[1]
            continue
        if day is None:
            raise ValueError(f"карточка до первого DAY: {it[2][:60]}")
        deck, kind, front, back, *rest = it
        keep = next((r["id"] for r in rest if isinstance(r, dict)), None)
        out.append((day, deck, kind, front, back, keep))
    return out
