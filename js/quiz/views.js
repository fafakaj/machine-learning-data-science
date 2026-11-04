// Quiz ML screens: home, topic, catalog, custom set, a round and its results. The question itself is question.js.
// Progress lives in progress.pyquiz[<id>] = {box, due, seen, wrong, last: "ok"|"bad"}; it is always read anew,
// because loadProgress/pullRemote replace the whole progress object.
import { logout } from "../auth.js";
import { icon } from "../icons.js";
import { pickRandom, pickSmart, schedule } from "../leitner.js";
import { esc } from "../md.js";
import { backend, onSaveState, progress, scheduleSave } from "../store.js";
import { renderQuestion } from "./question.js";

const ROUND = 10;
const CUSTOM = 20;
const CUSTOM_KEY = "quizml-custom";
const app = document.getElementById("app");
const bank = { topics: [], methods: {}, byId: new Map(), byTopic: new Map() };
// The current round, in memory only: {title, ids, i, answers: {id: {value, ok}}, again: () => ids, back: hash}.
let round = null;

export function setBank(data) {
  bank.topics = data.topics;
  bank.methods = data.methods;
  for (const t of data.topics) bank.byTopic.set(t.id, []);
  for (const q of data.questions) {
    bank.byId.set(q.id, q);
    bank.byTopic.get(q.topic)?.push(q.id);
  }
}

const recs = () => progress.pyquiz || {};
const topicOf = (id) => bank.topics.find((t) => t.id === id);
/** "list: сложность" → "<code>list</code>: сложность". */
const titleHTML = (title) => esc(title).replace(/^(list|dict|set|str)\b/, "<code>$1</code>");
const plural = (n, one, few, many) => {
  const d = n % 10;
  const dd = n % 100;
  return d === 1 && dd !== 11 ? one : d >= 2 && d <= 4 && (dd < 12 || dd > 14) ? few : many;
};
const questionsWord = (n) => `${n} ${plural(n, "вопрос", "вопроса", "вопросов")}`;

function record(q, ok) {
  progress.pyquiz ||= {};
  progress.pyquiz[q.id] = { ...schedule(progress.pyquiz[q.id], ok ? "good" : "again", Date.now()), last: ok ? "ok" : "bad" };
  scheduleSave();
}

function topicStats(id, now = Date.now()) {
  const ids = bank.byTopic.get(id) || [];
  const r = recs();
  let ok = 0;
  let due = 0;
  for (const qid of ids) {
    const x = r[qid];
    if (!x) continue;
    if (x.last === "ok") ok++;
    if (x.due <= now) due++;
  }
  return { total: ids.length, ok, due };
}

// ---------------------------------------------------------------- chrome

function header() {
  const s = backend.user;
  return `<header class="qz-top">
      <a class="brand" href="#/" aria-label="Quiz ML: все темы"><span class="logo">${icon("help")}</span><span>Quiz ML</span></a>
      <span class="spacer"></span>
      <span class="dot" data-save></span>
      <a class="nav-link" href="index.html" title="Вернуться на ML-дорожку">${icon("trend")}<span>ML-дорожка</span></a>
      ${s ? `<button class="user" data-logout title="Выйти из аккаунта ${esc(s.user)}"><span class="avatar">${esc(s.user[0].toUpperCase())}</span></button>` : ""}
    </header>`;
}

function bindChrome() {
  const save = app.querySelector("[data-save]");
  if (save) {
    onSaveState((s) => {
      if (!save.isConnected) return;
      save.className = `dot save-${s}`;
      save.title = { saved: "Сохранено", pending: "Сохраняю", error: "Не удалось сохранить, повторю", local: "Сохранено только в браузере" }[s];
    });
  }
  app.querySelector("[data-logout]")?.addEventListener("click", () => {
    if (!confirm("Выйти из аккаунта на этом устройстве?")) return;
    logout();
    location.hash = "#/";
    location.reload();
  });
}

const back = (href, label) => `<a class="qz-back" href="${href}">${icon("left")}<span>${label}</span></a>`;

// ---------------------------------------------------------------- screens

