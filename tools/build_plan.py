"""Build and validate app/data/plan.json from the week definitions in tools/plan_weeks.py.

Checks: 91 consecutive days from the start date; unique step ids; every theory topic exists in
data/sources.json; every problem, quiz and exercise exists; every review comes after the problem.
A source with url "#/read/<slug>" is a translation: data/articles/<slug>.md must exist with front matter
(title, original, kind) and the source must name its "original".
--check-links additionally requests every source URL (HTTP status must be < 400); for a translation, its original.
"""

import argparse
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from plan_weeks import BLOCK_DAYS, BLOCK_TITLES, GITHUB_USER, START, WEEKS  # noqa: E402

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
HOURS = {"mon": 2.5, "tue": 2.5, "wed": 0, "thu": 2.5, "fri": 2.5, "sat": 5, "sun": 5}
PATTERN_TOPIC = {
    "hash-set": "lc-hash-set", "hash-map": "lc-hash-map", "hash-map-count": "lc-hash-map", "hash-map-bijection": "lc-hash-map",
    "running-min": "lc-bigo", "two-pointers": "lc-two-pointers", "two-pointers-from-end": "lc-two-pointers",
    "two-pointers-gap": "lc-two-pointers", "expand-around-center": "lc-two-pointers", "boyer-moore": "lc-majority",
    "stack": "lc-stack", "stack-design": "lc-stack", "monotonic-stack": "lc-stack", "binary-search": "lc-binary-search",
    "binary-search-answer": "lc-binary-search", "dp-1d": "lc-dp-1d", "dp-2d": "lc-dp-1d", "kadane": "lc-dp-1d",
    "linked-list": "lc-linked-list", "hash-map-linked-list": "lc-linked-list", "sliding-window": "lc-sliding-window",
    "sliding-window-set": "lc-sliding-window", "sliding-window-count": "lc-sliding-window", "intervals": "lc-intervals",
    "intervals-greedy": "lc-intervals", "bucket-sort": "lc-heap-top-k", "heap": "lc-heap-top-k", "hash-map-key": "lc-group-anagrams",
    "prefix-suffix": "lc-prefix-suffix", "sort-two-pointers": "lc-3sum", "fast-slow-pointers": "lc-fast-slow-pointers",
    "tree-dfs": "lc-tree-dfs", "tree-dfs-postorder": "lc-tree-dfs", "tree-bfs": "lc-tree-bfs", "bst-bounds": "lc-bst",
    "bst-inorder": "lc-bst", "grid-dfs": "lc-graph-bfs-dfs", "grid-bfs-multi": "lc-graph-bfs-dfs", "dp-unbounded": "lc-dp-coin-change",
    "topological-sort": "lc-topological-sort",
}


