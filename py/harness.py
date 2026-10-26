"""Test runner for LeetCode-style problems.

Runs in the browser (Pyodide, inside a Web Worker) and in CPython (validation).
Entry point: run(problem, user_code, include_hidden) -> dict (JSON-serializable).

Problem spec (one entry of app/data/problems.json):
    method       name of the Solution method, e.g. "twoSum"
                 (for kind == "design": the class name, e.g. "MinStack")
    kind         "function" (default) or "design"
    arg_types    list of type names, one per argument (see TYPES)
    ret_type     type name of the return value
    compare      "exact" | "unordered" | "unordered_nested" | "float" | "check"
    inplace      index of the argument to compare instead of the return value, or null
    check        Python source with `def check(args, result, expected) -> bool`
                 (args are the plain JSON values, result is already dumped to JSON form)
    tests        [{"args": [...], "expected": ..., "hidden": bool}]
    perf         [{"gen": "<source with def gen(): return [args...]>",
                   "expected": ... or "expected_sha256": digest(answer), "time_limit_ms": 1000}]
    design tests {"ops": ["MinStack", "push", ...], "args": [[], [1], ...],
                  "expected": [null, null, ...]}
"""

from __future__ import annotations

import bisect
import collections
import contextlib
import copy
import functools
import hashlib
import heapq
import itertools
import json
import io
import linecache
import math
import re
import sys
import time
import types
import traceback
from typing import Dict, List, Optional, Set, Tuple

STDOUT_LIMIT = 2000
DUMP_LIMIT = 100_000


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"


def _build_list(values):
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def _build_list_cycle(spec):
    # spec = {"values": [...], "pos": k}; pos == -1 means no cycle.
    head = _build_list(spec["values"])
    pos = spec.get("pos", -1)
    if head is None or pos < 0:
        return head
    nodes = []
    node = head
    while node:
        nodes.append(node)
        node = node.next
    nodes[-1].next = nodes[pos]
    return head


def _build_tree(values):
    # LeetCode level order: [3, 9, 20, null, null, 15, 7]
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = collections.deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def _dump_list(head):
    out = []
    seen = set()
    while head is not None:
        if id(head) in seen or len(out) > DUMP_LIMIT:
            raise ValueError("список зациклен или слишком длинный")
        seen.add(id(head))
        out.append(head.val)
        head = head.next
    return out


def _dump_tree(root):
    out = []
    queue = collections.deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        if len(out) > DUMP_LIMIT:
            raise ValueError("дерево слишком большое или зациклено")
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


BUILDERS = {
    "ListNode": _build_list,
    "ListNodeCycle": _build_list_cycle,
    "TreeNode": _build_tree,
}
DUMPERS = {
    "ListNode": _dump_list,
    "TreeNode": _dump_tree,
}


def build(type_name, value):
    builder = BUILDERS.get(type_name)
    return builder(value) if builder else copy.deepcopy(value)


def dump(type_name, value):
    dumper = DUMPERS.get(type_name)
    if dumper:
        return dumper(value)
    if isinstance(value, tuple):
        return list(value)
    return value


def _sorted_key(x):
    return (str(type(x)), x if not isinstance(x, list) else _nested_key(x))


def _nested_key(x):
    return [_sorted_key(i) for i in x]


def normalize(mode, value):
    """Canonical order for unordered answers, so one digest fits every valid order."""
    try:
        if mode == "unordered":
            return sorted(value, key=_sorted_key)
        if mode == "unordered_nested":
            return sorted((sorted(x, key=_sorted_key) for x in value), key=_nested_key)
    except TypeError:
        return value
    return value


def compare(mode, got, expected, args, check_fn):
    if mode == "check":
        return bool(check_fn(copy.deepcopy(args), got, expected))
    if mode == "float":
        return isinstance(got, (int, float)) and math.isclose(got, expected, rel_tol=1e-5, abs_tol=1e-5)
    if mode == "unordered":
        return isinstance(got, list) and sorted(got, key=_sorted_key) == sorted(expected, key=_sorted_key)
    if mode == "unordered_nested":
        if not isinstance(got, list) or not all(isinstance(g, list) for g in got):
            return False
        norm = lambda xs: sorted((sorted(x, key=_sorted_key) for x in xs), key=_nested_key)  # noqa: E731
        return norm(got) == norm(expected)
    # exact: bool must stay bool (LeetCode accepts 1 for True, we do too)
    return got == expected


