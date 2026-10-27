"""Week 2 content: iterators/generators, decorators, context managers, exceptions, OOP, GIL; linear algebra."""

from textwrap import dedent as d

QUIZZES = {
    "q-w2-gen": {
        "title": "Итераторы и генераторы",
        "questions": [
            {"type": "output", "code": "g = (x * x for x in range(3))\nprint(list(g))\nprint(list(g))",
             "explain": "Генератор одноразовый: после первого прохода он исчерпан, второй `list` пустой."},
            {"type": "output", "code": "def gen():\n    print(\"старт\")\n    yield 1\n    print(\"после 1\")\n    yield 2\n\ng = gen()\nprint(\"создан\")\nprint(next(g))\nprint(next(g))",
             "explain": "Тело генератора не выполняется при вызове `gen()`. Оно идёт до ближайшего `yield` при каждом `next`."},
            {"type": "output", "code": "def gen():\n    yield 1\n\ng = gen()\nnext(g)\ntry:\n    next(g)\nexcept StopIteration:\n    print(\"StopIteration\")",
             "explain": "Когда тело генератора закончилось, `next` бросает `StopIteration`. Цикл `for` ловит его сам."},
            {"type": "output", "code": "def inner():\n    yield 1\n    yield 2\n\ndef outer():\n    yield 0\n    yield from inner()\n    yield 3\n\nprint(list(outer()))",
             "explain": "`yield from` отдаёт все значения вложенного итератора по очереди."},
            {"type": "output", "code": "it = iter([10, 20, 30])\nfor x in it:\n    print(x)\n    break\nprint(list(it))",
             "explain": "Итератор помнит позицию. `for` с `break` взял только первый элемент; остаток можно дочитать."},
            {"type": "output", "code": "import sys\nprint(sys.getsizeof(range(10**6)) < 100, sys.getsizeof([0] * 10**6) > 10**6)",
             "explain": "`range` и генераторы не хранят все значения — они вычисляют их по запросу. Список хранит миллион ссылок (≈8 МБ)."},
            {"type": "choice", "q": "Чем генератор отличается от списка?",
             "options": ["Генератор быстрее при любом доступе по индексу", "Генератор ленивый: значения вычисляются по одному по запросу, он одноразовый и не поддерживает индексы",
                         "Генератор хранит значения в словаре", "Ничем, это синоним"],
             "answer": 1, "explain": "Память O(1) вместо O(n); бесконечные последовательности возможны; но `g[5]` и повторный проход — нет."},
            {"type": "multi", "q": "Какие объекты — итераторы (у них есть `__next__`)?",
             "options": ["`[1, 2, 3]`", "`iter([1, 2, 3])`", "`(x for x in range(3))`", "`range(3)`"],
             "answers": [1, 2], "explain": "Список и `range` — итерируемые (`__iter__`), но не итераторы. `iter(...)` и генератор — итераторы."},
        ],
    },
    "q-w2-deco": {
        "title": "Декораторы, контекстные менеджеры, исключения",
        "questions": [
            {"type": "output", "code": "def shout(f):\n    def wrapper(*a, **k):\n        return f(*a, **k).upper()\n    return wrapper\n\n@shout\ndef hello(name):\n    return f\"hi {name}\"\n\nprint(hello(\"ann\"))",
             "explain": "`@shout` — это `hello = shout(hello)`. Вызов идёт через `wrapper`."},
            {"type": "output", "code": "def deco(f):\n    def wrapper():\n        return f()\n    return wrapper\n\n@deco\ndef work():\n    \"\"\"docs\"\"\"\n\nprint(work.__name__)",
             "explain": "Без `functools.wraps` у функции имя и docstring обёртки. Это ломает отладку и документацию."},
            {"type": "output", "code": "import functools\n\ndef deco(f):\n    @functools.wraps(f)\n    def wrapper():\n        return f()\n    return wrapper\n\n@deco\ndef work():\n    pass\n\nprint(work.__name__)",
             "explain": "`functools.wraps` копирует `__name__`, `__doc__` и др. и ставит `__wrapped__`."},
            {"type": "output", "code": "def tag(name):\n    def deco(f):\n        def wrapper():\n            return f\"<{name}>{f()}</{name}>\"\n        return wrapper\n    return deco\n\n@tag(\"b\")\n@tag(\"i\")\ndef text():\n    return \"x\"\n\nprint(text())",
             "explain": "Декоратор с параметром — это фабрика: `tag(\"b\")` возвращает декоратор. Декораторы применяются снизу вверх: `tag('b')(tag('i')(text))`."},
            {"type": "output", "code": "def f():\n    try:\n        print(\"try\")\n        return 1\n    except ValueError:\n        print(\"except\")\n    else:\n        print(\"else\")\n    finally:\n        print(\"finally\")\n\nprint(f())",
             "explain": "`return` внутри `try` пропускает `else`, но `finally` выполняется всегда — до фактического выхода из функции."},
            {"type": "output", "code": "class Box:\n    def __enter__(self):\n        print(\"enter\")\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        print(\"exit\", exc_type.__name__ if exc_type else None)\n        return True\n\nwith Box():\n    print(\"body\")\n    raise KeyError(\"k\")\nprint(\"after\")",
             "explain": "`__exit__` вызывается и при исключении. Если он вернул `True`, исключение подавлено и код идёт дальше."},
            {"type": "output", "code": "from contextlib import contextmanager\n\n@contextmanager\ndef step(name):\n    print(\"start\", name)\n    try:\n        yield name.upper()\n    finally:\n        print(\"stop\", name)\n\nwith step(\"a\") as s:\n    print(s)",
             "explain": "`@contextmanager`: код до `yield` — это `__enter__`, после — `__exit__`. `try/finally` нужен, чтобы «stop» выполнился и при ошибке."},
            {"type": "output", "code": "try:\n    try:\n        1 / 0\n    except ZeroDivisionError as e:\n        raise ValueError(\"плохие данные\") from e\nexcept ValueError as e:\n    print(type(e.__cause__).__name__)",
             "explain": "`raise ... from e` сохраняет исходную причину в `__cause__` — traceback покажет обе ошибки."},
            {"type": "text", "q": "напишите (мысленно или на бумаге) декоратор `timer`, который печатает время работы функции и возвращает её результат. Что в нём обязательно?",
             "model": "Обёртка `wrapper(*args, **kwargs)`, внутри `start = time.perf_counter()`, вызов `result = func(*args, **kwargs)`, печать `perf_counter() - start`, `return result`. Плюс `@functools.wraps(func)`. Для точности — `perf_counter`, не `time.time`."},
        ],
    },
    "q-w2-oop": {
        "title": "ООП: staticmethod, classmethod, MRO, super, dunder, dataclasses",
        "questions": [
            {"type": "output", "code": "class A:\n    count = 0\n    @classmethod\n    def make(cls):\n        cls.count += 1\n        return cls()\n    @staticmethod\n    def add(a, b):\n        return a + b\n\nclass B(A):\n    pass\n\nprint(type(B.make()).__name__, A.add(2, 3))",
             "explain": "`classmethod` получает класс, через который его вызвали (`B`) — удобно для фабрик в наследниках. `staticmethod` не получает ни `self`, ни `cls`."},
            {"type": "output", "code": "class A:\n    def hi(self): return \"A\"\nclass B(A):\n    def hi(self): return \"B\" + super().hi()\nclass C(A):\n    def hi(self): return \"C\" + super().hi()\nclass D(B, C):\n    def hi(self): return \"D\" + super().hi()\n\nprint(D().hi())\nprint([k.__name__ for k in D.__mro__])",
             "explain": "MRO (C3-линеаризация) для D: D, B, C, A, object. `super()` идёт к **следующему в MRO**, а не к родителю: из B — в C, а не в A."},
            {"type": "output", "code": "class V:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __add__(self, o):\n        return V(self.x + o.x, self.y + o.y)\n    def __repr__(self):\n        return f\"V({self.x}, {self.y})\"\n\nprint(V(1, 2) + V(3, 4))",
             "explain": "`a + b` вызывает `a.__add__(b)`; `print` использует `__repr__`, если нет `__str__`."},
            {"type": "output", "code": "class P:\n    def __init__(self, x):\n        self.x = x\n    def __eq__(self, o):\n        return self.x == o.x\n\ntry:\n    print({P(1)})\nexcept TypeError:\n    print(\"unhashable\")",
             "explain": "Если определить `__eq__` без `__hash__`, Python ставит `__hash__ = None`: объект перестаёт быть hashable (а ключом `dict` может быть только hashable-объект)."},
            {"type": "output", "code": "from dataclasses import dataclass, field\n\n@dataclass(frozen=True, order=True)\nclass Pt:\n    x: int\n    y: int = 0\n    tags: tuple = field(default=(), compare=False)\n\nprint(Pt(1) < Pt(1, 5), Pt(2, tags=(\"a\",)) == Pt(2), len({Pt(1), Pt(1)}))",
             "explain": "`order=True` сравнивает поля по порядку; `compare=False` исключает поле из сравнения; `frozen=True` делает объект неизменяемым и hashable."},
            {"type": "output", "code": "from dataclasses import dataclass\n\ntry:\n    @dataclass\n    class Bad:\n        items: list = []\nexcept ValueError:\n    print(\"ValueError: используйте field(default_factory=list)\")",
             "explain": "dataclasses защищают от ловушки `def f(x=[])` (общий список у всех вызовов): изменяемый default запрещён, нужен `field(default_factory=list)`."},
            {"type": "choice", "q": "Чем `@staticmethod` отличается от `@classmethod`?",
             "options": ["Ничем", "staticmethod — обычная функция в пространстве имён класса; classmethod получает первым аргументом класс (`cls`), через который вызван",
                         "classmethod нельзя вызвать у экземпляра", "staticmethod получает `self`"],
             "answer": 1, "explain": "Типичное применение classmethod — альтернативные конструкторы (`dict.fromkeys`, `datetime.fromisoformat`), которые работают и в наследниках."},
        ],
    },
    "q-w2-gil": {
        "title": "GIL: threading, multiprocessing, asyncio",
        "questions": [
            {"type": "choice", "q": "Что такое GIL в CPython?",
             "options": ["Блокировка, из-за которой байткод Python в одном процессе выполняет только один поток одновременно",
                         "Библиотека для GPU", "Механизм, запрещающий создавать больше одного потока", "Сборщик мусора"],
             "answer": 0, "explain": "Потоки создавать можно, но выполнять Python-код в один момент может только один. (С Python 3.13 есть экспериментальная сборка без GIL — free-threaded, но по умолчанию GIL есть.)"},
            {"type": "choice", "q": "CPU-тяжёлая функция на чистом Python (циклы, арифметика) в 4 потоках `threading` на 4 ядрах будет:",
             "options": ["≈ в 4 раза быстрее", "≈ так же или чуть медленнее, чем в одном потоке", "в 16 раз быстрее", "не запустится"],
             "answer": 1, "explain": "Из-за GIL потоки выполняют Python-байткод по очереди. Для CPU нужен `multiprocessing` / `ProcessPoolExecutor`: у каждого процесса свой интерпретатор и свой GIL."},
            {"type": "choice", "q": "Код, который в основном ждёт сеть или диск (I/O), в 10 потоках:",
             "options": ["не ускорится", "ускорится: во время ожидания I/O поток отпускает GIL, и другие потоки работают",
                         "упадёт с ошибкой GIL", "ускорится, только если процессор многоядерный"],
             "answer": 1, "explain": "`time.sleep`, сокеты, чтение файлов отпускают GIL. Поэтому потоки и `asyncio` хороши для ожидания."},
            {"type": "multi", "q": "Что выбрать для каких задач?",
             "options": ["CPU-тяжёлое (обработка чисел на Python) → multiprocessing", "Много сетевых запросов → threading или asyncio",
                         "CPU-тяжёлое → asyncio", "NumPy-операции над большими массивами часто отпускают GIL внутри C-кода"],
             "answers": [0, 1, 3], "explain": "asyncio — один поток, кооперативная многозадачность: CPU-работу он не распараллелит."},
            {"type": "text", "q": "Своими словами: что такое GIL, ускорят ли потоки CPU-код и код, который ждёт сеть?",
             "model": "GIL — глобальная блокировка интерпретатора CPython: в процессе байткод исполняет один поток за раз. CPU-код потоки не ускорят (нужны процессы). Код, ждущий сеть, ускорят: во время ожидания GIL отпускается, и ожидания идут параллельно."},
        ],
    },
    "q-w2-linalg1": {
        "title": "Векторы, линейные комбинации, матрицы как преобразования",
        "questions": [
            {"type": "vector", "q": "Сложите векторы (1, 2) + (3, −1)", "answer": [4, 1], "tol": 1e-9, "labels": ["x", "y"],
             "explain": "Покоординатно. Геометрически — «пройти первый вектор, затем второй»."},
            {"type": "vector", "q": "Вычислите 3·(1, −2) − 2·(0, 1)", "answer": [3, -8], "tol": 1e-9, "labels": ["x", "y"],
             "explain": "Это линейная комбинация векторов с коэффициентами 3 и −2."},
            {"type": "choice", "q": "Что такое линейная оболочка (span) векторов v и w на плоскости, если они не лежат на одной прямой?",
             "options": ["Только прямая", "Вся плоскость", "Только точка 0", "Отрезок между ними"], "answer": 1,
             "explain": "Все a·v + b·w покрывают всю плоскость. Если v и w коллинеарны — только прямую (они линейно зависимы)."},
            {"type": "choice", "q": "Столбцы матрицы 2×2 — это…",
             "options": ["Куда переходят базисные векторы î и ĵ", "Собственные значения", "Строки, записанные вертикально", "Координаты точки"],
             "answer": 0, "explain": "Главная идея 3Blue1Brown гл. 3: матрица записывает, куда преобразование отправляет î = (1, 0) и ĵ = (0, 1)."},
            {"type": "vector", "q": "A = [[2, 1], [0, 3]] (строки). Найдите A·(1, 2)", "answer": [4, 6], "tol": 1e-9, "labels": ["x", "y"],
             "explain": "1·(столбец 1) + 2·(столбец 2) = 1·(2, 0) + 2·(1, 3) = (4, 6)."},
            {"type": "vector", "q": "Преобразование поворачивает плоскость на 90° против часовой стрелки. Куда перейдёт вектор (3, 1)?", "answer": [-1, 3], "tol": 1e-9, "labels": ["x", "y"],
             "explain": "î → (0, 1), ĵ → (−1, 0). Матрица [[0, −1], [1, 0]]; (3, 1) → 3·(0, 1) + 1·(−1, 0) = (−1, 3)."},
            {"type": "vector", "q": "A = [[1, 2], [3, 4]], B = [[0, 1], [1, 0]]. Найдите первую строку A·B", "answer": [2, 1], "tol": 1e-9, "labels": ["(AB)₁₁", "(AB)₁₂"],
             "explain": "Строка A на столбцы B: (1·0 + 2·1, 1·1 + 2·0) = (2, 1). B меняет столбцы A местами."},
            {"type": "choice", "q": "A·B — это композиция преобразований. В каком порядке они применяются к вектору x в (A·B)·x?",
             "options": ["Сначала A, потом B", "Сначала B, потом A", "Одновременно", "Порядок не важен"], "answer": 1,
             "explain": "(AB)x = A(Bx): справа налево, как у функций f(g(x)). Поэтому в общем случае AB ≠ BA."},
        ],
    },
    "q-w2-linalg2": {
        "title": "Определитель, обратная матрица, ранг, скалярное произведение, собственные векторы",
        "questions": [
            {"type": "number", "q": "det [[3, 1], [2, 4]]", "answer": 10, "tol": 1e-9, "explain": "ad − bc = 12 − 2 = 10. Преобразование увеличивает площади в 10 раз."},
            {"type": "choice", "q": "Что значит det A = 0?",
             "options": ["A — единичная матрица", "Преобразование сплющивает плоскость в прямую или точку; обратной матрицы нет", "Все элементы нули", "A симметрична"],
             "answer": 1, "explain": "Площадь стала 0 — информация потеряна, «отменить» преобразование нельзя. Столбцы линейно зависимы."},
            {"type": "number", "q": "При каком k матрица [[2, 4], [1, k]] вырождена (det = 0)?", "answer": 2, "tol": 1e-9, "explain": "2k − 4 = 0 → k = 2. Тогда второй столбец = 2·первый."},
            {"type": "number", "q": "Ранг матрицы [[1, 2, 3], [2, 4, 6]]", "answer": 1, "tol": 1e-9, "explain": "Вторая строка = 2·первая: размерность образа — 1."},
            {"type": "number", "q": "Скалярное произведение (1, 2, 3)·(4, −5, 6)", "answer": 12, "tol": 1e-9, "explain": "4 − 10 + 18 = 12."},
            {"type": "choice", "q": "Скалярное произведение двух ненулевых векторов равно 0. Значит, векторы…",
             "options": ["Равны", "Перпендикулярны", "Коллинеарны", "Единичные"], "answer": 1, "explain": "a·b = |a||b|cos θ = 0 → θ = 90°. Отсюда косинусное сходство эмбеддингов (неделя 9)."},
            {"type": "vector", "q": "Собственные значения A = [[2, 0], [0, 3]] (по возрастанию)", "answer": [2, 3], "tol": 1e-9, "labels": ["λ₁", "λ₂"],
             "explain": "Диагональная матрица растягивает оси: собственные векторы — оси, значения — числа на диагонали."},
            {"type": "choice", "q": "A = [[2, 1], [1, 2]]. Какой вектор — собственный с λ = 3?",
             "options": ["(1, 0)", "(1, 1)", "(1, −1)", "(0, 1)"], "answer": 1, "explain": "A·(1, 1) = (3, 3) = 3·(1, 1). А (1, −1) — собственный с λ = 1."},
            {"type": "text", "q": "Своими словами: что такое собственный вектор преобразования?",
             "model": "Ненулевой вектор, который преобразование не поворачивает с его прямой, а только растягивает или сжимает: A·v = λ·v. λ — во сколько раз."},
        ],
    },
}

