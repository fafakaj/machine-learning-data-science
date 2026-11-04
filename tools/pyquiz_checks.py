"""Checks of the Quiz ML question bank. Each check returns a list of error strings; empty means OK.

- coverage: every public method of list/dict/set/str has a description and at least one question;
- wiki: a complexity answer equals its cell in the TimeComplexity table (site translation);
- measure: timeit at 5 sizes, the best-fitting complexity class equals the answer;
- explanations: "why" and an explanation for every wrong option;
- schema and runnable "check" code (asserts).
"""

import math
import re
import sys
import timeit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "py"))

import harness  # noqa: E402

TYPES = {"list": list, "dict": dict, "set": set, "str": str}
TOPIC_TYPES = {"choice", "input"}
MIN_WHY = 80
MIN_WRONG = 40

# Complexity classes the measurement can tell apart. 2**n is infinite for large n: the model is skipped there.
CLASSES = {
    "1": lambda n: 1.0,
    "logn": lambda n: math.log2(n),
    "sqrtn": lambda n: math.sqrt(n),
    "n": lambda n: float(n),
    "nlogn": lambda n: n * math.log2(n),
    "n2": lambda n: float(n) ** 2,
    "n3": lambda n: float(n) ** 3,
    "2n": lambda n: 2.0**n if n < 1000 else math.inf,
}
# The timer cannot separate these pairs: a log factor over 16x of n is smaller than cache effects
# (a 300k-element list scan already looks like n log n). Line counting ("by": "ops") separates them exactly.
NEIGHBOURS = [{"1", "logn"}, {"n", "nlogn"}]


def public_methods(tp):
    return sorted(n for n in dir(tp) if not n.startswith("_"))


def check_coverage(methods, questions, types=tuple(TYPES)):
    covered = {c for q in questions for c in q.get("covers", [])}
    errors = []
    for name in types:
        real = public_methods(TYPES[name])
        own = methods.get(name, {})
        errors += [f"{name}.{m}: такого метода нет в dir({name})" for m in own if m not in real]
        for m in real:
            if not own.get(m, "").strip():
                errors.append(f"{name}.{m}: нет описания в справочнике методов")
            if f"{name}.{m}" not in covered:
                errors.append(f"{name}.{m}: нет ни одного вопроса (covers)")
    return errors


def _cells(line):
    parts = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    return [re.sub(r"\s*\[\d+\]$", "", p.strip().replace("\\|", "|")) for p in parts]


