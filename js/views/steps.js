// Non-code steps: theory, Anki cards, practice checklist.
import { esc, md } from "../md.js";
import { data, isDone, logEvent, markDone, markUndone, progress, scheduleSave, stepState } from "../store.js";
import { sourceCard } from "./common.js";
import { ankiToday, runSession } from "./review.js";

function doneBar(step, label = "Отметить как сделано") {
  return isDone(step.id)
    ? `<div class="done-bar ok">Сделано <button class="link-btn" data-act="undo">отменить</button></div>`
    : `<div class="done-bar"><button class="btn primary" data-act="done">${label}</button></div>`;
}

function bindDone(root, step, onDone, rerender) {
  root.addEventListener("click", (e) => {
    const act = e.target.closest("[data-act]")?.dataset.act;
    if (act === "done") {
      markDone(step.id);
      onDone?.();
      rerender();
    }
    if (act === "undo") {
      markUndone(step.id);
      rerender();
    }
  });
}

export function renderTheory(root, step, ctx) {
  const st = stepState(step.id);
  const draw = () => {
    const opened = st.opened || isDone(step.id);
    root.innerHTML = `<div class="card theory">
        ${step.intro ? `<div class="md">${md(step.intro)}</div>` : ""}
        ${sourceCard(step.source, { big: true })}
        ${step.alt?.length ? `<details class="alt"><summary>Другие источники</summary>${step.alt.map((s) => sourceCard(s)).join("")}</details>` : ""}
        ${step.do ? `<div class="md do">${md(step.do)}</div>` : ""}
        ${opened ? doneBar(step, "Прочитал") : `<div class="done-bar"><span class="muted small">Сначала откройте источник</span><button class="btn primary" disabled>Прочитал</button></div>`}
      </div>`;
  };
  root.addEventListener("click", (e) => {
    if (e.target.closest("[data-source]") && !st.opened) {
      st.opened = new Date().toISOString();
      logEvent("open", step.id);
      setTimeout(draw, 300);
    }
  });
  bindDone(root, step, ctx.onDone, draw);
  draw();
}

/**
 * Anki inside the site: due cards of every deck, then new cards of this step's deck in plan order.
 * Answers go to the shared review boxes, so the cards come back in "Повторение" on their own.
 */
export function renderAnki(root, step, ctx) {
  const deck = step.deck || "ML";
  root.innerHTML = '<div class="card anki-step" data-anki></div>';
  const box = root.querySelector("[data-anki]");
  const start = (extra = 0) => {
    const t = ankiToday(deck);
    const fresh = extra ? t.fresh.slice(0, t.newToday.length + extra) : t.newToday;
    runSession(box, [...t.due, ...fresh], {
      onFinish: (right, total) => {
        if (!isDone(step.id)) {
          markDone(step.id);
          ctx.onDone?.();
        }
        draw(`Готово: ${right} из ${total} с первого раза.`);
      },
    });
  };
  const draw = (summary = "") => {
    box.onclick = null;
    const t = ankiToday(deck);
    const queue = t.due.length + t.newToday.length;
    const more = t.fresh.length > t.newToday.length;
    const scope = deck === "ML" ? "Все колоды" : `Колода «${esc(deck)}»`;
    box.innerHTML = `
      ${step.intro ? `<div class="md">${md(step.intro)}</div>` : ""}
      ${summary ? `<div class="callout ok">${esc(summary)}</div>` : ""}
      <div class="anki-stats">
        <div><b>${t.due.length}</b><span>к повторению</span></div>
        <div><b>${t.newToday.length}</b><span>новых сегодня</span></div>
        <div><b>${t.met} из ${t.total}</b><span>${scope}: изучено</span></div>
      </div>
      <div class="review-actions">
        ${queue ? `<button class="btn primary big" data-anki-start>Начать (${queue})</button>` : ""}
        ${more ? `<button class="btn ${queue ? "ghost" : ""}" data-anki-more>Ещё 10 новых</button>` : ""}
      </div>
      ${queue ? "" : `<p class="muted">${more ? "Лимит новых карточек на сегодня исчерпан." : "На сегодня карточек нет."}</p>`}
      <p class="muted small">Карточки повторяются прямо здесь, приложение Anki не нужно. Ответы попадают в общее «Повторение»: карточки вернутся сами по расписанию. Клавиши: пробел — ответ, 1–3 — оценка.</p>
      ${!queue || isDone(step.id) ? doneBar(step, "Повторил") : ""}`;
  };
  box.addEventListener("click", (e) => {
    if (e.target.closest("[data-anki-start]")) start();
    if (e.target.closest("[data-anki-more]")) start(10);
  });
  bindDone(root, step, ctx.onDone, () => draw());
  draw();
}

