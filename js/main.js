import { accountConfigured, login, logout, session } from "./auth.js";
import { esc, md } from "./md.js";
import { onStatus, warmUp } from "./py.js";
import {
  backend, blockLate, blockProgress, calendarWeek, currentStep, data, fmtDate, getStep, isDone, loadData, loadProgress,
  markDone, nextStepAfter, onSaveState, overallProgress, progress, pullRemote, rateStep, scheduleSave, weekProgress,
} from "./store.js";
import { renderCode } from "./views/code.js";
import { renderQuiz } from "./views/quiz.js";
import { dueCount, renderReview } from "./views/review.js";
import { renderAnki, renderHours, renderPractice, renderTheory } from "./views/steps.js";

const TYPE_RU = { leetcode: "Задача", review: "Повтор задачи", exercise: "Упражнение", theory: "Теория", quiz: "Квиз", oral: "Вопросы вслух", anki: "Anki", practice: "Практика", hours: "Итог недели" };
const PANEL_KEY = "ml-panel";
const app = document.getElementById("app");
let cleanup = null;

// ---------------------------------------------------------------- side panel prefs

function panelPrefs() {
  // On a phone the step list starts folded so the task itself is on the first screen.
  const base = { w: 300, collapsed: matchMedia("(max-width: 820px)").matches };
  try {
    return { ...base, ...JSON.parse(localStorage.getItem(PANEL_KEY) || "{}") };
  } catch {
    return base;
  }
}

function savePanelPrefs(p) {
  try {
    localStorage.setItem(PANEL_KEY, JSON.stringify(p));
  } catch {
    /* not remembered */
  }
}

// ---------------------------------------------------------------- chrome

function header() {
  const p = overallProgress();
  const cur = currentStep();
  const weekNo = cur ? getStep(cur.id).week.n : data.plan.weeks.length;
  const due = dueCount();
  const s = backend.gist;
  return `<header class="top">
      <a class="brand" href="#/">ML-дорожка</a>
      <div class="top-mid">
        <span class="small">Неделя ${weekNo} из ${data.plan.weeks.length}</span>
        <div class="bar wide" title="${p.done} из ${p.total} шагов"><div style="width:${(100 * p.done) / p.total}%"></div></div>
      </div>
      <nav class="top-right">
        <a class="nav-link" href="#/review">Повторение${due ? ` <span class="count">${due}</span>` : ""}</a>
        <a class="nav-link" href="#/map">Карта</a>
        ${s ? `<button class="nav-link" data-logout title="Выйти">${esc(s.user)}</button>` : `<a class="nav-link" href="#/login">Войти</a>`}
        <span class="dot" data-py title="Python"></span><span class="dot" data-save title="Сохранение"></span>
      </nav>
    </header>`;
}

function timeline(activeWeek) {
  const cal = calendarWeek();
  return `<nav class="timeline">${data.plan.weeks
    .map((w) => {
      const p = weekProgress(w);
      const cls = [w === cal ? "cur" : "", w.n === activeWeek ? "active" : "", p.done === p.total ? "full" : ""].join(" ");
      return `<a class="tl-week ${cls}" href="#/block/${w.blocks[0].id}" title="Неделя ${w.n}: ${esc(w.title)}">
          <span class="tl-fill" style="height:${(100 * p.done) / Math.max(1, p.total)}%"></span>
          <span class="tl-n">${w.n}</span><span class="tl-label">${esc(w.short || w.title)}</span></a>`;
    })
    .join("")}</nav>`;
}

function stepRow(s, activeStepId) {
  const done = isDone(s.id);
  return `<li class="${done ? "done" : ""} ${s.id === activeStepId ? "active" : ""} ${s.optional ? "opt" : ""}">
      <a href="#/step/${s.id}"><span class="st-mark"></span><span class="st-title">${esc(s.title)}</span></a></li>`;
}

function panel(week, block, activeStepId) {
  const prefs = panelPrefs();
  const tabs = week.blocks
    .map((b) => {
      const p = blockProgress(b);
      const cls = [b === block ? "active" : "", p.done === p.total ? "full" : "", blockLate(b) ? "late" : ""].join(" ");
      return `<a class="block-tab ${cls}" href="#/block/${b.id}" title="${esc(b.title)}">
          <span>Блок ${b.n}</span><i style="--p:${p.total ? p.done / p.total : 0}"></i></a>`;
    })
    .join("");
  const p = blockProgress(block);
  return `<aside class="panel ${prefs.collapsed ? "collapsed" : ""}" style="--panel-w:${prefs.w}px">
      <div class="panel-head">
        <div class="week-title"><span class="muted small">Неделя ${week.n}</span><b>${esc(week.title)}</b></div>
        <button class="icon-btn" data-collapse title="Свернуть или показать шаги" aria-label="Свернуть панель"><span class="chev"></span></button>
      </div>
      <div class="panel-body">
        <div class="blocks">${tabs}</div>
        <div class="block-title"><b>${esc(block.title)}</b> <span class="muted small">${p.done}/${p.total}</span></div>
        <ol class="steps">${block.items.map((s) => stepRow(s, activeStepId)).join("")}</ol>
        ${week.goal ? `<details class="week-goal"><summary>Цель недели</summary><div class="md small">${md(week.goal)}</div></details>` : ""}
      </div>
      <div class="resizer" data-resize title="Потяните, чтобы изменить ширину"></div>
    </aside>`;
}

