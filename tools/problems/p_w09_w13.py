"""Weeks 9–13: grid graphs, DP, topological sort, binary search, design, interview mocks."""

import math
from collections import OrderedDict, deque
from functools import lru_cache
from textwrap import dedent as d

from .common import rand_grid, rand_ints, rand_word

LIST_NODE_DOC = """# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
"""


def _islands_brute(grid):
    # Union-find over land cells.
    rows, cols = len(grid), len(grid[0])
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                parent[(r, c)] = (r, c)
    for r, c in list(parent):
        for nr, nc in ((r + 1, c), (r, c + 1)):
            if (nr, nc) in parent:
                parent[find((r, c))] = find((nr, nc))
    return len({find(x) for x in parent})


def _flood_brute(image, sr, sc, color):
    image = [row[:] for row in image]
    old = image[sr][sc]
    if old == color:
        return image
    q = deque([(sr, sc)])
    seen = {(sr, sc)}
    while q:
        r, c = q.popleft()
        image[r][c] = color
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < len(image) and 0 <= nc < len(image[0]) and (nr, nc) not in seen and image[nr][nc] == old:
                seen.add((nr, nc))
                q.append((nr, nc))
    return image


def _flood_rand(rng):
    image = rand_grid(rng, 5, 5, [0, 1, 2])
    return [image, rng.randrange(len(image)), rng.randrange(len(image[0])), rng.randint(0, 2)]


def _coin_brute(coins, amount):
    # BFS over amounts: the first time we reach `amount` uses the fewest coins.
    dist = {0: 0}
    q = deque([0])
    while q:
        a = q.popleft()
        if a == amount:
            return dist[a]
        for c in coins:
            if a + c <= amount and a + c not in dist:
                dist[a + c] = dist[a] + 1
                q.append(a + c)
    return -1


def _area_brute(grid):
    best = 0
    seen = set()
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1 and (r, c) not in seen:
                size = 0
                q = deque([(r, c)])
                seen.add((r, c))
                while q:
                    x, y = q.popleft()
                    size += 1
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 1 and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            q.append((nx, ny))
                best = max(best, size)
    return best


