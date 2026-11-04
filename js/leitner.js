// Leitner boxes, shared by the site's review and by Quiz ML. Pure functions: no DOM, no storage.
// A right answer moves a card one box up (easy: two), a wrong one sends it back to box 0.
// The box decides when the card is due again.

export const INTERVAL_DAYS = [0, 1, 2, 4, 8, 16, 32];
export const DAY = 86400000;

/** The card's record after an answer. grade: "again" | "good" | "easy". Returns a new object. */
export function schedule(rec, grade, now) {
  const r = { box: 0, due: 0, seen: 0, wrong: 0, ...rec };
  r.seen += 1;
  if (grade === "again") {
    r.box = 0;
    r.wrong += 1;
  } else {
    r.box = Math.min(r.box + (grade === "easy" ? 2 : 1), INTERVAL_DAYS.length - 1);
  }
  r.due = now + INTERVAL_DAYS[r.box] * DAY;
  return r;
}

function shuffle(a, rand) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const byBoxThenDue = (recs) => (x, y) => recs[x].box - recs[y].box || recs[x].due - recs[y].due;

/**
 * Up to `size` cards for a "smart" round: due cards (lower box first, then the oldest due),
 * then new cards in random order, then cards due later (lower box first, then the nearest due).
 */
export function pickSmart(ids, recs, now, size, rand = Math.random) {
  const seen = ids.filter((id) => recs[id]);
  const due = seen.filter((id) => recs[id].due <= now).sort(byBoxThenDue(recs));
  const fresh = shuffle(ids.filter((id) => !recs[id]), rand);
  const later = seen.filter((id) => recs[id].due > now).sort(byBoxThenDue(recs));
  return [...due, ...fresh, ...later].slice(0, size);
}

/** Up to `size` different cards in random order. */
export function pickRandom(ids, size, rand = Math.random) {
  return shuffle([...ids], rand).slice(0, size);
}
