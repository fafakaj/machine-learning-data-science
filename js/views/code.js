// Code step: LeetCode problem, re-solve ("review") or Python exercise.
import { createEditor } from "../editor.js";
import { icon } from "../icons.js";
import { esc, md } from "../md.js";
import { runProblem, runScript, TimeoutError } from "../py.js";
import { openTutor } from "../tutor.js";
import { data, isDone, logEvent, markDone, progress, scheduleSave, stepState } from "../store.js";
import { sourceCard } from "./common.js";

const STATUS = {
  OK: ["ok", "верно"],
  WA: ["bad", "неверный ответ"],
  RE: ["bad", "ошибка выполнения"],
  TLE: ["warn", "слишком медленно"],
};

function codeKey(step) {
  // A re-solve starts from the starter code, not from the first solution.
  if (step.type === "review") return `step:${step.id}`;
  if (step.type === "exercise") return `ex:${step.exercise}`;
  return `lc:${step.problem}`;
}

export function resultsHTML(res, mode) {
  if (!res.compiled) {
    return `<div class="verdict bad">Код не запускается</div><pre class="err">${esc(res.error)}</pre>`;
  }
  const allOk = res.passed === res.total && res.total > 0;
  const firstBad = res.results.find((r) => r.status !== "OK");
  let head;
  if (allOk && mode === "submit") head = `<div class="verdict ok">Принято: ${res.passed} из ${res.total} тестов</div>`;
  else if (allOk) head = `<div class="verdict ok">Видимые тесты: ${res.passed} из ${res.total}. Теперь «Сдать».</div>`;
  else head = `<div class="verdict bad">Пройдено ${res.passed} из ${res.total}${firstBad ? `. Тест ${firstBad.n}: ${STATUS[firstBad.status][1]}` : ""}</div>`;

  const rows = res.results.map((r) => {
    const [cls, label] = STATUS[r.status];
    const title = r.title ? esc(r.title) : r.kind === "perf" ? "Тест на скорость" : r.hidden ? `Скрытый тест ${r.n}` : `Тест ${r.n}`;
    const open = r.status !== "OK" && r === firstBad ? " open" : "";
    let body = "";
    if (r.args !== undefined) body += `<div class="kv"><span>Вход</span><code>${esc(r.args)}</code></div>`;
    if (r.expected !== undefined) body += `<div class="kv"><span>Ожидалось</span><code>${esc(r.expected)}</code></div>`;
    if (r.got !== undefined && !(r.hidden && r.status === "OK")) body += `<div class="kv"><span>Ваш ответ</span><code>${esc(r.got)}</code></div>`;
    if (r.hidden && r.status === "WA") body += `<div class="note">Вход скрыт. Проверьте крайние случаи: пусто, один элемент, повторы, отрицательные.</div>`;
    if (r.status === "TLE") body += `<div class="note">${r.ms} мс при лимите ${r.limit_ms} мс. Нужна сложность лучше.</div>`;
    if (r.error) body += `<pre class="err">${esc(r.error)}</pre>`;
    if (r.stdout) body += `<div class="kv"><span>print()</span><pre class="stdout">${esc(r.stdout)}</pre></div>`;
    return `<details class="test ${cls}"${open}><summary><span class="t-mark"></span>${title} <small>${label}</small></summary>${body || '<div class="note">Без деталей</div>'}</details>`;
  });
  return head + `<div class="tests">${rows.join("")}</div>`;
}

