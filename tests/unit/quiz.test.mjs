// Unit tests of Quiz ML answer checks. Run: node --test tests/unit/
import { test } from "node:test";
import assert from "node:assert/strict";
import { answerOk, inputMistake, normalizeMethod } from "../../js/quiz/answer.js";

const input = { type: "input", of: "str", answer: ["rsplit"] };
const choice = { type: "choice", options: ["O(1)", "O(n)"], answer: 1 };
const METHODS = { str: { split: "делит строку слева направо", rsplit: "делит справа" } };

test("normalizeMethod drops the type, dot, call parens, spaces and case", () => {
  for (const s of ["rsplit", "rsplit()", ".rsplit", "str.rsplit", "RSPLIT", "  rsplit ", "str.rsplit('.', 1)", "r split"]) {
    assert.equal(normalizeMethod(s), "rsplit", s);
  }
});

test("normalizeMethod keeps the underscores of a name", () => {
  assert.equal(normalizeMethod("list.__len__"), "__len__");
});

test("answerOk compares the chosen index for a choice question", () => {
  assert.equal(answerOk(choice, 1), true);
  assert.equal(answerOk(choice, 0), false);
});

test("answerOk accepts any spelling of the method for an input question", () => {
  assert.equal(answerOk(input, "str.rsplit()"), true);
  assert.equal(answerOk(input, "split"), false);
  assert.equal(answerOk(input, ""), false);
});

test("inputMistake describes a real method and names a missing one", () => {
  assert.match(inputMistake(input, "split()", METHODS), /`split`.*делит строку слева направо/);
  assert.match(inputMistake(input, "rspilt", METHODS), /у `str` нет метода `rspilt`/);
});