def _oranges_brute(grid):
    grid = [row[:] for row in grid]
    minutes = 0
    while True:
        rot = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 1
               and any(0 <= r + dr < len(grid) and 0 <= c + dc < len(grid[0]) and grid[r + dr][c + dc] == 2
                       for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        if not rot:
            break
        for r, c in rot:
            grid[r][c] = 2
        minutes += 1
    return -1 if any(1 in row for row in grid) else minutes


def _rob_brute(nums, circular=False):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        if mask & (mask >> 1):
            continue
        if circular and n > 1 and mask & 1 and mask >> (n - 1) & 1:
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def _courses_rand(rng):
    n = rng.randint(1, 6)
    edges = set()
    for _ in range(rng.randint(0, 7)):
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            if rng.random() < 0.75 and a < b:
                a, b = b, a  # mostly acyclic: course a needs an earlier course b
            edges.add((a, b))
    return [n, [list(e) for e in sorted(edges)]]


def _kahn(n, prereq):
    indeg = [0] * n
    after = [[] for _ in range(n)]
    for a, b in prereq:
        after[b].append(a)
        indeg[a] += 1
    order = [i for i in range(n) if indeg[i] == 0]
    for x in order:
        for y in after[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                order.append(y)
    return order if len(order) == n else []


def _rotated_rand(rng):
    nums = sorted(rng.sample(range(-20, 20), rng.randint(1, 9)))
    k = rng.randrange(len(nums))
    return nums[k:] + nums[:k]


def _combination_brute(candidates, target):
    # DP over sums: ways[s] = set of sorted combinations reaching s.
    ways = [set() for _ in range(target + 1)]
    ways[0].add(())
    for c in sorted(candidates):
        for s in range(c, target + 1):
            for combo in ways[s - c]:
                ways[s].add(combo + (c,))
    return [list(x) for x in sorted(ways[target])]


@lru_cache(maxsize=None)
def _lis_from(nums, i):
    return 1 + max([_lis_from(nums, j) for j in range(i + 1, len(nums)) if nums[j] > nums[i]], default=0)


def _min_stack_brute(ops, args):
    data, out = [], []
    for op, a in zip(ops, args):
        if op == "MinStack":
            out.append(None)
        elif op == "push":
            data.append(a[0])
            out.append(None)
        elif op == "pop":
            data.pop()
            out.append(None)
        elif op == "top":
            out.append(data[-1])
        else:
            out.append(min(data))
    return out


def _min_stack_rand(rng):
    ops, args, size = ["MinStack"], [[]], 0
    for _ in range(rng.randint(1, 12)):
        choices = ["push"] + (["pop", "top", "getMin", "getMin"] if size else [])
        op = rng.choice(choices)
        ops.append(op)
        if op == "push":
            args.append([rng.randint(-5, 5)])
            size += 1
        else:
            args.append([])
            size -= op == "pop"
    return [ops, args]


def _lru_brute(ops, args):
    out = []
    cache = OrderedDict()
    cap = 0
    for op, a in zip(ops, args):
        if op == "LRUCache":
            cap = a[0]
            out.append(None)
        elif op == "get":
            if a[0] in cache:
                cache.move_to_end(a[0])
                out.append(cache[a[0]])
            else:
                out.append(-1)
        else:
            cache[a[0]] = a[1]
            cache.move_to_end(a[0])
            if len(cache) > cap:
                cache.popitem(last=False)
            out.append(None)
    return out


def _lru_rand(rng):
    ops, args = ["LRUCache"], [[rng.randint(1, 3)]]
    for _ in range(rng.randint(1, 14)):
        if rng.random() < 0.5:
            ops.append("put")
            args.append([rng.randint(1, 5), rng.randint(0, 9)])
        else:
            ops.append("get")
            args.append([rng.randint(1, 5)])
    return [ops, args]


def _koko_brute(piles, h):
    k = 1
    while sum(math.ceil(p / k) for p in piles) > h:
        k += 1
    return k


def _koko_rand(rng):
    piles = rand_ints(rng, 1, 6, 1, 30)
    return [piles, rng.randint(len(piles), len(piles) + 12)]


def _palindrome_brute(s):
    best = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            sub = s[i : j + 1]
            if sub == sub[::-1] and len(sub) > len(best):
                best = sub
    return best


def _subsets_brute(nums):
    return [[nums[i] for i in range(len(nums)) if mask >> i & 1] for mask in range(1 << len(nums))]


PROBLEMS = [
    # ---------------------------------------------------------------- Week 9
    {
        "id": 200, "slug": "number-of-islands", "title_en": "Number of Islands",
        "title_ru": "Число островов", "difficulty": "Medium", "week": 9,
        "pattern": "grid-dfs", "pattern_ru": "сетка как граф: DFS / BFS",
        "leetcode_url": "https://leetcode.com/problems/number-of-islands/",
        "statement_ru": d("""\
            Дана карта `grid` из строк `"1"` (суша) и `"0"` (вода). Остров — группа клеток суши,
            соединённых по горизонтали или вертикали (не по диагонали). Края карты — вода.
            Верните число островов."""),
        "examples": [
            {"input": 'grid = [["1","1","0"],["1","0","0"],["0","0","1"]]', "output": "2", "explain_ru": ""},
            {"input": 'grid = [["1","1","1"],["0","1","0"],["1","1","1"]]', "output": "1", "explain_ru": "Все единицы связаны через центр."},
        ],
        "constraints_ru": ["1 ≤ строк, столбцов ≤ 300", "grid[i][j] — \"0\" или \"1\""],
        "complexity_target": "O(строк · столбцов)",
        "starter_code": "class Solution:\n    def numIslands(self, grid: List[List[str]]) -> int:\n        pass\n",
        "method": "numIslands", "arg_types": ["list[list[str]]"], "ret_type": "int",
        "hints_ru": [
            "Вы нашли клетку суши. Как узнать все клетки этого же острова? Как не посчитать этот остров второй раз, когда внешний цикл дойдёт до его других клеток?",
            "Сетка — граф: клетка — вершина, 4 соседа — рёбра; остров — компонента связности. Обход (DFS или BFS) от найденной суши «затапливает» весь остров: меняет `\"1\"` на `\"0\"`. Затопленная клетка больше не начнёт новый остров.",
            "1) `count = 0`. 2) Для каждой клетки: если `\"1\"` — `count += 1`, затопите остров стеком. 3) Затопление: снимите клетку со стека, для 4 соседей внутри границ с `\"1\"` — поставьте `\"0\"` и положите в стек. 4) Верните `count`. Ставьте `\"0\"` при добавлении в стек, иначе клетка попадёт туда дважды.",
        ],
        "brute": _islands_brute,
        "ref": d("""\
            class Solution:
                def numIslands(self, grid):
                    rows, cols = len(grid), len(grid[0])
                    count = 0
                    for r in range(rows):
                        for c in range(cols):
                            if grid[r][c] == "1":
                                count += 1
                                grid[r][c] = "0"
                                stack = [(r, c)]
                                while stack:
                                    x, y = stack.pop()
                                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "1":
                                            grid[nx][ny] = "0"
                                            stack.append((nx, ny))
                    return count
            """),
        "cases": [[[["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]]], [[["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]]], [[["0"]]], [[["1"]]],
                  [[["1", "0", "1", "0", "1"]]], [[["1", "0"], ["0", "1"]]],
                  [[["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]]]],
        "rand": lambda rng: [rand_grid(rng, 6, 6, ["0", "1"])],
    },
    {
        "id": 733, "slug": "flood-fill", "title_en": "Flood Fill",
        "title_ru": "Заливка", "difficulty": "Easy", "week": 9,
        "pattern": "grid-dfs", "pattern_ru": "сетка: DFS от одной клетки",
        "leetcode_url": "https://leetcode.com/problems/flood-fill/",
        "statement_ru": d("""\
            `image` — картинка из чисел-цветов. Начните с клетки `(sr, sc)` и перекрасьте в `color`
            её и все клетки того же исходного цвета, связанные с ней по горизонтали и вертикали,
            как «заливка» в Paint. Верните картинку."""),
        "examples": [
            {"input": "image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1, color = 2", "output": "[[2,2,2],[2,2,0],[2,0,1]]", "explain_ru": "Правая нижняя 1 не связана с центром."},
            {"input": "image = [[0,0,0],[0,0,0]], sr = 0, sc = 0, color = 0", "output": "[[0,0,0],[0,0,0]]", "explain_ru": "Цвет уже тот же."},
        ],
        "constraints_ru": ["1 ≤ строк, столбцов ≤ 50", "0 ≤ цвет < 2^16"],
        "complexity_target": "O(число клеток)",
        "starter_code": "class Solution:\n    def floodFill(self, image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:\n        pass\n",
        "method": "floodFill", "arg_types": ["list[list[int]]", "int", "int", "int"], "ret_type": "list[list[int]]",
        "hints_ru": [
            "Какие клетки нужно перекрасить: все клетки цвета `color` или только клетки исходного цвета стартовой клетки? Что будет, если новый цвет равен исходному?",
            "Обход DFS от одной клетки: перекрасьте её и идите в 4 соседей исходного цвета. Перекрашенная клетка больше не подходит под условие — так обход не вернётся в неё. Но если `color` равен исходному цвету, условие не меняется, и обход зациклится.",
            "1) `old = image[sr][sc]`; если `old == color` — сразу верните `image`. 2) `fill(r, c)`: если клетка внутри картинки и её цвет `old` — покрасьте в `color` и вызовите `fill` для 4 соседей. 3) `fill(sr, sc)`, верните `image`.",
        ],
        "brute": _flood_brute,
        "ref": d("""\
            class Solution:
                def floodFill(self, image, sr, sc, color):
                    old = image[sr][sc]
                    if old == color:
                        return image
                    def fill(r, c):
                        if 0 <= r < len(image) and 0 <= c < len(image[0]) and image[r][c] == old:
                            image[r][c] = color
                            fill(r + 1, c); fill(r - 1, c); fill(r, c + 1); fill(r, c - 1)
                    fill(sr, sc)
                    return image
            """),
        "cases": [[[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], [[[0, 0, 0], [0, 0, 0]], 0, 0, 0], [[[5]], 0, 0, 7], [[[0, 1], [1, 0]], 0, 0, 3],
                  [[[1, 1], [1, 1]], 1, 0, 9], [[[2, 2, 2], [2, 0, 2], [2, 2, 2]], 1, 1, 2], [[[1, 2, 1], [2, 1, 2]], 0, 2, 4]],
        "rand": _flood_rand,
    },
    {
        "id": 322, "slug": "coin-change", "title_en": "Coin Change",
        "title_ru": "Размен монет", "difficulty": "Medium", "week": 9,
        "pattern": "dp-unbounded", "pattern_ru": "DP по сумме",
        "leetcode_url": "https://leetcode.com/problems/coin-change/",
        "statement_ru": d("""\
            Даны номиналы монет `coins` (каждой монеты сколько угодно) и сумма `amount`.
            Верните наименьшее число монет, которыми можно набрать ровно `amount`.
            Если набрать нельзя, верните `-1`."""),
        "examples": [
            {"input": "coins = [1,2,5], amount = 11", "output": "3", "explain_ru": "5 + 5 + 1."},
            {"input": "coins = [2], amount = 3", "output": "-1", "explain_ru": ""},
            {"input": "coins = [1], amount = 0", "output": "0", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(coins) ≤ 12", "1 ≤ coins[i] ≤ 2^31 − 1", "0 ≤ amount ≤ 10^4"],
        "complexity_target": "O(amount · len(coins))",
        "starter_code": "class Solution:\n    def coinChange(self, coins: List[int], amount: int) -> int:\n        pass\n",
        "method": "coinChange", "arg_types": ["list[int]", "int"], "ret_type": "int",
        "hints_ru": [
            "Попробуйте жадно «брать самую крупную монету» для `coins = [1,3,4]`, `amount = 6`. Сколько монет вышло? А какой ответ лучший?",
            "Динамическое программирование по сумме: `dp[s]` — минимум монет для суммы `s`. Последняя монета — какая-то `c`, поэтому `dp[s] = 1 + min(dp[s - c])`. Каждая сумма считается один раз, итого O(amount · len(coins)).",
            "1) `dp = [0] + [inf] * amount`. 2) Для `s` от 1 до `amount`: для каждой монеты `c <= s` — `dp[s] = min(dp[s], dp[s - c] + 1)`. 3) Верните `dp[amount]` или `-1`, если там `inf`. `amount = 0` — ответ 0.",
        ],
        "brute": _coin_brute,
        "ref": d("""\
            class Solution:
                def coinChange(self, coins, amount):
                    dp = [0] + [float("inf")] * amount
                    for s in range(1, amount + 1):
                        for c in coins:
                            if c <= s and dp[s - c] + 1 < dp[s]:
                                dp[s] = dp[s - c] + 1
                    return dp[amount] if dp[amount] != float("inf") else -1
            """),
        "naive": d("""\
            class Solution:
                def coinChange(self, coins, amount):
                    def best(s):
                        if s == 0:
                            return 0
                        res = float("inf")
                        for c in coins:
                            if c <= s:
                                res = min(res, 1 + best(s - c))
                        return res
                    r = best(amount)
                    return r if r != float("inf") else -1
            """),
        "cases": [[[1, 2, 5], 11], [[2], 3], [[1], 0], [[1, 3, 4], 6], [[2, 5, 10, 1], 27], [[186, 419, 83, 408], 6249], [[3, 7], 5], [[5], 10], [[2147483647], 2]],
        "rand": lambda rng: [sorted(set(rand_ints(rng, 1, 4, 1, 9))), rng.randint(0, 30)],
        "perf": [d("""\
            def gen():
                return [[1, 2, 5], 100]
            """)],
    },
    {
        "id": 695, "slug": "max-area-of-island", "title_en": "Max Area of Island",
        "title_ru": "Самый большой остров", "difficulty": "Medium", "week": 9,
        "pattern": "grid-dfs", "pattern_ru": "сетка: DFS возвращает размер",
        "leetcode_url": "https://leetcode.com/problems/max-area-of-island/",
        "statement_ru": d("""\
            Дана карта `grid` из чисел `1` (суша) и `0` (вода). Площадь острова — число клеток
            в нём (связь по горизонтали и вертикали). Верните наибольшую площадь острова или `0`."""),
        "examples": [
            {"input": "grid = [[1,1,0],[0,1,0],[0,0,1]]", "output": "3", "explain_ru": ""},
            {"input": "grid = [[0,0,0]]", "output": "0", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ строк, столбцов ≤ 50"],
        "complexity_target": "O(строк · столбцов)",
        "starter_code": "class Solution:\n    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:\n        pass\n",
        "method": "maxAreaOfIsland", "arg_types": ["list[list[int]]"], "ret_type": "int",
        "hints_ru": [
            "Это как #200, но теперь важен размер острова. Как узнать число клеток острова, пока вы его обходите?",
            "DFS, который возвращает размер: размер острова от клетки = 1 + размеры от 4 соседей. Затапливайте клетку (`1 → 0`) до рекурсии в соседей, иначе её посчитают дважды. Вода и выход за границу дают 0.",
            "1) `sink(r, c)`: клетка вне сетки или не `1` — верните 0. 2) Иначе `grid[r][c] = 0` и верните `1 + sink` для 4 соседей. 3) Ответ — максимум `sink(r, c)` по всем клеткам. Сетка без суши — 0.",
        ],
        "brute": _area_brute,
        "ref": d("""\
            class Solution:
                def maxAreaOfIsland(self, grid):
                    rows, cols = len(grid), len(grid[0])
                    def sink(r, c):
                        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == 1:
                            grid[r][c] = 0
                            return 1 + sink(r + 1, c) + sink(r - 1, c) + sink(r, c + 1) + sink(r, c - 1)
                        return 0
                    return max(sink(r, c) for r in range(rows) for c in range(cols))
            """),
        "cases": [[[[1, 1, 0], [0, 1, 0], [0, 0, 1]]], [[[0, 0, 0]]], [[[1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[1, 1], [1, 1]]], [[[0, 1, 1, 0, 1, 1, 1]]]],
        "rand": lambda rng: [rand_grid(rng, 6, 6, [0, 1])],
    },
    {
        "id": 994, "slug": "rotting-oranges", "title_en": "Rotting Oranges",
        "title_ru": "Гнилые апельсины", "difficulty": "Medium", "week": 9,
        "pattern": "grid-bfs-multi", "pattern_ru": "BFS сразу от многих источников",
        "leetcode_url": "https://leetcode.com/problems/rotting-oranges/",
        "statement_ru": d("""\
            В сетке `0` — пусто, `1` — свежий апельсин, `2` — гнилой. Каждую минуту каждый
            свежий апельсин рядом с гнилым (по 4 сторонам) гниёт. Верните, через сколько минут
            свежих апельсинов не останется. Если это невозможно, верните `-1`."""),
        "examples": [
            {"input": "grid = [[2,1,1],[1,1,0],[0,1,1]]", "output": "4", "explain_ru": ""},
            {"input": "grid = [[2,1,1],[0,1,1],[1,0,1]]", "output": "-1", "explain_ru": "Апельсин в левом нижнем углу не достижим."},
            {"input": "grid = [[0,2]]", "output": "0", "explain_ru": "Свежих нет с самого начала."},
        ],
        "constraints_ru": ["1 ≤ строк, столбцов ≤ 10", "grid[i][j] ∈ {0, 1, 2}"],
        "complexity_target": "O(строк · столбцов)",
        "starter_code": "class Solution:\n    def orangesRotting(self, grid: List[List[int]]) -> int:\n        pass\n",
        "method": "orangesRotting", "arg_types": ["list[list[int]]"], "ret_type": "int",
        "hints_ru": [
            "Гниль идёт «волнами»: за минуту — на соседей. Сколько источников у первой волны? Как считать минуты, если источников несколько?",
            "BFS от многих источников: положите в очередь все гнилые апельсины сразу. Обрабатывайте очередь уровнями: один уровень — одна минута. Счётчик свежих апельсинов показывает, остались ли недостижимые.",
            "1) `q` — все клетки с `2`; `fresh` — число `1`. 2) Пока `q` и `fresh`: `minutes += 1`; обработайте `len(q)` клеток; свежий сосед становится `2`, `fresh -= 1`, сосед — в очередь. 3) Верните `-1`, если `fresh > 0`, иначе `minutes`. Нет свежих с самого начала — 0.",
        ],
        "brute": _oranges_brute,
        "ref": d("""\
            class Solution:
                def orangesRotting(self, grid):
                    rows, cols = len(grid), len(grid[0])
                    q = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2)
                    fresh = sum(row.count(1) for row in grid)
                    minutes = 0
                    while q and fresh:
                        minutes += 1
                        for _ in range(len(q)):
                            r, c = q.popleft()
                            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                                    grid[nr][nc] = 2
                                    fresh -= 1
                                    q.append((nr, nc))
                    return -1 if fresh else minutes
            """),
        "cases": [[[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], [[[0, 2]]], [[[0]]], [[[1]]], [[[2, 2], [1, 1]]], [[[2, 1, 1, 1, 1, 1, 2]]], [[[1, 2, 1], [1, 1, 1], [0, 0, 1]]]],
        "rand": lambda rng: [rand_grid(rng, 5, 5, [0, 1, 2], [2, 5, 1])],
    },
    # ---------------------------------------------------------------- Week 10
    {
        "id": 198, "slug": "house-robber", "title_en": "House Robber",
        "title_ru": "Грабитель", "difficulty": "Medium", "week": 10,
        "pattern": "dp-1d", "pattern_ru": "DP: взять или пропустить",
        "leetcode_url": "https://leetcode.com/problems/house-robber/",
        "statement_ru": d("""\
            Дома стоят в ряд, `nums[i]` — деньги в доме `i`. Нельзя грабить два соседних дома:
            сработает сигнализация. Верните наибольшую сумму, которую можно унести."""),
        "examples": [
            {"input": "nums = [1,2,3,1]", "output": "4", "explain_ru": "Дома 0 и 2: 1 + 3."},
            {"input": "nums = [2,7,9,3,1]", "output": "12", "explain_ru": "Дома 0, 2, 4: 2 + 9 + 1."},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 400"],
        "complexity_target": "O(n) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def rob(self, nums: List[int]) -> int:\n        pass\n",
        "method": "rob", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Вы стоите у дома `i`. Какие два решения возможны? Что каждое из них говорит о доме `i - 1`?",
            "Динамическое программирование «взять или пропустить»: `best(i) = max(best(i - 1), best(i - 2) + nums[i])`. Прямая рекурсия считает одно и то же много раз, O(2^n). Снизу вверх нужны только два последних значения, как в #70.",
            "1) `prev = cur = 0` — лучшие суммы для двух прошлых позиций. 2) Для каждого `x`: `prev, cur = cur, max(cur, prev + x)`. 3) Верните `cur`. Один дом — его сумма.",
        ],
        "brute": _rob_brute,
        "ref": d("""\
            class Solution:
                def rob(self, nums):
                    prev = cur = 0
                    for x in nums:
                        prev, cur = cur, max(cur, prev + x)
                    return cur
            """),
        "naive": d("""\
            class Solution:
                def rob(self, nums):
                    def best(i):
                        if i < 0:
                            return 0
                        return max(best(i - 1), best(i - 2) + nums[i])
                    return best(len(nums) - 1)
            """),
        "cases": [[[1, 2, 3, 1]], [[2, 7, 9, 3, 1]], [[5]], [[1, 2]], [[2, 1, 1, 2]], [[0, 0, 0]], [[400, 0, 400, 0, 400]], [[1, 3, 1, 3, 100]]],
        "rand": lambda rng: [rand_ints(rng, 1, 12, 0, 20)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(198)
                return [[rng.randint(0, 400) for _ in range(40)]]
            """)],
    },
    {
        "id": 207, "slug": "course-schedule", "title_en": "Course Schedule",
        "title_ru": "Расписание курсов", "difficulty": "Medium", "week": 10,
        "pattern": "topological-sort", "pattern_ru": "граф: поиск цикла / топологическая сортировка",
        "leetcode_url": "https://leetcode.com/problems/course-schedule/",
        "statement_ru": d("""\
            Есть `numCourses` курсов с номерами от 0 до `numCourses - 1`. Пара `[a, b]` в
            `prerequisites` значит: чтобы пройти курс `a`, сначала нужно пройти курс `b`.
            Верните `True`, если можно пройти все курсы."""),
        "examples": [
            {"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "true", "explain_ru": "Сначала 0, потом 1."},
            {"input": "numCourses = 2, prerequisites = [[1,0],[0,1]]", "output": "false", "explain_ru": "Курсы ждут друг друга — цикл."},
        ],
        "constraints_ru": ["1 ≤ numCourses ≤ 2000", "0 ≤ len(prerequisites) ≤ 5000", "Все пары разные"],
        "complexity_target": "O(V + E)",
        "starter_code": "class Solution:\n    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:\n        pass\n",
        "method": "canFinish", "arg_types": ["int", "list[list[int]]"], "ret_type": "bool",
        "hints_ru": [
            "Нарисуйте курсы точками, а требования — стрелками `b → a`. При каком рисунке пройти все курсы нельзя?",
            "Пройти нельзя, если в направленном графе есть цикл. Поиск цикла через DFS с тремя состояниями: 0 — новая вершина, 1 — на текущем пути, 2 — готова. Ребро в вершину с состоянием 1 — цикл. Другой путь — алгоритм Кана: снимайте курсы без требований по одному.",
            "1) Список смежности: для `[a, b]` — `graph[b].append(a)`. 2) Для каждой новой вершины запустите DFS: при входе `state = 1`, при выходе `state = 2`. 3) Сосед с `state == 1` — верните `False`. 4) Все обходы закончились — `True`. Стек вместо рекурсии защищает от глубокой рекурсии.",
        ],
        "brute": lambda n, pre: len(_kahn(n, pre)) == n,
        "ref": d("""\
            class Solution:
                def canFinish(self, numCourses, prerequisites):
                    graph = [[] for _ in range(numCourses)]
                    for a, b in prerequisites:
                        graph[b].append(a)
                    state = [0] * numCourses   # 0 new, 1 on the stack, 2 done
                    for start in range(numCourses):
                        if state[start]:
                            continue
                        stack = [(start, iter(graph[start]))]
                        state[start] = 1
                        while stack:
                            node, it = stack[-1]
                            nxt = next(it, None)
                            if nxt is None:
                                state[node] = 2
                                stack.pop()
                            elif state[nxt] == 1:
                                return False
                            elif state[nxt] == 0:
                                state[nxt] = 1
                                stack.append((nxt, iter(graph[nxt])))
                    return True
            """),
        "cases": [[2, [[1, 0]]], [2, [[1, 0], [0, 1]]], [1, []], [3, []], [3, [[0, 1], [1, 2], [2, 0]]], [4, [[1, 0], [2, 1], [3, 2]]],
                  [5, [[1, 4], [2, 4], [3, 1], [3, 2]]], [3, [[1, 0], [2, 0], [2, 1]]], [4, [[1, 0], [2, 1], [1, 2], [3, 0]]]],
        "rand": _courses_rand,
    },
    {
        "id": 213, "slug": "house-robber-ii", "title_en": "House Robber II",
        "title_ru": "Грабитель на кольце", "difficulty": "Medium", "week": 10,
        "pattern": "dp-1d", "pattern_ru": "DP: свести к прошлой задаче",
        "leetcode_url": "https://leetcode.com/problems/house-robber-ii/",
        "statement_ru": d("""\
            Как в #198, но дома стоят по **кругу**: первый и последний дом — соседи.
            Верните наибольшую сумму без двух соседних домов."""),
        "examples": [
            {"input": "nums = [2,3,2]", "output": "3", "explain_ru": "Дома 0 и 2 — соседи по кругу."},
            {"input": "nums = [1,2,3,1]", "output": "4", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 1000"],
        "complexity_target": "O(n)",
        "starter_code": "class Solution:\n    def rob(self, nums: List[int]) -> int:\n        pass\n",
        "method": "rob", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Дома стоят по кругу: первый и последний — соседи. Можно ли взять оба? Что тогда точно верно про один из них?",
            "Сведите задачу к #198: один из крайних домов точно не берём. Значит, ответ — лучший из двух линейных случаев: без первого дома (`nums[1:]`) и без последнего (`nums[:-1]`).",
            "1) Напишите `line(arr)` из #198. 2) Если дом один — верните `nums[0]`: оба среза пусты. 3) Верните `max(line(nums[1:]), line(nums[:-1]))`.",
        ],
        "brute": lambda nums: _rob_brute(nums, circular=True),
        "ref": d("""\
            class Solution:
                def rob(self, nums):
                    def line(arr):
                        prev = cur = 0
                        for x in arr:
                            prev, cur = cur, max(cur, prev + x)
                        return cur
                    if len(nums) == 1:
                        return nums[0]
                    return max(line(nums[1:]), line(nums[:-1]))
            """),
        "cases": [[[2, 3, 2]], [[1, 2, 3, 1]], [[1, 2, 3]], [[5]], [[1, 7]], [[200, 3, 140, 20, 10]], [[0, 0]], [[4, 1, 2, 7, 5, 3, 1]]],
        "rand": lambda rng: [rand_ints(rng, 1, 12, 0, 20)],
    },
    {
        "id": 210, "slug": "course-schedule-ii", "title_en": "Course Schedule II",
        "title_ru": "Порядок курсов", "difficulty": "Medium", "week": 10,
        "pattern": "topological-sort", "pattern_ru": "топологическая сортировка (Кан)",
        "leetcode_url": "https://leetcode.com/problems/course-schedule-ii/",
        "statement_ru": d("""\
            Условие как в #207. Верните **порядок**, в котором можно пройти все курсы.
            Подходит любой верный порядок. Если пройти все курсы нельзя, верните пустой список."""),
        "examples": [
            {"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "[0,1]", "explain_ru": ""},
            {"input": "numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]", "output": "[0,2,1,3]", "explain_ru": "[0,1,2,3] тоже верно."},
            {"input": "numCourses = 1, prerequisites = []", "output": "[0]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ numCourses ≤ 2000", "Все пары разные"],
        "complexity_target": "O(V + E)",
        "starter_code": "class Solution:\n    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:\n        pass\n",
        "method": "findOrder", "arg_types": ["int", "list[list[int]]"], "ret_type": "list[int]", "compare": "check",
        "check": d("""\
            def check(args, result, expected):
                n, pre = args
                if not expected:
                    return result == []
                if not isinstance(result, list) or sorted(result) != list(range(n)):
                    return False
                pos = {c: i for i, c in enumerate(result)}
                return all(pos[b] < pos[a] for a, b in pre)
            """),
        "hints_ru": [
            "Вы уже умеете проверять, что цикла нет (#207). В какой момент обхода курс «готов», то есть все курсы после него уже обработаны?",
            "Топологическая сортировка через DFS: вершина получает состояние «готова», когда обработаны все её потомки. Список таких вершин (порядок выхода), развёрнутый задом наперёд, — верный порядок. Другой путь — Кан: порядок извлечения из очереди вершин с входящей степенью 0.",
            "1) Граф и три состояния, как в #207. 2) При выходе из вершины добавьте её в `post`. 3) Нашли цикл — верните `[]`. 4) Верните `post[::-1]`. Курсы без требований тоже попадут в ответ: DFS запускается от каждой новой вершины.",
        ],
        "brute": _kahn,
        "ref": d("""\
            class Solution:
                def findOrder(self, numCourses, prerequisites):
                    graph = [[] for _ in range(numCourses)]
                    for a, b in prerequisites:
                        graph[b].append(a)
                    state = [0] * numCourses
                    post = []
                    for start in range(numCourses):
                        if state[start]:
                            continue
                        stack = [(start, iter(graph[start]))]
                        state[start] = 1
                        while stack:
                            node, it = stack[-1]
                            nxt = next(it, None)
                            if nxt is None:
                                state[node] = 2
                                post.append(node)
                                stack.pop()
                            elif state[nxt] == 1:
                                return []
                            elif state[nxt] == 0:
                                state[nxt] = 1
                                stack.append((nxt, iter(graph[nxt])))
                    return post[::-1]
            """),
        "cases": [[2, [[1, 0]]], [4, [[1, 0], [2, 0], [3, 1], [3, 2]]], [1, []], [2, [[0, 1], [1, 0]]], [3, []], [3, [[0, 1], [1, 2]]], [3, [[1, 0], [1, 2], [0, 1]]]],
        "rand": _courses_rand,
    },
    {
        "id": 62, "slug": "unique-paths", "title_en": "Unique Paths",
        "title_ru": "Пути в сетке", "difficulty": "Medium", "week": 10,
        "pattern": "dp-2d", "pattern_ru": "DP по сетке",
        "leetcode_url": "https://leetcode.com/problems/unique-paths/",
        "statement_ru": d("""\
            Робот стоит в левом верхнем углу сетки `m × n` и ходит только вправо или вниз.
            Сколько разных путей ведут в правый нижний угол?"""),
        "examples": [
            {"input": "m = 3, n = 7", "output": "28", "explain_ru": ""},
            {"input": "m = 3, n = 2", "output": "3", "explain_ru": "→↓↓, ↓→↓, ↓↓→."},
        ],
        "constraints_ru": ["1 ≤ m, n ≤ 100", "Ответ ≤ 2·10^9"],
        "complexity_target": "O(m · n) по времени, O(n) по памяти",
        "starter_code": "class Solution:\n    def uniquePaths(self, m: int, n: int) -> int:\n        pass\n",
        "method": "uniquePaths", "arg_types": ["int", "int"], "ret_type": "int",
        "hints_ru": [
            "Робот ходит только вправо и вниз. Откуда он мог прийти в клетку `(r, c)`?",
            "Динамическое программирование по сетке: `paths[r][c] = paths[r-1][c] + paths[r][c-1]`. В первой строке и первом столбце — по 1 пути. Для подсчёта строки нужна только прошлая строка, поэтому хватит одного списка.",
            "1) `row = [1] * n`. 2) Повторите `m - 1` раз: для `c` от 1 до `n - 1` — `row[c] += row[c - 1]`. 3) Верните `row[-1]`. Проверка: 3 × 7 → 28. Бонус: ответ равен C(m + n − 2, m − 1).",
        ],
        "brute": lambda m, n: math.comb(m + n - 2, m - 1),
        "ref": d("""\
            class Solution:
                def uniquePaths(self, m, n):
                    row = [1] * n
                    for _ in range(m - 1):
                        for c in range(1, n):
                            row[c] += row[c - 1]
                    return row[-1]
            """),
        "cases": [[3, 7], [3, 2], [1, 1], [1, 10], [10, 1], [2, 2], [7, 3], [10, 10], [23, 12]],
        "rand": lambda rng: [rng.randint(1, 12), rng.randint(1, 12)],
    },
    # ---------------------------------------------------------------- Week 11
    {
        "id": 33, "slug": "search-in-rotated-sorted-array", "title_en": "Search in Rotated Sorted Array",
        "title_ru": "Поиск в сдвинутом списке", "difficulty": "Medium", "week": 11,
        "pattern": "binary-search", "pattern_ru": "бинарный поиск: какая половина отсортирована",
        "leetcode_url": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
        "statement_ru": d("""\
            Отсортированный список разных чисел циклически сдвинули: `[0,1,2,4,5,6,7]` мог стать
            `[4,5,6,7,0,1,2]`. Найдите индекс `target` или верните `-1`. Нужно O(log n)."""),
        "examples": [
            {"input": "nums = [4,5,6,7,0,1,2], target = 0", "output": "4", "explain_ru": ""},
            {"input": "nums = [4,5,6,7,0,1,2], target = 3", "output": "-1", "explain_ru": ""},
            {"input": "nums = [1], target = 0", "output": "-1", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 5000", "Все числа разные"],
        "complexity_target": "O(log n)",
        "starter_code": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        pass\n",
        "method": "search", "arg_types": ["list[int]", "int"], "ret_type": "int",
        "hints_ru": [
            "Разрежьте сдвинутый список посередине. Может ли разрыв (место сдвига) быть в обеих половинах сразу? Что тогда верно про одну из половин?",
            "Бинарный поиск: хотя бы одна половина всегда отсортирована. Если `nums[lo] <= nums[mid]` — отсортирована левая. В отсортированной половине легко проверить, лежит ли там `target`: сравните с её краями.",
            "1) `lo, hi`; `mid`; равно — верните `mid`. 2) Левая отсортирована: если `nums[lo] <= target < nums[mid]` — `hi = mid - 1`, иначе `lo = mid + 1`. 3) Иначе правая: если `nums[mid] < target <= nums[hi]` — `lo = mid + 1`, иначе `hi = mid - 1`. 4) Цикл закончился — `-1`.",
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
                        if nums[lo] <= nums[mid]:
                            if nums[lo] <= target < nums[mid]:
                                hi = mid - 1
                            else:
                                lo = mid + 1
                        else:
                            if nums[mid] < target <= nums[hi]:
                                lo = mid + 1
                            else:
                                hi = mid - 1
                    return -1
            """),
        "cases": [[[4, 5, 6, 7, 0, 1, 2], 0], [[4, 5, 6, 7, 0, 1, 2], 3], [[1], 0], [[1], 1], [[3, 1], 1], [[1, 3], 3], [[5, 1, 3], 5], [[6, 7, 1, 2, 3, 4, 5], 7], [[2, 3, 4, 5, 6, 7, 1], 1]],
        "rand": lambda rng: (lambda nums: [nums, rng.choice(nums + [99])])(_rotated_rand(rng)),
    },
    {
        "id": 153, "slug": "find-minimum-in-rotated-sorted-array", "title_en": "Find Minimum in Rotated Sorted Array",
        "title_ru": "Минимум в сдвинутом списке", "difficulty": "Medium", "week": 11,
        "pattern": "binary-search", "pattern_ru": "бинарный поиск по условию",
        "leetcode_url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/",
        "statement_ru": d("""\
            Список разных чисел был отсортирован и циклически сдвинут (как в #33).
            Верните его минимальный элемент за O(log n)."""),
        "examples": [
            {"input": "nums = [3,4,5,1,2]", "output": "1", "explain_ru": ""},
            {"input": "nums = [11,13,15,17]", "output": "11", "explain_ru": "Сдвиг на 0."},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 5000", "Все числа разные"],
        "complexity_target": "O(log n)",
        "starter_code": "class Solution:\n    def findMin(self, nums: List[int]) -> int:\n        pass\n",
        "method": "findMin", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Сравните средний элемент с последним. Если средний больше последнего, где тогда находится «обрыв» — место, где числа падают?",
            "Бинарный поиск по условию: `nums[mid] > nums[hi]` значит, что минимум правее `mid`. Иначе правая часть от `mid` отсортирована, и минимум в `[lo, mid]`; сам `mid` может быть минимумом. Инвариант: минимум всегда в `[lo, hi]`.",
            "1) `lo, hi = 0, n - 1`. 2) Пока `lo < hi`: `mid = (lo + hi) // 2`; если `nums[mid] > nums[hi]` — `lo = mid + 1`, иначе `hi = mid`. 3) Верните `nums[lo]`. Несдвинутый список и один элемент тоже работают.",
        ],
        "brute": lambda nums: min(nums),
        "ref": d("""\
            class Solution:
                def findMin(self, nums):
                    lo, hi = 0, len(nums) - 1
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if nums[mid] > nums[hi]:
                            lo = mid + 1
                        else:
                            hi = mid
                    return nums[lo]
            """),
        "cases": [[[3, 4, 5, 1, 2]], [[11, 13, 15, 17]], [[4, 5, 6, 7, 0, 1, 2]], [[1]], [[2, 1]], [[1, 2]], [[5, 1, 2, 3, 4]], [[2, 3, 4, 5, 1]]],
        "rand": lambda rng: [_rotated_rand(rng)],
    },
    {
        "id": 739, "slug": "daily-temperatures", "title_en": "Daily Temperatures",
        "title_ru": "Ждать тепла", "difficulty": "Medium", "week": 11,
        "pattern": "monotonic-stack", "pattern_ru": "монотонный стек",
        "leetcode_url": "https://leetcode.com/problems/daily-temperatures/",
        "statement_ru": d("""\
            `temperatures[i]` — температура в день `i`. Для каждого дня верните, сколько дней
            ждать до более тёплого дня. Если теплее уже не будет, поставьте `0`."""),
        "examples": [
            {"input": "temperatures = [73,74,75,71,69,72,76,73]", "output": "[1,1,4,2,1,1,0,0]", "explain_ru": "После 75 теплее станет только в день 6 (76): ждать 4 дня."},
            {"input": "temperatures = [30,40,50,60]", "output": "[1,1,1,0]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(temperatures) ≤ 10^5", "30 ≤ temperatures[i] ≤ 100"],
        "complexity_target": "O(n)",
        "starter_code": "class Solution:\n    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:\n        pass\n",
        "method": "dailyTemperatures", "arg_types": ["list[int]"], "ret_type": "list[int]",
        "hints_ru": [
            "Искать для каждого дня вперёд — O(n²). Посмотрите наоборот: пришёл тёплый день. Для каких прошлых дней он сразу даёт ответ?",
            "Монотонный стек индексов дней, для которых ответ ещё не найден. Температуры в стеке убывают снизу вверх. Новый день снимает все более холодные дни сверху. Каждый индекс входит и выходит один раз — O(n).",
            "1) `answer = [0] * n`, `stack = []`. 2) Для `i, t`: пока стек не пуст и `temperatures[stack[-1]] < t` — `j = stack.pop()`, `answer[j] = i - j`. 3) Положите `i`. 4) Оставшиеся в стеке дни сохраняют 0. Равная температура — не теплее.",
        ],
        "brute": lambda t: [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))],
        "ref": d("""\
            class Solution:
                def dailyTemperatures(self, temperatures):
                    answer = [0] * len(temperatures)
                    stack = []
                    for i, t in enumerate(temperatures):
                        while stack and temperatures[stack[-1]] < t:
                            j = stack.pop()
                            answer[j] = i - j
                        stack.append(i)
                    return answer
            """),
        "naive": d("""\
            class Solution:
                def dailyTemperatures(self, temperatures):
                    n = len(temperatures)
                    answer = [0] * n
                    for i in range(n):
                        for j in range(i + 1, n):
                            if temperatures[j] > temperatures[i]:
                                answer[i] = j - i
                                break
                    return answer
            """),
        "cases": [[[73, 74, 75, 71, 69, 72, 76, 73]], [[30, 40, 50, 60]], [[30, 60, 90]], [[90, 60, 30]], [[50]], [[50, 50, 51]], [[100, 30, 100]]],
        "rand": lambda rng: [rand_ints(rng, 1, 10, 30, 40)],
        "perf": [d("""\
            def gen():
                n = 10**5
                return [[50] * (n - 1) + [100]]   # every day waits for the very last one
            """)],
    },
    {
        "id": 39, "slug": "combination-sum", "title_en": "Combination Sum",
        "title_ru": "Наборы с заданной суммой", "difficulty": "Medium", "week": 11,
        "pattern": "backtracking", "pattern_ru": "перебор с возвратом",
        "leetcode_url": "https://leetcode.com/problems/combination-sum/",
        "statement_ru": d("""\
            Даны разные положительные числа `candidates` и число `target`. Верните все разные
            наборы чисел из `candidates` с суммой `target`. Одно число можно брать сколько угодно раз.
            Наборы, которые отличаются только порядком, — один набор. Порядок не важен."""),
        "examples": [
            {"input": "candidates = [2,3,6,7], target = 7", "output": "[[2,2,3],[7]]", "explain_ru": ""},
            {"input": "candidates = [2,3,5], target = 8", "output": "[[2,2,2,2],[2,3,3],[3,5]]", "explain_ru": ""},
            {"input": "candidates = [2], target = 1", "output": "[]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(candidates) ≤ 30", "2 ≤ candidates[i] ≤ 40, все разные", "1 ≤ target ≤ 40"],
        "complexity_target": "Перебор; важно не порождать повторы",
        "starter_code": "class Solution:\n    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:\n        pass\n",
        "method": "combinationSum", "arg_types": ["list[int]", "int"], "ret_type": "list[list[int]]", "compare": "unordered_nested",
        "hints_ru": [
            "Наборы `[2,3]` и `[3,2]` — один и тот же. Как строить наборы так, чтобы каждый набор появлялся ровно в одном порядке?",
            "Перебор с возвратом (backtracking): добавляйте числа только в неубывающем порядке индексов. После `candidates[i]` можно брать `candidates[i:]` — то же число снова, но не более ранние. Так каждый набор строится один раз.",
            "1) `backtrack(start, remaining)`. 2) `remaining == 0` — сохраните копию `path[:]`. 3) Для `i` от `start`: если `candidates[i] <= remaining` — `path.append`, рекурсия `backtrack(i, remaining - c)`, `path.pop()`. 4) Запуск `backtrack(0, target)`. Копия нужна: `path` дальше меняется.",
        ],
        "brute": _combination_brute,
        "ref": d("""\
            class Solution:
                def combinationSum(self, candidates, target):
                    out = []
                    path = []
                    def backtrack(start, remaining):
                        if remaining == 0:
                            out.append(path[:])
                            return
                        for i in range(start, len(candidates)):
                            c = candidates[i]
                            if c <= remaining:
                                path.append(c)
                                backtrack(i, remaining - c)
                                path.pop()
                    backtrack(0, target)
                    return out
            """),
        "cases": [[[2, 3, 6, 7], 7], [[2, 3, 5], 8], [[2], 1], [[7, 3, 2], 18], [[5], 5], [[3, 4], 2], [[8, 7, 4, 3], 11]],
        "rand": lambda rng: [rng.sample(range(2, 9), rng.randint(1, 4)), rng.randint(1, 16)],
    },
    {
        "id": 300, "slug": "longest-increasing-subsequence", "title_en": "Longest Increasing Subsequence",
        "title_ru": "Наибольшая возрастающая подпоследовательность", "difficulty": "Medium", "week": 11,
        "pattern": "dp-1d", "pattern_ru": "DP O(n²) → бинарный поиск O(n log n)",
        "leetcode_url": "https://leetcode.com/problems/longest-increasing-subsequence/",
        "statement_ru": d("""\
            Дан список `nums`. Верните длину самой длинной **строго возрастающей**
            подпоследовательности (элементы не обязательно подряд, порядок сохраняется)."""),
        "examples": [
            {"input": "nums = [10,9,2,5,3,7,101,18]", "output": "4", "explain_ru": "Например, 2, 3, 7, 101."},
            {"input": "nums = [7,7,7,7]", "output": "1", "explain_ru": "Строго возрастающая: равные не подходят."},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 2500", "-10^4 ≤ nums[i] ≤ 10^4"],
        "complexity_target": "O(n²) — зачёт, O(n log n) — бонус",
        "starter_code": "class Solution:\n    def lengthOfLIS(self, nums: List[int]) -> int:\n        pass\n",
        "method": "lengthOfLIS", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Подпоследовательность заканчивается на `nums[i]`. Что нужно знать про более ранние элементы, чтобы продлить её?",
            "Динамическое программирование: `dp[i]` — длина лучшей подпоследовательности, которая заканчивается на `nums[i]`; `dp[i] = 1 + max(dp[j])` для `j < i`, `nums[j] < nums[i]`. Это O(n²). Быстрее: `tails[k]` — наименьший хвост подпоследовательности длины k + 1. Список `tails` возрастает, поэтому подходит бинарный поиск.",
            "1) `tails = []`. 2) Для `x`: `i = bisect_left(tails, x)`. 3) `i == len(tails)` — `tails.append(x)`, иначе `tails[i] = x`. 4) Верните `len(tails)`. `bisect_left` важен для строгого возрастания: `[7,7,7]` → 1.",
        ],
        "brute": lambda nums: max(_lis_from(tuple(nums), i) for i in range(len(nums))),
        "ref": d("""\
            class Solution:
                def lengthOfLIS(self, nums):
                    tails = []
                    for x in nums:
                        i = bisect_left(tails, x)
                        if i == len(tails):
                            tails.append(x)
                        else:
                            tails[i] = x
                    return len(tails)
            """),
        "cases": [[[10, 9, 2, 5, 3, 7, 101, 18]], [[7, 7, 7, 7]], [[0, 1, 0, 3, 2, 3]], [[1]], [[5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5]], [[4, 10, 4, 3, 8, 9]], [[3, 5, 6, 2, 5, 4, 19, 5, 6, 7, 12]]],
        "rand": lambda rng: [rand_ints(rng, 1, 10, -5, 5)],
    },
    # ---------------------------------------------------------------- Week 12
    {
        "id": 155, "slug": "min-stack", "title_en": "Min Stack", "kind": "design",
        "title_ru": "Стек с минимумом", "difficulty": "Medium", "week": 12,
        "pattern": "stack-design", "pattern_ru": "проектирование класса: стек пар",
        "leetcode_url": "https://leetcode.com/problems/min-stack/",
        "statement_ru": d("""\
            Напишите класс `MinStack`. Все операции — за O(1):
            - `push(val)` — положить число;
            - `pop()` — убрать верхнее число;
            - `top()` — вернуть верхнее число;
            - `getMin()` — вернуть минимум среди всех чисел в стеке.

            Тест — это последовательность вызовов: `ops[i]` — имя метода, `args[i]` — его аргументы.
            `pop`, `top`, `getMin` вызываются только на непустом стеке."""),
        "examples": [
            {"input": 'ops = ["MinStack","push","push","push","getMin","pop","top","getMin"]\nargs = [[],[-2],[0],[-3],[],[],[],[]]',
             "output": "[null,null,null,null,-3,null,0,-2]", "explain_ru": "После pop() число -3 ушло, минимум снова -2."},
        ],
        "constraints_ru": ["-2^31 ≤ val ≤ 2^31 − 1", "До 3·10^4 вызовов"],
        "complexity_target": "O(1) на каждую операцию",
        "starter_code": "class MinStack:\n\n    def __init__(self):\n        pass\n\n    def push(self, val: int) -> None:\n        pass\n\n    def pop(self) -> None:\n        pass\n\n    def top(self) -> int:\n        pass\n\n    def getMin(self) -> int:\n        pass\n",
        "method": "MinStack", "arg_types": [], "ret_type": None,
        "hints_ru": [
            "`min(self.data)` — O(n). После `pop` минимум может вернуться к старому значению. Откуда его взять за O(1)?",
            "Стек пар: вместе с числом храните минимум стека на момент его добавления. При `pop` пара уходит, и вершина сразу знает прошлый минимум. Инвариант: вторая часть верхней пары — минимум всего стека.",
            "1) `push(val)`: новый минимум — `min(val, текущий минимум)`, или `val` для пустого стека; положите пару. 2) `pop`: снимите пару. 3) `top`: `data[-1][0]`. 4) `getMin`: `data[-1][1]`.",
        ],
        "brute": _min_stack_brute,
        "ref": d("""\
            class MinStack:
                def __init__(self):
                    self.data = []
                def push(self, val):
                    self.data.append((val, min(val, self.data[-1][1]) if self.data else val))
                def pop(self):
                    self.data.pop()
                def top(self):
                    return self.data[-1][0]
                def getMin(self):
                    return self.data[-1][1]
            """),
        "cases": [[["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"], [[], [-2], [0], [-3], [], [], [], []]],
                  [["MinStack", "push", "getMin", "top"], [[], [5], [], []]],
                  [["MinStack", "push", "push", "getMin", "pop", "getMin"], [[], [1], [1], [], [], []]],
                  [["MinStack", "push", "push", "push", "getMin", "pop", "getMin", "pop", "getMin"], [[], [3], [2], [1], [], [], [], [], []]]],
        "visible": 1,
        "rand": _min_stack_rand,
    },
    {
        "id": 875, "slug": "koko-eating-bananas", "title_en": "Koko Eating Bananas",
        "title_ru": "Коко и бананы", "difficulty": "Medium", "week": 12,
        "pattern": "binary-search-answer", "pattern_ru": "бинарный поиск по ответу",
        "leetcode_url": "https://leetcode.com/problems/koko-eating-bananas/",
        "statement_ru": d("""\
            Есть кучки бананов `piles`. Обезьянка Коко ест со скоростью `k` бананов в час:
            каждый час она выбирает одну кучку и съедает из неё `k` бананов (если в кучке меньше —
            съедает всю, и остаток часа отдыхает). Найдите наименьшее целое `k`, при котором Коко
            съест всё за `h` часов."""),
        "examples": [
            {"input": "piles = [3,6,7,11], h = 8", "output": "4", "explain_ru": "При k = 4: 1 + 2 + 2 + 3 = 8 часов."},
            {"input": "piles = [30,11,23,4,20], h = 5", "output": "30", "explain_ru": "По часу на кучку — нужно k = max(piles)."},
        ],
        "constraints_ru": ["1 ≤ len(piles) ≤ h ≤ 10^9", "1 ≤ piles[i] ≤ 10^9", "len(piles) ≤ 10^4"],
        "complexity_target": "O(n log max(piles))",
        "starter_code": "class Solution:\n    def minEatingSpeed(self, piles: List[int], h: int) -> int:\n        pass\n",
        "method": "minEatingSpeed", "arg_types": ["list[int]", "int"], "ret_type": "int",
        "hints_ru": [
            "Возьмите конкретную скорость `k`. Сколько часов нужно Коко? Как меняется это число, если увеличивать `k`?",
            "Бинарный поиск по ответу: число часов `sum(ceil(p / k))` не растёт с ростом `k` — функция монотонна. Ищите наименьшее `k` в `[1, max(piles)]`, при котором часов ≤ `h`. При `k = max(piles)` каждая кучка съедается за 1 час.",
            "1) `lo, hi = 1, max(piles)`. 2) Пока `lo < hi`: `mid`; часы `sum((p + mid - 1) // mid for p in piles)`. 3) Часов ≤ h — `hi = mid`; иначе `lo = mid + 1`. 4) Верните `lo`. Целочисленный `ceil` без `float` избегает ошибок округления.",
        ],
        "brute": _koko_brute,
        "ref": d("""\
            class Solution:
                def minEatingSpeed(self, piles, h):
                    lo, hi = 1, max(piles)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if sum((p + mid - 1) // mid for p in piles) <= h:
                            hi = mid
                        else:
                            lo = mid + 1
                    return lo
            """),
        "naive": d("""\
            class Solution:
                def minEatingSpeed(self, piles, h):
                    k = 1
                    while sum((p + k - 1) // k for p in piles) > h:
                        k += 1
                    return k
            """),
        "cases": [[[3, 6, 7, 11], 8], [[30, 11, 23, 4, 20], 5], [[30, 11, 23, 4, 20], 6], [[1], 1], [[1000000000], 2], [[312884470], 968709470], [[2, 2], 4], [[5, 5, 5], 3]],
        "rand": _koko_rand,
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(875)
                piles = [rng.randint(10**8, 10**9) for _ in range(1000)]
                return [piles, 1000 + 10**5]
            """)],
    },
    {
        "id": 19, "slug": "remove-nth-node-from-end-of-list", "title_en": "Remove Nth Node From End of List",
        "title_ru": "Удалить n-й узел с конца", "difficulty": "Medium", "week": 12,
        "pattern": "two-pointers-gap", "pattern_ru": "два указателя с отставанием",
        "leetcode_url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/",
        "statement_ru": d("""\
            Удалите из связного списка `n`-й узел с конца и верните голову списка.
            Попробуйте сделать это за один проход."""),
        "examples": [
            {"input": "head = [1,2,3,4,5], n = 2", "output": "[1,2,3,5]", "explain_ru": "Второй с конца — 4."},
            {"input": "head = [1], n = 1", "output": "[]", "explain_ru": ""},
            {"input": "head = [1,2], n = 2", "output": "[2]", "explain_ru": "Удаляется голова."},
        ],
        "constraints_ru": ["1 ≤ число узлов ≤ 30", "1 ≤ n ≤ число узлов"],
        "complexity_target": "O(L), один проход",
        "starter_code": LIST_NODE_DOC + "class Solution:\n    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:\n        pass\n",
        "method": "removeNthFromEnd", "arg_types": ["ListNode", "int"], "ret_type": "ListNode",
        "hints_ru": [
            "За два прохода просто: посчитать длину и дойти до узла перед удаляемым. Как за один проход узнать, что до конца осталось ровно `n` узлов?",
            "Два указателя с отставанием: быстрый уходит на `n` шагов вперёд, затем оба идут вместе. Расстояние между ними всё время `n`. Когда быстрый на последнем узле, медленный — перед удаляемым. Фиктивный узел `dummy` перед головой убирает особый случай «удалить голову».",
            "1) `dummy = ListNode(0, head)`; `fast = slow = dummy`. 2) `fast` делает `n` шагов. 3) Пока `fast.next`: сдвигайте оба. 4) `slow.next = slow.next.next`. 5) Верните `dummy.next`. Список из одного узла, n = 1 → пустой список.",
        ],
        "brute": lambda values, n: values[: len(values) - n] + values[len(values) - n + 1 :],
        "ref": d("""\
            class Solution:
                def removeNthFromEnd(self, head, n):
                    dummy = ListNode(0, head)
                    fast = slow = dummy
                    for _ in range(n):
                        fast = fast.next
                    while fast.next:
                        fast, slow = fast.next, slow.next
                    slow.next = slow.next.next
                    return dummy.next
            """),
        "cases": [[[1, 2, 3, 4, 5], 2], [[1], 1], [[1, 2], 2], [[1, 2], 1], [[1, 2, 3], 3], [[1, 2, 3], 1], [[5, 6, 7, 8], 2]],
        "rand": lambda rng: (lambda v: [v, rng.randint(1, len(v))])(rand_ints(rng, 1, 9, 0, 9)),
    },
    {
        "id": 74, "slug": "search-a-2d-matrix", "title_en": "Search a 2D Matrix",
        "title_ru": "Поиск в матрице", "difficulty": "Medium", "week": 12,
        "pattern": "binary-search", "pattern_ru": "бинарный поиск по «развёрнутой» матрице",
        "leetcode_url": "https://leetcode.com/problems/search-a-2d-matrix/",
        "statement_ru": d("""\
            Матрица `m × n`: каждая строка отсортирована, и первое число строки больше последнего
            числа предыдущей строки. Верните `True`, если `target` есть в матрице. Нужно O(log(m·n))."""),
        "examples": [
            {"input": "matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3", "output": "true", "explain_ru": ""},
            {"input": "matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13", "output": "false", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ m, n ≤ 100"],
        "complexity_target": "O(log(m · n))",
        "starter_code": "class Solution:\n    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:\n        pass\n",
        "method": "searchMatrix", "arg_types": ["list[list[int]]", "int"], "ret_type": "bool",
        "hints_ru": [
            "Выпишите все строки матрицы подряд в одну линию. Какой список получится? Можно ли искать в нём, не создавая его?",
            "Бинарный поиск по «развёрнутой» матрице: индекс `i` линии — это клетка `matrix[i // n][i % n]`, где `n` — число столбцов. Так поиск идёт за O(log(m·n)) без лишней памяти.",
            "1) `n = len(matrix[0])`; `lo, hi = 0, m * n - 1`. 2) Пока `lo <= hi`: `mid`; `v = matrix[mid // n][mid % n]`. 3) Равно — `True`; `v < target` — `lo = mid + 1`; иначе `hi = mid - 1`. 4) Верните `False`.",
        ],
        "brute": lambda matrix, target: any(target in row for row in matrix),
        "ref": d("""\
            class Solution:
                def searchMatrix(self, matrix, target):
                    n = len(matrix[0])
                    lo, hi = 0, len(matrix) * n - 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        v = matrix[mid // n][mid % n]
                        if v == target:
                            return True
                        if v < target:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    return False
            """),
        "cases": [[[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3], [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13], [[[1]], 1], [[[1]], 2],
                  [[[1, 3]], 3], [[[1], [3]], 3], [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 60], [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 0]],
        "rand": lambda rng: (lambda m, n: (lambda flat: [[flat[i * n:(i + 1) * n] for i in range(m)], rng.choice(flat + [rng.randint(-40, 40)])])(sorted(rng.sample(range(-40, 40), m * n))))(rng.randint(1, 4), rng.randint(1, 4)),
    },
    {
        "id": 53, "slug": "maximum-subarray", "title_en": "Maximum Subarray",
        "title_ru": "Подмассив с наибольшей суммой", "difficulty": "Medium", "week": 12,
        "pattern": "kadane", "pattern_ru": "алгоритм Кадане",
        "leetcode_url": "https://leetcode.com/problems/maximum-subarray/",
        "statement_ru": d("""\
            Дан список `nums`. Найдите непустой подмассив (идущие подряд элементы) с наибольшей
            суммой и верните эту сумму."""),
        "examples": [
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explain_ru": "Подмассив [4,-1,2,1]."},
            {"input": "nums = [1]", "output": "1", "explain_ru": ""},
            {"input": "nums = [5,4,-1,7,8]", "output": "23", "explain_ru": "Весь список."},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10^5", "-10^4 ≤ nums[i] ≤ 10^4"],
        "complexity_target": "O(n)",
        "starter_code": "class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:\n        pass\n",
        "method": "maxSubArray", "arg_types": ["list[int]"], "ret_type": "int",
        "hints_ru": [
            "Возьмите лучший подмассив, который кончается на предыдущем элементе. Когда выгодно продолжить его текущим элементом, а когда начать заново?",
            "Алгоритм Кадане: `cur` — лучшая сумма подмассива, который кончается на текущем элементе. Отрицательный «хвост» только уменьшает сумму, поэтому `cur = max(x, cur + x)`. Ответ — максимум `cur` по всем позициям.",
            "1) `cur = best = nums[0]`. 2) Для `x` в `nums[1:]`: `cur = max(x, cur + x)`; `best = max(best, cur)`. 3) Верните `best`. Старт с `nums[0]`, а не с 0, нужен для списка из одних отрицательных чисел.",
        ],
        "brute": lambda nums: max(sum(nums[i:j + 1]) for i in range(len(nums)) for j in range(i, len(nums))),
        "ref": d("""\
            class Solution:
                def maxSubArray(self, nums):
                    cur = best = nums[0]
                    for x in nums[1:]:
                        cur = max(x, cur + x)
                        best = max(best, cur)
                    return best
            """),
        "naive": d("""\
            class Solution:
                def maxSubArray(self, nums):
                    best = nums[0]
                    for i in range(len(nums)):
                        s = 0
                        for j in range(i, len(nums)):
                            s += nums[j]
                            best = max(best, s)
                    return best
            """),
        "cases": [[[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[1]], [[5, 4, -1, 7, 8]], [[-1]], [[-3, -1, -2]], [[0, 0]], [[2, -1, 2]], [[-2, 1]], [[1, -10, 1, 1]]],
        "rand": lambda rng: [rand_ints(rng, 1, 10, -6, 6)],
        "perf": [d("""\
            def gen():
                import random
                rng = random.Random(53)
                return [[rng.randint(-10**4, 10**4) for _ in range(10**5)]]
            """)],
    },
    # ---------------------------------------------------------------- Week 13 (mock interview)
    {
        "id": 146, "slug": "lru-cache", "title_en": "LRU Cache", "kind": "design",
        "title_ru": "LRU-кэш", "difficulty": "Medium", "week": 13,
        "pattern": "hash-map-linked-list", "pattern_ru": "словарь + двусвязный список",
        "leetcode_url": "https://leetcode.com/problems/lru-cache/",
        "statement_ru": d("""\
            Напишите класс `LRUCache(capacity)` — кэш на `capacity` ключей:
            - `get(key)` — вернуть значение или `-1`, если ключа нет;
            - `put(key, value)` — записать значение. Если ключей стало больше `capacity`,
              удалить ключ, к которому дольше всего не обращались (least recently used).

            И `get`, и `put` считаются обращением к ключу. Обе операции — за O(1).
            Решите сначала без `OrderedDict`: так спросят на собеседовании."""),
        "examples": [
            {"input": 'ops = ["LRUCache","put","put","get","put","get","put","get","get","get"]\nargs = [[2],[1,1],[2,2],[1],[3,3],[2],[4,4],[1],[3],[4]]',
             "output": "[null,null,null,1,null,-1,null,-1,3,4]", "explain_ru": "put(3) вытесняет ключ 2: к ключу 1 обращались позже."},
        ],
        "constraints_ru": ["1 ≤ capacity ≤ 3000", "До 2·10^5 вызовов"],
        "complexity_target": "O(1) на get и put",
        "starter_code": "class LRUCache:\n\n    def __init__(self, capacity: int):\n        pass\n\n    def get(self, key: int) -> int:\n        pass\n\n    def put(self, key: int, value: int) -> None:\n        pass\n",
        "method": "LRUCache", "arg_types": [], "ret_type": None,
        "hints_ru": [
            "Нужны две операции за O(1): найти значение по ключу и найти ключ, к которому дольше всего не обращались. Может ли одна обычная структура дать обе?",
            "Словарь + двусвязный список. Словарь: ключ → узел, поиск O(1). Список хранит порядок обращений: свежие — в конце, старый — в начале. Узел двусвязного списка можно вынуть за O(1), если он известен. В Python есть короткий путь: `dict` хранит порядок вставки, а `pop` и повторная вставка переносят ключ в конец.",
            "1) Фиктивные узлы `head` и `tail` убирают особые случаи. 2) `get`: ключа нет — `-1`; есть — перенесите узел в конец, верните значение. 3) `put`: удалите старый узел ключа, вставьте новый в конец. 4) Больше `capacity` — удалите `head.next` и его ключ из словаря. Вариант на `dict`: самый старый ключ — `next(iter(self.data))`.",
        ],
        "brute": _lru_brute,
        "ref": d("""\
            class LRUCache:
                def __init__(self, capacity):
                    self.cap = capacity
                    self.data = {}
                def get(self, key):
                    if key not in self.data:
                        return -1
                    self.data[key] = self.data.pop(key)
                    return self.data[key]
                def put(self, key, value):
                    self.data.pop(key, None)
                    self.data[key] = value
                    if len(self.data) > self.cap:
                        del self.data[next(iter(self.data))]
            """),
        "cases": [[["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]],
                  [["LRUCache", "put", "get", "put", "get", "get"], [[1], [2, 1], [2], [3, 2], [2], [3]]],
                  [["LRUCache", "put", "put", "put", "put", "get", "get"], [[2], [2, 1], [1, 1], [2, 3], [4, 1], [1], [2]]],
                  [["LRUCache", "get", "put", "get"], [[1], [5], [5, 7], [5]]]],
        "visible": 1,
        "rand": _lru_rand,
    },
    {
        "id": 5, "slug": "longest-palindromic-substring", "title_en": "Longest Palindromic Substring",
        "title_ru": "Самая длинная подстрока-палиндром", "difficulty": "Medium", "week": 13,
        "pattern": "expand-around-center", "pattern_ru": "расширение от центра",
        "leetcode_url": "https://leetcode.com/problems/longest-palindromic-substring/",
        "statement_ru": d("""\
            Дана строка `s`. Верните самую длинную подстроку `s`, которая является палиндромом.
            Если таких несколько, подходит любая."""),
        "examples": [
            {"input": 's = "babad"', "output": '"bab"', "explain_ru": '"aba" тоже верно.'},
            {"input": 's = "cbbd"', "output": '"bb"', "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(s) ≤ 1000", "Латинские буквы и цифры"],
        "complexity_target": "O(n²) по времени, O(1) по памяти",
        "starter_code": "class Solution:\n    def longestPalindrome(self, s: str) -> str:\n        pass\n",
        "method": "longestPalindrome", "arg_types": ["str"], "ret_type": "str", "compare": "check",
        "check": d("""\
            def check(args, result, expected):
                s = args[0]
                return isinstance(result, str) and len(result) == len(expected) and result in s and result == result[::-1]
            """),
        "hints_ru": [
            "Проверка всех подстрок — O(n³). Палиндром симметричен относительно центра. Откуда тогда удобнее его строить: с краёв или из середины?",
            "Расширение от центра. Центров `2n - 1`: каждый символ (нечётная длина) и каждый промежуток между соседями (чётная длина). От центра расширяйте края, пока символы равны. Итого O(n²) времени и O(1) памяти.",
            "1) Для `c` от 0 до `2n - 2`: `l, r = c // 2, (c + 1) // 2`. 2) Пока `l >= 0`, `r < n` и `s[l] == s[r]`: `l -= 1`, `r += 1`. 3) Палиндром — `s[l + 1:r]`; длиннее лучшего — запомните. Строка из одного символа — она сама.",
        ],
        "brute": _palindrome_brute,
        "ref": d("""\
            class Solution:
                def longestPalindrome(self, s):
                    best = ""
                    for c in range(2 * len(s) - 1):
                        l, r = c // 2, (c + 1) // 2
                        while l >= 0 and r < len(s) and s[l] == s[r]:
                            l -= 1
                            r += 1
                        if r - l - 1 > len(best):
                            best = s[l + 1:r]
                    return best
            """),
        "cases": [["babad"], ["cbbd"], ["a"], ["ac"], ["aaaa"], ["abacdfgdcaba"], ["forgeeksskeegfor"], ["xyzzyx"], ["abcba1"]],
        "rand": lambda rng: [rand_word(rng, 1, 10, "ab")],
    },
    {
        "id": 78, "slug": "subsets", "title_en": "Subsets",
        "title_ru": "Все подмножества", "difficulty": "Medium", "week": 13,
        "pattern": "backtracking", "pattern_ru": "перебор: брать или не брать",
        "leetcode_url": "https://leetcode.com/problems/subsets/",
        "statement_ru": d("""\
            Дан список **разных** чисел `nums`. Верните все его подмножества (включая пустое
            и сам список). Повторов быть не должно. Порядок любой."""),
        "examples": [
            {"input": "nums = [1,2,3]", "output": "[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]", "explain_ru": "2³ = 8 подмножеств."},
            {"input": "nums = [0]", "output": "[[],[0]]", "explain_ru": ""},
        ],
        "constraints_ru": ["1 ≤ len(nums) ≤ 10", "Все числа разные"],
        "complexity_target": "O(n · 2^n)",
        "starter_code": "class Solution:\n    def subsets(self, nums: List[int]) -> List[List[int]]:\n        pass\n",
        "method": "subsets", "arg_types": ["list[int]"], "ret_type": "list[list[int]]", "compare": "unordered_nested",
        "hints_ru": [
            "Для каждого элемента есть ровно два решения. Какие? Сколько тогда всего подмножеств у списка из n элементов?",
            "Перебор «брать или не брать»: рекурсия по индексу `i`, на каждом шаге две ветки. Дошли до конца — сохраните копию текущего набора. Другой путь — итеративно: каждое новое число удваивает ответ, добавляясь ко всем уже собранным подмножествам.",
            "1) `go(i)`: если `i == len(nums)` — сохраните `path[:]`. 2) Ветка «не брать»: `go(i + 1)`. 3) Ветка «брать»: `path.append(nums[i])`, `go(i + 1)`, `path.pop()`. 4) Запуск `go(0)`. Итеративно: `out = [[]]`; для `x`: `out += [s + [x] for s in out]`.",
        ],
        "brute": _subsets_brute,
        "ref": d("""\
            class Solution:
                def subsets(self, nums):
                    out = []
                    path = []
                    def go(i):
                        if i == len(nums):
                            out.append(path[:])
                            return
                        go(i + 1)
                        path.append(nums[i])
                        go(i + 1)
                        path.pop()
                    go(0)
                    return out
            """),
        "cases": [[[1, 2, 3]], [[0]], [[5, -5]], [[1, 2, 3, 4]], [[9, 0, 3, 1, 7]]],
        "rand": lambda rng: [rng.sample(range(-9, 10), rng.randint(1, 5))],
    },
]