async function autoCheck(auto, owner) {
  const repo = `${owner}/${auto.repo}`;
  const api = `https://api.github.com/repos/${repo}`;
  const res = async (url) => {
    const r = await fetch(url, { headers: { Accept: "application/vnd.github+json" } });
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`GitHub ответил ${r.status}`);
    return r.json();
  };
  if (auto.kind === "github-repo") {
    const j = await res(api);
    return j ? { ok: true, msg: `Репозиторий ${repo} найден` } : { ok: false, msg: `Репозиторий ${repo} не найден (или он приватный)` };
  }
  if (auto.kind === "github-file") {
    const j = await res(`${api}/contents/${auto.path}`);
    return j ? { ok: true, msg: `Файл ${auto.path} есть` } : { ok: false, msg: `Нет файла ${auto.path} в ${repo}` };
  }
  if (auto.kind === "github-ci") {
    const j = await res(`${api}/actions/runs?branch=main&per_page=1`);
    const run = j?.workflow_runs?.[0];
    if (!run) return { ok: false, msg: "Запусков GitHub Actions на main пока нет" };
    if (run.status !== "completed") return { ok: false, msg: `CI ещё идёт (${run.status})` };
    return run.conclusion === "success"
      ? { ok: true, msg: `Последний запуск CI зелёный: ${run.head_commit?.message?.split("\n")[0] || run.head_sha.slice(0, 7)}` }
      : { ok: false, msg: `Последний запуск CI: ${run.conclusion}. Откройте Actions и исправьте ошибку.` };
  }
  return { ok: false, msg: "Неизвестная проверка" };
}

export function renderPractice(root, step, ctx) {
  const checks = (progress.checklist[step.id] ||= {});
  const owner = data.plan.github_user;
  const draw = () => {
    const items = step.items.map((it, i) => {
      const c = checks[i];
      const auto = it.auto
        ? `<button class="btn small" data-auto="${i}">Проверить на GitHub</button><span class="small ${c?.ok ? "ok" : c?.msg ? "bad" : "muted"}">${esc(c?.msg || "")}</span>`
        : "";
      const note = it.write ? progress.notes[`${step.id}:${i}`] || "" : "";
      return `<li class="check-item ${c?.ok ? "ok" : ""}">
          <label><input type="checkbox" data-i="${i}" ${c?.ok ? "checked" : ""} ${it.auto || it.write ? "disabled" : ""}> <span class="md">${md(it.text)}</span></label>
          ${it.write ? `<textarea class="answer note-input" rows="${it.rows || 5}" data-note="${i}" placeholder="Пишите здесь — текст сохраняется сам">${esc(note)}</textarea>` : ""}
          ${it.source ? sourceCard(it.source) : ""}
          ${it.auto ? `<div class="auto">${auto}</div>` : ""}</li>`;
    });
    const allOk = step.items.every((_, i) => checks[i]?.ok);
    root.innerHTML = `<div class="card practice">
        ${step.intro ? `<div class="md">${md(step.intro)}</div>` : ""}
        <ol class="checklist">${items.join("")}</ol>
        ${isDone(step.id) ? doneBar(step) : allOk ? doneBar(step, "Готово") : `<div class="done-bar"><span class="muted small">Отметьте все пункты</span><button class="btn primary" disabled>Готово</button></div>`}
      </div>`;
  };
  // Written notes: saved on every keystroke; the item counts as done once the answer has some substance.
  root.addEventListener("input", (e) => {
    const i = e.target.dataset.note;
    if (i === undefined) return;
    const text = e.target.value;
    progress.notes[`${step.id}:${i}`] = text;
    const ok = text.trim().length >= 20;
    if (!!checks[i]?.ok !== ok) {
      checks[i] = { ok, at: new Date().toISOString() };
      const li = e.target.closest("li");
      li.classList.toggle("ok", ok);
      li.querySelector("input[type=checkbox]").checked = ok;
      const allOk = step.items.every((_, k) => checks[k]?.ok);
      const bar = root.querySelector(".done-bar");
      if (!isDone(step.id)) bar.outerHTML = allOk ? doneBar(step, "Готово") : bar.outerHTML;
    }
    scheduleSave();
  });
  root.addEventListener("change", (e) => {
    const i = e.target.dataset.i;
    if (i === undefined) return;
    checks[i] = { ok: e.target.checked, at: new Date().toISOString() };
    scheduleSave();
    draw();
  });
  root.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-auto]");
    if (!b) return;
    const i = +b.dataset.auto;
    b.disabled = true;
    b.textContent = "Проверяю…";
    try {
      checks[i] = { ...(await autoCheck(step.items[i].auto, owner)), at: new Date().toISOString() };
    } catch (err) {
      checks[i] = { ok: false, msg: `Не удалось проверить: ${err.message}` };
    }
    logEvent("autocheck", step.id, { i, ok: checks[i].ok });
    scheduleSave();
    draw();
  });
  bindDone(root, step, ctx.onDone, draw);
  draw();
}