function stageHead(step, isNow) {
  return `<div class="stage-head">
      <div class="kind">${isNow ? '<span class="now">сейчас</span>' : ""}<span class="muted small">${TYPE_RU[step.type] || ""}${step.optional ? ", по желанию" : ""}</span></div>
      <h1>${esc(step.title)}</h1>
      ${step.why && step.type !== "leetcode" ? `<div class="why">${md(step.why)}</div>` : ""}
    </div>`;
}

function stageFoot(step) {
  if (isDone(step.id) || step.type === "hours") return "";
  return `<div class="stage-foot"><button class="link-btn" data-skip title="Шаг засчитается, в журнале будет отметка «уже знаю»">Уже знаю, пропустить</button></div>`;
}

function rateHTML(step) {
  const r = progress.steps[step.id]?.rating;
  const opt = [["easy", "Легко"], ["ok", "Нормально"], ["hard", "Сложно"]];
  return `<span class="rate">${opt.map(([k, label]) => `<button class="chip ${r === k ? "on" : ""}" data-rate="${k}">${label}</button>`).join("")}</span>`;
}

function nextBanner(step) {
  const next = nextStepAfter(step.id);
  return `<div class="callout ok"><span>Сдано.</span>${rateHTML(step)}<span class="spacer"></span>
      ${next ? `<a class="btn primary" href="#/step/${next.id}">Дальше</a>` : "<span>Это был последний шаг плана.</span>"}</div>`;
}

// ---------------------------------------------------------------- pages

// Time on each step, for the learning log. Only visible time counts; one visit counts at most 2 hours.
let timing = null;
function stopTiming() {
  if (!timing) return;
  if (timing.since) timing.ms += Date.now() - timing.since;
  const s = Math.min(7200, Math.round(timing.ms / 1000));
  if (s >= 5) {
    const st = progress.steps[timing.id] || (progress.steps[timing.id] = { status: "todo" });
    st.time_s = (st.time_s || 0) + s;
    scheduleSave();
  }
  timing = null;
}
function startTiming(id) {
  stopTiming();
  timing = { id, ms: 0, since: document.visibilityState === "visible" ? Date.now() : 0 };
}

