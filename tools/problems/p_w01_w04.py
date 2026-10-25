"""Weeks 1–4: hash map/set, two pointers, stack, binary search, DP intro, linked list, sliding window."""

import itertools
from collections import Counter
from textwrap import dedent as d

from .common import rand_ints, rand_word

LIST_NODE_DOC = """# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
"""


def _two_sum_rand(rng):
    while True:
        nums = rand_ints(rng, 2, 9, -20, 20)
        pairs = [(i, j) for i in range(len(nums)) for j in range(i + 1, len(nums))]
        target = sum(nums[k] for k in rng.choice(pairs))
        if sum(nums[i] + nums[j] == target for i, j in pairs) == 1:
            return [nums, target]


def _two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]


def _two_sum_ii_rand(rng):
    while True:
        nums = sorted(rand_ints(rng, 2, 10, -15, 15))
        pairs = [(i, j) for i in range(len(nums)) for j in range(i + 1, len(nums))]
        target = sum(nums[k] for k in rng.choice(pairs))
        if sum(nums[i] + nums[j] == target for i, j in pairs) == 1:
            return [nums, target]


def _two_sum_ii_brute(numbers, target):
    i, j = _two_sum_brute(numbers, target)
    return [i + 1, j + 1]


def _merge_rand(rng):
    a = sorted(rand_ints(rng, 0, 6, -9, 9))
    b = sorted(rand_ints(rng, 0, 6, -9, 9))
    return [a + [0] * len(b), len(a), b, len(b)]


def _majority_rand(rng):
    n = rng.randint(1, 11)
    major = rng.randint(-5, 5)
    k = n // 2 + 1
    rest = [rng.randint(-5, 5) for _ in range(n - k)]
    nums = [major] * k + rest
    rng.shuffle(nums)
    return [nums]


def _parens_brute(s):
    prev = None
    while prev != s:
        prev = s
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""