def digest(value):
    """SHA-256 of a canonical JSON dump; perf tests store this instead of a huge answer."""
    text = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def _namespace():
    return {
        "__name__": "solution",
        "List": List,
        "Optional": Optional,
        "Dict": Dict,
        "Set": Set,
        "Tuple": Tuple,
        "ListNode": ListNode,
        "TreeNode": TreeNode,
        "collections": collections,
        "defaultdict": collections.defaultdict,
        "Counter": collections.Counter,
        "deque": collections.deque,
        "heapq": heapq,
        "heappush": heapq.heappush,
        "heappop": heapq.heappop,
        "bisect": bisect,
        "bisect_left": bisect.bisect_left,
        "bisect_right": bisect.bisect_right,
        "functools": functools,
        "lru_cache": functools.lru_cache,
        "cache": functools.cache,
        "itertools": itertools,
        "math": math,
        "inf": math.inf,
    }


def _short(value, limit=300):
    text = repr(value)
    return text if len(text) <= limit else text[:limit] + " …"


def _error_text(exc):
    # Keep only frames from the user's code ("<solution>").
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == "<solution>"]
    text = "".join(traceback.format_list(frames)) + "".join(traceback.format_exception_only(type(exc), exc))
    return text.strip()[-1500:]


def _call_function(problem, ns, args):
    """Return (dumped result, elapsed ms). Only the method call is timed."""
    solution_cls = ns.get("Solution")
    if solution_cls is None:
        raise NameError("Не найден класс Solution")
    method = getattr(solution_cls(), problem["method"], None)
    if method is None:
        raise NameError(f"В классе Solution нет метода {problem['method']}")
    built = [build(t, a) for t, a in zip(problem["arg_types"], args)]
    start = time.perf_counter()
    result = method(*built)
    elapsed = (time.perf_counter() - start) * 1000
    if problem.get("inplace") is not None:
        idx = problem["inplace"]
        return dump(problem["arg_types"][idx], built[idx]), elapsed
    return dump(problem.get("ret_type"), result), elapsed


def _call_design(problem, ns, test):
    cls = ns.get(problem["method"])
    if cls is None:
        raise NameError(f"Не найден класс {problem['method']}")
    out = [None]
    start = time.perf_counter()
    obj = cls(*test["args"][0])
    for op, op_args in zip(test["ops"][1:], test["args"][1:]):
        out.append(dump(None, getattr(obj, op)(*op_args)))
    return out, (time.perf_counter() - start) * 1000


def _compile_user(user_code):
    # A real module in sys.modules: dataclasses, pickle and typing look the module up by name.
    module = types.ModuleType("solution")
    sys.modules["solution"] = module
    ns = module.__dict__
    ns.update(_namespace())
    # Lets tracebacks show the student's source lines.
    linecache.cache["<solution>"] = (len(user_code), None, user_code.splitlines(True), "<solution>")
    exec(compile(user_code, "<solution>", "exec"), ns)
    return ns


def _summary(results):
    passed = sum(r["status"] == "OK" for r in results)
    return {"compiled": True, "error": None, "results": results, "passed": passed, "total": len(results)}


