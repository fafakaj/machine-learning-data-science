// Quiz ML answer checks, without DOM: a choice is an option index, an input is a method name.

/** "str.rsplit('.', 1)", ".RSPLIT", " rsplit() " → "rsplit". */
export function normalizeMethod(s) {
  return String(s)
    .replace(/\s+/g, "")
    .toLowerCase()
    .replace(/\(.*$/, "")
    .replace(/^(str|list|dict|set)\./, "")
    .replace(/^\.+/, "");
}

export function answerOk(q, value) {
  if (q.type === "input") {
    const name = normalizeMethod(value);
    return Boolean(name) && q.answer.some((a) => normalizeMethod(a) === name);
  }
  return value === q.answer;
}

/** "Where the mistake is" for a typed method name, as markdown: what that method does, or that the type has no such method. */
export function inputMistake(q, value, methods) {
  const name = normalizeMethod(value).replaceAll("`", "");
  const desc = methods[q.of]?.[name];
  if (desc) return `\`${name}\`: ${desc}`;
  return `у \`${q.of}\` нет метода \`${name || "…"}\`.`;
}
