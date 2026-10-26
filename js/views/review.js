// Review: one queue for everything already met. Questions of finished quizzes, solved problems
// (recall the technique from the statement, then re-solve if it did not come back) and Anki cards
// (the step "Anki" brings new ones in). Leitner boxes decide what comes back when.
import { createEditor } from "../editor.js";
import { grade, questionBody, readValue } from "../grade.js";
import { icon } from "../icons.js";
import { esc, md } from "../md.js";
import { runProblem, TimeoutError } from "../py.js";
import { openTutor } from "../tutor.js";
import { allSteps, data, isDone, logEvent, progress, scheduleSave, todayISO } from "../store.js";
import { resultsHTML } from "./code.js";

const INTERVAL_DAYS = [0, 1, 2, 4, 8, 16, 32];
const SESSION = 12;
const DAY = 86400000;
const NEW_PER_DAY = 15; // new Anki cards a day, as in the .apkg deck settings
const REQUEUE = 2; // an Anki card answered "again" comes back this many times within one session

function shuffle(a, seed = Math.random) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(seed() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ---------------------------------------------------------------- cards

const ankiCard = (c) => ({ key: `a:${c.id}`, kind: "anki", card: c, from: `Anki · ${c.deck}` });

function problemCard(p, stepId) {
  return { key: `p:${p.id}`, kind: "problem", p, stepId, from: `LeetCode · ${p.difficulty}` };
}

/** Every card the student has earned: questions from finished quizzes, solved problems, Anki cards already met. */
function pool() {
  const cards = [];
  const seenQuiz = new Set();
  for (const { step } of allSteps()) {
    if (!isDone(step.id) || progress.steps[step.id]?.skipped) continue;
    if ((step.type === "quiz" || step.type === "oral") && !seenQuiz.has(step.quiz)) {
      seenQuiz.add(step.quiz);
      data.quizzes[step.quiz]?.questions.forEach((q, i) => cards.push({ key: `q:${step.quiz}:${i}`, kind: "quiz", q, from: data.quizzes[step.quiz].title }));
    }
    if (step.type === "leetcode" && data.problems[step.problem]) cards.push(problemCard(data.problems[step.problem], step.id));
  }
  for (const c of data.anki.cards) if (progress.review[`a:${c.id}`]) cards.push(ankiCard(c));
  return cards;
}

const dueAt = (c) => progress.review[c.key]?.due ?? 0;

export function dueCount() {
  const now = Date.now();
  return pool().filter((c) => dueAt(c) <= now).length;
}

/**
 * Wrong options that look right: a technique for the same kind of input (same argument types),
 * from another family (a sibling technique of the same family may solve the problem too).
 * Techniques of solved problems come first: the student knows those words.
 */
function confusable(p) {
  const sig = (x) => (x.kind === "design" ? "design" : (x.arg_types || []).join(","));
  const family = (x) => x.pattern.split("-")[0];
  const solved = new Set(allSteps().filter(({ step }) => step.type === "leetcode" && isDone(step.id)).map(({ step }) => step.problem));
  const byName = new Map();
  for (const x of Object.values(data.problems)) {
    if (family(x) === family(p) || x.pattern_ru === p.pattern_ru) continue;
    const score = (sig(x) === sig(p) ? 2 : 0) + (solved.has(x.id) ? 1 : 0) + Math.random() * 0.9;
    if ((byName.get(x.pattern_ru) ?? -1) < score) byName.set(x.pattern_ru, score);
  }
  return [...byName].sort((a, b) => b[1] - a[1]).slice(0, 3).map(([name]) => name);
}

// ---------------------------------------------------------------- Leitner boxes

function box(key) {
  return (progress.review[key] ||= { box: 0, due: 0, seen: 0, wrong: 0 });
}

/** grade: "again" | "good" | "easy". */
function record(c, gradeName) {
  const b = box(c.key);
  b.seen += 1;
  b.intro ||= todayISO();
  if (gradeName === "again") {
    b.box = 0;
    b.wrong += 1;
  } else {
    b.box = Math.min(b.box + (gradeName === "easy" ? 2 : 1), INTERVAL_DAYS.length - 1);
  }
  b.due = Date.now() + INTERVAL_DAYS[b.box] * DAY;
  b.last = new Date().toISOString();
  logEvent("review", null, { card: c.key, ok: gradeName !== "again", grade: gradeName });
  scheduleSave();
}

// ---------------------------------------------------------------- Anki deck of a plan step

/**
 * What the Anki step of `deck` offers today: every due Anki card (as Anki's parent deck "ML" would)
 * and new cards of this deck in plan order, up to NEW_PER_DAY a day. Deck "ML" means all decks.
 */
export function ankiToday(deck) {
  const all = data.anki.cards;
  const own = all.filter((c) => deck === "ML" || c.deck === deck);
  const now = Date.now();
  const today = todayISO();
  const rec = (c) => progress.review[`a:${c.id}`];
  const due = all.filter((c) => rec(c) && rec(c).due <= now);
  const fresh = own.filter((c) => !rec(c));
  const metToday = all.filter((c) => rec(c)?.intro === today).length;
  return {
    total: own.length,
    met: own.length - fresh.length,
    due: due.map(ankiCard),
    fresh: fresh.map(ankiCard),
    newToday: fresh.slice(0, Math.max(0, NEW_PER_DAY - metToday)).map(ankiCard),
  };
}

// ---------------------------------------------------------------- one session

function answerHTML(q) {
  if (q.type === "output") return `<pre class="stdout">${esc(q.answer)}</pre>`;
  if (q.type === "choice") return md(q.options[q.answer]);
  if (q.type === "multi") return q.answers.map((k) => md(q.options[k])).join("");
  if (q.type === "number") return esc(String(+q.answer.toFixed(4)));
  if (q.type === "vector") return esc(q.answer.map((x) => +x.toFixed(4)).join("; "));
  if (q.type === "expr") return `<code>${esc(q.ref)}</code>`;
  return "";
}

function problemFace(p) {
  const ex = p.examples?.[0];
  return `<div class="md pr-statement">${md(p.statement_ru)}</div>
    ${ex ? `<div class="example"><div class="kv"><span>Вход</span><code>${esc(ex.input)}</code></div><div class="kv"><span>Выход</span><code>${esc(ex.output)}</code></div></div>` : ""}`;
}

function problemAnswer(c) {
  const p = c.p;
  const sol = progress.steps[c.stepId]?.solution;
  return `<div class="explain reveal">
      <div><b>Приём:</b> ${esc(p.pattern_ru)}${p.complexity_target ? ` <span class="muted">· ${esc(p.complexity_target)}</span>` : ""}</div>
      ${p.hints_ru?.[1] ? `<div class="md">${md(p.hints_ru[1])}</div>` : ""}
      <div class="muted small">Задача #${p.id} «${esc(p.title_ru)}»</div>
      ${sol ? `<details class="alt"><summary>Ваше решение</summary><pre class="code">${esc(sol)}</pre></details>` : ""}
    </div>`;
}

/**
 * Run `queue` card by card inside `root`. onFinish(right, total) is called once the queue is empty;
 * it may draw its own end screen, otherwise a default one is shown.
 */
export function runSession(root, queue, { onFinish, again } = {}) {
  queue = [...queue];
  let idx = 0;
  let right = 0;
  let answered = false;
  let stop = () => {};
  const requeued = new Map();

  const shell = (c, face, actions) => `<div class="review card review-${c.kind}">
      <div class="review-top"><span class="muted small">${esc(c.from)}</span><span class="muted small">${idx + 1} / ${queue.length}</span></div>
      <div class="bar"><div style="width:${(100 * idx) / queue.length}%"></div></div>
      <div class="question review-q" data-card>${face}</div>
      <div data-verdict></div>
      <div class="review-actions">${actions}</div>
      <div data-resolve></div>
    </div>`;
  const actions = (html) => {
    root.querySelector(".review-actions").innerHTML = html;
    root.querySelector(".review-actions .btn")?.focus();
  };

  const show = () => {
    stop();
    stop = () => {};
    if (idx >= queue.length) {
      const total = queue.length;
      root.innerHTML = `<div class="review card"><h1>Готово</h1><p>Верно ${right} из ${total}.</p>
        <div class="review-actions">${again ? '<button class="btn primary" data-again>Ещё раз</button>' : ""}<a class="btn ghost" href="#/">К плану</a></div></div>`;
      onFinish?.(right, total);
      return;
    }
    answered = false;
    const c = queue[idx];
    if (c.kind === "anki") {
      root.innerHTML = shell(c, `<div class="anki-face md">${c.card.front}</div>`, `<button class="btn primary" data-reveal title="Пробел">Показать ответ</button>`);
    } else if (c.kind === "problem") {
      root.innerHTML = shell(c, `${problemFace(c.p)}
          <div class="q-text">Каким приёмом решить и за какую сложность? Вспомните сами, потом проверьте себя.</div>
          <textarea class="answer" rows="2" placeholder="Ваш план: приём, структура данных, сложность (не обязательно)" data-plan></textarea>`,
        `<button class="btn primary" data-reveal>Показать ответ</button><button class="btn" data-choices>Выбрать из вариантов</button><button class="btn ghost" data-dunno>Не помню</button>`);
    } else {
      const self = c.q.type === "text";
      root.innerHTML = shell(c, questionBody(c.q, 0),
        self ? `<button class="btn primary" data-reveal>Показать ответ</button>` : `<button class="btn primary" data-check>Проверить</button><button class="btn ghost" data-dunno>Не помню</button>`);
    }
  };

  const next = () => {
    idx += 1;
    show();
  };

  const finishProblem = (ok) => {
    answered = true;
    record(queue[idx], ok ? "good" : "again");
    if (ok) right += 1;
    actions(ok
      ? `<button class="btn primary" data-next>Дальше</button><button class="btn ghost" data-resolve-open>Решить заново</button>`
      : `<button class="btn primary" data-resolve-open>Решить заново</button><button class="btn ghost" data-next>Дальше</button>`);
    if (!ok) root.querySelector("[data-verdict]").insertAdjacentHTML("beforeend", '<div class="note">Решите задачу ещё раз: так приём запомнится лучше, чем по ответу.</div>');
  };

  const verdict = (ok, msg = "", extra = "") => {
    const c = queue[idx];
    root.querySelector("[data-verdict]").innerHTML = `
      <div class="q-verdict ${ok ? "ok" : "bad"}">${ok ? "Верно" : `Неверно${msg ? `: ${esc(msg)}` : ""}`}</div>
      ${!ok && c.kind === "quiz" ? `<div class="explain"><b>Ответ:</b> ${answerHTML(c.q)}</div>` : ""}
      ${c.q?.explain ? `<div class="explain">${md(c.q.explain)}</div>` : ""}${extra}`;
  };

  const openResolve = () => {
    const c = queue[idx];
    const box_ = root.querySelector("[data-resolve]");
    if (box_.firstChild) return;
    box_.innerHTML = `<div class="resolve">
        <div class="sub">Решите заново</div>
        <div class="editor resolve-editor" data-editor></div>
        <div class="resolve-bar"><button class="btn primary" data-resolve-run title="Ctrl+Enter">Проверить все тесты</button>
          <button class="btn" data-resolve-trace>${icon("step")}По шагам</button></div>
        <div class="results" data-resolve-out><div class="muted small">Код проверяется на тех же тестах, что и в задаче.</div></div>
      </div>`;
    const out = box_.querySelector("[data-resolve-out]");
    let busy = false;
    const run = async () => {
      if (busy) return;
      busy = true;
      out.innerHTML = '<div class="muted spinner">Проверяю все тесты…</div>';
      try {
        const res = await runProblem(c.p, editor.value, true);
        out.innerHTML = resultsHTML(res, "submit");
        logEvent("resolve", c.stepId, { card: c.key, passed: res.passed, total: res.total });
      } catch (err) {
        out.innerHTML = err instanceof TimeoutError
          ? '<div class="verdict warn">Код работает дольше лимита и был остановлен</div>'
          : `<div class="verdict bad">Ошибка проверки</div><pre class="err">${esc(err.message)}</pre>`;
      } finally {
        busy = false;
      }
    };
    const editor = createEditor(box_.querySelector("[data-editor]"), { doc: c.p.starter_code, onRun: run, onSubmit: run });
    box_.querySelector("[data-resolve-run]").addEventListener("click", run);
    box_.querySelector("[data-resolve-trace]").addEventListener("click", () => openTutor({ code: editor.value, problem: c.p, title: `#${c.p.id} по шагам` }));
    editor.focus();
  };

  const ankiGrade = (gradeName) => {
    const c = queue[idx];
    record(c, gradeName);
    if (gradeName === "again") {
      const n = requeued.get(c.key) || 0;
      if (n < REQUEUE) {
        requeued.set(c.key, n + 1);
        queue.push(c);
      }
    } else if (!requeued.has(c.key)) right += 1;
    next();
  };

  root.onclick = async (e) => {
    const t = e.target.closest("button");
    if (!t || !root.contains(t)) return;
    const c = queue[idx];
    if (t.hasAttribute("data-again")) return again?.();
    if (t.hasAttribute("data-next")) return next();
    if (t.hasAttribute("data-resolve-open")) return openResolve();
    if (t.dataset.grade) return ankiGrade(t.dataset.grade);
    if (answered || !c) return;

    if (c.kind === "anki" && t.hasAttribute("data-reveal")) {
      root.querySelector("[data-card]").innerHTML = `<div class="anki-face md">${c.card.front}</div><hr class="anki-hr"><div class="anki-back md">${c.card.back || ""}</div>`;
      actions(`<button class="btn bad-btn" data-grade="again" title="1">Снова</button><button class="btn primary" data-grade="good" title="2">Хорошо</button><button class="btn" data-grade="easy" title="3">Легко</button>`);
      return;
    }
    if (c.kind === "problem") {
      if (t.hasAttribute("data-reveal")) {
        root.querySelector("[data-verdict]").innerHTML = problemAnswer(c);
        actions(`<button class="btn primary" data-self="1">Помнил</button><button class="btn ghost" data-self="0">Не помнил</button>`);
        return;
      }
      if (t.hasAttribute("data-dunno")) {
        root.querySelector("[data-verdict]").innerHTML = problemAnswer(c);
        return finishProblem(false);
      }
      if (t.dataset.self !== undefined) return finishProblem(t.dataset.self === "1");
      if (t.hasAttribute("data-choices")) {
        const options = shuffle([c.p.pattern_ru, ...confusable(c.p)]);
        c.q = { type: "choice", q: `Какой приём решает задачу${c.p.complexity_target ? ` за ${c.p.complexity_target}` : ""}?`, options, answer: options.indexOf(c.p.pattern_ru) };
        root.querySelector("[data-card]").innerHTML = problemFace(c.p) + questionBody(c.q, 0);
        actions(`<button class="btn primary" data-check>Проверить</button><button class="btn ghost" data-dunno>Не помню</button>`);
        return;
      }
      if (t.hasAttribute("data-check")) {
        const value = readValue(c.q, root.querySelector("[data-card]"));
        if (value === null) return;
        const { ok } = await grade(c.q, value);
        verdict(ok, "", problemAnswer(c));
        return finishProblem(ok);
      }
      return;
    }
    if (t.hasAttribute("data-dunno")) {
      answered = true;
      record(c, "again");
      verdict(false);
      return actions(`<button class="btn primary" data-next>Дальше</button>`);
    }
    if (t.hasAttribute("data-check")) {
      const value = readValue(c.q, root.querySelector("[data-card]"));
      if (value === null || value === "" || (Array.isArray(value) && !value.length)) return;
      answered = true;
      const { ok, msg } = await grade(c.q, value);
      record(c, ok ? "good" : "again");
      if (ok) right += 1;
      verdict(ok, msg);
      return actions(`<button class="btn primary" data-next>Дальше</button>`);
    }
    if (t.hasAttribute("data-reveal")) {
      root.querySelector("[data-verdict]").innerHTML = `<div class="explain"><b>Образец:</b> ${md(c.q.model)}</div>`;
      actions(`<button class="btn primary" data-self="1">Помнил</button><button class="btn ghost" data-self="0">Не помнил</button>`);
      return;
    }
    if (t.dataset.self !== undefined) {
      answered = true;
      const ok = t.dataset.self === "1";
      record(c, ok ? "good" : "again");
      if (ok) right += 1;
      next();
    }
  };
  root.onkeydown = (e) => {
    if (e.key === "Enter" && e.target.matches("input")) root.querySelector("[data-check], [data-next]")?.click();
  };
  // Anki shortcuts: Space shows the answer, 1-3 grade it. Not while typing.
  const keys = (e) => {
    if (!root.isConnected) return document.removeEventListener("keydown", keys);
    if (e.target.closest("input, textarea, .cm-editor") || queue[idx]?.kind !== "anki") return;
    const b = e.key === " " ? root.querySelector("[data-reveal]") : root.querySelector(`[data-grade="${{ 1: "again", 2: "good", 3: "easy" }[e.key]}"]`);
    if (b) {
      e.preventDefault();
      b.click();
    }
  };
  if (root.ankiKeys) document.removeEventListener("keydown", root.ankiKeys);
  root.ankiKeys = keys;
  document.addEventListener("keydown", keys);
  show();
}

// ---------------------------------------------------------------- the review page

export function renderReview(root) {
  const cards = pool();
  const now = Date.now();
  const due = cards.filter((c) => dueAt(c) <= now).sort((a, b) => dueAt(a) - dueAt(b));
  const kinds = { quiz: "вопросы квизов", problem: "задачи", anki: "карточки Anki" };
  const parts = Object.entries(kinds)
    .map(([k, label]) => [label, due.filter((c) => c.kind === k).length])
    .filter(([, n]) => n)
    .map(([label, n]) => `${label}: ${n}`)
    .join(", ");
  const random = () => runSession(root, shuffle([...cards]).slice(0, 10), { again: random });

  root.innerHTML = `<div class="review card">
      <h1>Повторение</h1>
      ${cards.length === 0
        ? `<p class="muted">Здесь появятся вопросы из пройденных квизов, решённые задачи и карточки Anki. Сдайте первый квиз — и можно повторять.</p>`
        : `<p>${due.length ? `К повторению: <b>${due.length}</b> <span class="muted small">(${parts})</span>` : "На сегодня всё повторено."} <span class="muted small">Всего карточек: ${cards.length}</span></p>
           <p class="muted small">Задачи показываются условием, без названия: вспомните приём и сложность сами. Если не вспомнили — решите задачу заново прямо здесь.</p>
           <div class="review-actions">
             ${due.length ? `<button class="btn primary" data-start>Начать (${Math.min(due.length, SESSION)})</button>` : ""}
             <button class="btn ${due.length ? "ghost" : "primary"}" data-extra>${due.length ? "Случайные 10" : "Ещё 10 случайных"}</button>
           </div>`}
    </div>`;
  root.onclick = (e) => {
    if (e.target.closest("[data-start]")) runSession(root, shuffle(due.slice(0, SESSION)), { again: () => renderReview(root) });
    else if (e.target.closest("[data-extra]")) random();
  };
}
