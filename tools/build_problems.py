"""Build and validate app/data/problems.json.

Usage: python3 app/tools/build_problems.py [--only 217,242]

For every problem:
  1. expected answers come from `brute` (independent of the reference solution);
  2. `ref` must pass every hand-picked, random and perf test;
  3. `ref` and `brute` must agree on 200 random small inputs;
  4. `naive` (if given) must pass the small tests and exceed the perf time limit;
  5. the starter code must fail at least one test.
Exit code 1 on any failure. problems.json is written only when everything passes.
"""

import argparse
import copy
import importlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "py"))
sys.path.insert(0, str(ROOT / "tools"))

import harness  # noqa: E402

MODULES = ["problems.p_w01_w04", "problems.p_w05_w08", "problems.p_w09_w13"]
PUBLIC = [
    "id", "slug", "title_en", "title_ru", "difficulty", "week", "optional", "pattern", "pattern_ru",
    "leetcode_url", "statement_ru", "examples", "constraints_ru", "complexity_target", "starter_code",
    "method", "kind", "arg_types", "ret_type", "compare", "inplace", "check", "hints_ru",
]
RANDOM_CHECKS = 200
RANDOM_HIDDEN = 8
PYODIDE_FACTOR = 10  # limit = 10x the reference time in CPython (Pyodide is ~2–4x slower)
MIN_LIMIT_MS = 800


def load_problems():
    problems = []
    for name in MODULES:
        problems += importlib.import_module(name).PROBLEMS
    return problems


def expected_of(p, args):
    return p["brute"](*copy.deepcopy(args))


def run_ref(p, spec):
    return harness.run(spec, p["ref"])


