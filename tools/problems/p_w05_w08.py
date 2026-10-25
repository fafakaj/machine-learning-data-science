"""Weeks 5–8: intervals, grouping, top-k, prefix products, 3Sum, cycle detection, trees, heap."""

from collections import Counter
from textwrap import dedent as d

from .common import build_tree, dump_tree, rand_bst, rand_ints, rand_tree, rand_word, tree_values_inorder

TREE_NODE_DOC = """# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
"""
LIST_NODE_DOC = """# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None
"""


def _rand_intervals(rng, n_max=6, hi=20):
    out = []
    for _ in range(rng.randint(1, n_max)):
        a = rng.randint(0, hi)
        out.append([a, a + rng.randint(0, 5)])
    return out


def _merge_brute(intervals):
    # Mark covered points on a doubled grid, so [1,2] and [3,4] stay apart but [1,2] and [2,3] join.
    hi = max(b for _, b in intervals)
    covered = [False] * (2 * hi + 2)
    for a, b in intervals:
        for x in range(2 * a, 2 * b + 1):
            covered[x] = True
    out, start = [], None
    for x, c in enumerate(covered):
        if c and start is None:
            start = x
        if not c and start is not None:
            out.append([start // 2, (x - 1) // 2])
            start = None
    return out


def _insert_rand(rng):
    merged = _merge_brute(_rand_intervals(rng, 5, 25))
    # Merged intervals can touch at no point; keep a strictly separated sorted list.
    clean = [iv for i, iv in enumerate(merged) if i == 0 or iv[0] > merged[i - 1][1]]
    if rng.random() < 0.2:
        clean = []
    a = rng.randint(0, 30)
    return [clean, [a, a + rng.randint(0, 6)]]


def _non_overlap_brute(intervals):
    # Max set of pairwise non-overlapping intervals by trying all subsets (n ≤ 10).
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(intervals[i] for i in range(n) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return n - best


def _group_brute(strs):
    groups = []
    for s in strs:
        for g in groups:
            if sorted(g[0]) == sorted(s):
                g.append(s)
                break
        else:
            groups.append([s])
    return groups


def _topk_rand(rng):
    while True:
        nums = rand_ints(rng, 1, 14, -4, 4)
        counts = sorted(Counter(nums).values(), reverse=True)
        k = rng.randint(1, len(counts))
        if k == len(counts) or counts[k - 1] != counts[k]:
            return [nums, k]


def _topk_brute(nums, k):
    distinct = list(set(nums))
    distinct.sort(key=lambda x: -nums.count(x))
    return distinct[:k]


def _product_brute(nums):
    out = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        out.append(p)
    return out


def _three_sum_brute(nums):
    found = set()
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    found.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in sorted(found)]


def _cycle_rand(rng):
    values = rand_ints(rng, 0, 8, -5, 5)
    pos = rng.randint(-1, len(values) - 1) if values else -1
    return [{"values": values, "pos": pos}]


def _subtrees(level):
    out = []

    def walk(node):
        if node:
            out.append(dump_tree(node))
            walk(node.left)
            walk(node.right)

    walk(build_tree(level))
    return out


def _depth(node):
    return 0 if node is None else 1 + max(_depth(node.left), _depth(node.right))


def _diameter_brute(level):
    # Longest path = max over nodes of depth(left) + depth(right).
    best = 0

    def walk(node):
        nonlocal best
        if node:
            best = max(best, _depth(node.left) + _depth(node.right))
            walk(node.left)
            walk(node.right)

    walk(build_tree(level))
    return best


def _levels_brute(level):
    root = build_tree(level)
    by_depth = {}

    def walk(node, depth):
        if node:
            by_depth.setdefault(depth, []).append(node.val)
            walk(node.left, depth + 1)
            walk(node.right, depth + 1)

    walk(root, 0)
    return [by_depth[k] for k in sorted(by_depth)]


def _is_bst_brute(level):
    vals = tree_values_inorder(level)
    return all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))


def _maybe_bst(rng):
    r = rng.random()
    if r < 0.45:
        return [rand_bst(rng, 9, n_min=1)]
    if r < 0.75:
        tree = rand_bst(rng, 9, n_min=2)
        idx = [i for i, v in enumerate(tree) if v is not None]
        tree[rng.choice(idx)] = rng.randint(-50, 50)  # usually breaks the order
        return [tree]
    return [rand_tree(rng, 7, -5, 5, n_min=1)]


def _kth_smallest_rand(rng):
    tree = rand_bst(rng, 10, n_min=1)
    return [tree, rng.randint(1, sum(v is not None for v in tree))]


def _stones_brute(stones):
    stones = list(stones)
    while len(stones) > 1:
        stones.sort()
        y = stones.pop()
        x = stones.pop()
        if y != x:
            stones.append(y - x)
    return stones[0] if stones else 0


