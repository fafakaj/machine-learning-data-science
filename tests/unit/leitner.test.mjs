// Unit tests of the Leitner boxes: scheduling and the "smart" pick. Run: node --test tests/unit/
import { test } from "node:test";
import assert from "node:assert/strict";
import { DAY, INTERVAL_DAYS, pickRandom, pickSmart, schedule } from "../../js/leitner.js";

const rec = (box, due, extra = {}) => ({ box, due, seen: 1, wrong: 0, ...extra });

/** A fixed sequence instead of Math.random, so a pick is reproducible. */
function seeded(seed = 1) {
  return () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
}

test("intervals are the site's: 0, 1, 2, 4, 8, 16, 32 days", () => {
  assert.deepEqual(INTERVAL_DAYS, [0, 1, 2, 4, 8, 16, 32]);
});

test("a first right answer moves a new card to box 1, due in a day", () => {
  assert.deepEqual(schedule(undefined, "good", 0), { box: 1, due: DAY, seen: 1, wrong: 0 });
});

test("easy jumps two boxes and stops at the last box", () => {
  assert.equal(schedule(rec(2, 0), "easy", 0).box, 4);
  assert.equal(schedule(rec(5, 0), "easy", 0).box, 6);
});

test("a wrong answer sends the card to box 0, due at once, and counts the error", () => {
  assert.deepEqual(schedule(rec(4, 0, { seen: 3, wrong: 1 }), "again", 1000), { box: 0, due: 1000, seen: 4, wrong: 2 });
});

test("schedule keeps other fields and does not change its input", () => {
  const before = rec(1, 0, { intro: "2026-11-05", last: "ok" });
  const after = schedule(before, "good", 0);
  assert.equal(after.intro, "2026-11-05");
  assert.equal(after.last, "ok");
  assert.equal(before.box, 1);
});

test("smart pick: due cards first, lower box first, then the oldest due", () => {
  const recs = { a: rec(2, 50), b: rec(0, 90), c: rec(0, 10), d: rec(3, 500) };
  assert.deepEqual(pickSmart(["a", "b", "c", "d"], recs, 100, 3, seeded()), ["c", "b", "a"]);
});

test("smart pick: new cards come after due ones", () => {
  const recs = { a: rec(1, 50) };
  const got = pickSmart(["n1", "a", "n2"], recs, 100, 3, seeded());
  assert.equal(got[0], "a");
  assert.deepEqual(new Set(got.slice(1)), new Set(["n1", "n2"]));
});

test("smart pick fills up with future cards: lower box, then the nearest due", () => {
  const recs = { a: rec(3, 200), b: rec(1, 900), c: rec(1, 300), d: rec(0, 10) };
  assert.deepEqual(pickSmart(["a", "b", "c", "d"], recs, 100, 4, seeded()), ["d", "c", "b", "a"]);
});

test("smart pick takes all cards when there are fewer than the round size", () => {
  assert.equal(pickSmart(["a", "b", "c"], {}, 0, 20, seeded()).length, 3);
});

test("picks never repeat a card", () => {
  const ids = Array.from({ length: 40 }, (_, i) => `q${i}`);
  const recs = Object.fromEntries(ids.slice(0, 15).map((id, i) => [id, rec(i % 7, i * 10)]));
  for (const got of [pickSmart(ids, recs, 70, 20, seeded()), pickRandom(ids, 20, seeded())]) {
    assert.equal(got.length, 20);
    assert.equal(new Set(got).size, 20);
  }
});

test("random pick is reproducible with the same random source", () => {
  const ids = Array.from({ length: 30 }, (_, i) => `q${i}`);
  assert.deepEqual(pickRandom(ids, 10, seeded(7)), pickRandom(ids, 10, seeded(7)));
  assert.notDeepEqual(pickRandom(ids, 10, seeded(7)), ids.slice(0, 10));
});
