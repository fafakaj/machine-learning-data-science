"""Helpers for the Anki card lists (anki_w1.py ... anki_w4.py).

A list holds DAY(...) markers and cards. A card belongs to the last DAY above it: the plan date of
the theory it repeats. The site brings a card in only once the student has reached that day.
Card: (deck, kind, front, back); kind is "basic", "cloze" (front only) or "output" (front is code,
back is a comment; tools/build_anki.py runs the code and puts its real output on the back).
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


def with_days(items):
    """[DAY, card, card, DAY, ...] -> [(day, deck, kind, front, back), ...]."""
    out, day = [], None
    for it in items:
        if it[0] == "DAY":
            day = it[1]
            continue
        if day is None:
            raise ValueError(f"карточка до первого DAY: {it[2][:60]}")
        deck, kind, front, back, *_ = it
        out.append((day, deck, kind, front, back))
    return out
