"""Build and validate app/data/quizzes.json and app/data/exercises.json.

- "output" questions: the answer is the real stdout of the code (CPython 3.14 = Pyodide 3.14);
- "expr" questions: the reference must evaluate at 6 random points of the domain;
- exercises: the reference passes every test, the starter code fails at least one.
Exit code 1 on any failure; files are written only when everything passes.
"""

import importlib
import json
import pkgutil
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "py"))
sys.path.insert(0, str(ROOT / "tools"))

import harness  # noqa: E402

TYPES = {"output", "choice", "multi", "expr", "number", "vector", "text"}


def check_question(qid, i, q, rng, errors):
    where = f"{qid}[{i}]"
    t = q.get("type")
    if t not in TYPES:
        errors.append(f"{where}: неизвестный тип {t}")
        return q
    q = dict(q)
    if t == "output":
        r = harness.run_snippet(q["code"])
        if not r["ok"]:
            errors.append(f"{where}: код упал: {r.get('error')}")
        q["answer"] = r["stdout"]
    elif t in ("choice", "multi"):
        n = len(q["options"])
        picks = [q["answer"]] if t == "choice" else q["answers"]
        if not picks or any(not 0 <= p < n for p in picks):
            errors.append(f"{where}: ответ вне вариантов")
    elif t == "expr":
        points = [[round(rng.uniform(lo, hi), 4) for lo, hi in q["domain"]] for _ in range(6)]
        res = harness.check_expr(q["ref"], q["ref"], q["vars"], points)
        if not res["ok"]:
            errors.append(f"{where}: эталон не вычисляется: {res['error']}")
        q["points"] = points
    elif t == "vector":
        if len(q["answer"]) != len(q.get("labels", q["answer"])):
            errors.append(f"{where}: labels и answer разной длины")
    elif t == "text":
        if not q.get("model"):
            errors.append(f"{where}: нет образца ответа")
    if not q.get("q") and t != "output":
        errors.append(f"{where}: нет текста вопроса")
    return q


def check_exercise(eid, ex, errors):
    spec = {"tests": ex["tests"]}
    r = harness.run_script(spec, ex["ref"])
    if not r["compiled"] or r["passed"] != r["total"] or r["total"] == 0:
        bad = [x for x in r["results"] if x["status"] != "OK"]
        errors.append(f"{eid}: эталон не проходит: {r.get('error') or bad[:1]}")
    s = harness.run_script(spec, ex["starter_code"])
    if s["compiled"] and s["passed"] == s["total"]:
        errors.append(f"{eid}: шаблон проходит все тесты")
    if len(ex.get("hints_ru", [])) != 3:
        errors.append(f"{eid}: нужно 3 подсказки")
    out = {k: v for k, v in ex.items() if k != "ref"}
    out["n_tests"] = r["total"]
    return out


def main():
    import content

    quizzes, exercises, errors = {}, {}, []
    for mod in sorted(m.name for m in pkgutil.iter_modules(content.__path__)):
        module = importlib.import_module(f"content.{mod}")
        for qid, quiz in getattr(module, "QUIZZES", {}).items():
            if qid in quizzes:
                errors.append(f"повтор id {qid}")
            rng = random.Random(qid)
            qs = [check_question(qid, i, q, rng, errors) for i, q in enumerate(quiz["questions"])]
            quizzes[qid] = dict(quiz, questions=qs)
        for eid, ex in getattr(module, "EXERCISES", {}).items():
            if eid in exercises:
                errors.append(f"повтор id {eid}")
            exercises[eid] = check_exercise(eid, ex, errors)
        print(f"{mod}: квизов {len(getattr(module, 'QUIZZES', {}))}, упражнений {len(getattr(module, 'EXERCISES', {}))}")

    n_q = sum(len(q["questions"]) for q in quizzes.values())
    print(f"Итого: квизов {len(quizzes)} ({n_q} вопросов), упражнений {len(exercises)}")
    if errors:
        print("Ошибки:")
        for e in errors:
            print("  -", e)
        return 1
    (ROOT / "data" / "quizzes.json").write_text(json.dumps(quizzes, ensure_ascii=False, indent=1))
    (ROOT / "data" / "exercises.json").write_text(json.dumps(exercises, ensure_ascii=False, indent=1))
    print("Записано: data/quizzes.json, data/exercises.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