function renderHome() {
  const now = Date.now();
  const groups = new Map();
  for (const t of bank.topics) {
    if (!groups.has(t.group)) groups.set(t.group, []);
    groups.get(t.group).push(t);
  }
  let dueAll = 0;
  const sections = [...groups]
    .map(([name, topics]) => {
      const rows = topics
        .map((t) => {
          const st = topicStats(t.id, now);
          dueAll += st.due;
          return `<a class="qz-row" href="#/topic/${t.id}">
              <span class="qz-row-t"><b>${titleHTML(t.title)}</b><small>верно ${st.ok} из ${st.total}${st.due ? `, к повторению ${st.due}` : ""}</small></span>
              <span class="qz-meter" title="Решено верно ${st.ok} из ${st.total}"><i style="width:${(100 * st.ok) / st.total}%"></i></span>
            </a>`;
        })
        .join("");
      return `<section class="qz-group"><h2>${esc(name)}</h2><div class="qz-list">${rows}</div></section>`;
    })
    .join("");
  app.innerHTML = `${header()}<main class="qz-main">
      <div class="qz-head"><h1>Темы</h1>
        <p class="muted">${questionsWord(bank.byId.size)} по Python. ${dueAll ? `Пора повторить: ${dueAll}.` : "Повторять пока нечего."}</p></div>
      <a class="qz-custom" href="#/custom"><span class="qz-custom-t"><b>Свой набор</b><small>${CUSTOM} вопросов из тем, которые вы выберете</small></span>${icon("arrow")}</a>
      ${sections}
    </main>`;
  bindChrome();
}

function ladderHTML(topicId) {
  const r = recs();
  const counts = Array(8).fill(0); // [new, box 0 … box 6]
  for (const qid of bank.byTopic.get(topicId)) counts[r[qid] ? r[qid].box + 1 : 0]++;
  const max = Math.max(...counts, 1);
  const cells = counts
    .map((n, k) => `<div class="qz-rung ${k === 0 ? "fresh" : ""}"><span class="n">${n}</span><i style="height:${Math.round((40 * n) / max)}px"></i></div>`)
    .join("");
  const labels = counts.map((_, k) => `<span>${k === 0 ? "новые" : k - 1}</span>`).join("");
  return `<figure class="qz-ladder"><div class="qz-rungs">${cells}</div><div class="qz-rung-labels">${labels}</div>
      <figcaption class="muted small">Коробки Лейтнера. Верный ответ поднимает вопрос на одну коробку, ошибка возвращает в 0. Чем выше коробка, тем реже вопрос приходит в «Умных».</figcaption></figure>`;
}

function renderTopic(id) {
  const t = topicOf(id);
  if (!t) return renderHome();
  const st = topicStats(id);
  const ids = bank.byTopic.get(id);
  app.innerHTML = `${header()}<main class="qz-main">
      ${back("#/", "Все темы")}
      <div class="qz-head"><p class="muted small">${esc(t.group)}</p><h1>${titleHTML(t.title)}</h1></div>
      <div class="qz-stats">
        <div class="qz-stat"><b>${st.total}</b><span>${plural(st.total, "вопрос", "вопроса", "вопросов")}</span></div>
        <div class="qz-stat"><b>${st.ok}</b><span>решено верно</span></div>
        <div class="qz-stat"><b>${st.due}</b><span>к повторению</span></div>
      </div>
      <div class="qz-modes">
        <button class="qz-mode primary" data-mode="smart"><b>Умные ${ROUND}</b><small>Сначала ошибки и вопросы, которым пора на повтор, потом новые</small></button>
        <button class="qz-mode" data-mode="random"><b>Случайные ${ROUND}</b><small>${ROUND} разных вопросов темы в случайном порядке</small></button>
        <a class="qz-mode" href="#/catalog/${id}"><b>Каталог</b><small>Все ${questionsWord(st.total)} темы списком</small></a>
      </div>
      ${ladderHTML(id)}
    </main>`;
  bindChrome();
  app.querySelector(".qz-modes").addEventListener("click", (e) => {
    const m = e.target.closest("[data-mode]")?.dataset.mode;
    if (!m) return;
    const pick = m === "smart" ? () => pickSmart(ids, recs(), Date.now(), ROUND) : () => pickRandom(ids, ROUND);
    startRound(pick(), `${t.title}, ${m === "smart" ? "умные" : "случайные"} ${ROUND}`, { again: pick, back: `#/topic/${id}` });
  });
}

function statusOf(rec) {
  if (!rec) return { cls: "is-new", ico: "dot", text: "не решал" };
  return rec.last === "ok" ? { cls: "is-ok", ico: "check", text: "верно" } : { cls: "is-bad", ico: "close", text: "ошибка" };
}