def wiki_tables(md_path):
    """{"list": {"Pop из середины": ("O(n)", "O(n)")}} from the tables under the "## <type>" headings."""
    tables, section = {}, None
    for line in Path(md_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if section and line.startswith("|") and not line.startswith("|---"):
            cells = _cells(line)
            if cells[0] == "Операция":
                continue
            tables.setdefault(section, {})[cells[0]] = (cells[1], cells[2] if len(cells) > 2 else "")
    return tables


def _squash(s):
    return re.sub(r"\s+", "", s)


def check_wiki(q, tables):
    if "wiki" not in q:
        return []
    section, op, case = q["wiki"]
    row = tables.get(section, {}).get(op)
    if row is None:
        return [f"{q['id']}: в таблице «{section}» нет строки «{op}»"]
    cell = row[0 if case == "avg" else 1]
    if not cell:
        return [f"{q['id']}: в таблице «{section}» у «{op}» пустая ячейка ({case})"]
    got = q["options"][q["answer"]]
    return [] if _squash(got) == _squash(cell) else [f"{q['id']}: ответ {got}, а в вики {cell} ({section}, {op}, {case})"]


def fit_class(ns, times):
    """Classes sorted by the relative least-squares error of t ≈ c·f(n)."""
    ranking = []
    for name, f in CLASSES.items():
        fs = [f(n) for n in ns]
        if any(math.isinf(x) for x in fs):
            continue
        ratios = [x / t for x, t in zip(fs, times)]
        c = sum(ratios) / sum(r * r for r in ratios)
        err = math.sqrt(sum((1 - c * r) ** 2 for r in ratios) / len(ratios))
        ranking.append((name, err))
    return sorted(ranking, key=lambda x: x[1])


def default_timer(setup, stmt, n):
    """Best of 5 runs, seconds per statement; the run count grows until one run takes at least 20 ms."""
    t = timeit.Timer(stmt, setup, globals={"n": n})
    number = 1
    while t.timeit(number) < 0.02:
        number *= 2
    return min(t.repeat(5, number)) / number


def count_lines(setup, stmt, n):
    """Python lines executed by stmt (and by functions defined in setup): an exact cost of Python-level loops."""
    g = {"n": n}
    exec(compile(setup, "<setup>", "exec"), g)
    code = compile(stmt, "<stmt>", "exec")
    count = 0

    def tracer(frame, event, arg):
        nonlocal count
        if frame.f_code.co_filename not in ("<setup>", "<stmt>"):
            return None
        if event == "line":
            count += 1
        return tracer

    sys.settrace(tracer)
    try:
        exec(code, g)
    finally:
        sys.settrace(None)
    return max(count, 1)


def check_measure(q, timer=default_timer):
    if "measure" not in q:
        return []
    m = q["measure"]
    by_ops = m.get("by") == "ops"
    cost = count_lines if by_ops else timer
    ranking = fit_class(m["ns"], [cost(m.get("setup", ""), m["stmt"], n) for n in m["ns"]])
    best = ranking[0][0]
    if best == m["cls"] or (not by_ops and {best, m["cls"]} in NEIGHBOURS):
        return []
    top = ", ".join(f"{k} {e:.3f}" for k, e in ranking[:3])
    return [f"{q['id']}: замер даёт {best}, а ответ {m['cls']} (ошибки подгонки: {top})"]


def check_explanations(q):
    errors = []
    if len(q.get("why", "").strip()) < MIN_WHY:
        errors.append(f"{q['id']}: «почему верно» короче {MIN_WHY} символов")
    if q.get("type") == "choice":
        wrong = q.get("wrong", {})
        for i in range(len(q.get("options", []))):
            if i == q.get("answer"):
                continue
            if len(wrong.get(str(i), "").strip()) < MIN_WRONG:
                errors.append(f"{q['id']}: нет разбора неверного варианта {i} (или он короче {MIN_WRONG} символов)")
    return errors


def check_schema(q, topics):
    qid = q.get("id", "?")
    errors = [f"{qid}: нет поля {k}" for k in ("id", "topic", "type", "q", "why", "src") if not q.get(k)]
    if q.get("topic") not in topics:
        errors.append(f"{qid}: неизвестная тема {q.get('topic')}")
    if q.get("type") not in TOPIC_TYPES:
        errors.append(f"{qid}: неизвестный тип {q.get('type')}")
    if any(not s.startswith("https://") for s in q.get("src", [])):
        errors.append(f"{qid}: источник не https-ссылка")
    if q.get("type") == "choice":
        opts = q.get("options", [])
        if len(opts) < 2 or len(set(opts)) != len(opts):
            errors.append(f"{qid}: меньше двух вариантов или есть повторы")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(opts):
            errors.append(f"{qid}: ответ вне списка вариантов")
    if q.get("type") == "input":
        if q.get("of") not in TYPES:
            errors.append(f"{qid}: поле of должно быть list/dict/set/str")
        if not q.get("answer") or not all(isinstance(a, str) and a for a in q["answer"]):
            errors.append(f"{qid}: ответ — непустой список строк")
    return errors


def run_check(q):
    if "check" not in q:
        return []
    r = harness.run_snippet(q["check"])
    return [] if r["ok"] else [f"{q['id']}: код-проверка упала: {r.get('error', '').strip().splitlines()[-1:]}"]
