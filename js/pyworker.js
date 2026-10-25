// Web Worker: runs the student's Python with Pyodide and app/py/harness.py.
// Messages in:  {id, op: "run" | "script" | "snippet" | "expr", args: [...]}
// Messages out: {id, ok: true, result} | {id, ok: false, error} | {ready: true, ms}
import { loadPyodide } from "../vendor/pyodide/pyodide.mjs";

const started = performance.now();
const ready = (async () => {
  const py = await loadPyodide({ indexURL: new URL("../vendor/pyodide/", import.meta.url).href });
  const src = await (await fetch(new URL("../py/harness.py", import.meta.url), { cache: "no-store" })).text();
  py.FS.writeFile("/home/pyodide/harness.py", src);
  py.runPython(`
import sys, json
sys.path.insert(0, "/home/pyodide")
sys.setrecursionlimit(3000)
import harness

def _call(op, args_json):
    args = json.loads(args_json)
    if op == "run":
        out = harness.run(args[0], args[1], args[2])
    elif op == "script":
        out = harness.run_script(args[0], args[1])
    elif op == "snippet":
        out = harness.run_snippet(args[0])
    elif op == "expr":
        out = harness.check_expr(*args)
    else:
        raise ValueError(op)
    return json.dumps(out, ensure_ascii=False, default=repr)
`);
  self.postMessage({ ready: true, ms: Math.round(performance.now() - started) });
  return py;
})();

self.onmessage = async (event) => {
  const { id, op, args } = event.data;
  try {
    const py = await ready;
    // numpy / pandas / scikit-learn are local wheels in vendor/pyodide; load them on first import.
    const sources = op === "run" ? [args[1]] : op === "script" ? [args[1], args[0].tests] : op === "snippet" ? [args[0]] : [];
    const code = sources.join("\n");
    if (/\b(numpy|pandas|sklearn|scipy)\b/.test(code)) {
      self.postMessage({ loadingPackages: true });
      await py.loadPackagesFromImports(code);
    }
    const call = py.globals.get("_call");
    const result = JSON.parse(call(op, JSON.stringify(args)));
    call.destroy();
    self.postMessage({ id, ok: true, result });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err && err.message ? err.message : err) });
  }
};