def run(problem, user_code, include_hidden=True):
    """Return {"compiled": bool, "error": str|None, "results": [...], "passed": int, "total": int}."""
    try:
        ns = _compile_user(user_code)
    except Exception as exc:  # noqa: BLE001 — the student's code can raise anything
        return {"compiled": False, "error": _error_text(exc), "results": [], "passed": 0, "total": 0}

    check_fn = None
    if problem.get("compare") == "check":
        check_ns = {"math": math, "collections": collections}
        exec(problem["check"], check_ns)
        check_fn = check_ns["check"]

    cases = [dict(t, kind="test") for t in problem.get("tests", []) if include_hidden or not t.get("hidden")]
    if include_hidden:
        cases += [dict(p, kind="perf", hidden=True) for p in problem.get("perf", [])]

    results = []
    for i, case in enumerate(cases):
        res = {"n": i + 1, "kind": case["kind"], "hidden": bool(case.get("hidden")), "ms": 0.0}
        buf = io.StringIO()
        try:
            if case["kind"] == "perf":
                gen_ns = {"math": math}
                exec(case["gen"], gen_ns)
                args = gen_ns["gen"]()
            else:
                args = case.get("args")
        except Exception as exc:  # noqa: BLE001 — a broken test must not hide the others
            res.update(status="RE", error=f"Ошибка в самом тесте (не в вашем коде): {exc!r}", stdout="")
            results.append(res)
            continue
        try:
            with contextlib.redirect_stdout(buf):
                if problem.get("kind") == "design":
                    got, elapsed = _call_design(problem, ns, case)
                else:
                    got, elapsed = _call_function(problem, ns, args)
            if "expected_sha256" in case:
                ok = digest(normalize(problem.get("compare", "exact"), got)) == case["expected_sha256"]
            else:
                ok = compare(problem.get("compare", "exact"), got, case.get("expected"), args, check_fn)
            limit = case.get("time_limit_ms")
            if ok and limit and elapsed > limit:
                res["status"] = "TLE"
            else:
                res["status"] = "OK" if ok else "WA"
            res["got"] = _short(got)
            res["ms"] = round(elapsed, 1)
        except Exception as exc:  # noqa: BLE001
            res["status"] = "RE"
            res["error"] = _error_text(exc)
        res["stdout"] = buf.getvalue()[:STDOUT_LIMIT]
        if case["kind"] == "perf":
            res["limit_ms"] = case.get("time_limit_ms")
        if not res["hidden"]:
            res["args"] = _short(args if problem.get("kind") != "design" else {"ops": case["ops"], "args": case["args"]})
            res["expected"] = _short(case.get("expected"))
        results.append(res)
    return _summary(results)


def run_script(exercise, user_code):
    """Python exercises: `exercise["tests"]` is source with `def test_*():` functions.

    Test functions see every name the student defined. Each one is a separate result;
    the docstring of a test function is shown as its Russian title.
    """
    try:
        ns = _compile_user(user_code)
    except Exception as exc:  # noqa: BLE001
        return {"compiled": False, "error": _error_text(exc), "results": [], "passed": 0, "total": 0}
    test_ns = dict(ns)
    exec(exercise["tests"], test_ns)
    tests = [(name, fn) for name, fn in test_ns.items() if name.startswith("test_") and callable(fn)]
    results = []
    for i, (name, fn) in enumerate(tests):
        res = {"n": i + 1, "kind": "test", "hidden": False, "name": name, "title": (fn.__doc__ or name).strip()}
        buf = io.StringIO()
        start = time.perf_counter()
        try:
            with contextlib.redirect_stdout(buf):
                fn()
            res["status"] = "OK"
        except AssertionError as exc:
            res["status"] = "WA"
            res["error"] = str(exc) or "Условие теста не выполнено"
        except Exception as exc:  # noqa: BLE001
            res["status"] = "RE"
            res["error"] = _error_text(exc)
        res["ms"] = round((time.perf_counter() - start) * 1000, 1)
        res["stdout"] = buf.getvalue()[:STDOUT_LIMIT]
        results.append(res)
    return _summary(results)


def run_snippet(code):
    """Run a code snippet and return what it prints (for "predict the output" questions)."""
    buf = io.StringIO()
    try:
        module = types.ModuleType("snippet")
        sys.modules["snippet"] = module
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<snippet>", "exec"), module.__dict__)
        return {"ok": True, "stdout": buf.getvalue()[:STDOUT_LIMIT]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "stdout": buf.getvalue()[:STDOUT_LIMIT], "error": _error_text(exc)}


def check_expr(answer, reference, variables, points):
    """Compare two math expressions numerically at several points.

    Accepts student notation: ^ for power, implicit multiplication "2x", "3(x+1)", "x(x+1)".
    Returns {"ok": bool, "error": str|None}.
    """
    env = {name: getattr(math, name) for name in ("exp", "log", "sqrt", "sin", "cos", "tan", "pi", "e")}
    env["ln"] = math.log
    env["sigma"] = lambda x: 1 / (1 + math.exp(-x))
    text = answer.strip().replace("^", "**").replace("·", "*").replace("−", "-").replace(",", ".")
    text = re.sub(r"(\d)\s*([a-zA-Zσ(])", r"\1*\2", text)
    text = re.sub(r"\)\s*([\w(])", r")*\1", text)
    single = "|".join(v for v in variables if len(v) == 1)
    if single:
        text = re.sub(rf"(?<![A-Za-z])({single})\s*\(", r"\1*(", text)
    text = text.replace("σ", "sigma")
    try:
        code = compile(text, "<answer>", "eval")
    except SyntaxError:
        return {"ok": False, "error": "Не удалось разобрать выражение. Пишите умножение явно: 2*x, степень: x**2 или x^2."}
    ref_code = compile(reference, "<reference>", "eval")
    for point in points:
        scope = dict(env, **dict(zip(variables, point)))
        try:
            got = eval(code, {"__builtins__": {}}, scope)  # noqa: S307 — student's own math answer
        except NameError as exc:
            return {"ok": False, "error": f"Неизвестное имя: {exc.name}. Доступны: {', '.join(variables)}, exp, ln, sqrt, sin, cos."}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"Ошибка при вычислении: {exc}"}
        want = eval(ref_code, {"__builtins__": {}}, scope)  # noqa: S307
        if not isinstance(got, (int, float)):
            return {"ok": False, "error": "Ответ должен быть одним числом или выражением."}
        if not math.isclose(got, want, rel_tol=1e-6, abs_tol=1e-9):
            return {"ok": False, "error": None}
    return {"ok": True, "error": None}


