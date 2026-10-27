"""Month 1 weekend practice, inside the site (replaces the GitHub repo work at the user's request).

Tools (uv, ruff, pytest, CI) are covered by reading + a quiz; tests are written as check functions
that the site runs against a correct and a buggy implementation.
"""

from textwrap import dedent as d

from .w04 import SQL_SETUP

QUIZZES = {
    "q-w1-tools": {
        "title": "uv, ruff, pytest, GitHub Actions",
        "questions": [
            {"type": "choice", "q": "Какая команда uv добавляет pytest и ruff как зависимости для разработки?",
             "options": ["`uv pip install pytest ruff`", "`uv add --dev pytest ruff`", "`uv run pytest ruff`", "`uv init pytest ruff`"], "answer": 1,
             "explain": "`uv add` записывает зависимость в `pyproject.toml` и `uv.lock`; `--dev` — в группу разработки."},
            {"type": "choice", "q": "Что делает `uv run pytest`?",
             "options": ["Устанавливает pytest глобально", "Запускает pytest в виртуальном окружении проекта, перед этим синхронизирует зависимости", "Публикует пакет", "Создаёт проект"],
             "answer": 1},
            {"type": "choice", "q": "Какое правило ruff находит изменяемое значение по умолчанию, например `def f(x=[])`?",
             "options": ["E501", "B006 — изменяемое значение по умолчанию", "F401", "B023"], "answer": 1},
            {"type": "choice", "q": "Какое правило ruff находит позднее связывание: `lambda` в цикле читает переменную цикла, например `[lambda: i for i in range(3)]`?",
             "options": ["B006", "B023 — функция использует переменную цикла, связанную поздно", "E711", "UP006"], "answer": 1},
            {"type": "choice", "q": "Как pytest находит тесты по умолчанию?",
             "options": ["Только в файле tests.py", "Файлы `test_*.py` или `*_test.py`, в них функции `test_*`", "Все функции проекта", "Только классы"], "answer": 1},
            {"type": "choice", "q": "Что делает `@pytest.mark.parametrize(\"x, expected\", [(1, 2), (3, 4)])`?",
             "options": ["Запускает тест один раз", "Запускает тест дважды: с x=1, expected=2 и с x=3, expected=4 — это 2 отдельных теста", "Пропускает тест", "Помечает тест медленным"],
             "answer": 1},
            {"type": "choice", "q": "В GitHub Actions файл `.github/workflows/ci.yml` с `on: push` запускается…",
             "options": ["раз в день", "при каждом push в репозиторий", "только вручную", "при открытии сайта"], "answer": 1},
            {"type": "choice", "q": "Что должен делать минимальный CI для учебного репозитория?",
             "options": ["Деплой на сервер", "Поставить зависимости, `ruff check`, `ruff format --check`, `pytest`", "Только `git log`", "Ничего"], "answer": 1},
        ],
    },
    "q-w2-bench": {
        "title": "Замер: потоки и процессы (GIL)",
        "questions": [
            {"type": "number",
             "q": ("Замер на 4-ядерном ноутбуке. CPU-задача (считать простые числа): 1 поток — 4,0 с; 4 потока — 4,1 с; "
                   "4 процесса — 1,1 с. Во сколько раз процессы быстрее одного потока? (округлите до десятых)"),
             "answer": 3.6, "tol": 0.05},
            {"type": "choice", "q": "Замер на 4 ядрах, CPU-задача (считать простые числа): 1 поток — 4,0 с, 4 потока — 4,1 с. Почему 4 потока не быстрее одного?",
             "options": ["Потоки в Python не работают", "GIL: в один момент байт-код Python выполняет только один поток", "Мало памяти", "Процессор одноядерный"],
             "answer": 1},
            {"type": "choice", "q": "Задача с ожиданием (`time.sleep(1)` × 4): 1 поток — 4,0 с, 4 потока — 1,0 с. Почему здесь потоки помогли?",
             "options": ["GIL выключается навсегда", "Во время `sleep` и ввода-вывода поток отпускает GIL — остальные работают", "sleep работает быстрее в потоках", "Совпадение"],
             "answer": 1},
            {"type": "choice", "q": "Замер на 4 ядрах, CPU-задача: 1 поток — 4,0 с, 4 процесса — 1,1 с, то есть в 3,6 раза быстрее. Почему не ровно в 4 раза?",
             "options": ["Ошибка замера", "Накладные расходы: запуск процессов и передача данных между ними (pickle)", "GIL в процессах", "Так всегда"], "answer": 1},
            {"type": "choice", "q": "Нужно скачать 100 страниц по сети. Что выбрать?",
             "options": ["multiprocessing", "threading или asyncio — задача ждёт сеть", "Один поток", "numpy"], "answer": 1},
            {"type": "text", "q": ("Замер на 4 ядрах. CPU-задача: 1 поток — 4,0 с, 4 потока — 4,1 с, 4 процесса — 1,1 с. Задача с ожиданием (`time.sleep(1)` × 4): 1 поток — 4,0 с, 4 потока — 1,0 с. Объясните результат своими словами (3–4 предложения): что такое GIL, когда помогают потоки, когда процессы."),
             "model": ("GIL — блокировка в CPython: байт-код Python в один момент выполняет только один поток. Поэтому на CPU-задаче потоки "
                       "не ускоряют работу, а процессы ускоряют: у каждого процесса свой интерпретатор и свой GIL. На задачах с ожиданием "
                       "(сеть, диск, sleep) поток отпускает GIL, и потоки (или asyncio) дают ускорение. Процессы дороже: их запуск и передача "
                       "данных стоят времени.")},
        ],
    },
}

