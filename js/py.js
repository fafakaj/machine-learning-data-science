// Main-thread wrapper around pyworker.js with a wall-clock timeout.
// An infinite loop in the student's code cannot be interrupted inside the worker,
// so on timeout the worker is terminated and a fresh one is started.

const listeners = new Set();
let worker = null;
let status = "loading"; // loading | ready | busy
let seq = 0;
const pending = new Map();

function setStatus(s) {
  status = s;
  listeners.forEach((fn) => fn(status));
}

function spawn() {
  worker = new Worker(new URL("./pyworker.js", import.meta.url), { type: "module" });
  setStatus("loading");
  worker.onmessage = (event) => {
    const msg = event.data;
    if (msg.ready) {
      setStatus(pending.size ? "busy" : "ready");
      return;
    }
    if (msg.loadingPackages) {
      setStatus("packages");
      return;
    }
    const p = pending.get(msg.id);
    if (!p) return;
    pending.delete(msg.id);
    clearTimeout(p.timer);
    if (!pending.size) setStatus("ready");
    msg.ok ? p.resolve(msg.result) : p.reject(new Error(msg.error));
  };
  worker.onerror = (event) => {
    console.error("pyworker error", event);
  };
}

export function onStatus(fn) {
  listeners.add(fn);
  fn(status);
  return () => listeners.delete(fn);
}

export function pyStatus() {
  return status;
}

export class TimeoutError extends Error {}

function call(op, args, timeoutMs = 20000) {
  if (!worker) spawn();
  const id = ++seq;
  setStatus("busy");
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      // Kill the stuck worker; every pending call fails, the next call gets a new worker.
      worker.terminate();
      worker = null;
      for (const [, p] of pending) {
        clearTimeout(p.timer);
        p.reject(new TimeoutError("timeout"));
      }
      pending.clear();
      spawn();
    }, timeoutMs);
    pending.set(id, { resolve, reject, timer });
    worker.postMessage({ id, op, args });
  });
}

// Start loading Pyodide as soon as the app opens.
export function warmUp() {
  if (!worker) spawn();
}

export const runProblem = (problem, code, includeHidden) => call("run", [problem, code, includeHidden], includeHidden ? 25000 : 10000);
export const runScript = (exercise, code) => call("script", [exercise, code], 15000);
export const runSnippet = (code) => call("snippet", [code], 8000);
export const checkExpr = (answer, reference, vars, points) => call("expr", [answer, reference, vars, points], 5000);