def naive_time(p, spec, perf_case, timeout_s):
    """Run naive on one perf case in a subprocess; return elapsed ms or None on timeout."""
    one = dict(spec, tests=[], perf=[dict(perf_case, time_limit_ms=None)])
    code = (
        "import json,sys;sys.path.insert(0,%r);import harness;"
        "spec=json.loads(sys.stdin.read());r=harness.run(spec['p'],spec['c']);"
        "print(json.dumps(r['results'][0]))" % str(ROOT / "py")
    )
    try:
        out = subprocess.run(
            [sys.executable, "-c", code], input=json.dumps({"p": one, "c": p["naive"]}),
            capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return None
    res = json.loads(out.stdout)
    return res["ms"] if res["status"] == "OK" else f"{res['status']}: {res.get('error', '')}"


def run_isolated(spec, code, timeout_s):
    """harness.run in a subprocess; None on timeout."""
    script = (
        "import json,sys;sys.path.insert(0,%r);import harness;"
        "a=json.loads(sys.stdin.read());print(json.dumps(harness.run(a['p'],a['c'])))" % str(ROOT / "py")
    )
    try:
        out = subprocess.run(
            [sys.executable, "-c", script], input=json.dumps({"p": spec, "c": code}),
            capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return None
    return json.loads(out.stdout)


def build_one(p, rng):
    errors = []
    spec = {k: p.get(k) for k in PUBLIC}
    spec.setdefault("kind", "function")
    spec["kind"] = spec["kind"] or "function"
    spec["compare"] = spec["compare"] or "exact"
    spec["optional"] = bool(spec["optional"])

    # Schema.
    for key in ("id", "slug", "title_ru", "statement_ru", "starter_code", "method", "hints_ru", "examples"):
        if not p.get(key):
            errors.append(f"нет поля {key}")
    if len(p.get("hints_ru", [])) != 3:
        errors.append("нужно ровно 3 подсказки")
    if spec["kind"] == "function" and len(p["arg_types"]) != len(p["cases"][0]):
        errors.append("arg_types и аргументы теста разной длины")
    try:
        compile(p["starter_code"], "<starter>", "exec")
    except SyntaxError as exc:
        errors.append(f"starter_code не компилируется: {exc}")
    if p["method"] not in p["starter_code"]:
        errors.append("в starter_code нет метода")

    # Tests: hand-picked, then random hidden.
    visible = p.get("visible", len(p["examples"]))
    tests = []
    seen = set()
    for i, args in enumerate(p["cases"]):
        key = json.dumps(args, sort_keys=True)
        if key in seen:
            errors.append(f"повтор теста {key[:60]}")
        seen.add(key)
        tests.append({"args": args, "expected": expected_of(p, args), "hidden": i >= visible})
    randoms = []
    for _ in range(RANDOM_CHECKS):
        args = p["rand"](rng)
        randoms.append({"args": args, "expected": expected_of(p, args), "hidden": True})
    added = 0
    for t in randoms:
        key = json.dumps(t["args"], sort_keys=True)
        if added < RANDOM_HIDDEN and key not in seen:
            seen.add(key)
            tests.append(t)
            added += 1
    if spec["kind"] == "design":
        unique = {id(t): t for t in tests + randoms}
        for t in unique.values():
            t["ops"], t["args"] = t["args"]
    spec["tests"] = tests

    # Reference passes hand-picked + random checks.
    result = run_ref(p, dict(spec, tests=tests + randoms, perf=[]))
    if not result["compiled"]:
        errors.append(f"ref не компилируется: {result['error']}")
    else:
        bad = [r for r in result["results"] if r["status"] != "OK"]
        if bad:
            first = (tests + randoms)[bad[0]["n"] - 1]
            errors.append(
                f"ref ≠ brute на {len(bad)} тестах; пример: args={str(first.get('args'))[:120]} "
                f"expected={str(first['expected'])[:80]} got={bad[0].get('got', bad[0].get('error'))}"
            )

    # Perf: expected from ref, limit from the measured ref time.
    perf = []
    ref_ms = []
    for gen in p.get("perf", []):
        gen_ns = {"math": harness.math}
        exec(gen, gen_ns)
        args = gen_ns["gen"]()
        ns = harness._compile_user(p["ref"])
        best = None
        for _ in range(3):
            got, ms = harness._call_function(spec, ns, args)
            best = ms if best is None else min(best, ms)
        case = {"gen": gen, "time_limit_ms": max(MIN_LIMIT_MS, int(round(best * PYODIDE_FACTOR, -1)))}
        if spec["compare"] == "check":
            errors.append("perf и compare=check несовместимы")
        elif len(json.dumps(got)) > 2000:
            case["expected_sha256"] = harness.digest(harness.normalize(spec["compare"], got))
        else:
            case["expected"] = got
        perf.append(case)
        ref_ms.append(round(best, 1))
    spec["perf"] = perf
    if perf:
        r = run_ref(p, dict(spec, tests=[]))
        if r["passed"] != r["total"]:
            errors.append(f"ref не проходит perf: {[x['status'] for x in r['results']]}")

    # Naive: correct on small tests, too slow on perf.
    naive_ms = []
    if p.get("naive"):
        r = run_isolated(dict(spec, perf=[]), p["naive"], timeout_s=10)
        if r is None:
            # Exponential naive solutions may already time out on the largest normal test; that is fine.
            naive_ms.append("timeout на обычных тестах")
        elif r["passed"] != r["total"]:
            errors.append(f"naive не проходит обычные тесты: {r['passed']}/{r['total']}")
        for case in perf:
            t = naive_time(p, spec, case, timeout_s=3 * case["time_limit_ms"] / 1000)
            naive_ms.append(t)
            if isinstance(t, (int, float)) and t <= case["time_limit_ms"]:
                errors.append(f"naive укладывается в лимит: {t} ms ≤ {case['time_limit_ms']} ms")
            if isinstance(t, str):
                errors.append(f"naive упал на perf: {t}")
    elif perf:
        errors.append("есть perf, но нет naive для калибровки")

    # Starter must fail.
    r = harness.run(spec, p["starter_code"])
    if r["compiled"] and r["passed"] == r["total"]:
        errors.append("пустой шаблон проходит все тесты")

    stats = {
        "tests": len(tests), "visible": sum(not t["hidden"] for t in tests), "perf": len(perf),
        "ref_ms": ref_ms, "limit_ms": [c["time_limit_ms"] for c in perf],
        "naive_ms": ["timeout" if t is None else t for t in naive_ms],
    }
    return spec, errors, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    opts = ap.parse_args()
    only = {int(x) for x in opts.only.split(",") if x}

    problems = load_problems()
    ids = [p["id"] for p in problems]
    if len(ids) != len(set(ids)):
        print("Повтор id задач:", sorted({i for i in ids if ids.count(i) > 1}))
        return 1

    refs = ROOT / "data" / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    specs, failed = [], 0
    start = time.perf_counter()
    for p in problems:
        if only and p["id"] not in only:
            continue
        rng = random.Random(p["id"])
        spec, errors, st = build_one(p, rng)
        specs.append(spec)
        (refs / f"{p['id']}.py").write_text(p["ref"])
        if p.get("naive"):
            (refs / f"{p['id']}_naive.py").write_text(p["naive"])
        mark = "OK " if not errors else "ERR"
        print(
            f"{mark} W{p['week']:02d} #{p['id']:<5} {p['title_en'][:38]:<38} tests={st['tests']:>2} "
            f"vis={st['visible']} perf={st['perf']} ref={st['ref_ms']} limit={st['limit_ms']} naive={st['naive_ms']}"
        )
        for e in errors:
            print("      -", e)
        failed += bool(errors)

    print(f"\nЗадач: {len(specs)}, с ошибками: {failed}, время {time.perf_counter() - start:.1f} с")
    if failed:
        return 1
    if not only:
        out = ROOT / "data" / "problems.json"
        out.write_text(json.dumps({"problems": specs}, ensure_ascii=False, indent=1))
        print("Записано:", out, f"{out.stat().st_size // 1024} КБ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