function render() {
  cleanup?.();
  cleanup = null;
  stopTiming();
  const hash = location.hash || "#/";
  const [, route, arg] = hash.match(/^#\/(\w*)\/?(.*)$/) || [];

  if (route === "login") return renderLogin();
  if (route === "map") return renderMap();
  if (route === "review") return renderReviewPage();

  let step = null;
  if (route === "step") step = getStep(arg)?.step || null;
  if (route === "block") {
    const block = data.plan.weeks.flatMap((w) => w.blocks).find((b) => b.id === arg);
    if (block) step = block.items.find((s) => !s.optional && !isDone(s.id)) || block.items[0];
  }
  const now = currentStep();
  step ||= now;
  if (!step) return renderFinished();
  const entry = getStep(step.id);
  startTiming(step.id);

  app.innerHTML = `${header()}${timeline(entry.week.n)}
    <main class="layout">${panel(entry.week, entry.block, step.id)}
      <section class="stage">${stageHead(step, step === now)}<div data-next></div><div data-body></div>${stageFoot(step)}</section>
    </main>`;
  bindChrome();
  bindPanel();
  const body = app.querySelector("[data-body]");
  const nextEl = app.querySelector("[data-next]");
  const ctx = {
    week: entry.week,
    onDone: () => {
      refreshChrome(entry, step);
      nextEl.innerHTML = nextBanner(step);
      app.querySelector(".stage-foot")?.remove();
      nextEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    },
  };
  if (["leetcode", "review", "exercise"].includes(step.type)) cleanup = renderCode(body, step, ctx);
  else if (step.type === "quiz" || step.type === "oral") renderQuiz(body, step, ctx);
  else if (step.type === "theory") renderTheory(body, step, ctx);
  else if (step.type === "anki") renderAnki(body, step, ctx);
  else if (step.type === "practice") renderPractice(body, step, ctx);
  else if (step.type === "hours") renderHours(body, step, ctx);
  if (isDone(step.id)) nextEl.innerHTML = nextBanner(step);

  app.querySelector(".stage").addEventListener("click", (e) => {
    if (e.target.closest("[data-skip]")) {
      markDone(step.id, { skipped: true });
      render();
      return;
    }
    const r = e.target.closest("[data-rate]");
    if (r) {
      rateStep(step.id, r.dataset.rate);
      r.parentElement.outerHTML = rateHTML(step);
    }
  });
  window.scrollTo(0, 0);
}

function refreshChrome(entry, step) {
  app.querySelector("header.top").outerHTML = header();
  app.querySelector("nav.timeline").outerHTML = timeline(entry.week.n);
  app.querySelector("aside.panel").outerHTML = panel(entry.week, entry.block, step.id);
  bindChrome();
  bindPanel();
}

function renderMap() {
  const weeks = data.plan.weeks
    .map((w) => {
      const blocks = w.blocks
        .map((b) => {
          const p = blockProgress(b);
          const cls = [p.done === p.total ? "full" : "", blockLate(b) ? "late" : ""].join(" ");
          return `<a class="map-block ${cls}" href="#/block/${b.id}"><span>${esc(b.title)}</span><i style="--p:${p.total ? p.done / p.total : 0}"></i></a>`;
        })
        .join("");
      return `<div class="map-week"><div class="map-head"><b>${w.n}.</b> ${esc(w.title)} <span class="muted small">${fmtDate(w.days[0].date, false)} – ${fmtDate(w.days[6].date, false)}</span></div><div class="map-blocks">${blocks}</div></div>`;
    })
    .join("");
  app.innerHTML = `${header()}${timeline(0)}<main class="map">${weeks}</main>`;
  bindChrome();
}

function renderReviewPage() {
  app.innerHTML = `${header()}<main class="review-page"><div data-body></div></main>`;
  bindChrome();
  renderReview(app.querySelector("[data-body]"));
}

function renderFinished() {
  app.innerHTML = `${header()}${timeline(0)}<main class="map"><div class="card"><h2>Все шаги плана сданы</h2></div></main>`;
  bindChrome();
}

function renderLogin(message = "") {
  app.innerHTML = `<main class="login"><form class="card login-card" data-login>
      <h1>ML-дорожка</h1>
      <label>Логин<input class="answer" name="user" autocomplete="username" autocapitalize="off" required></label>
      <label>Пароль<input class="answer" name="password" type="password" autocomplete="current-password" required></label>
      <div class="bad small" data-msg>${esc(message)}</div>
      <button class="btn primary" type="submit">Войти</button>
      ${backend.server ? '<a class="small" href="#/">Продолжить без входа</a>' : ""}
    </form></main>`;
  app.querySelector("[data-login]").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const btn = e.target.querySelector("button");
    btn.disabled = true;
    btn.textContent = "Вхожу…";
    try {
      await login(String(f.get("user")), String(f.get("password")));
      await loadProgress();
      location.hash = "#/";
      render();
    } catch (err) {
      renderLogin(err.message);
    }
  });
}

// ---------------------------------------------------------------- bindings

function bindChrome() {
  const py = app.querySelector("[data-py]");
  if (py) {
    onStatus((s) => {
      if (!py.isConnected) return;
      py.className = `dot py-${s}`;
      py.title = { loading: "Python загружается", ready: "Python готов", busy: "Python работает", packages: "Загружаю numpy/pandas" }[s];
    });
  }
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
    backend.gist = null;
    location.hash = "#/login";
  });
}

function bindPanel() {
  const aside = app.querySelector("aside.panel");
  if (!aside) return;
  aside.querySelector("[data-collapse]").addEventListener("click", () => {
    const p = panelPrefs();
    p.collapsed = !p.collapsed;
    savePanelPrefs(p);
    aside.classList.toggle("collapsed", p.collapsed);
  });
  const handle = aside.querySelector("[data-resize]");
  handle.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    handle.setPointerCapture(e.pointerId);
    const startX = e.clientX;
    const startW = aside.getBoundingClientRect().width;
    const move = (ev) => {
      const w = Math.max(200, Math.min(560, startW + ev.clientX - startX));
      aside.style.setProperty("--panel-w", `${w}px`);
    };
    const up = () => {
      handle.removeEventListener("pointermove", move);
      const p = panelPrefs();
      p.w = Math.round(aside.getBoundingClientRect().width);
      savePanelPrefs(p);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up, { once: true });
  });
}

async function main() {
  try {
    await loadData();
    await loadProgress();
  } catch (err) {
    app.innerHTML = `<div class="card pad"><h2>Не удалось загрузить данные</h2><pre class="err">${esc(err.message)}</pre></div>`;
    return;
  }
  // On the hosted site the account is the only storage; locally the server works without it.
  if (!backend.server && !session() && (await accountConfigured()) && location.hash !== "#/login") location.hash = "#/login";
  warmUp();
  window.addEventListener("hashchange", render);
  document.addEventListener("visibilitychange", async () => {
    if (timing) {
      if (document.visibilityState === "visible") timing.since = Date.now();
      else if (timing.since) {
        timing.ms += Date.now() - timing.since;
        timing.since = 0;
      }
    }
    if (document.visibilityState === "visible" && (await pullRemote())) render();
    if (document.visibilityState === "hidden" && timing) {
      // Save the time so far: a phone may close the tab without warning.
      const id = timing.id;
      stopTiming();
      startTiming(id);
      timing.since = 0;
    }
  });
  render();
}

main();