PROBLEMS = [
    # ---------------------------------------------------------------- Week 5
    {
        "id": 56, "slug": "merge-intervals", "title_en": "Merge Intervals",
        "title_ru": "Слияние отрезков", "difficulty": "Medium", "week": 5,
        "pattern": "intervals", "pattern_ru": "отрезки: сортировка по началу",
        "leetcode_url": "https://leetcode.com/problems/merge-intervals/",
        "statement_ru": d("""\
            Дан список отрезков `intervals`, каждый — `[start, end]`. Слейте все пересекающиеся
            отрезки и верните список отрезков без пересечений, который покрывает те же точки.
            Отрезки, которые касаются (`[1,4]` и `[4,5]`), тоже сливаются. Порядок отрезков в ответе не важен."""),
        "examples": [
            {"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]", "explain_ru": "[1,3] и [2,6] пересекаются."},
            {"input": "intervals = [[1,4],[4,5]]", "output": "[[1,5]]", "explain_ru": "Отрезки касаются в точке 4."},
        ],
        "constraints_ru": ["1 ≤ len(intervals) ≤ 10^4", "0 ≤ start ≤ end ≤ 10^4"],
        "complexity_target": "O(n log n) по времени",
        "starter_code": "class Solution:\n    def merge(self, intervals: List[List[int]]) -> List[List[int]]:\n        pass\n",
        "method": "merge", "arg_types": ["list[list[int]]"], "ret_type": "list[list[int]]", "compare": "unordered_nested",
        "hints_ru": [
            "В случайном порядке трудно понять, кто с кем пересекается. В каком порядке отрезков пересечения видны сразу, с соседом?",
            "Сортировка по началу. После неё новый отрезок может пересечься только с последним отрезком ответа. Инвариант: отрезки в ответе не пересекаются и идут по возрастанию.",
            "1) `out = []`. 2) Для `start, end` из `sorted(intervals)`: если `out` не пуст и `start <= out[-1][1]` — `out[-1][1] = max(out[-1][1], end)`. 3) Иначе `out.append([start, end])`. Знак `<=` сливает касание `[1,4]` и `[4,5]`. Отрезок внутри другого тоже поглощается благодаря `max`.",
        ],
        "brute": _merge_brute,
        "ref": d("""\
            class Solution:
                def merge(self, intervals):
                    out = []
                    for start, end in sorted(intervals):
                        if out and start <= out[-1][1]:
                            out[-1][1] = max(out[-1][1], end)
                        else:
                            out.append([start, end])
                    return out
            """),
        "cases": [[[[1, 3], [2, 6], [8, 10], [15, 18]]], [[[1, 4], [4, 5]]], [[[1, 4]]], [[[1, 4], [0, 4]]], [[[1, 4], [2, 3]]],
                  [[[4, 7], [1, 4]]], [[[1, 2], [3, 4]]], [[[0, 0], [0, 0]]], [[[2, 3], [4, 5], [6, 7], [1, 10]]], [[[5, 5], [1, 2], [2, 5]]]],
        "rand": lambda rng: [_rand_intervals(rng)],
    },
    {
        "id": 49, "slug": "group-anagrams", "title_en": "Group Anagrams",
        "title_ru": "Сгруппировать анаграммы", "difficulty": "Medium", "week": 5,
        "pattern": "hash-map-key", "pattern_ru": "словарь с вычисляемым ключом",
        "leetcode_url": "https://leetcode.com/problems/group-anagrams/",
        "statement_ru": d("""\
            Дан список строк `strs`. Сгруппируйте анаграммы: строки из одних и тех же букв
            в одном количестве. Верните список групп. Порядок групп и порядок строк внутри
            группы не важен."""),
        "examples": [
            {"input": 'strs = ["eat","tea","tan","ate","nat","bat"]', "output": '[["bat"],["nat","tan"],["ate","eat","tea"]]', "explain_ru": ""},
            {"input": 'strs = [""]', "output": '[[""]]', "explain_ru": ""},
            {"input": 'strs = ["a"]', "output": '[["a"]]', "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(strs) ≤ 10^4", "0 ≤ len(strs[i]) ≤ 100", "Только маленькие латинские буквы"],
        "complexity_target": "O(n · k log k) или O(n · k), где k — длина строки",
        "starter_code": "class Solution:\n    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:\n        pass\n",
        "method": "groupAnagrams", "arg_types": ["list[str]"], "ret_type": "list[list[str]]", "compare": "unordered_nested",
        "hints_ru": [
            "Сравнивать каждую строку с каждой группой — O(n²). Какое значение можно вычислить по строке так, чтобы у всех анаграмм оно было одинаковым, а у остальных строк — разным?",
            "Словарь с вычисляемым ключом. Ключ — отсортированные буквы `\"\".join(sorted(s))` или кортеж из 26 счётчиков. Ключ словаря должен быть hashable: `str` и `tuple` подходят, `list` — нет.",
            "1) `groups = defaultdict(list)`. 2) Для каждой строки: `groups[ключ(s)].append(s)`. 3) Верните `list(groups.values())`. Пустая строка `\"\"` — тоже группа со своим ключом.",
        ],
        "brute": _group_brute,
        "ref": d("""\
            class Solution:
                def groupAnagrams(self, strs):
                    groups = defaultdict(list)
                    for s in strs:
                        groups["".join(sorted(s))].append(s)
                    return list(groups.values())
            """),
        "naive": d("""\
            class Solution:
                def groupAnagrams(self, strs):
                    groups = []
                    for s in strs:
                        for g in groups:
                            if sorted(g[0]) == sorted(s):
                                g.append(s)
                                break
                        else:
                            groups.append([s])
                    return groups
            """),
        "cases": [[["eat", "tea", "tan", "ate", "nat", "bat"]], [[""]], [["a"]], [["", ""]], [["ab", "ba", "abc"]],
                  [["abc", "bca", "cab", "xyz"]], [["aab", "aba", "abb"]], [["x", "y", "x"]], [["listen", "silent", "enlist", "google"]]],
        "rand": lambda rng: [[rand_word(rng, 0, 3, "ab") for _ in range(rng.randint(1, 7))]],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(49)
                letters = "abcdefghijklmnopqrstuvwxyz"
                return [["".join(rng.choice(letters) for _ in range(8)) for _ in range(10**4)]]
            """)],
    },
    {
        "id": 347, "slug": "top-k-frequent-elements", "title_en": "Top K Frequent Elements",
        "title_ru": "k самых частых", "difficulty": "Medium", "week": 5,
        "pattern": "bucket-sort", "pattern_ru": "подсчёт + сортировка корзинами / куча",
        "leetcode_url": "https://leetcode.com/problems/top-k-frequent-elements/",
        "statement_ru": d("""\
            Дан список `nums` и число `k`. Верните `k` чисел, которые встречаются чаще всего.
            Гарантия: ответ единственный. Порядок чисел в ответе не важен."""),
        "examples": [
            {"input": "nums = [1,1,1,2,2,3], k = 2", "output": "[1,2]", "explain_ru": "1 — три раза, 2 — два раза."},
            {"input": "nums = [1], k = 1", "output": "[1]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^5", "1 ≤ k ≤ число разных элементов", "Ответ единственный"],
        "complexity_target": "Лучше, чем O(n log n): O(n) корзинами или O(n log k) кучей",
        "starter_code": "class Solution:\n    def topKFrequent(self, nums: List[int], k: int) -> List[int]:\n        pass\n",
        "method": "topKFrequent", "arg_types": ["list[int]", "int"], "ret_type": "list[int]", "compare": "unordered",
        "hints_ru": [
            "Сначала узнайте частоту каждого числа. Какие значения может принимать частота в списке длины n? Нужна ли тогда полная сортировка по частоте?",
            "Сортировка корзинами: частота — целое от 1 до n, поэтому создайте n + 1 корзин; в корзине `f` лежат числа с частотой `f`. Это O(n). Другой путь — куча: `heapq.nlargest(k, counts, key=counts.get)`, O(n log k).",
            "1) `counts = Counter(nums)`. 2) `buckets = [[] for _ in range(n + 1)]`; для каждой пары `x, c`: `buckets[c].append(x)`. 3) Идите от `c = n` вниз до 1, собирайте числа. 4) Набрали `k` — верните ответ.",
        ],
        "brute": _topk_brute,
        "ref": d("""\
            class Solution:
                def topKFrequent(self, nums, k):
                    counts = Counter(nums)
                    buckets = [[] for _ in range(len(nums) + 1)]
                    for x, c in counts.items():
                        buckets[c].append(x)
                    out = []
                    for c in range(len(nums), 0, -1):
                        for x in buckets[c]:
                            out.append(x)
                            if len(out) == k:
                                return out
            """),
        "naive": d("""\
            class Solution:
                def topKFrequent(self, nums, k):
                    distinct = list(set(nums))
                    distinct.sort(key=lambda x: -nums.count(x))
                    return distinct[:k]
            """),
        "cases": [[[1, 1, 1, 2, 2, 3], 2], [[1], 1], [[4, 4, 4, 5, 5, 6], 1], [[-1, -1], 1], [[1, 2], 2], [[5, 3, 5, 3, 5, 1], 2],
                  [[7, 7, 8, 8, 8, 9, 9, 9, 9], 3], [[0, 0, 0, -3, -3, 2], 2], [[1, 2, 3, 3], 1]],
        "rand": _topk_rand,
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(347)
                nums = []
                for v in range(20000):
                    nums += [v] * (1 if v >= 3 else 1000 - v)   # 0, 1, 2 are the most frequent
                rng.shuffle(nums)
                return [nums, 3]
            """)],
    },
    {
        "id": 57, "slug": "insert-interval", "title_en": "Insert Interval",
        "title_ru": "Вставить отрезок", "difficulty": "Medium", "week": 5,
        "pattern": "intervals", "pattern_ru": "отрезки: три фазы прохода",
        "leetcode_url": "https://leetcode.com/problems/insert-interval/",
        "statement_ru": d("""\
            Список `intervals` отсортирован по началу, отрезки в нём не пересекаются.
            Вставьте отрезок `newInterval` и, если нужно, слейте пересекающиеся отрезки.
            Верните новый отсортированный список без пересечений."""),
        "examples": [
            {"input": "intervals = [[1,3],[6,9]], newInterval = [2,5]", "output": "[[1,5],[6,9]]", "explain_ru": ""},
            {"input": "intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]", "output": "[[1,2],[3,10],[12,16]]", "explain_ru": "[4,8] пересекает [3,5], [6,7], [8,10]."},
        ],
        "constraints_ru": ["0 ≤ len(intervals) ≤ 10^4", "intervals отсортирован, без пересечений"],
        "complexity_target": "O(n) по времени",
        "starter_code": "class Solution:\n    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:\n        pass\n",
        "method": "insert", "arg_types": ["list[list[int]]", "list[int]"], "ret_type": "list[list[int]]",
        "hints_ru": [
            "Список уже отсортирован и без пересечений. Как расположены старые отрезки относительно нового: какие точно не трогает слияние?",
            "Три группы: целиком левее (`end < new_start`), пересекаются с новым, целиком правее (`start > new_end`). Левые и правые идут в ответ без изменений. Пересекающиеся сливаются с новым в один отрезок. Повторная сортировка не нужна.",
            "1) `s, e = newInterval`. 2) `left` — отрезки с `b < s`; `right` — с `a > e`. 3) Для остальных: `s = min(s, a)`, `e = max(e, b)`. 4) Верните `left + [[s, e]] + right`. Пустой `intervals` — ответ `[newInterval]`.",
        ],
        "brute": lambda intervals, new: _merge_brute(intervals + [new]),
        "ref": d("""\
            class Solution:
                def insert(self, intervals, newInterval):
                    s, e = newInterval
                    left = [iv for iv in intervals if iv[1] < s]
                    right = [iv for iv in intervals if iv[0] > e]
                    for a, b in intervals:
                        if b >= s and a <= e:
                            s, e = min(s, a), max(e, b)
                    return left + [[s, e]] + right
            """),
        "cases": [[[[1, 3], [6, 9]], [2, 5]], [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]], [[], [5, 7]], [[[1, 5]], [2, 3]],
                  [[[1, 5]], [6, 8]], [[[3, 5]], [0, 1]], [[[1, 5]], [0, 0]], [[[1, 5]], [5, 7]], [[[1, 2], [5, 6]], [3, 4]], [[[2, 4], [6, 8]], [0, 10]]],
        "rand": _insert_rand,
    },
    {
        "id": 435, "slug": "non-overlapping-intervals", "title_en": "Non-overlapping Intervals",
        "title_ru": "Убрать пересечения", "difficulty": "Medium", "week": 5,
        "pattern": "intervals-greedy", "pattern_ru": "жадный выбор по концу отрезка",
        "leetcode_url": "https://leetcode.com/problems/non-overlapping-intervals/",
        "statement_ru": d("""\
            Дан список отрезков. Найдите, какое **наименьшее** число отрезков нужно удалить,
            чтобы оставшиеся не пересекались. Отрезки, которые только касаются (`[1,2]` и `[2,3]`),
            не пересекаются."""),
        "examples": [
            {"input": "intervals = [[1,2],[2,3],[3,4],[1,3]]", "output": "1", "explain_ru": "Удалите [1,3]."},
            {"input": "intervals = [[1,2],[1,2],[1,2]]", "output": "2", "explain_ru": ""},
            {"input": "intervals = [[1,2],[2,3]]", "output": "0", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(intervals) ≤ 10^5", "-5·10^4 ≤ start < end ≤ 5·10^4"],
        "complexity_target": "O(n log n) по времени",
        "starter_code": "class Solution:\n    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:\n        pass\n",
        "method": "eraseOverlapIntervals", "arg_types": ["list[list[int]]"], "ret_type": "int",
        "hints_ru": [
            "Удалить минимум отрезков — значит оставить максимум непересекающихся. Какой отрезок выгоднее всего оставить первым?",
            "Жадный выбор по концу: отрезок, который кончается раньше всех, оставляет больше места справа. Сортируйте по концу. Инвариант: `end` — конец последнего оставленного отрезка.",
            "1) `removed = 0`, `end = -inf`. 2) Для отрезков, отсортированных по `iv[1]`: если `s >= end` — оставьте, `end = e`. 3) Иначе `removed += 1`. 4) Верните `removed`. `>=`: касание не пересечение.",
        ],
        "brute": _non_overlap_brute,
        "ref": d("""\
            class Solution:
                def eraseOverlapIntervals(self, intervals):
                    removed = 0
                    end = float("-inf")
                    for s, e in sorted(intervals, key=lambda iv: iv[1]):
                        if s >= end:
                            end = e
                        else:
                            removed += 1
                    return removed
            """),
        "naive": d("""\
            class Solution:
                def eraseOverlapIntervals(self, intervals):
                    iv = sorted(intervals)
                    n = len(iv)
                    best = [1] * n
                    for i in range(n):
                        for j in range(i):
                            if iv[j][1] <= iv[i][0]:
                                best[i] = max(best[i], best[j] + 1)
                    return n - max(best)
            """),
        "cases": [[[[1, 2], [2, 3], [3, 4], [1, 3]]], [[[1, 2], [1, 2], [1, 2]]], [[[1, 2], [2, 3]]], [[[0, 1]]], [[[1, 100], [11, 22], [1, 11], [2, 12]]],
                  [[[-5, -1], [-3, 0], [0, 2]]], [[[1, 5], [2, 3], [3, 4]]], [[[0, 2], [1, 3], [2, 4], [3, 5], [4, 6]]]],
        "rand": lambda rng: [[(lambda a: [a, a + rng.randint(1, 4)])(rng.randint(-5, 8)) for _ in range(rng.randint(1, 8))]],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(435)
                out = []
                for _ in range(2 * 10**4):
                    a = rng.randint(-5 * 10**4, 5 * 10**4 - 10)
                    out.append([a, a + rng.randint(1, 10)])
                return [out]
            """)],
    },
    # ---------------------------------------------------------------- Week 6
    {
        "id": 238, "slug": "product-of-array-except-self", "title_en": "Product of Array Except Self",
        "title_ru": "Произведение всех, кроме себя", "difficulty": "Medium", "week": 6,
        "pattern": "prefix-suffix", "pattern_ru": "префиксы и суффиксы",
        "leetcode_url": "https://leetcode.com/problems/product-of-array-except-self/",
        "statement_ru": d("""\
            Дан список `nums`. Верните список `answer`, где `answer[i]` — произведение всех
            элементов `nums`, кроме `nums[i]`. **Деление использовать нельзя.**
            Решение — за O(n)."""),
        "examples": [
            {"input": "nums = [1,2,3,4]", "output": "[24,12,8,6]", "explain_ru": "answer[0] = 2·3·4 = 24."},
            {"input": "nums = [-1,1,0,-3,3]", "output": "[0,0,9,0,0]", "explain_ru": "Ноль на позиции 2 обнуляет все, кроме answer[2]."},
        ],
        "constraints_ru": ["2 ≤ len(nums) ≤ 10^5", "-30 ≤ nums[i] ≤ 30", "Любое произведение помещается в 32-битное целое"],
        "complexity_target": "O(n) по времени; бонус — O(1) доп. памяти (ответ не считается)",
        "starter_code": "class Solution:\n    def productExceptSelf(self, nums: List[int]) -> List[int]:\n        pass\n",
        "method": "productExceptSelf", "arg_types": ["list[int]"], "ret_type": "list[int]",
        "hints_ru": [
            "Деление запрещено. Разбейте «все кроме `nums[i]`» на две части: что стоит левее `i` и что правее?",
            "Префиксы и суффиксы: `answer[i] = (произведение слева) × (произведение справа)`. Произведения слева считаются одним проходом слева направо, справа — одним проходом справа налево. Ноль в списке не мешает: деления нет.",
            "1) `out = [1] * n`, `left = 1`. 2) Слева направо: `out[i] = left`, затем `left *= nums[i]`. 3) `right = 1`; справа налево: `out[i] *= right`, затем `right *= nums[i]`. 4) Верните `out`. Порядок «записать, потом умножить» исключает сам `nums[i]`.",
        ],
        "brute": _product_brute,
        "ref": d("""\
            class Solution:
                def productExceptSelf(self, nums):
                    n = len(nums)
                    out = [1] * n
                    left = 1
                    for i in range(n):
                        out[i] = left
                        left *= nums[i]
                    right = 1
                    for i in range(n - 1, -1, -1):
                        out[i] *= right
                        right *= nums[i]
                    return out
            """),
        "naive": d("""\
            class Solution:
                def productExceptSelf(self, nums):
                    out = []
                    for i in range(len(nums)):
                        p = 1
                        for j in range(len(nums)):
                            if j != i:
                                p *= nums[j]
                        out.append(p)
                    return out
            """),
        "cases": [[[1, 2, 3, 4]], [[-1, 1, 0, -3, 3]], [[2, 3]], [[0, 0]], [[0, 5]], [[1, 1, 1, 1]], [[-2, -3, 4]], [[5, 0, 2, 0]], [[30, -30, 2]]],
        "rand": lambda rng: [rand_ints(rng, 2, 7, -4, 4)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(238)
                nums = [rng.choice([1, -1]) for _ in range(10**5)]
                for i in rng.sample(range(10**5), 10):
                    nums[i] = 2
                return [nums]
            """)],
    },
    {
        "id": 15, "slug": "3sum", "title_en": "3Sum",
        "title_ru": "Сумма трёх", "difficulty": "Medium", "week": 6,
        "pattern": "sort-two-pointers", "pattern_ru": "сортировка + два указателя",
        "leetcode_url": "https://leetcode.com/problems/3sum/",
        "statement_ru": d("""\
            Дан список `nums`. Найдите все **разные** тройки чисел `[a, b, c]` из разных позиций
            списка, у которых `a + b + c == 0`. Тройки из одних и тех же чисел — одна тройка.
            Порядок троек и порядок чисел внутри тройки не важен."""),
        "examples": [
            {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]", "explain_ru": "Тройка [-1,0,1] собирается двумя способами, но в ответе одна."},
            {"input": "nums = [0,1,1]", "output": "[]", "explain_ru": ""},
            {"input": "nums = [0,0,0]", "output": "[[0,0,0]]", "explain_ru": ""},
        ],
        "constraints_ru": ["3 ≤ len(nums) ≤ 3000", "-10^5 ≤ nums[i] ≤ 10^5"],
        "complexity_target": "O(n²) по времени",
        "starter_code": "class Solution:\n    def threeSum(self, nums: List[int]) -> List[List[int]]:\n        pass\n",
        "method": "threeSum", "arg_types": ["list[int]"], "ret_type": "list[list[int]]", "compare": "unordered_nested",
        "hints_ru": [
            "Зафиксируйте первое число тройки `a`. Какая задача остаётся для двух других чисел? Вы её уже решали.",
            "Сортировка + два указателя (#167): для каждого `i` ищите в `nums[i+1:]` пару с суммой `-nums[i]`. Итого O(n²). Отсортированный список помогает и с повторами: равные числа стоят рядом.",
            "1) `nums = sorted(nums)`. 2) Для `i`: если `i > 0` и `nums[i] == nums[i-1]` — пропустите. 3) `l, r = i + 1, n - 1`; сумма < 0 — `l += 1`; > 0 — `r -= 1`; = 0 — запишите тройку, `l += 1` и пропускайте `l`, пока `nums[l] == nums[l-1]`. Случай `[0,0,0,0]` — одна тройка.",
        ],
        "brute": _three_sum_brute,
        "ref": d("""\
            class Solution:
                def threeSum(self, nums):
                    nums = sorted(nums)
                    out = []
                    for i in range(len(nums) - 2):
                        if i and nums[i] == nums[i - 1]:
                            continue
                        l, r = i + 1, len(nums) - 1
                        while l < r:
                            s = nums[i] + nums[l] + nums[r]
                            if s < 0:
                                l += 1
                            elif s > 0:
                                r -= 1
                            else:
                                out.append([nums[i], nums[l], nums[r]])
                                l += 1
                                while l < r and nums[l] == nums[l - 1]:
                                    l += 1
                    return out
            """),
        "naive": d("""\
            class Solution:
                def threeSum(self, nums):
                    found = set()
                    n = len(nums)
                    for i in range(n):
                        for j in range(i + 1, n):
                            for k in range(j + 1, n):
                                if nums[i] + nums[j] + nums[k] == 0:
                                    found.add(tuple(sorted((nums[i], nums[j], nums[k]))))
                    return [list(t) for t in found]
            """),
        "cases": [[[-1, 0, 1, 2, -1, -4]], [[0, 1, 1]], [[0, 0, 0]], [[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[1, 2, -3]],
                  [[-1, 0, 1, 0]], [[3, -2, 1, 0]], [[-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6]], [[1, 1, 1]]],
        "rand": lambda rng: [rand_ints(rng, 3, 9, -4, 4)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(15)
                nums = [rng.randint(-10**5, 10**5) for _ in range(1500)]
                return [nums]
            """)],
    },
    {
        "id": 141, "slug": "linked-list-cycle", "title_en": "Linked List Cycle",
        "title_ru": "Цикл в связном списке", "difficulty": "Easy", "week": 6,
        "pattern": "fast-slow-pointers", "pattern_ru": "быстрый и медленный указатели",
        "leetcode_url": "https://leetcode.com/problems/linked-list-cycle/",
        "statement_ru": d("""\
            Дана голова `head` связного списка. Верните `True`, если в списке есть цикл:
            идя по `next`, можно вернуться в уже пройденный узел.
            В тестах список задан как `{"values": [...], "pos": k}`: последний узел ссылается
            на узел с индексом `k`; `pos = -1` — цикла нет. Функция получает только `head`."""),
        "examples": [
            {"input": 'head = {"values": [3,2,0,-4], "pos": 1}', "output": "true", "explain_ru": "-4 ссылается на узел 2."},
            {"input": 'head = {"values": [1,2], "pos": 0}', "output": "true", "explain_ru": ""},
            {"input": 'head = {"values": [1], "pos": -1}', "output": "false", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 10^4", "pos = -1 или корректный индекс"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": LIST_NODE_DOC + "class Solution:\n    def hasCycle(self, head: Optional[ListNode]) -> bool:\n        pass\n",
        "method": "hasCycle", "arg_types": ["ListNodeCycle"], "ret_type": "bool",
        "hints_ru": [
            "Вы идёте по `next`. Если цикла нет, что случится в конце? Если цикл есть, как это заметить, не храня все пройденные узлы?",
            "Быстрый и медленный указатели (Флойд): медленный делает 1 шаг, быстрый — 2. В цикле быстрый догоняет медленного на 1 узел за ход, поэтому встреча неизбежна. Память O(1). Вариант с `set` должен хранить узлы, а не значения.",
            "1) `slow = fast = head`. 2) Пока `fast` и `fast.next`: `slow = slow.next`, `fast = fast.next.next`. 3) `slow is fast` — верните `True`. 4) Цикл закончился — `False`. Пустой список — `False`.",
        ],
        "brute": lambda spec: spec["pos"] != -1 and bool(spec["values"]),
        "ref": d("""\
            class Solution:
                def hasCycle(self, head):
                    slow = fast = head
                    while fast and fast.next:
                        slow = slow.next
                        fast = fast.next.next
                        if slow is fast:
                            return True
                    return False
            """),
        "cases": [[{"values": [3, 2, 0, -4], "pos": 1}], [{"values": [1, 2], "pos": 0}], [{"values": [1], "pos": -1}], [{"values": [], "pos": -1}],
                  [{"values": [1], "pos": 0}], [{"values": [1, 1, 1], "pos": -1}], [{"values": [1, 2, 3, 4, 5], "pos": 4}], [{"values": list(range(500)), "pos": 250}]],
        "rand": _cycle_rand,
    },
    {
        "id": 11, "slug": "container-with-most-water", "title_en": "Container With Most Water",
        "title_ru": "Сосуд с наибольшим объёмом", "difficulty": "Medium", "week": 6,
        "pattern": "two-pointers", "pattern_ru": "два указателя: сдвиг меньшей стенки",
        "leetcode_url": "https://leetcode.com/problems/container-with-most-water/",
        "statement_ru": d("""\
            `height[i]` — высота вертикальной стенки в точке `i`. Выберите две стенки:
            вместе с осью X они образуют сосуд. Объём воды — `min(height[i], height[j]) * (j - i)`.
            Верните наибольший возможный объём."""),
        "examples": [
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49", "explain_ru": "Стенки 1 и 8: min(8, 7) · 7 = 49."},
            {"input": "height = [1,1]", "output": "1", "explain_ru": ""},
        ],
        "constraints_ru": ["2 ≤ len(height) ≤ 10^5", "0 ≤ height[i] ≤ 10^4"],
        "complexity_target": "O(n) по времени",
        "starter_code": "class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        pass\n",
        "method": "maxArea", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Начните с самых дальних стенок: ширина максимальна. Если сдвинуть внутрь более высокую стенку, может ли объём вырасти?",
            "Два указателя с концов. Объём ограничен меньшей стенкой. Сдвиг большей уменьшает ширину и не поднимает минимум, поэтому сдвигайте меньшую. Так каждая отброшенная пара заведомо не лучше ответа.",
            "1) `l, r = 0, n - 1`, `best = 0`. 2) Пока `l < r`: `best = max(best, min(h[l], h[r]) * (r - l))`. 3) Если `h[l] < h[r]` — `l += 1`, иначе `r -= 1`. 4) Верните `best`.",
        ],
        "brute": lambda h: max(min(h[i], h[j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h))),
        "ref": d("""\
            class Solution:
                def maxArea(self, height):
                    l, r = 0, len(height) - 1
                    best = 0
                    while l < r:
                        best = max(best, min(height[l], height[r]) * (r - l))
                        if height[l] < height[r]:
                            l += 1
                        else:
                            r -= 1
                    return best
            """),
        "naive": d("""\
            class Solution:
                def maxArea(self, height):
                    best = 0
                    for i in range(len(height)):
                        for j in range(i + 1, len(height)):
                            best = max(best, min(height[i], height[j]) * (j - i))
                    return best
            """),
        "cases": [[[1, 8, 6, 2, 5, 4, 8, 3, 7]], [[1, 1]], [[0, 0]], [[4, 3, 2, 1, 4]], [[1, 2, 1]], [[2, 3, 4, 5, 18, 17, 6]],
                  [[10000, 1, 10000]], [[1, 2, 3, 4, 5]], [[0, 5]]],
        "rand": lambda rng: [rand_ints(rng, 2, 9, 0, 9)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(11)
                return [[rng.randint(0, 10**4) for _ in range(10**5)]]
            """)],
    },
    {
        "id": 128, "slug": "longest-consecutive-sequence", "title_en": "Longest Consecutive Sequence",
        "title_ru": "Самая длинная цепочка подряд идущих", "difficulty": "Medium", "week": 6,
        "pattern": "hash-set", "pattern_ru": "set: начинать только с начала цепочки",
        "leetcode_url": "https://leetcode.com/problems/longest-consecutive-sequence/",
        "statement_ru": d("""\
            Дан неотсортированный список `nums`. Найдите длину самой длинной цепочки чисел
            `x, x+1, x+2, …`, которые все есть в списке (в любом порядке). Нужно O(n)."""),
        "examples": [
            {"input": "nums = [100,4,200,1,3,2]", "output": "4", "explain_ru": "Цепочка 1, 2, 3, 4."},
            {"input": "nums = [0,3,7,2,5,8,4,6,0,1]", "output": "9", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ len(nums) ≤ 10^5", "-10^9 ≤ nums[i] ≤ 10^9"],
        "complexity_target": "O(n) по времени",
        "starter_code": "class Solution:\n    def longestConsecutive(self, nums: List[int]) -> int:\n        pass\n",
        "method": "longestConsecutive", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Сортировка даёт O(n log n), а нужно O(n). Как без сортировки проверить, что число `x + 1` есть в списке? От каких чисел вообще стоит начинать счёт цепочки?",
            "Положите числа в `set`: проверка `x + 1 in s` — O(1). Начинайте счёт только с начала цепочки: `x - 1 not in s`. Тогда каждое число войдёт в счёт один раз, и общее время O(n).",
            "1) `s = set(nums)`, `best = 0`. 2) Для `x` в `s`: если `x - 1 not in s` — `y = x`; пока `y + 1 in s`: `y += 1`. 3) `best = max(best, y - x + 1)`. Пустой список — 0. Перебирайте `s`, а не `nums`: повторы не нужны.",
        ],
        "brute": lambda nums: max([0] + [next(L for L in range(len(nums) + 1, 0, -1) if all(x + t in nums for t in range(L))) for x in nums]),
        "ref": d("""\
            class Solution:
                def longestConsecutive(self, nums):
                    s = set(nums)
                    best = 0
                    for x in s:
                        if x - 1 not in s:
                            y = x
                            while y + 1 in s:
                                y += 1
                            best = max(best, y - x + 1)
                    return best
            """),
        "naive": d("""\
            class Solution:
                def longestConsecutive(self, nums):
                    s = set(nums)
                    best = 0
                    for x in nums:
                        y = x
                        while y + 1 in s:
                            y += 1
                        best = max(best, y - x + 1)
                    return best
            """),
        "cases": [[[100, 4, 200, 1, 3, 2]], [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], [[]], [[5]], [[1, 1, 1]], [[1, 3, 5]], [[-1, 0, 1]],
                  [[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]], [[10**9, 10**9 - 1, -10**9]]],
        "rand": lambda rng: [rand_ints(rng, 0, 9, -6, 6)],
        "perf": [d("""\
            def gen():
                n = 10**5
                return [list(range(n, 0, -1))]   # one long chain: naive restarts from every number
            """)],
    },
    # ---------------------------------------------------------------- Week 7
    {
        "id": 226, "slug": "invert-binary-tree", "title_en": "Invert Binary Tree",
        "title_ru": "Отразить дерево", "difficulty": "Easy", "week": 7,
        "pattern": "tree-dfs", "pattern_ru": "дерево: рекурсия",
        "leetcode_url": "https://leetcode.com/problems/invert-binary-tree/",
        "statement_ru": d("""\
            Дан корень `root` двоичного дерева. Отразите дерево зеркально: в каждом узле
            поменяйте местами левое и правое поддерево. Верните корень.
            Дерево в тестах записано по уровням, как на LeetCode: `[4,2,7,1,3,6,9]`, `null` — нет узла."""),
        "examples": [
            {"input": "root = [4,2,7,1,3,6,9]", "output": "[4,7,2,9,6,3,1]", "explain_ru": ""},
            {"input": "root = [2,1,3]", "output": "[2,3,1]", "explain_ru": ""},
            {"input": "root = []", "output": "[]", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 100", "-100 ≤ Node.val ≤ 100"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:\n        pass\n",
        "method": "invertTree", "arg_types": ["TreeNode"], "ret_type": "TreeNode",
        "hints_ru": [
            "Посмотрите на отражённое дерево. Где теперь левое поддерево корня? Отражено ли оно само?",
            "Рекурсия: отразить дерево = поменять детей корня и отразить каждое поддерево. База — пустое дерево (`None`): верните как есть. Без рекурсии работает обход со стеком: каждый узел обрабатывается один раз.",
            "1) `stack = [root]`. 2) Пока стек не пуст: `node = stack.pop()`; если `node` — обменяйте `node.left` и `node.right`, положите обоих детей в стек. 3) Верните `root`. Рекурсивно: `root.left, root.right = invert(root.right), invert(root.left)`.",
        ],
        "brute": lambda level: dump_tree(_mirror(build_tree(level))),
        "ref": d("""\
            class Solution:
                def invertTree(self, root):
                    stack = [root]
                    while stack:
                        node = stack.pop()
                        if node:
                            node.left, node.right = node.right, node.left
                            stack += [node.left, node.right]
                    return root
            """),
        "cases": [[[4, 2, 7, 1, 3, 6, 9]], [[2, 1, 3]], [[]], [[1]], [[1, 2]], [[1, None, 2]], [[1, 2, None, 3, None, 4]], [[3, 9, 20, None, None, 15, 7]]],
        "rand": lambda rng: [rand_tree(rng, 10)],
    },
    {
        "id": 104, "slug": "maximum-depth-of-binary-tree", "title_en": "Maximum Depth of Binary Tree",
        "title_ru": "Глубина дерева", "difficulty": "Easy", "week": 7,
        "pattern": "tree-dfs", "pattern_ru": "дерево: рекурсия / BFS по уровням",
        "leetcode_url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/",
        "statement_ru": d("""\
            Верните глубину двоичного дерева: число узлов на самом длинном пути от корня
            до листа. У пустого дерева глубина 0."""),
        "examples": [
            {"input": "root = [3,9,20,null,null,15,7]", "output": "3", "explain_ru": "Путь 3 → 20 → 15."},
            {"input": "root = [1,null,2]", "output": "2", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 10^4"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def maxDepth(self, root: Optional[TreeNode]) -> int:\n        pass\n",
        "method": "maxDepth", "arg_types": ["TreeNode"], "ret_type": "int",
        "hints_ru": [
            "Пусть глубины левого и правого поддерева уже известны. Как получить из них глубину всего дерева?",
            "Рекурсия: `depth(node) = 1 + max(depth(left), depth(right))`, `depth(None) = 0`. Другой путь — обход по уровням (BFS): глубина равна числу уровней.",
            "1) `level = [root]` (или `[]` для пустого). 2) Пока `level` не пуст: `depth += 1`; новый `level` — все непустые дети узлов текущего уровня. 3) Верните `depth`. Пустое дерево — 0.",
        ],
        "brute": lambda level: _depth(build_tree(level)),
        "ref": d("""\
            class Solution:
                def maxDepth(self, root):
                    level = [root] if root else []
                    depth = 0
                    while level:
                        depth += 1
                        level = [c for n in level for c in (n.left, n.right) if c]
                    return depth
            """),
        "cases": [[[3, 9, 20, None, None, 15, 7]], [[1, None, 2]], [[]], [[0]], [[1, 2, 3, 4, None, None, 5, 6]], [[1, 2, None, 3, None, 4, None, 5]]],
        "rand": lambda rng: [rand_tree(rng, 12)],
    },
    {
        "id": 100, "slug": "same-tree", "title_en": "Same Tree",
        "title_ru": "Одинаковые деревья", "difficulty": "Easy", "week": 7,
        "pattern": "tree-dfs", "pattern_ru": "дерево: рекурсия по двум деревьям",
        "leetcode_url": "https://leetcode.com/problems/same-tree/",
        "statement_ru": d("""\
            Даны корни `p` и `q` двух двоичных деревьев. Верните `True`, если деревья
            одинаковые: та же форма и те же значения в узлах."""),
        "examples": [
            {"input": "p = [1,2,3], q = [1,2,3]", "output": "true", "explain_ru": ""},
            {"input": "p = [1,2], q = [1,null,2]", "output": "false", "explain_ru": "Значения те же, форма разная."},
            {"input": "p = [1,2,1], q = [1,1,2]", "output": "false", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 100"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:\n        pass\n",
        "method": "isSameTree", "arg_types": ["TreeNode", "TreeNode"], "ret_type": "bool",
        "hints_ru": [
            "Корни двух деревьев совпали. Что ещё должно быть верно, чтобы деревья были одинаковыми?",
            "Рекурсия по двум деревьям одновременно. Деревья равны, если равны корни и попарно равны левые и правые поддеревья. Сначала обработайте `None`: иначе `p.val` упадёт.",
            "1) Если `p` или `q` — `None`: верните `p is q` (оба пустые — `True`, один — `False`). 2) Иначе верните `p.val == q.val and same(p.left, q.left) and same(p.right, q.right)`.",
        ],
        "brute": lambda a, b: a == b,
        "ref": d("""\
            class Solution:
                def isSameTree(self, p, q):
                    if p is None or q is None:
                        return p is q
                    return p.val == q.val and self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
            """),
        "cases": [[[1, 2, 3], [1, 2, 3]], [[1, 2], [1, None, 2]], [[1, 2, 1], [1, 1, 2]], [[], []], [[1], []], [[], [1]], [[1], [1]], [[5, 4, 6, None, 7], [5, 4, 6, None, 7]], [[5, 4, 6, None, 7], [5, 4, 6, 7]]],
        "rand": lambda rng: (lambda t: [t, list(t) if rng.random() < 0.5 else rand_tree(rng, 4, 0, 2)])(rand_tree(rng, 4, 0, 2)),
    },
    {
        "id": 572, "slug": "subtree-of-another-tree", "title_en": "Subtree of Another Tree",
        "title_ru": "Поддерево", "difficulty": "Easy", "week": 7,
        "pattern": "tree-dfs", "pattern_ru": "дерево: обход + сравнение деревьев",
        "leetcode_url": "https://leetcode.com/problems/subtree-of-another-tree/",
        "statement_ru": d("""\
            Даны деревья `root` и `subRoot`. Верните `True`, если в `root` есть узел, поддерево
            которого (узел и **все** его потомки) совпадает с `subRoot` по форме и значениям."""),
        "examples": [
            {"input": "root = [3,4,5,1,2], subRoot = [4,1,2]", "output": "true", "explain_ru": ""},
            {"input": "root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,1,2]", "output": "false", "explain_ru": "У узла 4 в root есть лишний потомок 0."},
        ],
        "constraints_ru": ["1 ≤ узлов в root ≤ 2000", "1 ≤ узлов в subRoot ≤ 1000"],
        "complexity_target": "O(n · m) по времени — достаточно",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:\n        pass\n",
        "method": "isSubtree", "arg_types": ["TreeNode", "TreeNode"], "ret_type": "bool",
        "hints_ru": [
            "Вы уже умеете проверять, что два дерева одинаковые (#100). В каком узле `root` может начинаться копия `subRoot`?",
            "Обход + сравнение: для каждого узла `root` вызовите проверку «дерево с корнем здесь совпадает с `subRoot`». Сложность O(n·m). Сравнение проверяет поддерево целиком, поэтому лишние потомки дадут `False`.",
            "1) Напишите `same(a, b)` из #100. 2) Обойдите `root` стеком или рекурсией. 3) Для каждого узла: `same(node, subRoot)` — верните `True`. 4) Обход закончился — `False`. Пустой `root` — `False`.",
        ],
        "brute": lambda root, sub: sub in _subtrees(root),
        "ref": d("""\
            class Solution:
                def isSubtree(self, root, subRoot):
                    def same(a, b):
                        if a is None or b is None:
                            return a is b
                        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)
                    stack = [root]
                    while stack:
                        node = stack.pop()
                        if node:
                            if same(node, subRoot):
                                return True
                            stack += [node.left, node.right]
                    return False
            """),
        "cases": [[[3, 4, 5, 1, 2], [4, 1, 2]], [[3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2]], [[1], [1]], [[1, 1], [1]], [[1, 2], [2]], [[1, 2], [3]],
                  [[1, 2, 3], [1, 2]], [[3, 4, 5, 1, None, 2], [3, 1, 2]], [[4, 1, None, 1], [1, 1]]],
        "rand": lambda rng: (lambda t: [t, rng.choice(_subtrees(t)) if rng.random() < 0.5 else rand_tree(rng, 3, 0, 2, n_min=1)])(rand_tree(rng, 8, 0, 2, n_min=1)),
    },
    {
        "id": 543, "slug": "diameter-of-binary-tree", "title_en": "Diameter of Binary Tree",
        "title_ru": "Диаметр дерева", "difficulty": "Easy", "week": 7,
        "pattern": "tree-dfs-postorder", "pattern_ru": "дерево: рекурсия возвращает глубину, ответ — в общей переменной",
        "leetcode_url": "https://leetcode.com/problems/diameter-of-binary-tree/",
        "statement_ru": d("""\
            Верните диаметр двоичного дерева: длину самого длинного пути между двумя любыми
            узлами. Длина пути — число **рёбер**. Путь может не проходить через корень."""),
        "examples": [
            {"input": "root = [1,2,3,4,5]", "output": "3", "explain_ru": "Путь 4 → 2 → 1 → 3 или 5 → 2 → 1 → 3."},
            {"input": "root = [1,2]", "output": "1", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ число узлов ≤ 10^4"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:\n        pass\n",
        "method": "diameterOfBinaryTree", "arg_types": ["TreeNode"], "ret_type": "int",
        "hints_ru": [
            "Самый длинный путь где-то «перегибается»: поднимается к узлу и спускается обратно. Чему равна длина такого пути через узел?",
            "Длина пути через узел = глубина левого + глубина правого поддерева. Вызывать `maxDepth` для каждого узла — O(n²). Один обход: рекурсия возвращает глубину, а лучший путь обновляет внешнюю переменную через `nonlocal` (неделя 1).",
            "1) `best = 0`. 2) `depth(node)`: `None` → 0; `l, r = depth(left), depth(right)`; `best = max(best, l + r)`; верните `1 + max(l, r)`. 3) Вызовите `depth(root)`, верните `best`. Путь считается в рёбрах: одно дерево из одного узла — 0.",
        ],
        "brute": _diameter_brute,
        "ref": d("""\
            class Solution:
                def diameterOfBinaryTree(self, root):
                    best = 0
                    def depth(node):
                        nonlocal best
                        if node is None:
                            return 0
                        l, r = depth(node.left), depth(node.right)
                        best = max(best, l + r)
                        return 1 + max(l, r)
                    depth(root)
                    return best
            """),
        "cases": [[[1, 2, 3, 4, 5]], [[1, 2]], [[1]], [[1, 2, None, 3, None, 4]], [[4, -7, -3, None, None, -9, -3, 9, -7, -4, None, 6, None, -6, -6, None, None, 0, 6, 5, None, 9, None, None, -1, -4, None, None, None, -2]],
                  [[1, 2, 3, None, None, 4, 5, 6, None, None, 7]]],
        "rand": lambda rng: [rand_tree(rng, 12, n_min=1)],
    },
    # ---------------------------------------------------------------- Week 8
    {
        "id": 102, "slug": "binary-tree-level-order-traversal", "title_en": "Binary Tree Level Order Traversal",
        "title_ru": "Обход дерева по уровням", "difficulty": "Medium", "week": 8,
        "pattern": "tree-bfs", "pattern_ru": "BFS с очередью",
        "leetcode_url": "https://leetcode.com/problems/binary-tree-level-order-traversal/",
        "statement_ru": d("""\
            Верните значения узлов двоичного дерева по уровням: список уровней сверху вниз,
            внутри уровня — слева направо."""),
        "examples": [
            {"input": "root = [3,9,20,null,null,15,7]", "output": "[[3],[9,20],[15,7]]", "explain_ru": ""},
            {"input": "root = [1]", "output": "[[1]]", "explain_ru": ""},
            {"input": "root = []", "output": "[]", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 2000"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:\n        pass\n",
        "method": "levelOrder", "arg_types": ["TreeNode"], "ret_type": "list[list[int]]",
        "hints_ru": [
            "Нужно выдавать узлы уровень за уровнем: сначала все узлы глубины 0, потом 1. В каком порядке их обрабатывать: «первым пришёл — первым ушёл» или наоборот?",
            "BFS с очередью `collections.deque`: `popleft` за O(1). Чтобы отделить уровни, в начале шага запомните `len(q)`: в этот момент в очереди лежит ровно один уровень.",
            "1) `q = deque([root])`, если корень есть. 2) Пока `q`: `level = []`; повторите `len(q)` раз: `popleft`, значение в `level`, непустых детей — в очередь. 3) `out.append(level)`. Пустое дерево — `[]`.",
        ],
        "brute": _levels_brute,
        "ref": d("""\
            class Solution:
                def levelOrder(self, root):
                    out = []
                    q = deque([root] if root else [])
                    while q:
                        level = []
                        for _ in range(len(q)):
                            node = q.popleft()
                            level.append(node.val)
                            if node.left:
                                q.append(node.left)
                            if node.right:
                                q.append(node.right)
                        out.append(level)
                    return out
            """),
        "cases": [[[3, 9, 20, None, None, 15, 7]], [[1]], [[]], [[1, 2, 3, 4, None, None, 5]], [[1, None, 2, None, 3]], [[1, 2, 3, 4, 5, 6, 7]]],
        "rand": lambda rng: [rand_tree(rng, 12)],
    },
    {
        "id": 98, "slug": "validate-binary-search-tree", "title_en": "Validate Binary Search Tree",
        "title_ru": "Проверить дерево поиска", "difficulty": "Medium", "week": 8,
        "pattern": "bst-bounds", "pattern_ru": "BST: границы / симметричный обход",
        "leetcode_url": "https://leetcode.com/problems/validate-binary-search-tree/",
        "statement_ru": d("""\
            Верните `True`, если двоичное дерево — корректное дерево поиска (BST):
            все значения в левом поддереве узла **строго меньше** значения узла,
            все значения в правом — **строго больше**, и оба поддерева — тоже BST."""),
        "examples": [
            {"input": "root = [2,1,3]", "output": "true", "explain_ru": ""},
            {"input": "root = [5,1,4,null,null,3,6]", "output": "false", "explain_ru": "4 стоит справа от 5, но 4 < 5."},
            {"input": "root = [5,4,6,null,null,3,7]", "output": "false", "explain_ru": "3 в правом поддереве 5. Соседи 6 и 3 в порядке, а дерево — нет."},
        ],
        "constraints_ru": ["1 ≤ число узлов ≤ 10^4", "-2^31 ≤ Node.val ≤ 2^31 − 1"],
        "complexity_target": "O(n) по времени",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def isValidBST(self, root: Optional[TreeNode]) -> bool:\n        pass\n",
        "method": "isValidBST", "arg_types": ["TreeNode"], "ret_type": "bool",
        "hints_ru": [
            "Посмотрите на третий пример: у каждого узла левый ребёнок меньше, правый больше, но ответ `False`. Какое правило нарушено?",
            "Ограничения задают все предки, а не только родитель. Передавайте вниз интервал `(low, high)`: левый ребёнок получает `high = node.val`, правый — `low = node.val`. Корень — в `(-inf, inf)`. Другой путь: симметричный обход BST даёт строго возрастающую последовательность.",
            "1) `check(node, low, high)`: `None` — `True`. 2) Если не `low < node.val < high` — `False`. 3) Верните `check(left, low, node.val) and check(right, node.val, high)`. Неравенства строгие: два равных значения — не BST.",
        ],
        "brute": _is_bst_brute,
        "ref": d("""\
            class Solution:
                def isValidBST(self, root):
                    def check(node, low, high):
                        if node is None:
                            return True
                        if not (low < node.val < high):
                            return False
                        return check(node.left, low, node.val) and check(node.right, node.val, high)
                    return check(root, float("-inf"), float("inf"))
            """),
        "cases": [[[2, 1, 3]], [[5, 1, 4, None, None, 3, 6]], [[5, 4, 6, None, None, 3, 7]], [[1]], [[1, 1]], [[2, 2, 2]], [[2147483647]],
                  [[-2147483648, None, 2147483647]], [[3, 1, 5, 0, 2, 4, 6]], [[10, 5, 15, None, None, 6, 20]]],
        "rand": _maybe_bst,
    },
    {
        "id": 215, "slug": "kth-largest-element-in-an-array", "title_en": "Kth Largest Element in an Array",
        "title_ru": "k-й по величине", "difficulty": "Medium", "week": 8,
        "pattern": "heap", "pattern_ru": "куча размера k",
        "leetcode_url": "https://leetcode.com/problems/kth-largest-element-in-an-array/",
        "statement_ru": d("""\
            Дан список `nums` и число `k`. Верните `k`-й по величине элемент: тот, что стоит
            на месте `k` в списке, отсортированном по убыванию (повторы считаются).
            Попробуйте решить без полной сортировки."""),
        "examples": [
            {"input": "nums = [3,2,1,5,6,4], k = 2", "output": "5", "explain_ru": "По убыванию: 6, 5, …"},
            {"input": "nums = [3,2,3,1,2,4,5,5,6], k = 4", "output": "4", "explain_ru": "6, 5, 5, 4 — повторы считаются."},
        ],
        "constraints_ru": ["1 ≤ k ≤ len(nums) ≤ 10^5", "-10^4 ≤ nums[i] ≤ 10^4"],
        "complexity_target": "O(n log k) кучей (или O(n) в среднем — quickselect)",
        "starter_code": "class Solution:\n    def findKthLargest(self, nums: List[int], k: int) -> int:\n        pass\n",
        "method": "findKthLargest", "arg_types": ["list[int]", "int"], "ret_type": "int",
        "hints_ru": [
            "`sorted(nums)[-k]` работает за O(n log n). Нужны ли для ответа все элементы в порядке? Сколько самых больших элементов достаточно помнить?",
            "Min-куча размера `k`: в ней `k` самых больших элементов из просмотренных. Её минимум `h[0]` — k-й по величине. Каждый новый элемент больше минимума вытесняет его. Итого O(n log k).",
            "1) `h = nums[:k]`; `heapq.heapify(h)`. 2) Для `x` в `nums[k:]`: если `x > h[0]` — `heapq.heapreplace(h, x)`. 3) Верните `h[0]`. Повторы считаются: `[3,3,3]`, k = 2 → 3.",
        ],
        "brute": lambda nums, k: sorted(nums, reverse=True)[k - 1],
        "ref": d("""\
            class Solution:
                def findKthLargest(self, nums, k):
                    h = nums[:k]
                    heapq.heapify(h)
                    for x in nums[k:]:
                        if x > h[0]:
                            heapq.heapreplace(h, x)
                    return h[0]
            """),
        "naive": d("""\
            class Solution:
                def findKthLargest(self, nums, k):
                    nums = list(nums)
                    for _ in range(k - 1):
                        nums.remove(max(nums))
                    return max(nums)
            """),
        "cases": [[[3, 2, 1, 5, 6, 4], 2], [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], [[1], 1], [[2, 1], 2], [[2, 1], 1], [[5, 5, 5], 2], [[-1, -2, -3], 3], [[7, 6, 5, 4, 3, 2, 1], 5]],
        "rand": lambda rng: (lambda nums: [nums, rng.randint(1, len(nums))])(rand_ints(rng, 1, 10, -5, 5)),
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(215)
                nums = [rng.randint(-10**4, 10**4) for _ in range(10**5)]
                return [nums, 5 * 10**4]
            """)],
    },
    {
        "id": 230, "slug": "kth-smallest-element-in-a-bst", "title_en": "Kth Smallest Element in a BST",
        "title_ru": "k-й наименьший в дереве поиска", "difficulty": "Medium", "week": 8,
        "pattern": "bst-inorder", "pattern_ru": "BST: симметричный обход со стеком",
        "leetcode_url": "https://leetcode.com/problems/kth-smallest-element-in-a-bst/",
        "statement_ru": d("""\
            Дан корень дерева поиска (BST) и число `k`. Верните `k`-е по возрастанию
            значение в дереве (нумерация с 1)."""),
        "examples": [
            {"input": "root = [3,1,4,null,2], k = 1", "output": "1", "explain_ru": ""},
            {"input": "root = [5,3,6,2,4,null,null,1], k = 3", "output": "3", "explain_ru": "По возрастанию: 1, 2, 3, …"},
        ],
        "constraints_ru": ["1 ≤ k ≤ n ≤ 10^4", "Дерево — корректный BST"],
        "complexity_target": "O(h + k) по времени, h — высота дерева",
        "starter_code": TREE_NODE_DOC + "class Solution:\n    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:\n        pass\n",
        "method": "kthSmallest", "arg_types": ["TreeNode", "int"], "ret_type": "int",
        "hints_ru": [
            "В каком порядке обход «левое поддерево → узел → правое поддерево» выдаёт значения дерева поиска?",
            "Симметричный обход BST выдаёт значения по возрастанию. Значит, k-й выданный узел — ответ, и весь обход не нужен. Стек заменяет рекурсию и позволяет остановиться сразу.",
            "1) `stack = []`, `node = root`. 2) Идите влево до упора, кладя узлы в стек. 3) `node = stack.pop()` — очередное значение; `k -= 1`; `k == 0` — верните `node.val`. 4) `node = node.right`, повторите с шага 2.",
        ],
        "brute": lambda level, k: sorted(tree_values_inorder(level))[k - 1],
        "ref": d("""\
            class Solution:
                def kthSmallest(self, root, k):
                    stack = []
                    node = root
                    while True:
                        while node:
                            stack.append(node)
                            node = node.left
                        node = stack.pop()
                        k -= 1
                        if k == 0:
                            return node.val
                        node = node.right
            """),
        "cases": [[[3, 1, 4, None, 2], 1], [[5, 3, 6, 2, 4, None, None, 1], 3], [[1], 1], [[2, 1], 2], [[2, None, 3], 2], [[5, 3, 6, 2, 4, None, None, 1], 6], [[4, 2, 6, 1, 3, 5, 7], 4]],
        "rand": _kth_smallest_rand,
    },
    {
        "id": 1046, "slug": "last-stone-weight", "title_en": "Last Stone Weight",
        "title_ru": "Вес последнего камня", "difficulty": "Easy", "week": 8,
        "pattern": "heap", "pattern_ru": "max-куча через отрицательные числа",
        "leetcode_url": "https://leetcode.com/problems/last-stone-weight/",
        "statement_ru": d("""\
            Есть камни с весами `stones`. Каждый ход берём два самых тяжёлых камня `y ≥ x`
            и сталкиваем: если `x == y`, оба исчезают; иначе остаётся камень весом `y - x`.
            Повторяем, пока камней больше одного. Верните вес последнего камня или `0`, если камней нет."""),
        "examples": [
            {"input": "stones = [2,7,4,1,8,1]", "output": "1", "explain_ru": "8 и 7 → 1; 4 и 2 → 2; 2 и 1 → 1; 1 и 1 → 0; остался 1."},
            {"input": "stones = [1]", "output": "1", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(stones) ≤ 30", "1 ≤ stones[i] ≤ 1000"],
        "complexity_target": "O(n log n) по времени",
        "starter_code": "class Solution:\n    def lastStoneWeight(self, stones: List[int]) -> int:\n        pass\n",
        "method": "lastStoneWeight", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Каждый ход нужно взять два самых тяжёлых камня и иногда вернуть новый. Что будет со временем, если каждый раз искать максимум перебором или сортировать заново?",
            "Куча берёт максимум и добавляет элемент за O(log n). `heapq` в Python — только min-куча. Max-куча получается, если хранить вес со знаком минус.",
            "1) `h = [-s for s in stones]`; `heapq.heapify(h)`. 2) Пока `len(h) > 1`: `y = -heappop(h)`, `x = -heappop(h)`. 3) Если `y != x` — `heappush(h, -(y - x))`. 4) Верните `-h[0]`, если куча не пуста, иначе 0.",
        ],
        "brute": _stones_brute,
        "ref": d("""\
            class Solution:
                def lastStoneWeight(self, stones):
                    h = [-s for s in stones]
                    heapq.heapify(h)
                    while len(h) > 1:
                        y, x = -heapq.heappop(h), -heapq.heappop(h)
                        if y != x:
                            heapq.heappush(h, -(y - x))
                    return -h[0] if h else 0
            """),
        "cases": [[[2, 7, 4, 1, 8, 1]], [[1]], [[2, 2]], [[3, 7]], [[1, 1, 1]], [[10, 4, 2, 10]], [[1000] * 30]],
        "rand": lambda rng: [rand_ints(rng, 1, 8, 1, 12)],
    },
]


def _mirror(node):
    if node:
        node.left, node.right = _mirror(node.right), _mirror(node.left)
    return node
