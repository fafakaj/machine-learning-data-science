"""Progress report: what to shorten and what to strengthen in the plan.

Usage: python3 app/tools/analyze_progress.py [PROGRESS_JSON] [--plan app/data/plan.json]

Reads the progress file saved by the site (default ~/ai_career/logs/progress.json) and the plan.
Prints a Markdown report in Russian to stdout: per week and per topic — time, attempts, hints,
quiz mistakes, review mistakes, easy/hard ratings, "already know" skips. The last section lists
topics to shorten or to strengthen, by simple rules (see `verdict`). Standard library only.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROGRESS = Path.home() / "ai_career" / "logs" / "progress.json"
DEFAULT_PLAN = ROOT / "data" / "plan.json"

TYPE_RU = {
    "theory": "теория", "leetcode": "LeetCode", "review": "повторение", "anki": "Anki",
    "exercise": "упражнение", "practice": "практика", "quiz": "квиз", "hours": "учёт часов", "oral": "устный ответ",
}
FAST = 0.6       # faster than 60 % of the planned time — candidate to shorten
SLOW = 1.5       # slower than 150 % of the planned time — candidate to strengthen
MAX_GAP = 3      # an open→done gap longer than 3x the plan is a break, not work time
MANY_HINTS = 2   # average hints per problem/exercise step
MANY_TRIES = 3   # average attempts per problem/exercise step
QUIZ_BAD = 0.3   # share of quiz questions answered wrong at least once


def parse_time(s):
    try:
        return datetime.fromisoformat(s)
    except (AttributeError, ValueError):
        return None


def fmt_min(seconds):
    if seconds is None:
        return "—"
    m = seconds / 60
    return f"{m:.0f} мин" if m < 90 else f"{m / 60:.1f} ч"


class Stats:
    def __init__(self):
        self.steps = 0
        self.done = 0
        self.plan_s = 0        # planned time of the steps with a measured time
        self.plan_all_s = 0    # planned time of all steps
        self.time_s = 0
        self.measured = 0      # steps with a measured or estimated time
        self.coded = 0         # done leetcode/exercise steps (attempts and hints are counted for them)
        self.attempts = 0
        self.hints = 0
        self.q_total = 0       # quiz questions answered
        self.q_wrong = 0       # quiz questions answered wrong at least once
        self.q_errors = 0      # wrong attempts in total
        self.r_seen = 0        # review cards shown
        self.r_wrong = 0
        self.ratings = defaultdict(int)
        self.skipped = 0
        self.titles = []

    def add(self, other):
        for k, v in vars(other).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                setattr(self, k, getattr(self, k) + v)
        for k, v in other.ratings.items():
            self.ratings[k] += v
        self.titles += other.titles


def estimated_times(events, plan_minutes):
    """step id → seconds between the first "open" and the "done" event, if it looks like work time."""
    opened, out = {}, {}
    for e in events:
        t, step = parse_time(e.get("t")), e.get("step")
        if not t or not step:
            continue
        if e.get("type") == "open":
            opened.setdefault(step, t)
        elif e.get("type") in ("done", "skip") and step in opened:
            gap = (t - opened[step]).total_seconds()
            limit = MAX_GAP * plan_minutes.get(step, 30) * 60
            if 0 < gap <= limit:
                out[step] = gap
    return out


def collect(progress, plan):
    steps_state = progress.get("steps", {})
    quiz_state = progress.get("quiz", {})
    review_state = progress.get("review", {})
    plan_minutes = {}
    for w in plan["weeks"]:
        for d in w["days"]:
            for s in d["steps"]:
                plan_minutes[s["id"]] = s.get("minutes") or 0
    est = estimated_times(progress.get("events", []), plan_minutes)

    # review cards → steps: "q:<quiz id>:<i>" and "p:<problem id>"
    review_by_quiz, review_by_problem = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for key, card in review_state.items():
        parts = key.split(":")
        target = review_by_quiz[parts[1]] if parts[0] == "q" and len(parts) > 2 else (
            review_by_problem[parts[1]] if parts[0] == "p" and len(parts) > 1 else None)
        if target is not None:
            target[0] += card.get("seen", 0)
            target[1] += card.get("wrong", 0)
    review_used = set()

    weeks = []
    for w in plan["weeks"]:
        topics = {}
        for d in w["days"]:
            for s in d["steps"]:
                if s.get("optional"):
                    continue
                key = s.get("topic") or TYPE_RU.get(s["type"], s["type"])
                st = topics.setdefault(key, Stats())
                st.steps += 1
                st.plan_all_s += plan_minutes[s["id"]] * 60
                state = steps_state.get(s["id"], {})
                if state.get("status") != "done":
                    continue
                st.done += 1
                st.titles.append(s.get("title", s["id"]))
                t = state.get("time_s") or est.get(s["id"])
                if t:
                    st.time_s += t
                    st.plan_s += plan_minutes[s["id"]] * 60
                    st.measured += 1
                if s["type"] in ("leetcode", "exercise", "practice") and not state.get("skipped"):
                    st.coded += 1
                    st.attempts += state.get("attempts", 0)
                    st.hints += state.get("hints_used", 0) or state.get("hints", 0)
                for q in quiz_state.get(s["id"], {}).values():
                    if not isinstance(q, dict) or not ("ok" in q or "tried" in q):
                        continue
                    st.q_total += 1
                    st.q_errors += q.get("tried", 0) or 0
                    st.q_wrong += 1 if q.get("tried") else 0
                for rkey, table in ((s.get("quiz"), review_by_quiz), (s.get("problem"), review_by_problem)):
                    rkey = None if rkey is None else str(rkey)
                    if rkey in table and rkey not in review_used:
                        review_used.add(rkey)
                        st.r_seen += table[rkey][0]
                        st.r_wrong += table[rkey][1]
                if state.get("rating"):
                    st.ratings[state["rating"]] += 1
                if state.get("skipped"):
                    st.skipped += 1
        weeks.append((w, topics))
    return weeks


def verdict(st):
    """("cut" | "boost" | None, reasons)."""
    boost, cut = [], []
    if st.ratings.get("hard"):
        boost.append(f"«сложно» × {st.ratings['hard']}")
    if st.coded and st.hints / st.coded >= MANY_HINTS:
        boost.append(f"подсказок в среднем {st.hints / st.coded:.1f}")
    if st.coded and st.attempts / st.coded >= MANY_TRIES:
        boost.append(f"попыток в среднем {st.attempts / st.coded:.1f}")
    if st.q_total and st.q_wrong / st.q_total >= QUIZ_BAD:
        boost.append(f"ошибки в квизе: {st.q_wrong} из {st.q_total} вопросов")
    if st.r_seen and st.r_wrong / st.r_seen >= QUIZ_BAD:
        boost.append(f"ошибки в карточках: {st.r_wrong} из {st.r_seen}")
    if st.plan_s and st.time_s > SLOW * st.plan_s:
        boost.append(f"время {fmt_min(st.time_s)} при плане {fmt_min(st.plan_s)}")
    if boost:
        return "boost", boost

    clean = not st.hints and not st.q_wrong and not st.r_wrong and not st.ratings.get("hard")
    if st.skipped and clean:
        cut.append(f"«уже знаю» × {st.skipped}")
    if st.plan_s and st.time_s < FAST * st.plan_s and clean:
        cut.append(f"время {fmt_min(st.time_s)} при плане {fmt_min(st.plan_s)}, без подсказок и ошибок")
    if st.ratings.get("easy") and clean and st.ratings["easy"] >= st.done / 2:
        cut.append(f"«легко» × {st.ratings['easy']}")
    return ("cut", cut) if cut else (None, [])


def ratings_cell(st):
    r = st.ratings
    return f"{r.get('easy', 0)}/{r.get('ok', 0)}/{r.get('hard', 0)}" if r else "—"


def quiz_cell(st):
    return f"{st.q_wrong}/{st.q_total}" if st.q_total else "—"


def time_cell(st):
    if not st.measured:
        return f"— / {fmt_min(st.plan_all_s)}"
    return f"{fmt_min(st.time_s)} / {fmt_min(st.plan_s)}"


def row(name, st):
    review = f"{st.r_wrong}/{st.r_seen}" if st.r_seen else "—"
    return (f"| {name} | {st.done}/{st.steps} | {time_cell(st)} | {st.attempts or '—'} | {st.hints or '—'} "
            f"| {quiz_cell(st)} | {review} | {ratings_cell(st)} | {st.skipped or '—'} |")


def report(progress, plan, path):
    weeks = collect(progress, plan)
    out = ["# Отчёт о прогрессе", ""]
    events = progress.get("events", [])
    times = [t for t in (parse_time(e.get("t")) for e in events) if t]
    out.append(f"Файл: `{path}`. Сохранён: {progress.get('saved_at', '—')}.")
    if times:
        out.append(f"События: {len(events)}, с {min(times):%Y-%m-%d} по {max(times):%Y-%m-%d}.")
    out += ["", ("Время «факт / план» считается только по шагам, где время известно: `time_s` из редактора "
                 "или промежуток open → done из событий (если он не длиннее трёх планов)."),
            ("Квиз: вопросов с ошибкой / отвечено. Карточки (повторение на сайте): ошибок / показов. "
             "Оценки: легко/нормально/сложно."), ""]

    total = Stats()
    verdicts = []
    empty = []
    for w, topics in weeks:
        week_total = Stats()
        for st in topics.values():
            week_total.add(st)
        if not week_total.done:
            empty.append(str(w["n"]))
            continue
        total.add(week_total)
        out += [f"## Неделя {w['n']}. {w['title']}", "",
                "| Тема | Готово | Время факт / план | Попытки | Подсказки | Квиз | Карточки | Оценки | «Уже знаю» |",
                "|---|---|---|---|---|---|---|---|---|"]
        for name, st in topics.items():
            if st.done:
                out.append(row(f"`{name}`", st))
                kind, reasons = verdict(st)
                if kind:
                    verdicts.append((kind, w["n"], name, st, reasons))
        out += [row("**Итого за неделю**", week_total), ""]

    if empty:
        out += [f"Недели без выполненных шагов: {', '.join(empty)}.", ""]
    if total.done:
        out += ["## Итого", "", f"- Шагов готово: {total.done} из {total.steps}.",
                f"- Время: {time_cell(total)} (факт / план по измеренным шагам).",
                f"- Подсказок: {total.hints}, попыток: {total.attempts}, «уже знаю»: {total.skipped}.", ""]

    out += ["## Что можно сократить / усилить", ""]
    rules = (f"Правила. Усилить: есть оценка «сложно», ≥ {MANY_HINTS} подсказок или ≥ {MANY_TRIES} попыток "
             f"на задачу, ≥ {QUIZ_BAD:.0%} вопросов квиза или карточек с ошибкой, время > {SLOW:.0%} плана. "
             f"Сократить: нет подсказок, ошибок и «сложно», и при этом «уже знаю», время < {FAST:.0%} плана "
             f"или «легко» хотя бы у половины шагов.")
    out += [rules, ""]
    for kind, title in (("boost", "### Усилить"), ("cut", "### Можно сократить")):
        items = [v for v in verdicts if v[0] == kind]
        out += [title, ""]
        if not items:
            out += ["Нет кандидатов.", ""]
            continue
        for _, wn, name, st, reasons in items:
            shown = ", ".join(st.titles[:3]) + (" …" if len(st.titles) > 3 else "")
            out.append(f"- Неделя {wn}, `{name}` ({shown}): {'; '.join(reasons)}.")
        out.append("")
    if not total.done:
        out += ["Данных пока нет: ни один шаг не отмечен как выполненный.", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("progress", nargs="?", default=str(DEFAULT_PROGRESS), help="путь к progress.json")
    ap.add_argument("--plan", default=str(DEFAULT_PLAN), help="путь к plan.json")
    args = ap.parse_args(argv)
    try:
        progress = json.loads(Path(args.progress).expanduser().read_text(encoding="utf-8"))
        plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Ошибка чтения: {e}", file=sys.stderr)
        return 1
    print(report(progress, plan, args.progress))
    return 0


if __name__ == "__main__":
    sys.exit(main())
