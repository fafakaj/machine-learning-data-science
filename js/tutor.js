// Step-by-step view of a Python run, like Python Tutor: the code with the current line, the call
// stack with variables, the objects on the heap and arrows from names to objects.
// The trace comes from harness.trace() in the worker; this file only draws it.
import { createEditor } from "./editor.js";
import { icon } from "./icons.js";
import { esc } from "./md.js";
import { runTrace, TimeoutError } from "./py.js";
import { progress, scheduleSave } from "./store.js";

const SAMPLE = `def add(x, items=[]):
    items.append(x)
    return items

a = add(1)
b = add(2)
print(a, b, a is b)
`;

function prim(v) {
  return `<span class="tu-prim">${esc(v[1])}</span>`;
}

function val(v) {
  return v[0] === "P" ? prim(v) : `<span class="tu-ref" data-ref="${v[1]}" title="ссылка на объект"></span>`;
}

function object(id, o) {
  if (!o) return "";
  const head = (label) => `<div class="tu-obj-h">${esc(label)}</div>`;
  let body = "";
  if (["list", "tuple", "deque", "set", "frozenset"].includes(o.t)) {
    const indexed = o.t !== "set" && o.t !== "frozenset";
    body = o.items.length
      ? `<div class="tu-cells">${o.items.map((x, i) => `<div class="tu-cell">${indexed ? `<span class="tu-i">${i}</span>` : ""}<span class="tu-v">${val(x)}</span></div>`).join("")}${o.more ? '<div class="tu-cell more">…</div>' : ""}</div>`
      : '<div class="tu-empty">пусто</div>';
    return `<div class="tu-obj" data-obj="${id}">${head(o.t)}${body}</div>`;
  }
  if (o.t === "dict") {
    body = o.pairs.length
      ? `<table class="tu-kv">${o.pairs.map(([k, x]) => `<tr><td>${val(k)}</td><td>${val(x)}</td></tr>`).join("")}${o.more ? '<tr><td colspan="2">…</td></tr>' : ""}</table>`
      : '<div class="tu-empty">пусто</div>';
    return `<div class="tu-obj" data-obj="${id}">${head(o.name)}${body}</div>`;
  }
  if (o.t === "instance") {
    body = o.attrs.length ? `<table class="tu-kv">${o.attrs.map(([k, x]) => `<tr><td>${esc(k)}</td><td>${val(x)}</td></tr>`).join("")}</table>` : "";
    return `<div class="tu-obj" data-obj="${id}">${head(`${o.v} (объект)`)}${body}</div>`;
  }
  const label = { function: "функция", class: "класс", str: "str" }[o.t] || "объект";
  return `<div class="tu-obj" data-obj="${id}">${head(label)}<div class="tu-text">${esc(o.v)}</div></div>`;
}

function frame(f, i, n, step) {
  const ret = i === n - 1 && step.event === "return" ? `<tr class="tu-ret"><td>возврат</td><td>${val(step.ret)}</td></tr>` : "";
  const rows = f.vars.map(([k, x]) => `<tr><td>${esc(k)}</td><td>${val(x)}</td></tr>`).join("");
  return `<div class="tu-frame ${i === n - 1 ? "top" : ""}"><div class="tu-frame-h">${esc(f.name)}</div>
      ${rows || ret ? `<table class="tu-kv">${rows}${ret}</table>` : '<div class="tu-empty">нет переменных</div>'}</div>`;
}

function eventText(step, top) {
  if (step.event === "call") return `Вызов ${esc(top)}`;
  if (step.event === "return") return top === "Глобальные" ? "Программа закончилась" : `Возврат из ${esc(top)}`;
  if (step.event === "exception") return `<span class="bad">Исключение: ${esc(step.exc)}</span>`;
  return "";
}

/** Draw arrows from every reference dot to its object. Coordinates are relative to the canvas. */
function drawArrows(canvas) {
  const svg = canvas.querySelector("svg.tu-arrows");
  const box = canvas.getBoundingClientRect();
  svg.setAttribute("width", canvas.scrollWidth);
  svg.setAttribute("height", canvas.scrollHeight);
  const paths = [];
  for (const dot of canvas.querySelectorAll("[data-ref]")) {
    const target = canvas.querySelector(`[data-obj="${dot.dataset.ref}"]`);
    if (!target) continue;
    const a = dot.getBoundingClientRect();
    const b = target.getBoundingClientRect();
    const x1 = a.left + a.width / 2 - box.left + canvas.scrollLeft;
    const y1 = a.top + a.height / 2 - box.top + canvas.scrollTop;
    const x2 = b.left - box.left + canvas.scrollLeft - 2;
    const y2 = b.top + 14 - box.top + canvas.scrollTop;
    const bend = Math.max(30, Math.abs(x2 - x1) / 2);
    // A target to the left of the dot (a nested reference back up the heap) loops around its left side.
    const c1 = x2 > x1 ? `${x1 + bend} ${y1}` : `${x1 + 40} ${y1 + 30}`;
    const c2 = x2 > x1 ? `${x2 - bend} ${y2}` : `${x2 - 40} ${y2}`;
    paths.push(`<path d="M${x1} ${y1} C${c1} ${c2} ${x2} ${y2}" marker-end="url(#tu-head)"/>`);
  }
  svg.innerHTML = `<defs><marker id="tu-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z"/></marker></defs>${paths.join("")}`;
}

