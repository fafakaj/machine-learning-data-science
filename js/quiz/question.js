// Quiz ML question screen, variant A of the demo: the question on top, big answer buttons below,
// the analysis after the answer: why the right answer is right, where the chosen one is wrong, every other option, sources.
import { icon } from "../icons.js";
import { esc, md } from "../md.js";
import { answerOk, inputMistake } from "./answer.js";

/** Markdown for one line (an option): no paragraph around it. */
const inline = (s) => md(s).replace(/^<p>|<\/p>$/g, "");

function shuffled(n) {
  const a = [...Array(n).keys()];
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** "https://docs.python.org/3/library/asyncio-task.html#asyncio.run" → "docs.python.org: asyncio-task, asyncio.run". */
function srcLabel(url) {
  try {
    const u = new URL(url);
    const page = u.pathname.split("/").filter(Boolean).pop()?.replace(/\.html$/, "") || "";
    return [u.host.replace(/^www\./, ""), [page, u.hash.slice(1)].filter(Boolean).join(", ")].filter(Boolean).join(": ");
  } catch {
    return url;
  }
}

function sheetHTML(q, value, ok, opts) {
  const reveal = value === undefined;
  const input = q.type === "input";
  const mistake = reveal || ok ? "" : input ? inputMistake(q, value, opts.methods) : q.wrong[String(value)];
  const others = input
    ? []
    : q.options.map((o, k) => [o, k]).filter(([, k]) => k !== q.answer && (reveal || ok || k !== value));
  const verdict = reveal ? "Разбор" : ok ? "Верно" : "Неверно";
  const actions = opts.actions
    .map((a, k) => a.href
      ? `<a class="btn big ${a.primary ? "primary" : ""}" href="${a.href}">${esc(a.label)}</a>`
      : `<button class="btn big ${a.primary ? "primary" : ""}" data-act="${k}">${esc(a.label)}</button>`)
    .join("");
  return `<section class="qz-sheet ${reveal ? "" : ok ? "is-ok" : "is-bad"}" data-verdict="${reveal ? "reveal" : ok ? "ok" : "bad"}">
      <h2 class="qz-verdict">${reveal ? "" : icon(ok ? "check" : "close")}${verdict}</h2>
      ${input && !ok ? `<p class="qz-right">Верный ответ: <code>${esc(q.answer[0])}</code></p>` : ""}
      <h3>Почему так</h3><div class="md" data-why>${md(q.why)}</div>
      ${mistake ? `<h3>В чём ошибка</h3><div class="md" data-mistake>${md(mistake)}</div>` : ""}
      ${others.length
        ? `<details class="qz-all" ${reveal ? "open" : ""}><summary>${reveal || ok ? "Разбор неверных вариантов" : "Разбор всех вариантов"}</summary><ul>${others
          .map(([o, k]) => `<li><b class="${q.mono ? "mono" : ""}">${inline(o)}</b><div class="md">${md(q.wrong[String(k)])}</div></li>`)
          .join("")}</ul></details>`
        : ""}
      <p class="qz-src">${q.src.length > 1 ? "Источники:" : "Источник:"}${q.src.map((u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(srcLabel(u))}</a>`).join("")}</p>
    </section>
    <div class="qz-dock qz-next">${actions}</div>`;
}

/**
 * opts: {head, topic, methods, actions: [{label, primary?, href? | run?}], onAnswer?(ok, value), reveal?, given?}.
 * `given` is an answer made earlier: the screen opens with the analysis and records nothing.
 * `reveal` adds "show the analysis without an answer"; it records nothing either.
 */
export function renderQuestion(root, q, opts) {
  const order = q.type === "choice" ? shuffled(q.options.length) : [];
  const answerHTML = q.type === "input"
    ? `<form class="qz-input" data-form><input class="answer mono" name="a" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false"
          placeholder="имя метода ${esc(q.of)}" aria-label="Имя метода ${esc(q.of)}"><button class="btn primary big" type="submit">Проверить</button></form>`
    : `<div class="qz-opts">${order.map((k) => `<button class="qz-opt ${q.mono ? "mono" : ""}" data-pick="${k}">${inline(q.options[k])}</button>`).join("")}</div>`;
  root.innerHTML = `${opts.head}
    <div class="qz-stage" data-qid="${q.id}">
      <p class="qz-topic">${esc(opts.topic)}</p>
      <div class="qz-prompt md">${md(q.q)}</div>
      ${q.code ? `<pre class="code">${esc(q.code)}</pre>` : ""}
    </div>
    <div class="qz-answer">${answerHTML}
      ${opts.reveal ? '<button class="link-btn qz-reveal" data-reveal>Показать разбор без ответа</button>' : ""}</div>
    <div data-sheet></div>`;
  const sheet = root.querySelector("[data-sheet]");
  let done = false;

  // One answer per screen: a double tap or a second Enter does nothing.
  const finish = (value, { record = true } = {}) => {
    if (done) return;
    done = true;
    const reveal = value === undefined;
    const ok = !reveal && answerOk(q, value);
    root.querySelector("[data-reveal]")?.remove();
    if (q.type === "input") {
      const field = root.querySelector("[data-form] input");
      if (!reveal) field.value = value;
      field.disabled = true;
      field.classList.add(reveal ? "dim" : ok ? "right" : "wrong");
      root.querySelector("[data-form] button").disabled = true;
    } else {
      for (const b of root.querySelectorAll("[data-pick]")) {
        const k = Number(b.dataset.pick);
        b.disabled = true;
        b.classList.add(k === q.answer ? "right" : k === value ? "wrong" : "dim");
      }
    }
    if (record && !reveal) {
      opts.onAnswer?.(ok, value);
      // A short tap for a right answer, a double one for a wrong answer (Android; elsewhere vibrate is absent).
      navigator.vibrate?.(ok ? 12 : [30, 60, 30]);
    }
    sheet.innerHTML = sheetHTML(q, value, ok, opts);
    sheet.addEventListener("click", (e) => {
      const act = e.target.closest("[data-act]");
      if (!act || act.disabled) return;
      act.disabled = true;
      opts.actions[Number(act.dataset.act)].run();
    });
    if (record) {
      const smooth = !matchMedia("(prefers-reduced-motion: reduce)").matches;
      sheet.scrollIntoView({ block: "start", behavior: smooth ? "smooth" : "auto" });
    }
  };

  root.querySelector(".qz-opts")?.addEventListener("click", (e) => {
    const b = e.target.closest("[data-pick]");
    if (b) finish(Number(b.dataset.pick));
  });
  const form = root.querySelector("[data-form]");
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const value = form.elements.a.value;
    if (value.trim()) finish(value);
  });
  root.querySelector("[data-reveal]")?.addEventListener("click", () => finish(undefined, { record: false }));
  if (opts.given !== undefined) finish(opts.given, { record: false });
  else if (form && matchMedia("(hover: hover)").matches) form.elements.a.focus();
}