# ---------------------------------------------------------------- step-by-step tracer (Python Tutor)

TRACE_FILE = "<tutor>"
TRACE_STEPS = 800
TRACE_ITEMS = 40  # items of one container shown before "…"


class _TraceLimit(BaseException):
    """Raised from the tracer to stop a long run; BaseException so `except Exception` in user code cannot catch it."""


class _Heap:
    """Encodes values the way Python Tutor shows them: primitives inline, everything else as a reference."""

    def __init__(self):
        self.ids = {}
        self.keep = []  # holds every seen object, so a freed id() is never reused for another one

    def ref(self, obj):
        key = id(obj)
        if key not in self.ids:
            self.ids[key] = len(self.ids) + 1
            self.keep.append(obj)
        return self.ids[key]

    def value(self, obj, heap):
        if obj is None or isinstance(obj, (bool, int, float, complex)):
            return ["P", repr(obj)]
        if isinstance(obj, str) and len(obj) <= 60 and "\n" not in obj:
            return ["P", repr(obj)]
        n = self.ref(obj)
        if n not in heap:
            heap[n] = None  # placeholder first: cycles stop here
            heap[n] = self.encode(obj, heap)
        return ["R", n]

    def items(self, seq, heap):
        out = [self.value(x, heap) for x in itertools.islice(seq, TRACE_ITEMS)]
        return out, len(seq) > TRACE_ITEMS if hasattr(seq, "__len__") else False

    def encode(self, obj, heap):
        if isinstance(obj, str):
            return {"t": "str", "v": _short(obj, 400)}
        if isinstance(obj, (list, tuple, collections.deque)):
            items, more = self.items(obj, heap)
            return {"t": type(obj).__name__, "items": items, "more": more}
        if isinstance(obj, (set, frozenset)):
            try:
                ordered = sorted(obj, key=_sorted_key)
            except TypeError:
                ordered = list(obj)
            items, more = self.items(ordered, heap)
            return {"t": type(obj).__name__, "items": items, "more": more}
        if isinstance(obj, dict):
            pairs = [[self.value(k, heap), self.value(v, heap)] for k, v in itertools.islice(obj.items(), TRACE_ITEMS)]
            name = "dict" if type(obj) is dict else type(obj).__name__
            return {"t": "dict", "name": name, "pairs": pairs, "more": len(obj) > TRACE_ITEMS}
        if isinstance(obj, (types.FunctionType, types.MethodType)):
            fn = getattr(obj, "__func__", obj)
            return {"t": "function", "v": f"{fn.__qualname__}({', '.join(fn.__code__.co_varnames[: fn.__code__.co_argcount])})"}
        if isinstance(obj, type):
            return {"t": "class", "v": obj.__name__}
        if isinstance(obj, types.ModuleType):
            return {"t": "other", "v": f"модуль {obj.__name__}"}
        attrs = getattr(obj, "__dict__", None)
        if isinstance(attrs, dict) and type(obj).__module__ in ("solution", "tutor", __name__):
            pairs = [[k, self.value(v, heap)] for k, v in itertools.islice(attrs.items(), TRACE_ITEMS)]
            return {"t": "instance", "v": type(obj).__name__, "attrs": pairs}
        return {"t": "other", "v": _short(obj, 200)}