EXERCISES = {
    "ex-w1-tests": {
        "title": "Пишем тесты на три ловушки Python (как в pytest)",
        "statement_ru": d("""\
            Тест — это функция, которая падает (`assert`), если код неверный. Напишите четыре проверки.
            Каждая получает **реализацию** как аргумент и проверяет её через `assert`:

            - `check_add(add)` — функция `add(x, items=None)` добавляет `x` в список `items` и возвращает его.
              Ловушка — `items=[]` по умолчанию: два вызова без списка не должны делить один список;
            - `check_grid(make_grid)` — функция `make_grid(rows, cols)` возвращает матрицу `rows × cols` из нулей.
              Ловушка — `[[0] * cols] * rows`: строки должны быть независимы;
            - `check_multipliers(make_multipliers)` — функция `make_multipliers()` возвращает список функций
              `[×0, ×1, ×2, ×3]`, и `fs[i](2) == 2·i`. Ловушка — `[lambda x: i * x for i in range(4)]`:
              позднее связывание, все функции умножают на 3;
            - `check_copy(clone)` — `clone(matrix)` делает глубокую копию: изменение вложенного списка копии не меняет оригинал.

            Сайт запустит каждую проверку на **верной** реализации (проверка должна пройти) и на **реализации с ловушкой**
            (проверка должна упасть). Так работает любой хороший тест.

            Назовите функции `check_*`, а не `test_*`: на сайте `test_*` — это тесты самого сайта.
            В репозитории с pytest это были бы обычные `test_*`."""),
        "starter_code": "def check_add(add):\n    pass\n\n\ndef check_grid(make_grid):\n    pass\n\n\ndef check_multipliers(make_multipliers):\n    pass\n\n\ndef check_copy(clone):\n    pass\n",
        "tests": d('''\
            import copy

            def _passes(check, impl):
                try:
                    check(impl)
                    return True
                except AssertionError:
                    return False

            def good_add(x, items=None):
                if items is None:
                    items = []
                items.append(x)
                return items

            def bad_add(x, items=[]):
                items.append(x)
                return items

            def good_grid(rows, cols):
                return [[0] * cols for _ in range(rows)]

            def bad_grid(rows, cols):
                return [[0] * cols] * rows

            def good_mult():
                return [lambda x, i=i: x * i for i in range(4)]

            def bad_mult():
                return [lambda x: x * i for i in range(4)]

            def test_b1():
                """check_add: проходит на верной, падает на ловушке items=[]"""
                assert _passes(check_add, good_add), "проверка падает на верной реализации"
                assert not _passes(check_add, bad_add), "проверка не ловит ловушку items=[]"

            def test_b2():
                """check_grid: проходит на верной, падает на ловушке [[0] * cols] * rows"""
                assert _passes(check_grid, good_grid), "проверка падает на верной реализации"
                assert not _passes(check_grid, bad_grid), "проверка не ловит ловушку [[0] * cols] * rows"

            def test_b3():
                """check_multipliers: проходит на верной, падает на позднем связывании lambda"""
                assert _passes(check_multipliers, good_mult), "проверка падает на верной реализации"
                assert not _passes(check_multipliers, bad_mult), "проверка не ловит позднее связывание lambda"

            def test_copy():
                """check_copy: deepcopy проходит, copy.copy и срез — нет"""
                assert _passes(check_copy, copy.deepcopy), "проверка падает на deepcopy"
                assert not _passes(check_copy, copy.copy), "проверка не отличает поверхностную копию"
                assert not _passes(check_copy, lambda m: m[:]), "проверка не отличает срез"
            '''),
        "ref": d("""\
            def check_add(add):
                assert add(1) == [1]
                assert add(2) == [2]


            def check_grid(make_grid):
                g = make_grid(3, 2)
                g[0][0] = 1
                assert g == [[1, 0], [0, 0], [0, 0]]


            def check_multipliers(make_multipliers):
                fs = make_multipliers()
                assert [f(2) for f in fs] == [0, 2, 4, 6]


            def check_copy(clone):
                original = [[1, 2], [3]]
                c = clone(original)
                c[0].append(9)
                assert original == [[1, 2], [3]]
        """),
        "hints_ru": [
            "Каждая ловушка (общий список по умолчанию, общие строки матрицы, позднее связывание `lambda`) «молчит» при первом действии. Какое второе действие её показывает: второй вызов, изменение элемента, вызов другой функции?",
            "Тест — это вызов реализации и `assert` на результат. Сделайте действие, которое показывает ловушку, и сравните результат с правильным. Для копии: меняйте вложенный объект копии, затем проверяйте оригинал.",
            "1) `check_add`: `assert add(1) == [1]`, затем `assert add(2) == [2]`. 2) `check_grid`: `g = make_grid(3, 2)`, `g[0][0] = 1`, сравните всю сетку. 3) `check_multipliers`: `[f(2) for f in fs] == [0, 2, 4, 6]`. 4) `check_copy`: добавьте элемент во вложенный список копии и проверьте, что оригинал не изменился.",
        ],
    },
    "ex-w2-deco10": {
        "title": "Декоратор с нуля: count_calls",
        "statement_ru": d("""\
            Проверка недели 2: напишите декоратор с нуля, без подсказок и без прошлых решений.

            `@count_calls` считает вызовы функции: у обёрнутой функции есть атрибут `calls`.
            Обёртка передаёт любые аргументы и возвращает результат. Имя и docstring функции
            сохраняются (`functools.wraps`)."""),
        "starter_code": "import functools\n\n\ndef count_calls(func):\n    pass\n",
        "tests": d('''\
            @count_calls
            def add(a, b=0):
                """Сложить."""
                return a + b

            def test_counts():
                """Считает вызовы"""
                start = add.calls
                add(1); add(1, b=2); add(a=3)
                assert add.calls - start == 3

            def test_result():
                """Аргументы и результат проходят насквозь"""
                assert add(2, b=5) == 7

            def test_wraps():
                """Имя и docstring сохранены"""
                assert add.__name__ == "add" and add.__doc__ == "Сложить."

            def test_separate():
                """У каждой функции свой счётчик"""
                @count_calls
                def f():
                    return 1
                f(); f()
                assert f.calls == 2
            '''),
        "ref": d("""\
            import functools


            def count_calls(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    wrapper.calls += 1
                    return func(*args, **kwargs)
                wrapper.calls = 0
                return wrapper
        """),
        "hints_ru": [
            "Счётчик должен жить между вызовами и быть виден снаружи как `f.calls`. Где его хранить, если глобальные переменные не подходят?",
            "Функция — объект, у неё могут быть атрибуты. Храните счётчик атрибутом самой обёртки: `wrapper.calls`. `@functools.wraps(func)` копирует имя и docstring.",
            "1) `def count_calls(func):`. 2) Внутри `@functools.wraps(func)` и `def wrapper(*args, **kwargs):` — `wrapper.calls += 1`, затем `return func(*args, **kwargs)`. 3) После `def wrapper`: `wrapper.calls = 0`. 4) Верните `wrapper`.",
        ],
    },
    "ex-w3-eda": {
        "title": "EDA на pandas: датасет рака груди (sklearn)",
        "statement_ru": d("""\
            Датасет `load_breast_cancer` (569 опухолей, 30 признаков, `target`: 1 — доброкачественная).
            Напишите `eda(df)`, где `df` — таблица с признаками и столбцом `target`. Верните `dict`:
            - `"shape"` — `(строк, столбцов)`;
            - `"missing"` — общее число пропусков;
            - `"balance"` — доля класса 1, округлить до 3 знаков;
            - `"top_corr"` — 3 признака с наибольшей **по модулю** корреляцией с `target`, по убыванию;
            - `"mean_radius_by_class"` — `dict` класс → среднее `mean radius`, округлить до 2 знаков.

            Подсказка для запуска у себя: `df = load_breast_cancer(as_frame=True).frame`."""),
        "starter_code": "import pandas as pd\nfrom sklearn.datasets import load_breast_cancer\n\n\ndef eda(df):\n    pass\n",
        "tests": d('''\
            import pandas as pd
            from sklearn.datasets import load_breast_cancer

            DF = load_breast_cancer(as_frame=True).frame

            def test_basic():
                """Размер, пропуски, баланс классов"""
                r = eda(DF.copy())
                assert tuple(r["shape"]) == (569, 31)
                assert r["missing"] == 0
                assert r["balance"] == 0.627

            def test_corr():
                """Топ-3 признака по |корреляции| с target"""
                r = eda(DF.copy())
                assert list(r["top_corr"]) == ["worst concave points", "worst perimeter", "mean concave points"], r["top_corr"]

            def test_groupby():
                """Средний радиус по классам"""
                r = eda(DF.copy())
                assert r["mean_radius_by_class"] == {0: 17.46, 1: 12.15}, r["mean_radius_by_class"]

            def test_missing_counted():
                """Пропуски считаются"""
                df = DF.copy()
                df.iloc[0, 0] = None
                df.iloc[1, 2] = None
                assert eda(df)["missing"] == 2
            '''),
        "ref": d("""\
            import pandas as pd
            from sklearn.datasets import load_breast_cancer


            def eda(df):
                corr = df.corr()["target"].drop("target").abs().sort_values(ascending=False)
                means = df.groupby("target")["mean radius"].mean().round(2)
                return {
                    "shape": df.shape,
                    "missing": int(df.isna().sum().sum()),
                    "balance": round(float(df["target"].mean()), 3),
                    "top_corr": list(corr.index[:3]),
                    "mean_radius_by_class": {int(k): float(v) for k, v in means.items()},
                }
        """),
        "hints_ru": [
            "Какие из пяти полей считаются по всей таблице, а какие — по отдельным классам? Чему равно среднее столбца из нулей и единиц?",
            "Пропуски — `isna()` и двойная сумма. Доля класса 1 — среднее `target`. `df.corr()[\"target\"]` даёт корреляцию каждого столбца с target; сортируйте по модулю (`.abs()`), а target уберите. Средние по классу — `groupby`.",
            "1) `corr = df.corr()[\"target\"].drop(\"target\").abs().sort_values(ascending=False)`; `top_corr` — первые 3 имени. 2) `missing` — `int(...)`, `balance` — `round(float(...), 3)`. 3) `groupby(\"target\")[\"mean radius\"].mean().round(2)`. 4) Ключи приведите к `int`, значения к `float`.",
        ],
    },
    "ex-w4-sql-select": {
        "title": "SQL 1: SELECT, WHERE, ORDER BY, LIMIT",
        "statement_ru": d("""\
            Таблица `employees(id, name, dept, salary, manager_id)`. Запишите в `QUERY` запрос:
            два самых высокооплачиваемых сотрудника **не** из отдела ML: `name`, `salary`.
            При равной зарплате — по имени."""),
        "starter_code": "QUERY = \"\"\"\nSELECT name, salary\nFROM employees\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                assert rows == [("Егор", 180), ("Глеб", 150)], f"получилось {rows}"
            '''),
        "ref": "QUERY = \"\"\"\nSELECT name, salary\nFROM employees\nWHERE dept <> 'ML'\nORDER BY salary DESC, name\nLIMIT 2\n\"\"\"\n",
        "hints_ru": [
            "Нужны три действия: убрать отдел ML, упорядочить по зарплате, оставить двух лучших. В каком порядке SQL их выполняет?",
            "`WHERE dept <> 'ML'` убирает строки. Строки в SQL — в одинарных кавычках. `ORDER BY salary DESC, name` сортирует по зарплате и при равенстве по имени. `LIMIT 2` оставляет первые две строки после сортировки.",
            "1) `SELECT name, salary FROM employees`. 2) `WHERE dept <> 'ML'`. 3) `ORDER BY salary DESC, name`. 4) `LIMIT 2`.",
        ],
    },
    "ex-w4-sql-null": {
        "title": "SQL 2: NULL и руководители",
        "statement_ru": d("""\
            Выведите имена сотрудников **без** руководителя (`manager_id` пустой), по алфавиту.
            Столбец: `name`."""),
        "starter_code": "QUERY = \"\"\"\nSELECT name\nFROM employees\nWHERE manager_id = NULL\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                assert rows == [("Анна",), ("Глеб",), ("Егор",)], f"получилось {rows}"
            '''),
        "ref": "QUERY = \"\"\"\nSELECT name\nFROM employees\nWHERE manager_id IS NULL\nORDER BY name\n\"\"\"\n",
        "hints_ru": [
            "Запустите шаблон: результат пустой, хотя сотрудники без руководителя есть. Чему в SQL равно `NULL = NULL`?",
            "Сравнение с `NULL` через `=` даёт `NULL` (неизвестно), а не `TRUE`, и строка не проходит фильтр. Для проверки на пустое значение есть отдельный оператор `IS NULL`.",
            "1) `SELECT name FROM employees`. 2) `WHERE manager_id IS NULL`. 3) `ORDER BY name`.",
        ],
    },
    "ex-w4-sql-join": {
        "title": "SQL 3: сотрудник и его руководитель (self-join)",
        "statement_ru": d("""\
            Для **каждого** сотрудника выведите `name` и имя руководителя `manager` (NULL, если его нет).
            Сортировка по `id` сотрудника."""),
        "starter_code": "QUERY = \"\"\"\nSELECT w.name\nFROM employees w\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                expected = [("Анна", None), ("Борис", "Анна"), ("Вера", "Анна"), ("Глеб", None), ("Дина", "Глеб"), ("Егор", None)]
                assert rows == expected, f"получилось {rows}"
            '''),
        "ref": "QUERY = \"\"\"\nSELECT w.name, m.name AS manager\nFROM employees w\nLEFT JOIN employees m ON w.manager_id = m.id\nORDER BY w.id\n\"\"\"\n",
        "hints_ru": [
            "Имя сотрудника и имя руководителя лежат в одной таблице, но в разных строках. Как поставить эти две строки рядом?",
            "Self-join: соедините таблицу саму с собой через два псевдонима — `w` (сотрудник) и `m` (руководитель), условие `w.manager_id = m.id`. Обычный `JOIN` выбросит сотрудников без пары; `LEFT JOIN` сохранит их с `NULL`.",
            "1) `SELECT w.name, m.name AS manager`. 2) `FROM employees w LEFT JOIN employees m ON w.manager_id = m.id`. 3) `ORDER BY w.id`.",
        ],
    },
    "ex-w4-sql-case": {
        "title": "SQL 4: CASE и подсчёт по категориям",
        "statement_ru": d("""\
            Разбейте сотрудников на уровни зарплаты: `high` (≥ 200), `mid` (150–199), `low` (< 150).
            Выведите `level` и число сотрудников, сортировка по `level`."""),
        "starter_code": "QUERY = \"\"\"\nSELECT salary\nFROM employees\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                assert rows == [("high", 3), ("low", 1), ("mid", 2)], f"получилось {rows}"
            '''),
        "ref": ("QUERY = \"\"\"\nSELECT CASE WHEN salary >= 200 THEN 'high' WHEN salary >= 150 THEN 'mid' ELSE 'low' END AS level,\n"
                "       COUNT(*)\nFROM employees\nGROUP BY level\nORDER BY level\n\"\"\"\n"),
        "hints_ru": [
            "Столбца «уровень» в таблице нет. Как получить его из `salary` прямо в запросе и потом посчитать сотрудников каждого уровня?",
            "`CASE WHEN ... THEN ... ELSE ... END` — выражение, как тернарный оператор. Условия проверяются по порядку, поэтому сначала `>= 200`, потом `>= 150`, иначе `low`. По выражению с именем `AS level` можно группировать.",
            "1) В `SELECT` напишите `CASE` с тремя ветками и дайте ему имя `AS level`; рядом — `COUNT(*)`. 2) `FROM employees GROUP BY level`. 3) `ORDER BY level`. Проверьте границы: 200 → high, 150 → mid, 149 → low.",
        ],
    },
}
