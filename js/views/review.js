// Review: short sessions of questions from everything already done (quizzes of finished steps
// and "which technique?" cards for solved problems). Leitner boxes decide what comes back when.
import { grade, questionBody, readValue } from "../grade.js";
import { esc, md } from "../md.js";
import { allSteps, data, isDone, logEvent, progress, scheduleSave } from "../store.js";

const INTERVAL_DAYS = [0, 1, 2, 4, 8, 16, 32];
const SESSION = 12;
const DAY = 86400000;

function shuffle(a, seed = Math.random) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(seed() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** Every card the student has earned: questions from finished quizzes, techniques of solved problems. */
function pool() {
  const cards = [];
  const seenQuiz = new Set();
  const patterns = [...new Set(Object.values(data.problems).map((p) => p.pattern_ru))];
  for (const { step } of allSteps()) {
    if (!isDone(step.id) || progress.steps[step.id]?.skipped) continue;
    if ((step.type === "quiz" || step.type === "oral") && !seenQuiz.has(step.quiz)) {
      seenQuiz.add(step.quiz);
      data.quizzes[step.quiz]?.questions.forEach((q, i) => cards.push({ key: `q:${step.quiz}:${i}`, q, from: data.quizzes[step.quiz].title }));
    }
    if (step.type === "leetcode") {
      const p = data.problems[step.problem];
      const others = shuffle(patterns.filter((x) => x !== p.pattern_ru)).slice(0, 3);
      const options = shuffle([p.pattern_ru, ...others]);
      cards.push({
        key: `p:${p.id}`,
        from: "LeetCode",
        q: { type: "choice", q: `Задача #${p.id} «${p.title_ru}». Какой приём решает её за ${p.complexity_target || "нужное время"}?`,
             options, answer: options.indexOf(p.pattern_ru), explain: p.hints_ru?.[1] },
      });
    }
  }
  return cards;
}

function box(key) {
  return (progress.review[key] ||= { box: 0, due: 0, seen: 0, wrong: 0 });
}

export function dueCount() {
  const now = Date.now();
  return pool().filter((c) => (progress.review[c.key]?.due ?? 0) <= now).length;
}

export function renderReview(root) {
  const cards = pool();
  const now = Date.now();
  const due = cards.filter((c) => (progress.review[c.key]?.due ?? 0) <= now)
    .sort((a, b) => (progress.review[a.key]?.due ?? 0) - (progress.review[b.key]?.due ?? 0));
  let queue = shuffle(due.slice(0, SESSION));
  let idx = 0;
  let right = 0;
  let answered = false;

  const intro = () => {
    root.innerHTML = `<div class="review card">
        <h1>Повторение</h1>
        ${cards.length === 0
          ? `<p class="muted">Здесь появятся вопросы из пройденных квизов и задач. Сдайте первый квиз — и можно повторять.</p>`
          : `<p>${due.length ? `К повторению: <b>${due.length}</b>` : "На сегодня всё повторено."} <span class="muted small">Всего карточек: ${cards.length}</span></p>
             <div class="review-actions">
               ${due.length ? `<button class="btn primary" data-start>Начать (${queue.length})</button>` : ""}
               <button class="btn ${due.length ? "ghost" : "primary"}" data-extra>${due.length ? "Случайные 10" : "Ещё 10 случайных"}</button>
             </div>`}
      </div>`;
  };

  const show = () => {
    if (idx >= queue.length) {
      root.innerHTML = `<div class="review card"><h1>Готово</h1><p>Верно ${right} из ${queue.length}.</p>
        <div class="review-actions"><button class="btn primary" data-again>Ещё раз</button><a class="btn ghost" href="#/">К плану</a></div></div>`;
      return;
    }
    answered = false;
    const c = queue[idx];
    const self = c.q.type === "text";
    root.innerHTML = `<div class="review card">
        <div class="review-top"><span class="muted small">${esc(c.from)}</span><span class="muted small">${idx + 1} / ${queue.length}</span></div>
        <div class="bar"><div style="width:${(100 * idx) / queue.length}%"></div></div>
        <div class="question review-q" data-card>${questionBody(c.q, 0)}</div>
        <div data-verdict></div>
        <div class="review-actions">
          ${self ? `<button class="btn primary" data-reveal>Показать ответ</button>` : `<button class="btn primary" data-check>Проверить</button><button class="btn ghost" data-dunno>Не помню</button>`}
        </div>
      </div>`;
  };

  const record = (ok) => {
    const c = queue[idx];
    const b = box(c.key);
    b.seen += 1;
    if (ok) {
      b.box = Math.min(b.box + 1, INTERVAL_DAYS.length - 1);
      right += 1;
    } else {
      b.box = 0;
      b.wrong += 1;
    }
    b.due = Date.now() + INTERVAL_DAYS[b.box] * DAY;
    b.last = new Date().toISOString();
    logEvent("review", null, { card: c.key, ok });
    scheduleSave();
  };

  const answer = (c) => {
    if (c.q.type === "output") return `<pre class="stdout">${esc(c.q.answer)}</pre>`;
    if (c.q.type === "choice") return md(c.q.options[c.q.answer]);
    if (c.q.type === "multi") return c.q.answers.map((k) => md(c.q.options[k])).join("");
    if (c.q.type === "number") return esc(String(+c.q.answer.toFixed(4)));
    if (c.q.type === "vector") return esc(c.q.answer.map((x) => +x.toFixed(4)).join("; "));
    if (c.q.type === "expr") return `<code>${esc(c.q.ref)}</code>`;
    return "";
  };

  const verdict = (ok, msg = "") => {
    const c = queue[idx];
    root.querySelector("[data-verdict]").innerHTML = `
      <div class="q-verdict ${ok ? "ok" : "bad"}">${ok ? "Верно" : `Неверно${msg ? `: ${esc(msg)}` : ""}`}</div>
      ${!ok ? `<div class="explain"><b>Ответ:</b> ${answer(c)}</div>` : ""}
      ${c.q.explain ? `<div class="explain">${md(c.q.explain)}</div>` : ""}`;
    root.querySelector(".review-actions").innerHTML = `<button class="btn primary" data-next>Дальше</button>`;
    root.querySelector("[data-next]").focus();
  };

  root.onclick = async (e) => {
    const t = e.target.closest("button");
    if (!t) return;
    if (t.hasAttribute("data-start")) return show();
    if (t.hasAttribute("data-extra") || t.hasAttribute("data-again")) {
      queue = shuffle([...cards]).slice(0, 10);
      idx = 0;
      right = 0;
      return show();
    }
    if (t.hasAttribute("data-next")) {
      idx += 1;
      return show();
    }
    const c = queue[idx];
    if (answered) return;
    if (t.hasAttribute("data-dunno")) {
      answered = true;
      record(false);
      return verdict(false);
    }
    if (t.hasAttribute("data-check")) {
      const value = readValue(c.q, root.querySelector("[data-card]"));
      if (value === null || value === "" || (Array.isArray(value) && !value.length)) return;
      answered = true;
      const { ok, msg } = await grade(c.q, value);
      record(ok);
      return verdict(ok, msg);
    }
    if (t.hasAttribute("data-reveal")) {
      root.querySelector("[data-verdict]").innerHTML = `<div class="explain"><b>Образец:</b> ${md(c.q.model)}</div>`;
      root.querySelector(".review-actions").innerHTML = `<button class="btn primary" data-self="1">Помнил</button><button class="btn ghost" data-self="0">Не помнил</button>`;
      return;
    }
    if (t.dataset.self !== undefined) {
      answered = true;
      record(t.dataset.self === "1");
      idx += 1;
      return show();
    }
  };
  root.onkeydown = (e) => {
    if (e.key === "Enter" && e.target.matches("input")) root.querySelector("[data-check], [data-next]")?.click();
  };
  intro();
}