EXERCISES = {
    "ex-w2-fib": {
        "title": "бесконечный генератор Фибоначчи",
        "statement_ru": d("""\
            Напишите генератор `fib()`, который бесконечно отдаёт числа Фибоначчи: 0, 1, 1, 2, 3, 5, …
            Затем напишите `take(n, iterable)` — вернуть список из первых `n` элементов любого
            итерируемого объекта (без превращения всего объекта в список: он может быть бесконечным)."""),
        "starter_code": "def fib():\n    pass\n\n\ndef take(n, iterable):\n    pass\n",
        "tests": d('''\
            import itertools, types

            def test_is_generator():
                """fib() — генератор"""
                assert isinstance(fib(), types.GeneratorType), "используйте yield"

            def test_values():
                """Первые 10 чисел"""
                assert take(10, fib()) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

            def test_lazy_and_infinite():
                """Генератор бесконечный и ленивый"""
                g = fib()
                for _ in range(1000):
                    next(g)
                assert next(g) == 43466557686937456435688527675040625802564660517371780402481729089536555417949051890403879840079255169295922593080322634775209689623239873322471161642996440906533187938298969649928516003704476137795166849228875

            def test_take_any_iterable():
                """take работает с любым итерируемым и с n = 0"""
                assert take(3, "abcdef") == ["a", "b", "c"]
                assert take(0, fib()) == []
                assert take(5, range(2)) == [0, 1]
                assert take(2, itertools.count(7)) == [7, 8]
            '''),
        "ref": d("""\
            def fib():
                a, b = 0, 1
                while True:
                    yield a
                    a, b = b, a + b


            def take(n, iterable):
                out = []
                for x in iterable:
                    if len(out) >= n:
                        break
                    out.append(x)
                return out
            """),
        "hints_ru": [
            "Список всех чисел Фибоначчи построить нельзя: их бесконечно много. Как отдавать числа по одному, только когда их просят?",
            "Генератор — функция с `yield`. Он замирает на `yield` и продолжает с того же места при следующем `next`. Бесконечный генератор — это `while True` с `yield` внутри. Для `take` нельзя вызывать `list(iterable)`: он не закончится.",
            "1) `fib`: `a, b = 0, 1`; в цикле `yield a`, затем `a, b = b, a + b`. 2) `take`: идите `for x in iterable`, собирайте в список; набрали `n` — `break`. 3) Проверьте `take(0, fib())` — `[]`. Готовый вариант: `list(itertools.islice(iterable, n))`.",
        ],
    },
    "ex-w2-timer": {
        "title": "декоратор timer",
        "statement_ru": d("""\
            Напишите декоратор `timer`. Он:
            - вызывает функцию с теми же аргументами и возвращает её результат;
            - печатает строку `<имя функции>: <секунды> с` (например `slow: 0.1002 с`, 4 знака после точки);
            - сохраняет имя и docstring исходной функции;
            - записывает время последнего вызова в атрибут обёртки `last_time` (float, секунды).

            Время меряйте `time.perf_counter()`."""),
        "starter_code": "import time\nimport functools\n\n\ndef timer(func):\n    pass\n",
        "tests": d('''\
            import time

            def test_result_and_args():
                """Аргументы и результат проходят насквозь"""
                @timer
                def add(a, b=0, *, c=0):
                    return a + b + c
                assert add(1, 2, c=3) == 6

            def test_print_format():
                """Печатает имя и время"""
                import io, contextlib, re
                @timer
                def nap():
                    time.sleep(0.02)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    nap()
                line = buf.getvalue().strip()
                assert re.fullmatch(r"nap: \\d+\\.\\d{4} с", line), f"напечатано: {line!r}"

            def test_metadata():
                """functools.wraps сохраняет имя и docstring"""
                @timer
                def documented():
                    """Документация."""
                assert documented.__name__ == "documented"
                assert documented.__doc__ == "Документация."

            def test_last_time():
                """Атрибут last_time"""
                @timer
                def nap():
                    time.sleep(0.03)
                nap()
                assert 0.025 < nap.last_time < 1, f"last_time = {getattr(nap, 'last_time', None)}"
            '''),
        "ref": d("""\
            import time
            import functools


            def timer(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    start = time.perf_counter()
                    try:
                        return func(*args, **kwargs)
                    finally:
                        wrapper.last_time = time.perf_counter() - start
                        print(f"{func.__name__}: {wrapper.last_time:.4f} с")
                wrapper.last_time = None
                return wrapper
            """),
        "hints_ru": [
            "Декоратор заменяет функцию на другую. Что должна делать новая функция до и после вызова старой, чтобы снаружи всё выглядело как раньше?",
            "Обёртка `wrapper(*args, **kwargs)` принимает любые аргументы и передаёт их в `func`. `@functools.wraps(func)` копирует имя и docstring. Функция — объект, поэтому у обёртки может быть атрибут `last_time`.",
            "1) `start = time.perf_counter()`. 2) `result = func(*args, **kwargs)`. 3) `wrapper.last_time = perf_counter() - start`. 4) Напечатайте `f\"{func.__name__}: {wrapper.last_time:.4f} с\"`. 5) Верните `result`. Начальное значение: `wrapper.last_time = None` до первого вызова.",
        ],
    },
    "ex-w2-retry": {
        "title": "Декоратор с параметрами: retry",
        "statement_ru": d("""\
            Напишите `retry(times, exceptions=(Exception,))` — декоратор с параметрами.
            Обёрнутая функция вызывается до `times` раз подряд, пока не завершится без исключения
            из `exceptions`. Если все попытки упали — пробросьте **последнее** исключение.
            Исключения других типов пробрасывайте сразу, без повторов."""),
        "starter_code": "import functools\n\n\ndef retry(times, exceptions=(Exception,)):\n    pass\n",
        "tests": d('''\
            def test_succeeds_after_failures():
                """Успех с третьей попытки"""
                calls = []
                @retry(3)
                def flaky():
                    calls.append(1)
                    if len(calls) < 3:
                        raise ConnectionError("нет сети")
                    return "ok"
                assert flaky() == "ok" and len(calls) == 3

            def test_gives_up():
                """После times попыток — последнее исключение"""
                calls = []
                @retry(2, exceptions=(ValueError,))
                def bad():
                    calls.append(1)
                    raise ValueError(f"попытка {len(calls)}")
                try:
                    bad()
                except ValueError as e:
                    assert str(e) == "попытка 2" and len(calls) == 2
                else:
                    raise AssertionError("исключение не проброшено")

            def test_other_exceptions_not_retried():
                """Чужие исключения — сразу"""
                calls = []
                @retry(5, exceptions=(ValueError,))
                def boom():
                    calls.append(1)
                    raise KeyError("x")
                try:
                    boom()
                except KeyError:
                    pass
                assert len(calls) == 1, f"было {len(calls)} вызовов"

            def test_wraps():
                """Имя функции сохранено"""
                @retry(1)
                def named():
                    return 1
                assert named.__name__ == "named"
            '''),
        "ref": d("""\
            import functools


            def retry(times, exceptions=(Exception,)):
                def deco(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        for attempt in range(times):
                            try:
                                return func(*args, **kwargs)
                            except exceptions:
                                if attempt == times - 1:
                                    raise
                    return wrapper
                return deco
            """),
        "hints_ru": [
            "`@retry(times=3)` — сначала вызов `retry(3)`, и только его результат применяется к функции. Что тогда должна вернуть `retry`?",
            "Декоратор с параметрами — три уровня: `retry(times, exceptions)` возвращает `deco(func)`, а `deco` возвращает `wrapper(*args, **kwargs)`. Параметры доступны в `wrapper` через замыкание. `except exceptions` ловит только нужные типы; остальные исключения пройдут сами.",
            "1) В `wrapper`: `for attempt in range(times)`. 2) `try: return func(*args, **kwargs)`. 3) `except exceptions:` — если попытка последняя, голый `raise` пробрасывает текущее исключение; иначе цикл идёт дальше. 4) Не забудьте `@functools.wraps(func)`.",
        ],
    },
    "ex-w2-ctx": {
        "title": "Контекстный менеджер двумя способами",
        "statement_ru": d("""\
            1. Класс `Timer`: `with Timer() as t: ...` — после блока в `t.elapsed` лежит время в секундах
               (float). Исключения из блока **не подавлять**.
            2. Функция `suppress_log(*exc_types)` через `@contextlib.contextmanager`: подавляет
               исключения указанных типов и добавляет их имена в список `suppress_log.log`
               (атрибут функции, создайте его). Прочие исключения пробрасывает."""),
        "starter_code": "import time\nimport contextlib\n\n\nclass Timer:\n    pass\n\n\ndef suppress_log(*exc_types):\n    pass\n",
        "tests": d('''\
            import time

            def test_timer_measures():
                """Timer меряет время"""
                with Timer() as t:
                    time.sleep(0.02)
                assert 0.015 < t.elapsed < 1

            def test_timer_does_not_swallow():
                """Timer не подавляет исключения, но elapsed есть"""
                t = Timer()
                try:
                    with t:
                        raise RuntimeError("x")
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("исключение подавлено")
                assert t.elapsed is not None and t.elapsed >= 0

            def test_suppress_log():
                """suppress_log подавляет и записывает"""
                suppress_log.log.clear()
                with suppress_log(KeyError, ZeroDivisionError):
                    1 / 0
                with suppress_log(KeyError):
                    {}["k"]
                assert suppress_log.log == ["ZeroDivisionError", "KeyError"]

            def test_suppress_other():
                """Чужие исключения проходят"""
                try:
                    with suppress_log(KeyError):
                        raise ValueError("v")
                except ValueError:
                    return
                raise AssertionError("ValueError подавлен")
            '''),
        "ref": d("""\
            import time
            import contextlib


            class Timer:
                def __init__(self):
                    self.elapsed = None

                def __enter__(self):
                    self._start = time.perf_counter()
                    return self

                def __exit__(self, exc_type, exc, tb):
                    self.elapsed = time.perf_counter() - self._start
                    return False


            @contextlib.contextmanager
            def suppress_log(*exc_types):
                try:
                    yield
                except exc_types as e:
                    suppress_log.log.append(type(e).__name__)


            suppress_log.log = []
            """),
        "hints_ru": [
            "Блок `with` вызывает код при входе и при выходе, даже если внутри было исключение. Какие два метода класса Python вызывает для этого?",
            "Класс: `__enter__` возвращает объект для `as`, `__exit__(exc_type, exc, tb)` вызывается при выходе. Ложное значение из `__exit__` значит «не подавлять исключение». В `@contextlib.contextmanager` исключение из блока возникает в точке `yield`.",
            "1) `Timer.__enter__`: запомните `perf_counter()`, верните `self`. 2) `__exit__`: запишите `elapsed`, верните `False`. 3) `suppress_log`: `try: yield` / `except exc_types as e:` — добавьте `type(e).__name__` в `suppress_log.log`. 4) После `def` создайте `suppress_log.log = []`.",
        ],
    },
    "ex-w2-vector": {
        "title": "класс Vector с dunder-методами",
        "statement_ru": d("""\
            Напишите класс `Vector(*coords)` — вектор любой длины:
            - `repr(Vector(1, 2))` → `"Vector(1, 2)"`;
            - `len(v)`, итерация `for x in v`, индекс `v[0]`;
            - `v + w` (одинаковой длины, иначе `ValueError`), `v * 3` и `3 * v`;
            - `abs(v)` — длина (евклидова норма);
            - `v == w` и `hash(v)` — равные векторы имеют равный хэш;
            - `@classmethod zeros(n)` — нулевой вектор длины n; у наследника возвращает наследника."""),
        "starter_code": "import math\n\n\nclass Vector:\n    def __init__(self, *coords):\n        self.coords = coords\n",
        "tests": d('''\
            def test_repr_len_iter():
                """repr, len, итерация, индекс"""
                v = Vector(1, 2, 3)
                assert repr(v) == "Vector(1, 2, 3)"
                assert len(v) == 3 and list(v) == [1, 2, 3] and v[1] == 2

            def test_arithmetic():
                """+, *, abs"""
                assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)
                assert Vector(1, 2) * 3 == Vector(3, 6) == 3 * Vector(1, 2)
                assert abs(Vector(3, 4)) == 5

            def test_length_mismatch():
                """Разная длина — ValueError"""
                try:
                    Vector(1) + Vector(1, 2)
                except ValueError:
                    return
                raise AssertionError("нет ValueError")

            def test_hash():
                """Можно класть в set и dict"""
                assert len({Vector(1, 2), Vector(1, 2), Vector(2, 1)}) == 2

            def test_classmethod():
                """zeros у наследника"""
                class Vec3(Vector):
                    pass
                z = Vec3.zeros(3)
                assert type(z) is Vec3 and list(z) == [0, 0, 0]
            '''),
        "ref": d("""\
            import math


            class Vector:
                def __init__(self, *coords):
                    self.coords = tuple(coords)

                @classmethod
                def zeros(cls, n):
                    return cls(*([0] * n))

                def __repr__(self):
                    return f"Vector({', '.join(map(repr, self.coords))})"

                def __len__(self):
                    return len(self.coords)

                def __iter__(self):
                    return iter(self.coords)

                def __getitem__(self, i):
                    return self.coords[i]

                def __add__(self, other):
                    if len(self) != len(other):
                        raise ValueError("разная длина")
                    return type(self)(*(a + b for a, b in zip(self, other)))

                def __mul__(self, k):
                    return type(self)(*(a * k for a in self))

                __rmul__ = __mul__

                def __abs__(self):
                    return math.sqrt(sum(a * a for a in self))

                def __eq__(self, other):
                    return isinstance(other, Vector) and self.coords == other.coords

                def __hash__(self):
                    return hash(self.coords)
            """),
        "hints_ru": [
            "Как Python понимает, что значит `len(v)`, `v + w` или `abs(v)` для вашего класса? Какие методы он ищет у объекта?",
            "Каждой операции соответствует dunder-метод: `__repr__`, `__len__`, `__iter__`, `__getitem__`, `__add__`, `__mul__`, `__rmul__`, `__abs__`, `__eq__`, `__hash__`. Для `3 * v` `int` не умеет умножать на `Vector`, поэтому Python вызывает `v.__rmul__(3)`. Координаты храните в `tuple`: он неизменяемый и hashable.",
            "1) `__init__(*coords)`: `self.coords = tuple(coords)`. 2) `__add__`: разная длина — `ValueError`; иначе `type(self)(*(a + b ...))`. 3) `__rmul__ = __mul__`. 4) `__hash__`: `hash(self.coords)`. 5) `zeros` — `@classmethod`, верните `cls(*[0] * n)`: так наследник получит наследника.",
        ],
    },
    "ex-w2-dataclass": {
        "title": "dataclasses: заказ и позиции",
        "statement_ru": d("""\
            Опишите через `@dataclass`:
            - `Item(name: str, price: float, qty: int = 1)` с свойством `total` = price · qty;
            - `Order(id: int, items: list[Item] = <пустой список>)` с методом `add(item)` и свойством `total`;
              заказы сравниваются по `total` (`<`, `>`), поле `items` в `==` не участвует — два заказа равны,
              если равны их `id`.

            Ловушка: если написать `items: list = []`, у всех заказов будет один общий список (как в `def f(x=[])`).
            У двух `Order` не должно быть общего списка `items`."""),
        "starter_code": "from dataclasses import dataclass, field\n\n\n@dataclass\nclass Item:\n    name: str\n    price: float\n    qty: int = 1\n",
        "tests": d('''\
            def test_item_total():
                """Item.total"""
                assert Item("pen", 10.0, 3).total == 30.0
                assert Item("pen", 10.0).qty == 1

            def test_independent_items():
                """У разных заказов разные списки"""
                a, b = Order(1), Order(2)
                a.add(Item("x", 1.0))
                assert b.items == [], "заказы делят список items"

            def test_order_total_and_compare():
                """total и сравнение по total"""
                a, b = Order(1), Order(2)
                a.add(Item("x", 5.0, 2))
                b.add(Item("y", 3.0))
                assert a.total == 10.0 and b.total == 3.0
                assert b < a and a > b

            def test_equality_by_id():
                """== по id"""
                a, b = Order(7), Order(7)
                a.add(Item("x", 1.0))
                assert a == b and Order(1) != Order(2)
            '''),
        "ref": d("""\
            from dataclasses import dataclass, field


            @dataclass
            class Item:
                name: str
                price: float
                qty: int = 1

                @property
                def total(self):
                    return self.price * self.qty


            @dataclass
            class Order:
                id: int
                items: list = field(default_factory=list, compare=False)

                def add(self, item):
                    self.items.append(item)

                @property
                def total(self):
                    return sum(i.total for i in self.items)

                def __lt__(self, other):
                    return self.total < other.total

                def __gt__(self, other):
                    return self.total > other.total
            """),
        "hints_ru": [
            "`@dataclass` пишет `__init__`, `__repr__` и `__eq__` сам. Какие требования задачи он не выполнит по умолчанию?",
            "`field(default_factory=list)` создаёт новый список для каждого объекта — это защита от общего списка, как в `def f(x=[])`. `compare=False` убирает поле из `==`. `@property` даёт `total` без скобок. `order=True` сравнил бы по полям, а нужно по `total`, поэтому `__lt__` и `__gt__` пишите сами.",
            "1) `Item`: три поля, `@property total` → `price * qty`. 2) `Order`: `id: int`, `items: list = field(default_factory=list, compare=False)`. 3) `add` — `append`. 4) `total` — сумма `i.total`. 5) `__lt__` и `__gt__` сравнивают `self.total` и `other.total`.",
        ],
    },
}