def load(name):
    return json.loads((ROOT / "data" / name).read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-links", action="store_true")
    ap.add_argument("--problems", action="store_true", help="ignored (used by build_all.sh)")
    opts = ap.parse_args()

    topics = {t["id"]: t for t in load("sources.json")["topics"]}
    problems = {p["id"]: p for p in load("problems.json")["problems"]}
    quizzes = load("quizzes.json")
    exercises = load("exercises.json")
    errors = []
    used_topics = set()

    def check_article(src, topic_id):
        if not src["url"].startswith("#/read/"):
            return
        path = ROOT / "data" / "articles" / f"{src['url'][len('#/read/'):]}.md"
        head = path.read_text().split("---\n")[1] if path.exists() else ""
        missing = [k for k in ("title", "original", "kind") if f"\n{k}: " not in f"\n{head}"]
        if not path.exists() or missing or not src.get("original"):
            errors.append(f"{topic_id}: перевод {src['url']} — нет файла, полей {missing} или original в sources.json")

    def source_of(topic_id, where):
        t = topics.get(topic_id)
        if not t:
            errors.append(f"{where}: нет темы {topic_id} в sources.json")
            return None, []
        if topic_id not in used_topics:
            for src in t["sources"]:
                check_article(src, topic_id)
        used_topics.add(topic_id)
        # The main source is in Russian whenever the topic has one; the rest go to "alt".
        srcs = sorted(t["sources"], key=lambda x: x["lang"] != "ru")
        return srcs[0], srcs[1:]

    start = date.fromisoformat(START)
    weeks_out = []
    seen_ids = set()
    solved_at = {}
    for wi, week in enumerate(WEEKS):
        n = wi + 1
        days_out = []
        for di, wd in enumerate(WEEKDAYS):
            day_def = week["days"].get(wd, {})
            day_date = (start + timedelta(days=7 * wi + di)).isoformat()
            steps_out = []
            for si, raw in enumerate(day_def.get("steps", [])):
                step = dict(raw)
                step["id"] = f"w{n:02d}-{wd}-{si + 1:02d}"
                where = f"неделя {n}, {wd}, шаг {si + 1}"
                if step["id"] in seen_ids:
                    errors.append(f"{where}: повтор id")
                seen_ids.add(step["id"])
                t = step["type"]
                if t == "theory":
                    src, alt = source_of(step["topic"], where)
                    if src:
                        step["source"] = src
                        step["alt"] = alt
                        step.setdefault("minutes", src.get("minutes"))
                        step.setdefault("title", topics[raw["topic"]]["topic_ru"])
                elif t in ("leetcode", "review"):
                    p = problems.get(step["problem"])
                    if not p:
                        errors.append(f"{where}: нет задачи #{step['problem']}")
                        continue
                    step.setdefault("title", f"{'Повтор: ' if t == 'review' else ''}#{p['id']} {p['title_ru']}")
                    step.setdefault("minutes", 30 if t == "leetcode" else 15)
                    topic = PATTERN_TOPIC.get(p["pattern"])
                    if topic:
                        step["topic"] = topic
                        step["source"], _ = source_of(topic, where)
                    if t == "leetcode":
                        if step["problem"] in solved_at:
                            errors.append(f"{where}: задача #{p['id']} уже была {solved_at[step['problem']]}")
                        solved_at[step["problem"]] = day_date
                    elif step["problem"] not in solved_at or solved_at[step["problem"]] >= day_date:
                        errors.append(f"{where}: повтор #{p['id']} раньше самой задачи")
                elif t in ("quiz", "oral"):
                    q = quizzes.get(step["quiz"])
                    if not q:
                        errors.append(f"{where}: нет квиза {step['quiz']}")
                        continue
                    step.setdefault("title", q["title"])
                    step.setdefault("minutes", max(10, 2 * len(q["questions"])))
                elif t == "exercise":
                    e = exercises.get(step["exercise"])
                    if not e:
                        errors.append(f"{where}: нет упражнения {step['exercise']}")
                        continue
                    step.setdefault("title", e["title"])
                    step.setdefault("minutes", 20)
                elif t == "practice":
                    for it in step.get("items", []):
                        if "topic" in it:
                            it["source"], _ = source_of(it["topic"], where)
                elif t == "anki":
                    step.setdefault("title", "Anki: повторение")
                    step.setdefault("minutes", 15)
                else:
                    errors.append(f"{where}: неизвестный тип {t}")
                if not step.get("title"):
                    errors.append(f"{where}: нет заголовка")
                steps_out.append(step)
            optional = []
            for o in day_def.get("optional", []):
                o = dict(o)
                if "topic" in o:
                    o["source"], _ = source_of(o.pop("topic"), f"неделя {n}, {wd}, опционально")
                optional.append(o)
            days_out.append({
                "date": day_date, "weekday": wd, "title": day_def.get("title", "Буфер" if wd == "wed" else ""),
                "hours": HOURS[wd], "kind": "buffer" if wd == "wed" else "study", "intro": day_def.get("intro"),
                "optional": optional, "steps": steps_out,
            })
            if wd != "wed" and not steps_out:
                errors.append(f"неделя {n}, {wd}: нет шагов")
        by_day = {d["weekday"]: d for d in days_out}
        blocks = []
        for k, wds in enumerate(BLOCK_DAYS):
            blocks.append({
                "id": f"w{n:02d}-b{k + 1}", "n": k + 1, "title": BLOCK_TITLES[wi][k],
                # Soft deadline: the last day of the block.
                "due": by_day[wds[-1]]["date"],
                "steps": [s["id"] for wd in wds for s in by_day[wd]["steps"]],
            })
        weeks_out.append({"n": n, "title": week["title"], "short": week.get("short"), "goal": week.get("goal"),
                          "blocks": blocks, "days": days_out})

    if len(weeks_out) != 13:
        errors.append(f"недель {len(weeks_out)}, ожидалось 13")
    unused = sorted(set(topics) - used_topics)
    n_steps = sum(len(d["steps"]) for w in weeks_out for d in w["days"])
    print(f"Недель {len(weeks_out)}, шагов {n_steps}, задач {len(solved_at)}, тем использовано {len(used_topics)} из {len(topics)}")
    if unused:
        print("Темы без шага:", ", ".join(unused))
    unsolved = sorted(set(problems) - set(solved_at))
    if unsolved:
        errors.append(f"задачи без шага: {unsolved}")
    used_quizzes = {s.get("quiz") for w in weeks_out for d in w["days"] for s in d["steps"]}
    used_ex = {s.get("exercise") for w in weeks_out for d in w["days"] for s in d["steps"]}
    # Content written ahead of the plan (weeks 5+) waits until the user approves month 1.
    spare = sorted(set(quizzes) - used_quizzes) + sorted(set(exercises) - used_ex)
    if spare:
        print(f"Готово, но пока не в плане: {len(spare)} квизов и упражнений ({spare[0]} … {spare[-1]})")

    if opts.check_links:
        urls = sorted({s["source"].get("original", s["source"]["url"]) for w in weeks_out for d in w["days"] for s in d["steps"] if s.get("source")}
                      | {a.get("original", a["url"]) for w in weeks_out for d in w["days"] for s in d["steps"] for a in s.get("alt", [])})

        def status(url):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) study-app link check"})
            try:
                with urllib.request.urlopen(req, timeout=25) as r:
                    return url, r.status
            except urllib.error.HTTPError as e:
                return url, e.code
            except Exception as e:  # noqa: BLE001
                return url, repr(e)[:60]

        with ThreadPoolExecutor(12) as pool:
            results = list(pool.map(status, urls))
        bad = [(u, s) for u, s in results if not (isinstance(s, int) and s < 400)]
        print(f"Ссылок проверено: {len(results)}, с ошибкой: {len(bad)}")
        for u, s in bad:
            print(f"  {s}  {u}")

    if errors:
        print("Ошибки:")
        for e in errors:
            print("  -", e)
        return 1
    plan = {"start": START, "github_user": GITHUB_USER, "weeks": weeks_out}
    (ROOT / "data" / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print("Записано: data/plan.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