/** Interactive viewer of one trace inside `root`. Returns a cleanup function. */
export function mountViewer(root, code, res, { note = "" } = {}) {
  const lines = code.replace(/\n$/, "").split("\n");
  const steps = res.steps;
  if (!steps.length) {
    root.innerHTML = `<div class="verdict bad">Код не запускается</div><pre class="err">${esc(res.error || "Нет шагов")}</pre>`;
    return () => {};
  }
  let i = 0;
  root.innerHTML = `<div class="tutor">
      <div class="tu-left">
        ${res.call ? `<div class="small"><span class="muted">Запуск на тесте 1:</span> <code>${esc(res.call)}</code></div>` : ""}
        ${note ? `<div class="note">${esc(note)}</div>` : ""}
        <div class="tu-code" data-code>${lines.map((l, k) => `<div class="tu-line" data-line="${k + 1}"><span class="tu-mark"></span><span class="tu-n">${k + 1}</span><span class="tu-src">${esc(l) || " "}</span></div>`).join("")}</div>
        <div class="tu-legend small muted"><span class="tu-key prev"></span>только что выполнена <span class="tu-key cur"></span>выполнится следующей</div>
        <div class="tu-nav">
          <button class="btn small" data-go="first" aria-label="В начало">«</button>
          <button class="btn small" data-go="prev">${icon("left")}Назад</button>
          <button class="btn small primary" data-go="next">Вперёд${icon("arrow")}</button>
          <button class="btn small" data-go="last" aria-label="В конец">»</button>
        </div>
        <input class="tu-range" type="range" min="0" max="${steps.length - 1}" value="0" aria-label="Шаг" data-range>
        <div class="tu-status"><span data-count></span><span data-event></span></div>
        ${res.limited ? `<div class="note">Показаны первые ${steps.length} шагов: дальше код не трассируется.</div>` : ""}
        <div class="sub">Вывод</div><pre class="stdout tu-out" data-out></pre>
        ${res.error ? `<pre class="err" data-error hidden>${esc(res.error)}</pre>` : ""}
      </div>
      <div class="tu-canvas" data-canvas>
        <div class="tu-col"><div class="sub">Кадры</div><div data-frames></div></div>
        <div class="tu-col"><div class="sub">Объекты</div><div data-heap></div></div>
        <svg class="tu-arrows" aria-hidden="true"></svg>
      </div>
    </div>`;
  const canvas = root.querySelector("[data-canvas]");
  const codeBox = root.querySelector("[data-code]");

  const show = () => {
    const step = steps[i];
    const prev = steps[i - 1];
    root.querySelectorAll(".tu-line.cur, .tu-line.prev, .tu-line.ret").forEach((el) => el.classList.remove("cur", "prev", "ret"));
    if (prev && prev.line !== step.line) codeBox.querySelector(`[data-line="${prev.line}"]`)?.classList.add("prev");
    const cur = codeBox.querySelector(`[data-line="${step.line}"]`);
    cur?.classList.add(step.event === "return" ? "ret" : "cur");
    if (cur) {
      const top = cur.offsetTop - codeBox.offsetTop;
      if (top < codeBox.scrollTop || top > codeBox.scrollTop + codeBox.clientHeight - 30) codeBox.scrollTop = top - codeBox.clientHeight / 3;
    }
    const n = step.frames.length;
    root.querySelector("[data-frames]").innerHTML = step.frames.map((f, k) => frame(f, k, n, step)).join("") || '<div class="tu-empty">—</div>';
    const ids = Object.keys(step.heap).sort((a, b) => a - b);
    root.querySelector("[data-heap]").innerHTML = ids.map((id) => object(id, step.heap[id])).join("") || '<div class="tu-empty">Пока нет объектов</div>';
    root.querySelector("[data-count]").textContent = `Шаг ${i + 1} из ${steps.length}`;
    root.querySelector("[data-event]").innerHTML = eventText(step, step.frames[n - 1]?.name || "");
    root.querySelector("[data-out]").textContent = step.out || " ";
    root.querySelector("[data-range]").value = i;
    root.querySelector("[data-error]")?.toggleAttribute("hidden", i !== steps.length - 1);
    root.querySelector("[data-go=prev]").disabled = root.querySelector("[data-go=first]").disabled = i === 0;
    root.querySelector("[data-go=next]").disabled = root.querySelector("[data-go=last]").disabled = i === steps.length - 1;
    requestAnimationFrame(() => canvas.isConnected && drawArrows(canvas));
  };
  const go = (k) => {
    i = Math.max(0, Math.min(steps.length - 1, k));
    show();
  };
  root.addEventListener("click", (e) => {
    const b = e.target.closest("[data-go]");
    if (!b) return;
    const to = { first: 0, prev: i - 1, next: i + 1, last: steps.length - 1 }[b.dataset.go];
    go(to);
  });
  root.querySelector("[data-range]").addEventListener("input", (e) => go(+e.target.value));
  const keys = (e) => {
    if (e.target.closest(".cm-editor, input:not([type=range]), textarea")) return;
    if (e.key === "ArrowRight") go(i + 1);
    else if (e.key === "ArrowLeft") go(i - 1);
    else return;
    e.preventDefault();
  };
  document.addEventListener("keydown", keys);
  const ro = new ResizeObserver(() => drawArrows(canvas));
  ro.observe(canvas);
  canvas.addEventListener("scroll", () => drawArrows(canvas));
  show();
  return () => {
    document.removeEventListener("keydown", keys);
    ro.disconnect();
  };
}