export function renderCode(root, step, { onDone }) {
  const isExercise = step.type === "exercise";
  const item = isExercise ? data.exercises[step.exercise] : data.problems[step.problem];
  if (!item) {
    root.innerHTML = `<div class="card">Нет данных для шага (${esc(step.problem || step.exercise)}).</div>`;
    return;
  }
  const st = stepState(step.id);
  const key = codeKey(step);
  const starter = item.starter_code;
  const code = progress.code[key] ?? starter;
  const hintsShown = st.hints_used || 0;

  const examples = (item.examples || [])
    .map((e, i) => `<div class="example"><div class="ex-title">Пример ${i + 1}</div>
      <div class="kv"><span>Вход</span><code>${esc(e.input)}</code></div>
      <div class="kv"><span>Выход</span><code>${esc(e.output)}</code></div>
      ${e.explain_ru ? `<div class="note">${md(e.explain_ru)}</div>` : ""}</div>`)
    .join("");

  const meta = isExercise
    ? ""
    : `<div class="meta"><span class="tag diff-${item.difficulty.toLowerCase()}">${item.difficulty}</span>
        <a class="tag link" href="${item.leetcode_url}" target="_blank" rel="noopener">LeetCode</a></div>`;

  root.innerHTML = `
    <div class="code-step">
      <section class="statement card">
        ${isExercise ? "" : `<div class="muted small">${esc(item.title_en)}</div>`}
        ${meta}
        <div class="md">${md(item.statement_ru)}</div>
        ${examples}
        ${item.constraints_ru ? `<div class="sub">Ограничения</div><ul class="small">${item.constraints_ru.map((c) => `<li>${esc(c)}</li>`).join("")}</ul>` : ""}
        ${item.complexity_target ? `<p class="small"><span class="muted">Цель:</span> ${esc(item.complexity_target)}</p>` : ""}
        ${step.source ? `<details class="alt"><summary>Теория по приёму</summary>${sourceCard(step.source)}</details>` : ""}
        <div class="sub">Подсказки</div>
        <div class="hints">${item.hints_ru.map((hint, i) => `<div class="hint ${i < hintsShown ? "" : "hidden"}"><b>${i + 1}.</b> ${md(hint)}</div>`).join("")}</div>
        <button class="btn small" data-act="hint" ${hintsShown >= item.hints_ru.length ? "disabled" : ""}>Подсказка ${Math.min(hintsShown + 1, item.hints_ru.length)} из ${item.hints_ru.length}</button>
      </section>
      <section class="workbench">
        <div class="toolbar">
          <button class="btn" data-act="run" title="Ctrl+Enter">${icon("play")}Запустить</button>
          <button class="btn primary" data-act="submit" title="Ctrl+Shift+Enter">Сдать</button>
          <span class="spacer"></span>
          <button class="btn ghost small" data-act="trace" title="Выполнить код по шагам, как в Python Tutor" aria-label="По шагам">${icon("step")}<span class="btn-label">По шагам</span></button>
          <button class="btn ghost small" data-act="reset">Сбросить</button>
        </div>
        <div class="editor" data-editor></div>
        <div class="results" data-results>
          ${isDone(step.id) ? '<div class="verdict ok">Сдано</div>' : '<div class="muted small">«Запустить» (Ctrl+Enter) проверяет примеры, «Сдать» (Ctrl+Shift+Enter) — все тесты.</div>'}
        </div>
      </section>
    </div>`;

  const results = root.querySelector("[data-results]");
  const editor = createEditor(root.querySelector("[data-editor]"), {
    doc: code,
    onChange: (text) => {
      progress.code[key] = text;
      scheduleSave();
    },
    onRun: () => run(false),
    onSubmit: () => run(true),
  });


  let busy = false;
  async function run(submit) {
    if (busy) return;
    busy = true;
    root.querySelectorAll("[data-act=run],[data-act=submit]").forEach((b) => (b.disabled = true));
    results.innerHTML = `<div class="muted spinner">${submit ? "Проверяю все тесты…" : "Запускаю видимые тесты…"}</div>`;
    const source = editor.value;
    try {
      const res = isExercise ? await runScript(item, source) : await runProblem(item, source, submit);
      results.innerHTML = resultsHTML(res, isExercise || submit ? "submit" : "run");
      st.attempts = (st.attempts || 0) + (submit ? 1 : 0);
      logEvent(submit ? "submit" : "run", step.id, { passed: res.passed, total: res.total });
      const accepted = res.compiled && res.passed === res.total && res.total > 0 && (submit || isExercise);
      if (accepted && !isDone(step.id)) {
        markDone(step.id, { solution: source, hints: st.hints_used || 0 });
        onDone?.();
      }
    } catch (err) {
      if (err instanceof TimeoutError) {
        results.innerHTML = `<div class="verdict warn">Код работает дольше лимита и был остановлен</div>
          <div class="note">Чаще всего это бесконечный цикл (условие выхода из while не выполняется) или слишком медленный алгоритм. Python перезапускается, подождите пару секунд.</div>`;
        logEvent("timeout", step.id);
      } else {
        results.innerHTML = `<div class="verdict bad">Ошибка проверки</div><pre class="err">${esc(err.message)}</pre>`;
      }
    } finally {
      busy = false;
      root.querySelectorAll("[data-act=run],[data-act=submit]").forEach((b) => (b.disabled = false));
    }
  }

  root.addEventListener("click", (e) => {
    const act = e.target.closest("[data-act]")?.dataset.act;
    if (act === "run") run(false);
    if (act === "submit") run(true);
    if (act === "trace") openTutor({ code: editor.value, problem: isExercise ? null : item, title: isExercise ? "Код по шагам" : `#${item.id} по шагам` });
    if (act === "reset" && confirm("Заменить код шаблоном?")) {
      editor.value = starter;
    }
    if (act === "hint") {
      const n = (st.hints_used || 0) + 1;
      st.hints_used = n;
      root.querySelectorAll(".hint")[n - 1]?.classList.remove("hidden");
      const btn = e.target.closest("button");
      if (n >= item.hints_ru.length) btn.disabled = true;
      else btn.textContent = `Показать подсказку ${n + 1} из ${item.hints_ru.length}`;
      logEvent("hint", step.id, { n });
    }
  });
  if (!isExercise || step.type !== "review") editor.focus();
}
