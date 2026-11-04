"""Tests of the Quiz ML bank checks. Run: python3 tools/test_pyquiz_checks.py"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pyquiz_checks as pc  # noqa: E402

WIKI = ROOT / "data" / "articles" / "python-time-complexity.md"


def choice(**kw):
    q = {
        "id": "t-1", "topic": "list-o", "type": "choice", "q": "Сколько стоит `a.pop(0)`?",
        "options": ["O(1)", "O(n)", "O(log n)"], "answer": 1,
        "why": "list хранит указатели подряд в массиве. pop(0) сдвигает все n−1 элементов на одну позицию влево, это линейное время.",
        "wrong": {"0": "O(1) стоит pop() с конца: там ничего не сдвигается, а здесь сдвиг всех элементов.",
                  "2": "Логарифм был бы при делении задачи пополам, а сдвиг элементов проходит их все подряд."},
        "src": ["https://wiki.python.org/moin/TimeComplexity"],
    }
    q.update(kw)
    return q


class PublicMethods(unittest.TestCase):
    def test_list_has_eleven_public_methods(self):
        names = pc.public_methods(list)
        self.assertEqual(len(names), 11)
        self.assertIn("copy", names)
        self.assertFalse(any(n.startswith("_") for n in names))


class Coverage(unittest.TestCase):
    def test_missing_description_and_question_are_reported(self):
        methods = {"list": {n: "описание" for n in pc.public_methods(list) if n != "sort"}}
        questions = [{"covers": [f"list.{n}" for n in pc.public_methods(list) if n != "copy"]}]
        errors = pc.check_coverage(methods, questions, types=("list",))
        self.assertTrue(any("list.sort" in e and "описан" in e for e in errors), errors)
        self.assertTrue(any("list.copy" in e and "вопрос" in e for e in errors), errors)

    def test_unknown_method_name_is_reported(self):
        methods = {"list": {**{n: "описание" for n in pc.public_methods(list)}, "push": "нет такого"}}
        questions = [{"covers": [f"list.{n}" for n in pc.public_methods(list)]}]
        self.assertTrue(any("list.push" in e for e in pc.check_coverage(methods, questions, types=("list",))))

    def test_full_coverage_has_no_errors(self):
        methods = {"list": {n: "описание" for n in pc.public_methods(list)}}
        questions = [{"covers": [f"list.{n}" for n in pc.public_methods(list)]}]
        self.assertEqual(pc.check_coverage(methods, questions, types=("list",)), [])


class Wiki(unittest.TestCase):
    def test_tables_are_parsed_with_footnotes_stripped(self):
        t = pc.wiki_tables(WIKI)
        self.assertEqual(t["list"]["Pop из середины"], ("O(n)", "O(n)"))
        self.assertEqual(t["list"]["Append"], ("O(1)", "O(1)"))
        self.assertEqual(t["set"]["`x in s`"], ("O(1)", "O(n)"))
        self.assertEqual(t["set"]["Объединение `s | t`"], ("O(len(s)+len(t))", ""))
        self.assertEqual(t["dict"]["Копия"], ("O(n)", "O(n)"))

    def test_answer_must_match_the_cell(self):
        t = pc.wiki_tables(WIKI)
        self.assertEqual(pc.check_wiki(choice(wiki=["list", "Pop из середины", "avg"]), t), [])
        self.assertTrue(pc.check_wiki(choice(wiki=["list", "Append", "avg"]), t))
        self.assertTrue(pc.check_wiki(choice(wiki=["list", "Нет такой строки", "avg"]), t))


class FitClass(unittest.TestCase):
    NS = [1000, 4000, 16000, 64000, 256000]

    def test_quadratic_time_fits_n2(self):
        ranking = pc.fit_class(self.NS, [3e-7 * n * n for n in self.NS])
        self.assertEqual(ranking[0][0], "n2")

    def test_n_log_n_time_fits_n_or_nlogn(self):
        ranking = pc.fit_class(self.NS, [1e-6 * n * math.log2(n) for n in self.NS])
        self.assertEqual(ranking[0][0], "nlogn")

    def test_exponential_does_not_overflow_on_large_n(self):
        ranking = pc.fit_class(self.NS, [1e-6] * 5)
        self.assertEqual(ranking[0][0], "1")


class Measure(unittest.TestCase):
    def q(self, cls):
        return choice(measure={"setup": "", "stmt": "pass", "ns": [1000, 4000, 16000, 64000, 256000], "cls": cls})

    def test_wrong_class_is_reported(self):
        quadratic = lambda setup, stmt, n: 3e-7 * n * n  # noqa: E731
        self.assertTrue(pc.check_measure(self.q("n"), timer=quadratic))
        self.assertEqual(pc.check_measure(self.q("n2"), timer=quadratic), [])

    def test_neighbour_class_within_tolerance_passes(self):
        linear = lambda setup, stmt, n: 2e-7 * n + 1e-9 * n * math.log2(n)  # noqa: E731
        self.assertEqual(pc.check_measure(self.q("n"), timer=linear), [])

    def test_real_timer_sees_linear_scan(self):
        q = choice(measure={"setup": "a = list(range(n))", "stmt": "-1 in a", "ns": [20000, 40000, 80000, 160000, 320000], "cls": "n"})
        self.assertEqual(pc.check_measure(q), [])


class Explanations(unittest.TestCase):
    def test_complete_question_passes(self):
        self.assertEqual(pc.check_explanations(choice()), [])

    def test_missing_wrong_option_is_reported(self):
        q = choice(wrong={"0": choice()["wrong"]["0"]})
        self.assertTrue(any("2" in e for e in pc.check_explanations(q)))

    def test_short_why_is_reported(self):
        self.assertTrue(pc.check_explanations(choice(why="Потому что так.")))


class Schema(unittest.TestCase):
    def test_valid_choice_and_input(self):
        topics = {"list-o", "str-m"}
        self.assertEqual(pc.check_schema(choice(), topics), [])
        inp = {"id": "s-1", "topic": "str-m", "type": "input", "of": "str", "q": "…", "answer": ["rsplit"],
               "why": "x" * 90, "src": ["https://docs.python.org/3/library/stdtypes.html#str.rsplit"]}
        self.assertEqual(pc.check_schema(inp, topics), [])

    def test_answer_out_of_range_and_unknown_topic(self):
        errors = pc.check_schema(choice(answer=5, topic="nope"), {"list-o"})
        self.assertEqual(len(errors), 2, errors)


class RunCheck(unittest.TestCase):
    def test_failing_assert_is_reported(self):
        self.assertEqual(pc.run_check(choice(check="d = {}\nassert d.setdefault('k', []) == [] and d == {'k': []}")), [])
        self.assertTrue(pc.run_check(choice(check="assert [].pop() is None")))


if __name__ == "__main__":
    unittest.main(verbosity=1)