/** A question as one plain line for lists: markdown marks dropped. */
const plain = (s) => s.replace(/`([^`]*)`/g, "$1").replace(/\*\*?([^*]+)\*\*?/g, "$1");

function renderCatalog(id) {
  const t = topicOf(id);
  if (!t) return renderHome();
  const r = recs();
  const rows = bank.byTopic
    .get(id)
    .map((qid) => {
      const q = bank.byId.get(qid);
      const s = statusOf(r[qid]);
      return `<a class="qz-cat ${s.cls}" href="#/q/${qid}" data-qid="${qid}">${icon(s.ico, "qz-st")}
          <span class="qz-cat-t">${esc(plain(q.q))}</span><small>${s.text}${r[qid] ? `, коробка ${r[qid].box}` : ""}</small></a>`;
    })
    .join("");
  app.innerHTML = `${header()}<main class="qz-main">
      ${back(`#/topic/${id}`, titleHTML(t.title))}
      <div class="qz-head"><h1>Каталог</h1><p class="muted">${questionsWord(bank.byTopic.get(id).length)}. Коснитесь вопроса, чтобы ответить или сразу посмотреть разбор.</p></div>
      <div class="qz-list">${rows}</div>
    </main>`;
  bindChrome();
}

function loadCustom() {
  try {
    const saved = JSON.parse(localStorage.getItem(CUSTOM_KEY) || "[]");
    return new Set(saved.filter((id) => bank.byTopic.has(id)));
  } catch {
    return new Set();
  }
}

function saveCustom(set) {
  try {
    localStorage.setItem(CUSTOM_KEY, JSON.stringify([...set]));
  } catch {
    /* the choice is not remembered */
  }
}

function renderCustom() {
  const chosen = loadCustom();
  const groups = new Map();
  for (const t of bank.topics) {
    if (!groups.has(t.group)) groups.set(t.group, []);
    groups.get(t.group).push(t);
  }
  const sections = [...groups]
    .map(([name, topics]) => `<section class="qz-group"><h2>${esc(name)}</h2><div class="qz-list">${topics
      .map((t) => `<label class="qz-check"><input type="checkbox" value="${t.id}" ${chosen.has(t.id) ? "checked" : ""}>
          <span><b>${titleHTML(t.title)}</b><small>${questionsWord(bank.byTopic.get(t.id).length)}</small></span></label>`)
      .join("")}</div></section>`)
    .join("");
  app.innerHTML = `${header()}<main class="qz-main">
      ${back("#/", "Все темы")}
      <div class="qz-head"><h1>Свой набор</h1><p class="muted">Выберите темы. Квиз даст ${CUSTOM} вопросов: сначала ошибки и вопросы, которым пора на повтор, потом новые.</p></div>
      ${sections}
      <div class="qz-dock"><button class="btn primary big" data-start></button></div>
    </main>`;
  bindChrome();
  const btn = app.querySelector("[data-start]");
  const pool = () => [...chosen].flatMap((id) => bank.byTopic.get(id));
  const update = () => {
    const n = Math.min(CUSTOM, pool().length);
    btn.disabled = n === 0;
    btn.textContent = n ? `Начать: ${questionsWord(n)}` : "Выберите хотя бы одну тему";
  };
  update();
  app.querySelector("main").addEventListener("change", (e) => {
    const box = e.target.closest("input[type=checkbox]");
    if (!box) return;
    if (box.checked) chosen.add(box.value);
    else chosen.delete(box.value);
    saveCustom(chosen);
    update();
  });
  btn.addEventListener("click", () => {
    const ids = pool();
    const pick = () => pickSmart(ids, recs(), Date.now(), CUSTOM);
    startRound(pick(), "Свой набор", { again: pick, back: "#/custom" });
  });
}

// ---------------------------------------------------------------- round

export function startRound(ids, title, { again = () => ids, back: backHash = "#/" } = {}) {
  round = { title, ids, i: 0, answers: {}, again, back: backHash };
  if (location.hash === "#/run") render();
  else location.hash = "#/run";
}

function segsHTML() {
  return round.ids
    .map((id, k) => {
      const a = round.answers[id];
      return `<i class="${a ? (a.ok ? "ok" : "bad") : k === round.i ? "now" : ""}" data-seg="${k}"></i>`;
    })
    .join("");
}

function renderRun() {
  if (!round) {
    location.replace("#/");
    return;
  }
  if (round.i >= round.ids.length) return renderResults();
  const q = bank.byId.get(round.ids[round.i]);
  const last = round.i === round.ids.length - 1;
  app.innerHTML = `<main class="qz-main qz-q" data-body></main>`;
  const body = app.querySelector("[data-body]");
  renderQuestion(body, q, {
    head: `<div class="qz-qtop"><a class="icon-btn" href="${round.back}" title="Выйти из раунда" aria-label="Выйти из раунда">${icon("close")}</a>
        <span class="qz-segs">${segsHTML()}</span><span class="qz-count">${round.i + 1} из ${round.ids.length}</span></div>`,
    topic: topicOf(q.topic)?.title || "",
    methods: bank.methods,
    given: round.answers[q.id]?.value,
    onAnswer: (ok, value) => {
      round.answers[q.id] = { value, ok };
      record(q, ok);
      const seg = body.querySelector(`[data-seg="${round.i}"]`);
      if (seg) seg.className = ok ? "ok" : "bad";
    },
    actions: [{ label: last ? "Итог" : "Дальше", primary: true, run: () => { round.i++; render(); } }],
  });
}

function renderResults() {
  const n = round.ids.length;
  const score = round.ids.filter((id) => round.answers[id]?.ok).length;
  const rows = round.ids
    .map((id) => {
      const q = bank.byId.get(id);
      const ok = round.answers[id]?.ok;
      return `<a class="qz-cat ${ok ? "is-ok" : "is-bad"}" href="#/q/${id}">${icon(ok ? "check" : "close", "qz-st")}
          <span class="qz-cat-t">${esc(plain(q.q))}</span><small>${ok ? "верно" : "ошибка"}, открыть разбор</small></a>`;
    })
    .join("");
  const backLabel = round.back === "#/custom" ? "К выбору тем" : "К теме";
  app.innerHTML = `${header()}<main class="qz-main">
      <div class="qz-head"><p class="muted">${esc(round.title)}</p><p class="qz-score">${score} из ${n}</p>
        <p class="muted">${score === n ? "Все ответы верные." : `Ошибки вернутся в следующем раунде «Умных»: их коробка теперь 0.`}</p></div>
      <div class="qz-list">${rows}</div>
      <div class="qz-actions"><button class="btn primary big" data-again>Ещё раунд</button><a class="btn big" href="${round.back}">${backLabel}</a></div>
    </main>`;
  bindChrome();
  app.querySelector("[data-again]").addEventListener("click", () => startRound(round.again(), round.title, { again: round.again, back: round.back }));
}

/** One question by link: from the catalog it can be answered; from the results it opens with the analysis. */
function renderSingle(id) {
  const q = bank.byId.get(id);
  if (!q) return renderHome();
  const fromResults = round && round.i >= round.ids.length && round.answers[id];
  const ids = bank.byTopic.get(q.topic);
  const next = ids[ids.indexOf(id) + 1];
  const backHash = fromResults ? "#/run" : `#/catalog/${q.topic}`;
  app.innerHTML = `<main class="qz-main qz-q" data-body></main>`;
  renderQuestion(app.querySelector("[data-body]"), q, {
    head: `<div class="qz-qtop">${back(backHash, fromResults ? "К итогу" : "К каталогу")}</div>`,
    topic: topicOf(q.topic)?.title || "",
    methods: bank.methods,
    given: fromResults ? fromResults.value : undefined,
    reveal: !fromResults,
    onAnswer: (ok) => record(q, ok),
    actions: fromResults
      ? [{ label: "К итогу", primary: true, href: "#/run" }]
      : [next ? { label: "Следующий вопрос", primary: true, href: `#/q/${next}` } : { label: "К каталогу", primary: true, href: backHash }],
  });
}

export function render() {
  window.scrollTo(0, 0);
  const [, route = "", arg = ""] = (location.hash || "#/").match(/^#\/(\w*)\/?(.*)$/) || [];
  if (route === "topic") return renderTopic(arg);
  if (route === "catalog") return renderCatalog(arg);
  if (route === "custom") return renderCustom();
  if (route === "run") return renderRun();
  if (route === "q") return renderSingle(arg);
  return renderHome();
}
