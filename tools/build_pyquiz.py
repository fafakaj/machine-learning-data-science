"""Build and validate app/data/pyquiz.json (Quiz ML) from tools/pyquiz/*.py.

Every question passes: schema, explanations of every wrong option, its check code (asserts),
its TimeComplexity cell (wiki), its measured complexity class; and every public method of
list/dict/set/str has a description and a question. Exit code 1 on any failure; the file is
written only when everything passes.

    python3 tools/build_pyquiz.py              # all topics
    python3 tools/build_pyquiz.py --only list  # one module, for a quick loop (no file written)
"""

import argparse
import importlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pyquiz_checks as pc  # noqa: E402
from pyquiz.methods import METHODS  # noqa: E402

MODULES = ["list_", "dict_", "set_", "str_", "code", "conc"]
BUILD_ONLY = {"check", "wiki", "measure", "covers"}
OUT = ROOT / "data" / "pyquiz.json"
WIKI = ROOT / "data" / "articles" / "python-time-complexity.md"


def load(names):
    topics, questions = [], []
    for name in names:
        mod = importlib.import_module(f"pyquiz.{name}")
        topics += mod.TOPICS
        questions += mod.QUESTIONS
    return topics, questions


def validate(topics, questions, types):
    errors = []
    topic_ids = {t["id"] for t in topics}
    seen = set()
    for q in questions:
        if q.get("id") in seen:
            errors.append(f"{q['id']}: id повторяется")
        seen.add(q.get("id"))
    tables = pc.wiki_tables(WIKI)
    for q in questions:
        errors += pc.check_schema(q, topic_ids)
        errors += pc.check_explanations(q)
        errors += pc.check_wiki(q, tables)
        errors += pc.run_check(q)
        errors += pc.check_measure(q)
    errors += pc.check_coverage(METHODS, questions, types=types)
    empty = topic_ids - {q["topic"] for q in questions}
    errors += [f"тема {t}: нет вопросов" for t in sorted(empty)]
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=[m.rstrip("_") for m in MODULES], help="собрать одну тему и не писать файл")
    args = ap.parse_args()
    names = [m for m in MODULES if m.rstrip("_") == args.only] if args.only else MODULES
    types = tuple(n.rstrip("_") for n in names if n.rstrip("_") in pc.TYPES)

    t0 = time.time()
    topics, questions = load(names)
    errors = validate(topics, questions, types)
    if errors:
        print(f"Ошибок: {len(errors)}")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)

    per_topic = {t["id"]: sum(q["topic"] == t["id"] for q in questions) for t in topics}
    print(f"OK: {len(questions)} вопросов за {time.time() - t0:.0f} с —", ", ".join(f"{k} {v}" for k, v in per_topic.items()))
    if args.only:
        return
    out = {
        "topics": [{**t, "count": per_topic[t["id"]]} for t in topics],
        "methods": {t: METHODS[t] for t in types},
        "questions": [{k: v for k, v in q.items() if k not in BUILD_ONLY} for q in questions],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Записан {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