def _climb_brute(n):
    # Number of compositions of n into 1s and 2s: sum over k twos of C(n - k, k).
    from math import comb

    return sum(comb(n - k, k) for k in range(n // 2 + 1))


def _longest_unique_brute(s):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i : j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best


def _subseq_brute(s, t):
    subs = set()
    for r in range(len(t) + 1):
        for comb_idx in itertools.combinations(range(len(t)), r):
            subs.add("".join(t[i] for i in comb_idx))
    return s in subs


def _iso_brute(s, t):
    return [s.index(c) for c in s] == [t.index(c) for c in t]


PROBLEMS = [
    # ---------------------------------------------------------------- Week 1
    {
        "id": 217, "slug": "contains-duplicate", "title_en": "Contains Duplicate",
        "title_ru": "Есть ли повтор", "difficulty": "Easy", "week": 1,
        "pattern": "hash-set", "pattern_ru": "хэш-множество",
        "leetcode_url": "https://leetcode.com/problems/contains-duplicate/",
        "statement_ru": d("""\
            Дан список целых чисел `nums`. Верните `True`, если хотя бы одно число
            встречается в списке два раза или больше. Если все числа разные, верните `False`."""),
        "examples": [
            {"input": "nums = [1,2,3,1]", "output": "true", "explain_ru": "Число 1 стоит на позициях 0 и 3."},
            {"input": "nums = [1,2,3,4]", "output": "false", "explain_ru": "Все числа разные."},
            {"input": "nums = [1,1,1,3,3,4,3,2,4,2]", "output": "true", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^5", "-10^9 ≤ nums[i] ≤ 10^9"],
        "complexity_target": "O(n) по времени, O(n) по памяти",
        "starter_code": "class Solution:\n    def containsDuplicate(self, nums: List[int]) -> bool:\n        pass\n",
        "method": "containsDuplicate", "arg_types": ["list[int]"], "ret_type": "bool",
        "hints_ru": [
            "Что быстрее: каждый раз искать число среди всех прошлых или помнить прошлые числа так, чтобы проверка шла за один шаг?",
            "Храните просмотренные числа в `set`. Проверка `x in seen` стоит O(1) в среднем. Инвариант: в `seen` лежат все числа левее текущего.",
            "1) `seen = set()`. 2) Для каждого `x`: если `x in seen` — верните `True`. 3) Иначе `seen.add(x)`. 4) После цикла верните `False`. Список из одного числа — `False`.",
        ],
        "brute": lambda nums: any(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums))),
        "ref": d("""\
            class Solution:
                def containsDuplicate(self, nums):
                    seen = set()
                    for x in nums:
                        if x in seen:
                            return True
                        seen.add(x)
                    return False
            """),
        "naive": d("""\
            class Solution:
                def containsDuplicate(self, nums):
                    for i in range(len(nums)):
                        for j in range(i + 1, len(nums)):
                            if nums[i] == nums[j]:
                                return True
                    return False
            """),
        "cases": [[[1, 2, 3, 1]], [[1, 2, 3, 4]], [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], [[5]], [[7, 7]],
                  [[-1, 1]], [[0, -0]], [[10**9, -10**9, 10**9]], [[3, 1, 4, 1]], [[1, 2]]],
        "rand": lambda rng: [rand_ints(rng, 1, 9, -6, 6)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(217)
                nums = rng.sample(range(-10**9, 10**9), 10**5)
                return [nums]
            """)],
    },
    {
        "id": 242, "slug": "valid-anagram", "title_en": "Valid Anagram",
        "title_ru": "Анаграмма", "difficulty": "Easy", "week": 1,
        "pattern": "hash-map-count", "pattern_ru": "подсчёт в словаре",
        "leetcode_url": "https://leetcode.com/problems/valid-anagram/",
        "statement_ru": d("""\
            Даны две строки `s` и `t` из маленьких латинских букв. Верните `True`, если `t` —
            анаграмма `s`: в `t` те же буквы, что в `s`, в том же количестве, но, может быть,
            в другом порядке. Иначе верните `False`."""),
        "examples": [
            {"input": 's = "anagram", t = "nagaram"', "output": "true", "explain_ru": "Обе строки: a×3, n, g, r, m."},
            {"input": 's = "rat", t = "car"', "output": "false", "explain_ru": "В t нет буквы t, зато есть c."},
        ],
        "constraints_ru": ["1 ≤ len(s), len(t) ≤ 5·10^4", "s и t — только маленькие латинские буквы"],
        "complexity_target": "O(n) по времени, O(1) по памяти (26 букв)",
        "starter_code": "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        pass\n",
        "method": "isAnagram", "arg_types": ["str", "str"], "ret_type": "bool",
        "hints_ru": [
            "Порядок букв в анаграмме не важен. Какая характеристика строки остаётся та же после любой перестановки букв?",
            "Сравните количество каждой буквы. Словарь «буква → счётчик» строится за один проход, O(n). Сортировка тоже даёт ответ, но за O(n log n).",
            "1) Длины разные — `False`. 2) Один словарь: для буквы `s` прибавьте 1, для буквы `t` вычтите 1. 3) Верните `True`, если все значения равны 0.",
        ],
        "brute": lambda s, t: sorted(s) == sorted(t),
        "ref": d("""\
            class Solution:
                def isAnagram(self, s, t):
                    if len(s) != len(t):
                        return False
                    count = {}
                    for a, b in zip(s, t):
                        count[a] = count.get(a, 0) + 1
                        count[b] = count.get(b, 0) - 1
                    return all(v == 0 for v in count.values())
            """),
        "naive": d("""\
            class Solution:
                def isAnagram(self, s, t):
                    rest = list(t)
                    for ch in s:
                        if ch not in rest:
                            return False
                        rest.remove(ch)
                    return not rest
            """),
        "cases": [["anagram", "nagaram"], ["rat", "car"], ["a", "a"], ["a", "b"], ["ab", "a"], ["aacc", "ccac"],
                  ["listen", "silent"], ["aa", "bb"], ["abc", "cba"], ["abcd", "abce"]],
        "rand": lambda rng: [rand_word(rng, 1, 7), rand_word(rng, 1, 7)] if rng.random() < 0.5
        else (lambda w: [w, "".join(rng.sample(w, len(w)))])(rand_word(rng, 1, 7)),
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(242)
                s = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10**5))
                t = list(s)
                rng.shuffle(t)
                t = "".join(t)
                return [s, t]
            """)],
    },
    {
        "id": 1, "slug": "two-sum", "title_en": "Two Sum",
        "title_ru": "Сумма двух", "difficulty": "Easy", "week": 1,
        "pattern": "hash-map", "pattern_ru": "хэш-словарь: «что я ищу?»",
        "leetcode_url": "https://leetcode.com/problems/two-sum/",
        "statement_ru": d("""\
            Дан список целых чисел `nums` и число `target`. Найдите два **разных индекса** `i` и `j`,
            для которых `nums[i] + nums[j] == target`, и верните их списком `[i, j]`.
            Гарантия: подходящая пара ровно одна. Один элемент нельзя взять дважды.
            Порядок индексов в ответе не важен."""),
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explain_ru": "2 + 7 = 9."},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explain_ru": "2 + 4 = 6. Пара [0,0] не подходит: индекс один."},
            {"input": "nums = [3,3], target = 6", "output": "[0,1]", "explain_ru": ""},
        ],
        "constraints_ru": ["2 ≤ len(nums) ≤ 10^4", "-10^9 ≤ nums[i], target ≤ 10^9", "Ответ существует и единственный"],
        "complexity_target": "O(n) по времени, O(n) по памяти",
        "starter_code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass\n",
        "method": "twoSum", "arg_types": ["list[int]", "int"], "ret_type": "list[int]", "compare": "unordered",
        "hints_ru": [
            "Вы стоите на числе `x`. Какое конкретное число должно было встретиться раньше, чтобы пара сложилась в `target`?",
            "Ищите партнёра `target - x` в словаре «число → индекс» для уже пройденных чисел. Поиск в словаре — O(1), весь проход — O(n).",
            "1) `seen = {}`. 2) Для `i, x`: если `target - x in seen` — верните `[seen[target - x], i]`. 3) Только потом запишите `seen[x] = i`. Порядок шагов 2 и 3 защищает от пары элемента с самим собой (случай `[3,3]`, target 6).",
        ],
        "brute": _two_sum_brute,
        "ref": d("""\
            class Solution:
                def twoSum(self, nums, target):
                    seen = {}
                    for i, x in enumerate(nums):
                        if target - x in seen:
                            return [seen[target - x], i]
                        seen[x] = i
            """),
        "naive": d("""\
            class Solution:
                def twoSum(self, nums, target):
                    for i in range(len(nums)):
                        for j in range(i + 1, len(nums)):
                            if nums[i] + nums[j] == target:
                                return [i, j]
            """),
        "cases": [[[2, 7, 11, 15], 9], [[3, 2, 4], 6], [[3, 3], 6], [[1, 2], 3], [[-3, 4, 3, 90], 0],
                  [[0, 4, 3, 0], 0], [[-1, -2, -3, -4, -5], -8], [[5, 75, 25], 100], [[10**9, -10**9], 0],
                  [[1, 5, 2, 9], 10]],
        "rand": _two_sum_rand,
        "perf": [d("""\
            def gen():
                n = 10**4
                nums = list(range(1, 2 * n, 2))   # odd numbers: pair sums are even
                target = nums[-1] + nums[-2]      # the only pair is at the very end
                return [nums, target]
            """)],
    },
    {
        "id": 121, "slug": "best-time-to-buy-and-sell-stock", "title_en": "Best Time to Buy and Sell Stock",
        "title_ru": "Купить и продать акцию", "difficulty": "Easy", "week": 1,
        "pattern": "running-min", "pattern_ru": "один проход, текущий минимум",
        "leetcode_url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
        "statement_ru": d("""\
            `prices[i]` — цена акции в день `i`. Вы можете один раз купить акцию и позже,
            в другой день, один раз продать. Верните максимальную прибыль.
            Если прибыль получить нельзя, верните `0`."""),
        "examples": [
            {"input": "prices = [7,1,5,3,6,4]", "output": "5", "explain_ru": "Купить в день 1 (цена 1), продать в день 4 (цена 6): 6 − 1 = 5."},
            {"input": "prices = [7,6,4,3,1]", "output": "0", "explain_ru": "Цена только падает. Лучше не покупать."},
        ],
        "constraints_ru": ["1 ≤ len(prices) ≤ 10^5", "0 ≤ prices[i] ≤ 10^4"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def maxProfit(self, prices: List[int]) -> int:\n        pass\n",
        "method": "maxProfit", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Допустим, вы продаёте в день `j`. В какой день до `j` выгоднее всего было купить?",
            "Храните минимум цены среди прошлых дней. Тогда лучшая прибыль при продаже сегодня — `цена − минимум`. Так один проход заменяет перебор всех пар дней.",
            "1) `low = inf`, `best = 0`. 2) Для каждой цены `p`: `best = max(best, p - low)`, затем `low = min(low, p)`. 3) Верните `best`. Цены только падают — ответ 0.",
        ],
        "brute": lambda prices: max([0] + [prices[j] - prices[i] for i in range(len(prices)) for j in range(i + 1, len(prices))]),
        "ref": d("""\
            class Solution:
                def maxProfit(self, prices):
                    low = float("inf")
                    best = 0
                    for p in prices:
                        best = max(best, p - low)
                        low = min(low, p)
                    return best
            """),
        "naive": d("""\
            class Solution:
                def maxProfit(self, prices):
                    best = 0
                    for i in range(len(prices)):
                        for j in range(i + 1, len(prices)):
                            best = max(best, prices[j] - prices[i])
                    return best
            """),
        "cases": [[[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]], [[1]], [[1, 2]], [[2, 1]], [[3, 3, 3]],
                  [[2, 4, 1]], [[3, 2, 6, 5, 0, 3]], [[0, 10000]], [[1, 2, 4, 2, 5, 7, 2, 4, 9, 0]]],
        "rand": lambda rng: [rand_ints(rng, 1, 10, 0, 20)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(121)
                return [[rng.randint(0, 10**4) for _ in range(10**5)]]
            """)],
    },
    {
        "id": 383, "slug": "ransom-note", "title_en": "Ransom Note",
        "title_ru": "Записка из журнала", "difficulty": "Easy", "week": 1, "optional": True,
        "pattern": "hash-map-count", "pattern_ru": "подсчёт в словаре",
        "leetcode_url": "https://leetcode.com/problems/ransom-note/",
        "statement_ru": d("""\
            Даны строки `ransomNote` (записка) и `magazine` (журнал). Записку клеят из букв,
            вырезанных из журнала. Каждую букву журнала можно взять только один раз.
            Верните `True`, если записку можно собрать, иначе `False`."""),
        "examples": [
            {"input": 'ransomNote = "a", magazine = "b"', "output": "false", "explain_ru": ""},
            {"input": 'ransomNote = "aa", magazine = "ab"', "output": "false", "explain_ru": "Нужно две буквы a, а в журнале одна."},
            {"input": 'ransomNote = "aa", magazine = "aab"', "output": "true", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(ransomNote), len(magazine) ≤ 10^5", "Только маленькие латинские буквы"],
        "complexity_target": "O(n + m) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def canConstruct(self, ransomNote: str, magazine: str) -> bool:\n        pass\n",
        "method": "canConstruct", "arg_types": ["str", "str"], "ret_type": "bool",
        "hints_ru": [
            "Порядок букв в записке и журнале не важен. Что тогда решает, хватит ли букв журнала?",
            "Посчитайте буквы журнала: `Counter(magazine)`. Это запас. Каждая буква записки тратит одну единицу запаса; запас не может стать отрицательным.",
            "1) `stock = Counter(magazine)`. 2) Для каждой буквы `ch` записки: `stock[ch] -= 1`. 3) Если `stock[ch] < 0` — верните `False`. 4) После цикла — `True`.",
        ],
        "brute": lambda note, mag: all(note.count(c) <= mag.count(c) for c in set(note)),
        "ref": d("""\
            class Solution:
                def canConstruct(self, ransomNote, magazine):
                    stock = Counter(magazine)
                    for ch in ransomNote:
                        stock[ch] -= 1
                        if stock[ch] < 0:
                            return False
                    return True
            """),
        "naive": d("""\
            class Solution:
                def canConstruct(self, ransomNote, magazine):
                    rest = list(magazine)
                    for ch in ransomNote:
                        if ch not in rest:
                            return False
                        rest.remove(ch)
                    return True
            """),
        "cases": [["a", "b"], ["aa", "ab"], ["aa", "aab"], ["abc", "cba"], ["abc", "ab"], ["z", "z"],
                  ["aab", "baa"], ["bg", "efjbdfbdgfjhhaiigfhbaejahgfbbgbjagbddfgdiaigdadhcfcj"], ["xyz", "xxyy"], ["a", "aaaa"]],
        "rand": lambda rng: [rand_word(rng, 1, 6), rand_word(rng, 1, 9)],
        "perf": [d("""\
            def gen():
                import random
                half = 10**5 // 2
                mag = "a" * half + "b" * half   # every "b" sits behind 50 000 letters "a"
                note = "b" * half
                return [note, mag]
            """)],
    },
    # ---------------------------------------------------------------- Week 2
    {
        "id": 125, "slug": "valid-palindrome", "title_en": "Valid Palindrome",
        "title_ru": "Палиндром", "difficulty": "Easy", "week": 2,
        "pattern": "two-pointers", "pattern_ru": "два указателя",
        "leetcode_url": "https://leetcode.com/problems/valid-palindrome/",
        "statement_ru": d("""\
            Дана строка `s`. Уберите из неё всё, кроме букв и цифр, а заглавные буквы
            сделайте маленькими. Верните `True`, если результат читается одинаково слева
            направо и справа налево. Пустая строка — палиндром."""),
        "examples": [
            {"input": 's = "A man, a plan, a canal: Panama"', "output": "true", "explain_ru": "После очистки: amanaplanacanalpanama."},
            {"input": 's = "race a car"', "output": "false", "explain_ru": "raceacar справа налево — racaecar."},
            {"input": 's = " "', "output": "true", "explain_ru": "После очистки строка пустая."},
        ],
        "constraints_ru": ["1 ≤ len(s) ≤ 2·10^5", "s — печатные символы ASCII"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def isPalindrome(self, s: str) -> bool:\n        pass\n",
        "method": "isPalindrome", "arg_types": ["str"], "ret_type": "bool",
        "hints_ru": [
            "Палиндром сравнивает первый символ с последним, второй — с предпоследним. Нужно ли для этого строить новую строку?",
            "Два указателя: `l` идёт от начала, `r` — от конца. Инвариант: всё левее `l` и правее `r` уже проверено и совпало. Память O(1).",
            "1) `l, r = 0, len(s) - 1`. 2) Пока `l < r`: `s[l]` не `isalnum()` — `l += 1`; `s[r]` не `isalnum()` — `r -= 1`. 3) Иначе сравните `lower()` обоих; разные — `False`; равные — сдвиньте оба. 4) Верните `True`. Строка из одних знаков — `True`.",
        ],
        "brute": lambda s: (lambda c: c == c[::-1])([ch.lower() for ch in s if ch.isalnum()]),
        "ref": d("""\
            class Solution:
                def isPalindrome(self, s):
                    l, r = 0, len(s) - 1
                    while l < r:
                        if not s[l].isalnum():
                            l += 1
                        elif not s[r].isalnum():
                            r -= 1
                        elif s[l].lower() != s[r].lower():
                            return False
                        else:
                            l += 1
                            r -= 1
                    return True
            """),
        "cases": [["A man, a plan, a canal: Panama"], ["race a car"], [" "], ["a"], ["0P"], ["ab_a"], [".,"],
                  ["No 'x' in Nixon"], ["12321"], ["Aa"], ["a."]],
        "rand": lambda rng: [rand_word(rng, 0, 8, "aAb ,1")],
    },
    {
        "id": 167, "slug": "two-sum-ii-input-array-is-sorted", "title_en": "Two Sum II - Input Array Is Sorted",
        "title_ru": "Сумма двух в отсортированном списке", "difficulty": "Medium", "week": 2,
        "pattern": "two-pointers", "pattern_ru": "два указателя",
        "leetcode_url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/",
        "statement_ru": d("""\
            Список `numbers` отсортирован по неубыванию. Найдите два разных элемента с суммой
            `target`. Верните их **номера, начиная с 1**: `[index1, index2]`, где `index1 < index2`.
            Ответ ровно один. Дополнительная память — O(1): словарь из #1 здесь не нужен."""),
        "examples": [
            {"input": "numbers = [2,7,11,15], target = 9", "output": "[1,2]", "explain_ru": "2 + 7 = 9, номера 1 и 2."},
            {"input": "numbers = [2,3,4], target = 6", "output": "[1,3]", "explain_ru": ""},
            {"input": "numbers = [-1,0], target = -1", "output": "[1,2]", "explain_ru": ""},
        ],
        "constraints_ru": ["2 ≤ len(numbers) ≤ 3·10^4", "-1000 ≤ numbers[i] ≤ 1000", "Список отсортирован, ответ единственный"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def twoSum(self, numbers: List[int], target: int) -> List[int]:\n        pass\n",
        "method": "twoSum", "arg_types": ["list[int]", "int"], "ret_type": "list[int]",
        "hints_ru": [
            "Список отсортирован. Возьмите самый маленький и самый большой элементы. Их сумма меньше `target` — может ли самый маленький элемент войти в ответ?",
            "Два указателя с концов. Сумма мала — сдвиньте левый вправо, она вырастет. Сумма велика — сдвиньте правый влево. Инвариант: ответ всегда между `l` и `r`.",
            "1) `l, r = 0, len(numbers) - 1`. 2) Пока `l < r`: `s = numbers[l] + numbers[r]`. 3) `s == target` — верните `[l + 1, r + 1]`; `s < target` — `l += 1`; иначе `r -= 1`. Номера начинаются с 1.",
        ],
        "brute": _two_sum_ii_brute,
        "ref": d("""\
            class Solution:
                def twoSum(self, numbers, target):
                    l, r = 0, len(numbers) - 1
                    while l < r:
                        s = numbers[l] + numbers[r]
                        if s == target:
                            return [l + 1, r + 1]
                        if s < target:
                            l += 1
                        else:
                            r -= 1
            """),
        "naive": d("""\
            class Solution:
                def twoSum(self, numbers, target):
                    for i in range(len(numbers)):
                        for j in range(i + 1, len(numbers)):
                            if numbers[i] + numbers[j] == target:
                                return [i + 1, j + 1]
            """),
        "cases": [[[2, 7, 11, 15], 9], [[2, 3, 4], 6], [[-1, 0], -1], [[1, 2], 3], [[0, 0, 3, 4], 0],
                  [[-5, -3, 0, 2, 9], 6], [[1, 3, 5, 7, 9], 16], [[-1000, 1000], 0], [[1, 1, 2, 5], 7]],
        "rand": _two_sum_ii_rand,
        "perf": [d("""\
            def gen():
                n = 3 * 10**4
                nums = [2 * i for i in range(n)]     # even numbers
                return [nums, nums[-1] + nums[-2]]   # the pair is at the very end
            """)],
    },
    {
        "id": 88, "slug": "merge-sorted-array", "title_en": "Merge Sorted Array",
        "title_ru": "Слить два отсортированных списка", "difficulty": "Easy", "week": 2,
        "pattern": "two-pointers-from-end", "pattern_ru": "два указателя с конца",
        "leetcode_url": "https://leetcode.com/problems/merge-sorted-array/",
        "statement_ru": d("""\
            Даны два отсортированных списка. В `nums1` длина `m + n`: первые `m` элементов —
            данные, последние `n` — нули-заглушки. В `nums2` — `n` элементов.
            Слейте `nums2` в `nums1` **на месте**, чтобы `nums1` стал отсортированным.
            Функция ничего не возвращает: проверяется содержимое `nums1` после вызова."""),
        "examples": [
            {"input": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "output": "[1,2,2,3,5,6]", "explain_ru": ""},
            {"input": "nums1 = [1], m = 1, nums2 = [], n = 0", "output": "[1]", "explain_ru": ""},
            {"input": "nums1 = [0], m = 0, nums2 = [1], n = 1", "output": "[1]", "explain_ru": "Данных в nums1 нет, ноль — заглушка."},
        ],
        "constraints_ru": ["len(nums1) = m + n, len(nums2) = n", "0 ≤ m, n ≤ 200", "-10^9 ≤ nums1[i], nums2[j] ≤ 10^9"],
        "complexity_target": "O(m + n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:\n        \"\"\"\n        Do not return anything, modify nums1 in-place instead.\n        \"\"\"\n        pass\n",
        "method": "merge", "arg_types": ["list[int]", "int", "list[int]", "int"], "ret_type": "None", "inplace": 0,
        "hints_ru": [
            "Если писать в `nums1` с начала, вы затрёте ещё не обработанные числа. В какой части `nums1` место свободно?",
            "Заполняйте `nums1` с конца: на позицию `k` ставьте больший из последних необработанных элементов. Инвариант: справа от `k` лежат самые большие числа в правильном порядке.",
            "1) `i, j, k = m - 1, n - 1, m + n - 1`. 2) Пока `j >= 0`: если `i >= 0` и `nums1[i] > nums2[j]` — `nums1[k] = nums1[i]`, `i -= 1`; иначе `nums1[k] = nums2[j]`, `j -= 1`. 3) `k -= 1`. Остаток `nums1` уже на месте. Случай `m = 0` тоже работает.",
        ],
        "brute": lambda nums1, m, nums2, n: sorted(nums1[:m] + nums2),
        "ref": d("""\
            class Solution:
                def merge(self, nums1, m, nums2, n):
                    i, j, k = m - 1, n - 1, m + n - 1
                    while j >= 0:
                        if i >= 0 and nums1[i] > nums2[j]:
                            nums1[k] = nums1[i]
                            i -= 1
                        else:
                            nums1[k] = nums2[j]
                            j -= 1
                        k -= 1
            """),
        "cases": [[[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3], [[1], 1, [], 0], [[0], 0, [1], 1], [[4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3],
                  [[1, 2, 3, 0, 0, 0], 3, [4, 5, 6], 3], [[2, 0], 1, [1], 1], [[-1, 0, 0, 3, 3, 3, 0, 0, 0], 6, [1, 2, 2], 3],
                  [[0, 0, 0], 0, [-3, -2, -1], 3], [[1, 1, 0, 0], 2, [1, 1], 2]],
        "rand": _merge_rand,
    },
    {
        "id": 283, "slug": "move-zeroes", "title_en": "Move Zeroes",
        "title_ru": "Нули в конец", "difficulty": "Easy", "week": 2,
        "pattern": "two-pointers", "pattern_ru": "два указателя: чтение и запись",
        "leetcode_url": "https://leetcode.com/problems/move-zeroes/",
        "statement_ru": d("""\
            Перенесите все нули списка `nums` в конец. Порядок ненулевых элементов
            сохраните. Делайте **на месте**, без копии списка. Функция ничего не возвращает."""),
        "examples": [
            {"input": "nums = [0,1,0,3,12]", "output": "[1,3,12,0,0]", "explain_ru": ""},
            {"input": "nums = [0]", "output": "[0]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^4", "-2^31 ≤ nums[i] ≤ 2^31 − 1"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def moveZeroes(self, nums: List[int]) -> None:\n        \"\"\"\n        Do not return anything, modify nums in-place instead.\n        \"\"\"\n        pass\n",
        "method": "moveZeroes", "arg_types": ["list[int]"], "ret_type": "None", "inplace": 0,
        "hints_ru": [
            "Каждое удаление из середины списка сдвигает хвост. Можно ли просто переписать ненулевые числа подряд в начало?",
            "Два указателя: `read` проходит все элементы, `write` — место для следующего ненулевого. Инвариант: `nums[:write]` — ненулевые числа в исходном порядке.",
            "1) `write = 0`. 2) Для каждого `read`: если `nums[read] != 0` — обменяйте `nums[write]` и `nums[read]`, затем `write += 1`. 3) Ничего не возвращайте. Список без нулей и список из нулей не меняются.",
        ],
        "brute": lambda nums: [x for x in nums if x != 0] + [0] * nums.count(0),
        "ref": d("""\
            class Solution:
                def moveZeroes(self, nums):
                    write = 0
                    for read in range(len(nums)):
                        if nums[read] != 0:
                            nums[write], nums[read] = nums[read], nums[write]
                            write += 1
            """),
        "cases": [[[0, 1, 0, 3, 12]], [[0]], [[1]], [[1, 0]], [[0, 0, 1]], [[1, 2, 3]], [[0, 0, 0]],
                  [[4, 0, -2, 0, 0, 7]], [[-1, 0, 2**31 - 1, 0, -2**31]]],
        "rand": lambda rng: [[rng.choice([0, 0, rng.randint(-5, 5)]) for _ in range(rng.randint(1, 9))]],
    },
    {
        "id": 169, "slug": "majority-element", "title_en": "Majority Element",
        "title_ru": "Элемент большинства", "difficulty": "Easy", "week": 2,
        "pattern": "boyer-moore", "pattern_ru": "голосование Бойера — Мура",
        "leetcode_url": "https://leetcode.com/problems/majority-element/",
        "statement_ru": d("""\
            В списке `nums` длины `n` одно число встречается больше `n / 2` раз.
            Найдите и верните это число. Такое число всегда есть."""),
        "examples": [
            {"input": "nums = [3,2,3]", "output": "3", "explain_ru": ""},
            {"input": "nums = [2,2,1,1,1,2,2]", "output": "2", "explain_ru": "2 встречается 4 раза из 7."},
        ],
        "constraints_ru": ["1 ≤ n ≤ 5·10^4", "-10^9 ≤ nums[i] ≤ 10^9"],
        "complexity_target": "O(n) по времени. Бонус: O(1) по памяти",
        "starter_code": "class Solution:\n    def majorityElement(self, nums: List[int]) -> int:\n        pass\n",
        "method": "majorityElement", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Число большинства встречается больше половины раз. Что останется, если вычёркивать пары из двух разных чисел?",
            "Голосование Бойера — Мура: храните кандидата и счётчик. «Свой» голос увеличивает счётчик, «чужой» гасит один голос. Большинство нельзя погасить полностью, поэтому в конце кандидат — ответ. Память O(1).",
            "1) `candidate, count = None, 0`. 2) Для каждого `x`: если `count == 0` — `candidate = x`. 3) `count += 1`, если `x == candidate`, иначе `count -= 1`. 4) Верните `candidate`.",
        ],
        "brute": lambda nums: next(x for x in nums if nums.count(x) * 2 > len(nums)),
        "ref": d("""\
            class Solution:
                def majorityElement(self, nums):
                    candidate, count = None, 0
                    for x in nums:
                        if count == 0:
                            candidate = x
                        count += 1 if x == candidate else -1
                    return candidate
            """),
        "naive": d("""\
            class Solution:
                def majorityElement(self, nums):
                    for x in nums:
                        c = 0
                        for y in nums:
                            if y == x:
                                c += 1
                        if c * 2 > len(nums):
                            return x
            """),
        "cases": [[[3, 2, 3]], [[2, 2, 1, 1, 1, 2, 2]], [[1]], [[5, 5]], [[-1, -1, 2]], [[1, 2, 1, 2, 1]],
                  [[6, 5, 5]], [[10**9, -10**9, 10**9]], [[4, 4, 4, 4, 1, 2, 3]]],
        "rand": _majority_rand,
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(169)
                n = 5 * 10**4
                nums = [7] * (n // 2 + 1) + [rng.randint(-10**9, 10**9) for _ in range(n - n // 2 - 1)]
                rng.shuffle(nums)
                nums.sort(key=lambda x: x == 7)   # majority at the end: slow for the naive scan
                return [nums]
            """)],
    },
    # ---------------------------------------------------------------- Week 3
    {
        "id": 20, "slug": "valid-parentheses", "title_en": "Valid Parentheses",
        "title_ru": "Правильные скобки", "difficulty": "Easy", "week": 3,
        "pattern": "stack", "pattern_ru": "стек",
        "leetcode_url": "https://leetcode.com/problems/valid-parentheses/",
        "statement_ru": d("""\
            Строка `s` состоит только из символов `()[]{}`. Верните `True`, если скобки
            расставлены правильно: каждая открытая скобка закрыта скобкой того же типа,
            и скобки закрываются в правильном порядке."""),
        "examples": [
            {"input": 's = "()[]{}"', "output": "true", "explain_ru": ""},
            {"input": 's = "(]"', "output": "false", "explain_ru": "Круглую скобку закрыла квадратная."},
            {"input": 's = "([)]"', "output": "false", "explain_ru": "Порядок закрытия нарушен."},
        ],
        "constraints_ru": ["1 ≤ len(s) ≤ 10^4"],
        "complexity_target": "O(n) по времени, O(n) по памяти",
        "starter_code": "class Solution:\n    def isValid(self, s: str) -> bool:\n        pass\n",
        "method": "isValid", "arg_types": ["str"], "ret_type": "bool",
        "hints_ru": [
            "Посмотрите на `([)]`. Какая открытая скобка должна закрыться первой, когда приходит закрывающая?",
            "Нужна стопка открытых скобок: «последний вошёл — первый вышел». Это стек; в Python — `list` с `append` и `pop`. Инвариант: в стеке лежат открытые и ещё не закрытые скобки.",
            "1) Словарь пар `{')': '(', ...}`. 2) Открытую скобку кладите в стек. 3) Закрытая: стек пуст или `stack.pop()` не её пара — `False`. 4) В конце верните `not stack`. Строка `\"(\"` — `False`.",
        ],
        "brute": _parens_brute,
        "ref": d("""\
            class Solution:
                def isValid(self, s):
                    pair = {")": "(", "]": "[", "}": "{"}
                    stack = []
                    for ch in s:
                        if ch in pair:
                            if not stack or stack.pop() != pair[ch]:
                                return False
                        else:
                            stack.append(ch)
                    return not stack
            """),
        "cases": [["()[]{}"], ["(]"], ["([)]"], ["()"], ["{[]}"], ["("], [")"], ["(("], ["){"], ["([]{})[]"], ["]["]],
        "rand": lambda rng: [rand_word(rng, 1, 8, "()[]{}") if rng.random() < 0.5 else rng.choice(["()", "[]", "{}"]) * rng.randint(1, 3)],
    },
    {
        "id": 704, "slug": "binary-search", "title_en": "Binary Search",
        "title_ru": "Бинарный поиск", "difficulty": "Easy", "week": 3,
        "pattern": "binary-search", "pattern_ru": "бинарный поиск",
        "leetcode_url": "https://leetcode.com/problems/binary-search/",
        "statement_ru": d("""\
            Список `nums` отсортирован по возрастанию, все числа разные. Найдите индекс
            числа `target`. Если его нет, верните `-1`. Решение должно работать за O(log n):
            не используйте `nums.index` и `in`."""),
        "examples": [
            {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4", "explain_ru": ""},
            {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^4", "Все числа разные, список отсортирован"],
        "complexity_target": "O(log n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        pass\n",
        "method": "search", "arg_types": ["list[int]", "int"], "ret_type": "int",
        "hints_ru": [
            "Список отсортирован. Вы сравнили `target` с одним элементом в середине. Какую часть списка можно больше не смотреть?",
            "Бинарный поиск: храните границы `lo` и `hi` области, где ответ ещё возможен. Каждое сравнение со средним делит область пополам, итого O(log n).",
            "1) `lo, hi = 0, len(nums) - 1`. 2) Пока `lo <= hi`: `mid = (lo + hi) // 2`. 3) Равно — верните `mid`; `nums[mid] < target` — `lo = mid + 1`; иначе `hi = mid - 1`. 4) После цикла — `-1`. Проверьте список из одного элемента.",
        ],
        "brute": lambda nums, target: nums.index(target) if target in nums else -1,
        "ref": d("""\
            class Solution:
                def search(self, nums, target):
                    lo, hi = 0, len(nums) - 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if nums[mid] == target:
                            return mid
                        if nums[mid] < target:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    return -1
            """),
        "cases": [[[-1, 0, 3, 5, 9, 12], 9], [[-1, 0, 3, 5, 9, 12], 2], [[5], 5], [[5], -5], [[1, 3], 3], [[1, 3], 1],
                  [[1, 3], 2], [[-10, -5, 0, 5, 10], -10], [[-10, -5, 0, 5, 10], 10], [[-10, -5, 0, 5, 10], 11]],
        "rand": lambda rng: (lambda nums: [nums, rng.choice(nums + [rng.randint(-30, 30)])])(sorted(rng.sample(range(-30, 30), rng.randint(1, 10)))),
    },
    {
        "id": 70, "slug": "climbing-stairs", "title_en": "Climbing Stairs",
        "title_ru": "Лестница", "difficulty": "Easy", "week": 3,
        "pattern": "dp-1d", "pattern_ru": "динамическое программирование, одна переменная",
        "leetcode_url": "https://leetcode.com/problems/climbing-stairs/",
        "statement_ru": d("""\
            Лестница из `n` ступенек. За один шаг можно подняться на 1 или на 2 ступеньки.
            Сколькими разными способами можно дойти до верха?"""),
        "examples": [
            {"input": "n = 2", "output": "2", "explain_ru": "1+1 и 2."},
            {"input": "n = 3", "output": "3", "explain_ru": "1+1+1, 1+2, 2+1."},
        ],
        "constraints_ru": ["1 ≤ n ≤ 45"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        pass\n",
        "method": "climbStairs", "arg_types": ["int"], "ret_type": "int",
        "hints_ru": [
            "На ступеньку `n` вы пришли последним шагом. С каких ступенек мог быть этот шаг?",
            "Динамическое программирование: `ways(n) = ways(n - 1) + ways(n - 2)`. Прямая рекурсия считает одно и то же много раз, O(2^n). Считайте снизу вверх — каждое значение один раз.",
            "1) `a, b = 1, 1` — способы для ступенек 0 и 1. 2) Повторите `n` раз: `a, b = b, a + b`. 3) Верните `a`. Проверьте: n = 1 → 1, n = 2 → 2, n = 3 → 3.",
        ],
        "brute": _climb_brute,
        "ref": d("""\
            class Solution:
                def climbStairs(self, n):
                    a, b = 1, 1
                    for _ in range(n):
                        a, b = b, a + b
                    return a
            """),
        "naive": d("""\
            class Solution:
                def climbStairs(self, n):
                    if n <= 2:
                        return n
                    return self.climbStairs(n - 1) + self.climbStairs(n - 2)
            """),
        "cases": [[2], [3], [1], [4], [5], [10], [20], [45], [44], [30]],
        "visible": 2,
        "rand": lambda rng: [rng.randint(1, 25)],
        "perf": [d("""\
            def gen():
                return [38]
            """)],
        "perf_note": "Тест n = 45 уже есть в обычных тестах; perf ловит экспоненциальную рекурсию на n = 38.",
    },
    {
        "id": 206, "slug": "reverse-linked-list", "title_en": "Reverse Linked List",
        "title_ru": "Развернуть связный список", "difficulty": "Easy", "week": 3,
        "pattern": "linked-list", "pattern_ru": "связный список: перестановка указателей",
        "leetcode_url": "https://leetcode.com/problems/reverse-linked-list/",
        "statement_ru": d("""\
            Дана голова `head` односвязного списка. Разверните список и верните новую голову.
            В тестах список записан как `[1,2,3]`: это узлы 1 → 2 → 3. Класс `ListNode`
            уже определён."""),
        "examples": [
            {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]", "explain_ru": ""},
            {"input": "head = [1,2]", "output": "[2,1]", "explain_ru": ""},
            {"input": "head = []", "output": "[]", "explain_ru": "Пустой список: head = None."},
        ],
        "constraints_ru": ["0 ≤ число узлов ≤ 5000", "-5000 ≤ Node.val ≤ 5000"],
        "complexity_target": "O(n) по времени, O(1) по памяти (итеративно)",
        "starter_code": LIST_NODE_DOC + "class Solution:\n    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:\n        pass\n",
        "method": "reverseList", "arg_types": ["ListNode"], "ret_type": "ListNode",
        "hints_ru": [
            "Нарисуйте 1 → 2 → 3 на бумаге. Что должно случиться с каждой стрелкой? Что вы потеряете, если сразу перевернёте стрелку узла 1?",
            "Идите по списку и переворачивайте по одной стрелке. Перед этим запомните `cur.next`, иначе остаток списка потеряется. Инвариант: `prev` — голова уже развёрнутой части.",
            "1) `prev, cur = None, head`. 2) Пока `cur`: `nxt = cur.next`; `cur.next = prev`; `prev = cur`; `cur = nxt`. 3) Верните `prev`. Пустой список: цикл не идёт, ответ `None`.",
        ],
        "brute": lambda values: values[::-1],
        "ref": d("""\
            class Solution:
                def reverseList(self, head):
                    prev = None
                    while head:
                        head.next, prev, head = prev, head, head.next
                    return prev
            """),
        "cases": [[[1, 2, 3, 4, 5]], [[1, 2]], [[]], [[7]], [[1, 1, 2]], [[-5000, 0, 5000]], [list(range(300))]],
        "rand": lambda rng: [rand_ints(rng, 0, 10, -9, 9)],
    },
    {
        "id": 21, "slug": "merge-two-sorted-lists", "title_en": "Merge Two Sorted Lists",
        "title_ru": "Слить два отсортированных связных списка", "difficulty": "Easy", "week": 3,
        "pattern": "linked-list", "pattern_ru": "связный список: фиктивная голова",
        "leetcode_url": "https://leetcode.com/problems/merge-two-sorted-lists/",
        "statement_ru": d("""\
            Даны головы `list1` и `list2` двух отсортированных связных списков.
            Слейте их в один отсортированный список из тех же узлов и верните его голову."""),
        "examples": [
            {"input": "list1 = [1,2,4], list2 = [1,3,4]", "output": "[1,1,2,3,4,4]", "explain_ru": ""},
            {"input": "list1 = [], list2 = []", "output": "[]", "explain_ru": ""},
            {"input": "list1 = [], list2 = [0]", "output": "[0]", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ число узлов в каждом списке ≤ 50", "Оба списка отсортированы по неубыванию"],
        "complexity_target": "O(n + m) по времени, O(1) по памяти",
        "starter_code": LIST_NODE_DOC + "class Solution:\n    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:\n        pass\n",
        "method": "mergeTwoLists", "arg_types": ["ListNode", "ListNode"], "ret_type": "ListNode",
        "hints_ru": [
            "Посмотрите на первые узлы двух списков. Какой из них точно будет первым в ответе?",
            "Фиктивная голова: `dummy = ListNode()` и хвост `tail = dummy`. Так первый узел ответа не нужно обрабатывать отдельно. Инвариант: от `dummy.next` до `tail` — уже слитая отсортированная часть.",
            "1) Пока оба списка не пусты: прицепите меньший узел к `tail.next`, сдвиньте его список и `tail`. 2) Прицепите остаток: `tail.next = list1 or list2`. 3) Верните `dummy.next`. Один список пуст — ответ другой список.",
        ],
        "brute": lambda a, b: sorted(a + b),
        "ref": d("""\
            class Solution:
                def mergeTwoLists(self, list1, list2):
                    dummy = tail = ListNode()
                    while list1 and list2:
                        if list1.val <= list2.val:
                            tail.next, list1 = list1, list1.next
                        else:
                            tail.next, list2 = list2, list2.next
                        tail = tail.next
                    tail.next = list1 or list2
                    return dummy.next
            """),
        "cases": [[[1, 2, 4], [1, 3, 4]], [[], []], [[], [0]], [[5], []], [[1, 2, 3], [4, 5, 6]], [[4, 5, 6], [1, 2, 3]],
                  [[-3, 0, 0], [-3, 0]], [[1], [1]], [[2, 2, 2], [1, 3]]],
        "rand": lambda rng: [sorted(rand_ints(rng, 0, 6, -9, 9)), sorted(rand_ints(rng, 0, 6, -9, 9))],
    },
    # ---------------------------------------------------------------- Week 4
    {
        "id": 3, "slug": "longest-substring-without-repeating-characters",
        "title_en": "Longest Substring Without Repeating Characters",
        "title_ru": "Самая длинная подстрока без повторов", "difficulty": "Medium", "week": 4,
        "pattern": "sliding-window", "pattern_ru": "скользящее окно",
        "leetcode_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "statement_ru": d("""\
            Дана строка `s`. Найдите длину самой длинной **подстроки** (идущих подряд символов),
            в которой все символы разные."""),
        "examples": [
            {"input": 's = "abcabcbb"', "output": "3", "explain_ru": "Подстрока abc."},
            {"input": 's = "bbbbb"', "output": "1", "explain_ru": ""},
            {"input": 's = "pwwkew"', "output": "3", "explain_ru": "Подстрока wke. pwke — не подстрока: символы не подряд."},
        ],
        "constraints_ru": ["0 ≤ len(s) ≤ 5·10^4", "s — латинские буквы, цифры, символы и пробелы"],
        "complexity_target": "O(n) по времени",
        "starter_code": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        pass\n",
        "method": "lengthOfLongestSubstring", "arg_types": ["str"], "ret_type": "int",
        "hints_ru": [
            "Пусть вы знаете хороший участок без повторов. Справа пришёл символ, который уже есть на участке. Какую часть участка нужно отрезать слева?",
            "Скользящее окно `s[left:right+1]` без повторов и словарь «символ → последний индекс». При повторе левый край прыгает сразу за прошлое вхождение. Каждый край идёт только вперёд — O(n).",
            "1) `last = {}`, `left = best = 0`. 2) Для `right, ch`: если `last.get(ch, -1) >= left` — `left = last[ch] + 1`. 3) `last[ch] = right`; `best = max(best, right - left + 1)`. Проверка `>= left` важна: старое вхождение левее окна не считается. Пустая строка — 0.",
        ],
        "brute": _longest_unique_brute,
        "ref": d("""\
            class Solution:
                def lengthOfLongestSubstring(self, s):
                    last = {}
                    left = best = 0
                    for right, ch in enumerate(s):
                        if last.get(ch, -1) >= left:
                            left = last[ch] + 1
                        last[ch] = right
                        best = max(best, right - left + 1)
                    return best
            """),
        "cases": [["abcabcbb"], ["bbbbb"], ["pwwkew"], [""], [" "], ["au"], ["dvdf"], ["abba"], ["tmmzuxt"], ["abcdefg"]],
        "rand": lambda rng: [rand_word(rng, 0, 10, "abcd ")],
    },
    {
        "id": 219, "slug": "contains-duplicate-ii", "title_en": "Contains Duplicate II",
        "title_ru": "Близкий повтор", "difficulty": "Easy", "week": 4,
        "pattern": "sliding-window-set", "pattern_ru": "окно фиксированной ширины / словарь индексов",
        "leetcode_url": "https://leetcode.com/problems/contains-duplicate-ii/",
        "statement_ru": d("""\
            Дан список `nums` и число `k`. Верните `True`, если есть два разных индекса `i` и `j`,
            для которых `nums[i] == nums[j]` и `abs(i - j) <= k`. Иначе `False`."""),
        "examples": [
            {"input": "nums = [1,2,3,1], k = 3", "output": "true", "explain_ru": "Единицы на расстоянии 3."},
            {"input": "nums = [1,0,1,1], k = 1", "output": "true", "explain_ru": ""},
            {"input": "nums = [1,2,3,1,2,3], k = 2", "output": "false", "explain_ru": "Одинаковые числа стоят на расстоянии 3."},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^5", "0 ≤ k ≤ 10^5"],
        "complexity_target": "O(n) по времени, O(min(n, k)) по памяти",
        "starter_code": "class Solution:\n    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:\n        pass\n",
        "method": "containsNearbyDuplicate", "arg_types": ["list[int]", "int"], "ret_type": "bool",
        "hints_ru": [
            "Число `x` встретилось снова. Какое прошлое вхождение `x` важно для проверки расстояния: первое или последнее?",
            "Словарь «число → последний индекс». Последнее вхождение — самое близкое, поэтому других хранить не нужно. Другой вариант: `set` из последних `k` чисел — окно фиксированной ширины.",
            "1) `last = {}`. 2) Для `i, x`: если `x in last` и `i - last[x] <= k` — верните `True`. 3) Запишите `last[x] = i`. 4) После цикла — `False`. При `k = 0` ответ всегда `False`.",
        ],
        "brute": lambda nums, k: any(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, min(len(nums), i + k + 1))),
        "ref": d("""\
            class Solution:
                def containsNearbyDuplicate(self, nums, k):
                    last = {}
                    for i, x in enumerate(nums):
                        if x in last and i - last[x] <= k:
                            return True
                        last[x] = i
                    return False
            """),
        "naive": d("""\
            class Solution:
                def containsNearbyDuplicate(self, nums, k):
                    for i in range(len(nums)):
                        for j in range(i + 1, min(len(nums), i + k + 1)):
                            if nums[i] == nums[j]:
                                return True
                    return False
            """),
        "cases": [[[1, 2, 3, 1], 3], [[1, 0, 1, 1], 1], [[1, 2, 3, 1, 2, 3], 2], [[1], 0], [[1, 1], 0], [[1, 1], 1],
                  [[1, 2, 1], 1], [[99, 99], 2], [[4, 1, 2, 3, 1, 5], 3], [[-1, -1], 100000]],
        "rand": lambda rng: [rand_ints(rng, 1, 9, 0, 4), rng.randint(0, 4)],
        "perf": [d("""\
            def gen():
                n = 10**5
                return [list(range(n)), n]
            """)],
    },
    {
        "id": 567, "slug": "permutation-in-string", "title_en": "Permutation in String",
        "title_ru": "Перестановка внутри строки", "difficulty": "Medium", "week": 4,
        "pattern": "sliding-window-count", "pattern_ru": "окно фиксированной ширины + счётчик",
        "leetcode_url": "https://leetcode.com/problems/permutation-in-string/",
        "statement_ru": d("""\
            Даны строки `s1` и `s2`. Верните `True`, если в `s2` есть подстрока, которая
            является перестановкой `s1` (те же буквы в том же количестве, порядок любой)."""),
        "examples": [
            {"input": 's1 = "ab", s2 = "eidbaooo"', "output": "true", "explain_ru": "В s2 есть подстрока ba."},
            {"input": 's1 = "ab", s2 = "eidboaoo"', "output": "false", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(s1), len(s2) ≤ 10^4", "Только маленькие латинские буквы"],
        "complexity_target": "O(n) по времени (26 букв — константа)",
        "starter_code": "class Solution:\n    def checkInclusion(self, s1: str, s2: str) -> bool:\n        pass\n",
        "method": "checkInclusion", "arg_types": ["str", "str"], "ret_type": "bool",
        "hints_ru": [
            "Перестановка `s1` имеет длину `len(s1)`. Какие подстроки `s2` тогда стоит проверять? Что у перестановки общего с `s1`?",
            "Окно фиксированной ширины `len(s1)` и счётчик букв, как в #242. При сдвиге окна на 1 одна буква входит, одна выходит. Не пересчитывайте окно заново: обновите 2 счётчика.",
            "1) `len(s1) > len(s2)` — `False`. 2) Два списка по 26 счётчиков: `need` для `s1`, `have` для окна. 3) Для каждого `i`: добавьте `s2[i]`; если `i >= m` — уберите `s2[i - m]`. 4) `have == need` — `True`. Сравнение 26 чисел — O(1).",
        ],
        "brute": lambda s1, s2: any(sorted(s2[i : i + len(s1)]) == sorted(s1) for i in range(len(s2) - len(s1) + 1)),
        "ref": d("""\
            class Solution:
                def checkInclusion(self, s1, s2):
                    m = len(s1)
                    if m > len(s2):
                        return False
                    need = [0] * 26
                    have = [0] * 26
                    for ch in s1:
                        need[ord(ch) - 97] += 1
                    for i, ch in enumerate(s2):
                        have[ord(ch) - 97] += 1
                        if i >= m:
                            have[ord(s2[i - m]) - 97] -= 1
                        if have == need:
                            return True
                    return False
            """),
        "naive": d("""\
            class Solution:
                def checkInclusion(self, s1, s2):
                    target = sorted(s1)
                    for i in range(len(s2) - len(s1) + 1):
                        if sorted(s2[i:i + len(s1)]) == target:
                            return True
                    return False
            """),
        "cases": [["ab", "eidbaooo"], ["ab", "eidboaoo"], ["a", "a"], ["a", "b"], ["abc", "ab"], ["adc", "dcda"],
                  ["hello", "ooolleoooleh"], ["ab", "ab"], ["aab", "baxaab"], ["xyz", "zzyx"]],
        "rand": lambda rng: [rand_word(rng, 1, 3), rand_word(rng, 1, 8)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(567)
                s1 = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(5000)) + "z"
                s2 = "".join(rng.choice("abcdefghijklmnopqrstuvwxy") for _ in range(10**4))
                return [s1, s2]
            """)],
    },
    {
        "id": 392, "slug": "is-subsequence", "title_en": "Is Subsequence",
        "title_ru": "Подпоследовательность", "difficulty": "Easy", "week": 4,
        "pattern": "two-pointers", "pattern_ru": "два указателя по двум строкам",
        "leetcode_url": "https://leetcode.com/problems/is-subsequence/",
        "statement_ru": d("""\
            Даны строки `s` и `t`. Верните `True`, если `s` можно получить из `t`, удалив
            некоторые символы (или ни одного) и не меняя порядок оставшихся."""),
        "examples": [
            {"input": 's = "abc", t = "ahbgdc"', "output": "true", "explain_ru": "a, b, c стоят в t в этом порядке."},
            {"input": 's = "axc", t = "ahbgdc"', "output": "false", "explain_ru": ""},
        ],
        "constraints_ru": ["0 ≤ len(s) ≤ 100", "0 ≤ len(t) ≤ 10^4"],
        "complexity_target": "O(len(t)) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def isSubsequence(self, s: str, t: str) -> bool:\n        pass\n",
        "method": "isSubsequence", "arg_types": ["str", "str"], "ret_type": "bool",
        "hints_ru": [
            "Первая буква `s` совпала с символом `t` в начале. Есть ли смысл ждать более позднего совпадения этой же буквы?",
            "Жадный выбор и один указатель по `s`. Раннее совпадение оставляет больше символов `t` для остальных букв `s`. Инвариант: `s[:i]` уже найдена в просмотренной части `t`.",
            "1) `i = 0`. 2) Для каждого символа `ch` из `t`: если `i < len(s)` и `s[i] == ch` — `i += 1`. 3) Верните `i == len(s)`. Пустая `s` — всегда `True`.",
        ],
        "brute": _subseq_brute,
        "ref": d("""\
            class Solution:
                def isSubsequence(self, s, t):
                    i = 0
                    for ch in t:
                        if i < len(s) and s[i] == ch:
                            i += 1
                    return i == len(s)
            """),
        "cases": [["abc", "ahbgdc"], ["axc", "ahbgdc"], ["", "ahbgdc"], ["", ""], ["a", ""], ["aaa", "aa"], ["ab", "ba"],
                  ["b", "abc"], ["acb", "ahbgdc"], ["aaaaaa", "bbaaaa"]],
        "rand": lambda rng: [rand_word(rng, 0, 4, "ab"), rand_word(rng, 0, 10, "abc")],
    },
    {
        "id": 205, "slug": "isomorphic-strings", "title_en": "Isomorphic Strings",
        "title_ru": "Изоморфные строки", "difficulty": "Easy", "week": 4,
        "pattern": "hash-map-bijection", "pattern_ru": "два словаря: взаимно однозначное соответствие",
        "leetcode_url": "https://leetcode.com/problems/isomorphic-strings/",
        "statement_ru": d("""\
            Строки `s` и `t` одинаковой длины изоморфны, если символы `s` можно заменить и
            получить `t`. Правила: одинаковые символы заменяются одинаково, два разных символа
            не могут стать одним и тем же. Символ может перейти сам в себя. Верните `True` или `False`."""),
        "examples": [
            {"input": 's = "egg", t = "add"', "output": "true", "explain_ru": "e → a, g → d."},
            {"input": 's = "foo", t = "bar"', "output": "false", "explain_ru": "o должна стать и a, и r."},
            {"input": 's = "badc", t = "baba"', "output": "false", "explain_ru": "b и d обе стали бы b."},
        ],
        "constraints_ru": ["1 ≤ len(s) = len(t) ≤ 5·10^4", "Любые ASCII-символы"],
        "complexity_target": "O(n) по времени",
        "starter_code": "class Solution:\n    def isIsomorphic(self, s: str, t: str) -> bool:\n        pass\n",
        "method": "isIsomorphic", "arg_types": ["str", "str"], "ret_type": "bool",
        "hints_ru": [
            "Сравните пары `badc`/`baba` и `foo`/`bar`. Какое правило нарушено в каждой паре? Почему одной проверки «`a` всегда переходит в одно и то же» мало?",
            "Два словаря: `s → t` и `t → s`. Первый ловит «один символ переходит в разные», второй — «два символа переходят в один». Соответствие должно быть взаимно однозначным.",
            "1) `st, ts = {}, {}`. 2) Для пар `(a, b)` из `zip(s, t)`: если `st.setdefault(a, b) != b` или `ts.setdefault(b, a) != a` — `False`. 3) После цикла — `True`.",
        ],
        "brute": _iso_brute,
        "ref": d("""\
            class Solution:
                def isIsomorphic(self, s, t):
                    st, ts = {}, {}
                    for a, b in zip(s, t):
                        if st.setdefault(a, b) != b or ts.setdefault(b, a) != a:
                            return False
                    return True
            """),
        "cases": [["egg", "add"], ["foo", "bar"], ["badc", "baba"], ["paper", "title"], ["a", "a"], ["ab", "aa"],
                  ["aa", "ab"], ["13", "42"], ["abab", "baba"], ["abcd", "dcba"]],
        "rand": lambda rng: (lambda n: [rand_word(rng, n, n, "abc"), rand_word(rng, n, n, "xyz")])(rng.randint(1, 6)),
    },
]