async function traceInto(root, code, problem, note) {
  root.innerHTML = '<div class="muted spinner">Выполняю код по шагам…</div>';
  try {
    const res = await runTrace(code, problem);
    const noCalls = !problem && !res.steps.some((s) => s.frames.length > 1);
    return mountViewer(root, code, res, { note: note || (noCalls ? "Функции не вызывались. Чтобы увидеть, как работает функция, вызовите её в конце кода." : "") });
  } catch (err) {
    root.innerHTML = err instanceof TimeoutError
      ? '<div class="verdict warn">Код работает слишком долго и был остановлен</div>'
      : `<div class="verdict bad">Ошибка</div><pre class="err">${esc(err.message)}</pre>`;
    return () => {};
  }
}

/** Full-screen dialog over the current page: the code of a step, run step by step. */
export function openTutor({ code, problem = null, title = "По шагам" }) {
  const dlg = document.createElement("dialog");
  dlg.className = "tutor-dlg";
  dlg.innerHTML = `<div class="tutor-dlg-h"><b>${esc(title)}</b><span class="spacer"></span>
      <button class="icon-btn" data-close aria-label="Закрыть">${icon("close")}</button></div><div class="tutor-dlg-b" data-view></div>`;
  document.body.append(dlg);
  let cleanup = () => {};
  const close = () => {
    cleanup();
    dlg.remove();
  };
  dlg.addEventListener("close", close);
  dlg.querySelector("[data-close]").addEventListener("click", () => dlg.close());
  dlg.showModal();
  traceInto(dlg.querySelector("[data-view]"), code, problem).then((c) => {
    if (dlg.isConnected) cleanup = c;
    else c();
  });
}

/** The #/tutor page: any code, run step by step. The code is saved with the progress. */
export function renderTutorPage(root) {
  const KEY = "tutor";
  root.innerHTML = `<div class="page-head"><h1>Визуализатор кода</h1>
      <p class="muted">Как Python Tutor: код выполняется по шагам, видно переменные, объекты и ссылки между ними.</p></div>
    <div class="tutor-edit">
      <div class="editor tutor-editor" data-editor></div>
      <div class="toolbar"><button class="btn primary" data-act="trace" title="Ctrl+Enter">${icon("play")}Выполнить по шагам</button>
        <span class="spacer"></span><button class="btn ghost small" data-act="sample">Пример</button></div>
    </div>
    <div class="tutor-view" data-view></div>`;
  let cleanup = () => {};
  const view = root.querySelector("[data-view]");
  const run = async () => {
    cleanup();
    cleanup = await traceInto(view, editor.value, null);
  };
  const editor = createEditor(root.querySelector("[data-editor]"), {
    doc: progress.code[KEY] ?? SAMPLE,
    onChange: (text) => {
      progress.code[KEY] = text;
      scheduleSave();
    },
    onRun: run,
  });
  root.addEventListener("click", (e) => {
    const act = e.target.closest("[data-act]")?.dataset.act;
    if (act === "trace") run();
    if (act === "sample") editor.value = SAMPLE;
  });
  return () => cleanup();
}