def _frame_vars(frame, hidden):
    if frame.f_code.co_name == "<module>":
        names = [k for k in frame.f_globals if k not in hidden and not k.startswith("__")]
        return [(k, frame.f_globals[k]) for k in names]
    local = frame.f_locals
    order = list(frame.f_code.co_varnames) + [k for k in local if k not in frame.f_code.co_varnames]
    return [(k, local[k]) for k in order if k in local and not k.startswith((".", "__"))]


def trace(user_code, problem=None, max_steps=TRACE_STEPS):
    """Run the code line by line and return every step: line, call stack with variables, heap, output.

    With a problem the code is a LeetCode solution: after the module runs, the method is called on the
    first visible test (a design problem replays its operations). Only frames of the user's code are shown.
    Returns {"steps": [...], "error": str|None, "limited": bool, "call": str|None}.
    """
    module = types.ModuleType("tutor")
    sys.modules["tutor"] = module
    ns = module.__dict__
    ns.update(_namespace() if problem else {"__name__": "__main__"})
    hidden = set(ns)
    linecache.cache[TRACE_FILE] = (len(user_code), None, user_code.splitlines(True), TRACE_FILE)
    try:
        code = compile(user_code, TRACE_FILE, "exec")
    except SyntaxError as exc:
        return {"steps": [], "error": _error_text(exc).replace("<solution>", TRACE_FILE), "limited": False, "call": None}

    heap_enc = _Heap()
    out = io.StringIO()
    steps = []

    def snapshot(frame, event, arg):
        stack = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == TRACE_FILE:
                stack.append(f)
            f = f.f_back
        heap = {}
        frames = []
        for f in reversed(stack):
            name = "Глобальные" if f.f_code.co_name == "<module>" else f.f_code.co_qualname
            vars_ = [[k, heap_enc.value(v, heap)] for k, v in _frame_vars(f, hidden)]
            frames.append({"name": name, "vars": vars_})
        step = {"line": frame.f_lineno, "event": event, "frames": frames, "heap": heap, "out": out.getvalue()[-STDOUT_LIMIT:]}
        if event == "return":
            step["ret"] = heap_enc.value(arg, heap)
        if event == "exception":
            step["exc"] = "".join(traceback.format_exception_only(arg[0], arg[1])).strip()
        steps.append(step)
        if len(steps) >= max_steps:
            raise _TraceLimit

    def local_trace(frame, event, arg):
        if event in ("line", "return", "exception"):
            snapshot(frame, event, arg)
        return local_trace

    def global_trace(frame, event, arg):
        if frame.f_code.co_filename != TRACE_FILE:
            return None
        if frame.f_code.co_name not in ("<module>", "<listcomp>", "<genexpr>"):
            snapshot(frame, event, arg)  # the call itself: arguments are already bound
        return local_trace

    error = None
    limited = False
    call = None
    sys.settrace(global_trace)
    try:
        with contextlib.redirect_stdout(out):
            exec(code, ns)
            if problem:
                # A LeetCode solution: the module only defines the class, so start at the call.
                first = len(steps)
                call = _trace_call(problem, ns)
                del steps[:first]
    except _TraceLimit:
        limited = True
    except Exception as exc:  # noqa: BLE001 — the student's code can raise anything
        error = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    finally:
        sys.settrace(None)
    # Arrows point at ids that are stable across steps; JSON keys must be strings.
    for s in steps:
        s["heap"] = {str(k): v for k, v in s["heap"].items()}
    return {"steps": steps, "error": error, "limited": limited, "call": call}


def _trace_call(problem, ns):
    """Call the solution on the first visible test (traced by the caller). Returns the call as text."""
    test = next((t for t in problem.get("tests", []) if not t.get("hidden")), None)
    if test is None:
        return None
    if problem.get("kind") == "design":
        cls = ns.get(problem["method"])
        if cls is None:
            raise NameError(f"Не найден класс {problem['method']}")
        obj = cls(*test["args"][0])
        for op, op_args in zip(test["ops"][1:], test["args"][1:]):
            getattr(obj, op)(*op_args)
        return f"{problem['method']}: {', '.join(test['ops'][1:])}"
    solution_cls = ns.get("Solution")
    if solution_cls is None:
        raise NameError("Не найден класс Solution")
    built = [build(t, a) for t, a in zip(problem["arg_types"], test["args"])]
    getattr(solution_cls(), problem["method"])(*built)
    return f"Solution().{problem['method']}({', '.join(_short(a, 80) for a in test['args'])})"
