"""Week 5 content: trees, ensembles, boosting, SQL joins."""

from textwrap import dedent as d

from .w04 import SQL_SETUP

QUIZZES = {
    "q-w5-trees": {
        "title": "Решающие деревья, Random Forest, бэггинг и бустинг",
        "questions": [
            {"type": "number", "q": "Gini узла с классами [6 объектов класса A, 4 объекта класса B]: 1 − Σ pᵢ²",
             "answer": 1 - 0.6**2 - 0.4**2, "tol": 1e-6, "explain": "1 − 0,36 − 0,16 = 0,48."},
            {"type": "number", "q": "Разбиение дало левый узел [4 A, 0 B] и правый [2 A, 4 B]. Взвешенный Gini после разбиения?",
             "answer": 0.4 * 0 + 0.6 * (1 - (2 / 6) ** 2 - (4 / 6) ** 2), "tol": 1e-4,
             "explain": "Левый узел чистый (0). Правый: 1 − (1/3)² − (2/3)² = 4/9. Вес 6/10: 0,6 · 4/9 ≈ 0,267."},
            {"type": "choice", "q": "Дерево без ограничения глубины на обучающей выборке почти всегда…",
             "options": ["недообучается", "переобучается: доходит до чистых листьев и запоминает шум", "даёт линейную границу", "не зависит от данных"],
             "answer": 1, "explain": "Борьба: max_depth, min_samples_leaf, обрезка, ансамбли."},
            {"type": "choice", "q": "Что делает Random Forest поверх бэггинга деревьев?",
             "options": ["Обучает деревья последовательно на ошибках", "В каждом разбиении выбирает из случайного подмножества признаков — деревья меньше похожи друг на друга",
                         "Использует только линейные модели", "Убирает бутстрэп"],
             "answer": 1, "explain": "Декорреляция деревьев сильнее снижает дисперсию среднего."},
            {"type": "choice", "q": "Главное различие бэггинга и бустинга:",
             "options": ["Бэггинг: модели независимы, усредняем — снижаем дисперсию. Бустинг: модели строятся последовательно, каждая исправляет ошибки суммы — снижаем смещение",
                         "Бэггинг только для регрессии", "Бустинг всегда параллелится лучше", "Разницы нет"],
             "answer": 0},
            {"type": "choice", "q": "OOB-оценка (out-of-bag) в Random Forest — это…",
             "options": ["оценка на тесте", "качество каждого дерева на объектах, не попавших в его бутстрэп-выборку (~37%)", "ошибка на обучении", "кросс-валидация с 10 фолдами"],
             "answer": 1, "explain": "Вероятность не попасть в бутстрэп: (1 − 1/n)ⁿ → 1/e ≈ 0,37."},
            {"type": "multi", "q": "Какие утверждения верны для деревьев?",
             "options": ["Не нужна нормализация признаков", "Плохо экстраполируют за пределы обучающих значений", "Граница решения — кусочно-постоянная, из осе-параллельных отрезков", "Всегда лучше бустинга"],
             "answers": [0, 1, 2]},
        ],
    },
    "q-w5-boosting": {
        "title": "Градиентный бустинг, CatBoost / LightGBM / XGBoost, стекинг",
        "questions": [
            {"type": "choice", "q": "На что обучается каждое новое дерево в градиентном бустинге (MSE)?",
             "options": ["На исходный y", "На остатки y − F(x), то есть антиградиент функции потерь", "На случайный шум", "На предсказания прошлого дерева"],
             "answer": 1},
            {"type": "number", "q": "F₀ = 10, первое дерево предсказало остаток 4, learning_rate = 0,1. Чему равно F₁?", "answer": 10.4, "tol": 1e-9},
            {"type": "choice", "q": "Уменьшили learning_rate в 10 раз. Что обычно нужно сделать?",
             "options": ["Уменьшить число деревьев", "Увеличить число деревьев (и следить за early stopping)", "Ничего", "Убрать регуляризацию"], "answer": 1},
            {"type": "choice", "q": "Чем известен CatBoost?",
             "options": ["Рост дерева по листьям (leaf-wise)", "Нативная работа с категориальными признаками (ordered target statistics) и симметричные деревья",
                         "Только GPU", "Нет регуляризации"], "answer": 1},
            {"type": "choice", "q": "Чем известен LightGBM?",
             "options": ["Гистограммы признаков и рост по листьям (leaf-wise) — очень быстро на больших данных", "Только категориальные признаки", "Обучение без деревьев", "Симметричные деревья"],
             "answer": 0, "explain": "XGBoost классически растит дерево по уровням (level-wise) и добавляет регуляризацию в целевую функцию."},
            {"type": "choice", "q": "Стекинг: на чём обучать мета-модель?",
             "options": ["На предсказаниях базовых моделей на их же обучающих данных", "На out-of-fold предсказаниях базовых моделей (K-Fold) — иначе утечка",
                         "На тестовых метках", "На случайных числах"], "answer": 1},
        ],
    },
    "q-w5-sql": {
        "title": "SQL: JOIN, GROUP BY, HAVING",
        "questions": [
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT e.name, p.title FROM employees e JOIN projects p ON p.owner_id = e.id ORDER BY p.id\"))",
             "explain": "INNER JOIN оставляет только пары с совпадением. Борис владеет двумя проектами — две строки."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT e.name, COUNT(p.id) FROM employees e LEFT JOIN projects p ON p.owner_id = e.id GROUP BY e.id ORDER BY e.id\"))",
             "explain": "LEFT JOIN сохраняет всех сотрудников. COUNT(p.id) не считает NULL — у людей без проектов 0."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT e.name, COUNT(*) FROM employees e LEFT JOIN projects p ON p.owner_id = e.id GROUP BY e.id ORDER BY e.id\"))",
             "explain": "Ловушка: COUNT(*) считает строку с NULL как 1."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT e.dept, SUM(p.budget) FROM employees e JOIN projects p ON p.owner_id = e.id GROUP BY e.dept HAVING SUM(p.budget) > 25 ORDER BY e.dept\"))"},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT w.name, m.name FROM employees w LEFT JOIN employees m ON w.manager_id = m.id WHERE w.dept = 'ML' ORDER BY w.id\"))",
             "explain": "Self-join: таблица соединяется сама с собой."},
        ],
    },
}

EXERCISES = {
    "ex-w5-gini": {
        "title": "Лучшее разбиение по Gini ≈ дерево sklearn глубины 1",
        "statement_ru": d("""\
            Напишите:
            - `gini(y)` — Gini-нечистота массива меток: `1 − Σ pₖ²` (для пустого массива — 0);
            - `best_split(x, y)` — лучший порог для одного числового признака `x`. Порог — середина между
              соседними различными значениями `x`. Объект идёт влево, если `x <= порог`. Верните
              `(threshold, weighted_gini)` с минимальным взвешенным Gini детей.

            Тест сравнивает ответ с `DecisionTreeClassifier(max_depth=1)`."""),
        "starter_code": "import numpy as np\n\n\ndef gini(y):\n    pass\n\n\ndef best_split(x, y):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.tree import DecisionTreeClassifier

            def test_gini():
                """Gini для простых случаев"""
                assert gini([1, 1, 1]) == 0
                assert abs(gini([0, 1]) - 0.5) < 1e-12
                assert abs(gini([0, 0, 1, 2]) - (1 - 0.25 - 0.0625 - 0.0625)) < 1e-12

            def test_vs_sklearn():
                """Порог совпадает с деревом sklearn"""
                rng = np.random.default_rng(0)
                for _ in range(5):
                    x = rng.normal(size=60)
                    y = (x + rng.normal(scale=0.7, size=60) > 0.3).astype(int)
                    t, g = best_split(x, y)
                    tree = DecisionTreeClassifier(max_depth=1).fit(x[:, None], y)
                    # sklearn stores X as float32, so thresholds agree up to ~1e-7.
                    assert abs(t - tree.tree_.threshold[0]) < 1e-6, (t, tree.tree_.threshold[0])
                    imp = tree.tree_.impurity
                    n = tree.tree_.n_node_samples
                    assert abs(g - (n[1] * imp[1] + n[2] * imp[2]) / n[0]) < 1e-9
            '''),
        "ref": d("""\
            import numpy as np


            def gini(y):
                y = np.asarray(y)
                if len(y) == 0:
                    return 0.0
                _, counts = np.unique(y, return_counts=True)
                p = counts / len(y)
                return float(1 - (p ** 2).sum())


            def best_split(x, y):
                x = np.asarray(x, dtype=float)
                y = np.asarray(y)
                values = np.unique(x)
                best = (None, np.inf)
                for a, b in zip(values[:-1], values[1:]):
                    t = (a + b) / 2
                    left = x <= t
                    g = (left.sum() * gini(y[left]) + (~left).sum() * gini(y[~left])) / len(y)
                    if g < best[1] - 1e-12:
                        best = (t, g)
                return float(best[0]), float(best[1])
        """),
        "hints_ru": [
            "Порог между двумя соседними различными значениями `x` можно двигать — разбиение не меняется. Сколько тогда разных порогов стоит проверить?",
            "Перебор порогов-кандидатов: середины между соседними значениями `np.unique(x)`. Для каждого порога — взвешенный Gini детей: `(nL·gini(yL) + nR·gini(yR)) / n`. Вес по размеру нужен: маленький чистый лист не должен «перевешивать» большой грязный.",
            "1) `gini`: пустой массив — 0.0; иначе `p = counts / n`, верните `1 - (p ** 2).sum()`. 2) `best_split`: для пар соседних значений `t = (a + b) / 2`, `left = x <= t`. 3) Считайте взвешенный Gini; обновляйте лучший только при строго меньшем значении — так при равенстве остаётся первый порог, как в sklearn.",
        ],
    },
    "ex-w5-boost": {
        "title": "Градиентный бустинг для регрессии своими руками",
        "statement_ru": d("""\
            Реализуйте `boost_fit(X, y, n_estimators, lr, max_depth)` для MSE:
            1. `F₀` — среднее `y`.
            2. На каждом шаге обучите `DecisionTreeRegressor(max_depth=max_depth, random_state=0)` на остатках `y − F`
               и прибавьте `lr · tree.predict(X)` к `F`.

            Верните `(f0, trees)`. Функция `boost_predict(model, X, lr)` даёт предсказания.
            Тест сравнивает их с `GradientBoostingRegressor` из sklearn."""),
        "starter_code": "import numpy as np\nfrom sklearn.tree import DecisionTreeRegressor\n\n\ndef boost_fit(X, y, n_estimators=50, lr=0.1, max_depth=2):\n    pass\n\n\ndef boost_predict(model, X, lr=0.1):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.ensemble import GradientBoostingRegressor

            rng = np.random.default_rng(1)
            X = rng.uniform(-3, 3, size=(200, 2))
            y = np.sin(X[:, 0]) + 0.5 * X[:, 1] + rng.normal(scale=0.1, size=200)

            def test_first_step_is_mean():
                """F₀ — среднее y"""
                f0, trees = boost_fit(X, y, n_estimators=1)
                assert abs(f0 - y.mean()) < 1e-12 and len(trees) == 1

            def test_mse_decreases():
                """Ошибка на обучении падает с ростом числа деревьев"""
                m5 = boost_fit(X, y, n_estimators=5)
                m50 = boost_fit(X, y, n_estimators=50)
                e5 = ((boost_predict(m5, X) - y) ** 2).mean()
                e50 = ((boost_predict(m50, X) - y) ** 2).mean()
                assert e50 < e5

            def test_vs_sklearn():
                """Предсказания ≈ GradientBoostingRegressor"""
                sk = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, max_depth=2, random_state=0).fit(X, y)
                mine = boost_predict(boost_fit(X, y, 50, 0.1, 2), X, 0.1)
                assert np.allclose(mine, sk.predict(X), atol=1e-6), np.abs(mine - sk.predict(X)).max()
            '''),
        "ref": d("""\
            import numpy as np
            from sklearn.tree import DecisionTreeRegressor


            def boost_fit(X, y, n_estimators=50, lr=0.1, max_depth=2):
                y = np.asarray(y, dtype=float)
                f0 = float(y.mean())
                F = np.full(len(y), f0)
                trees = []
                for _ in range(n_estimators):
                    tree = DecisionTreeRegressor(max_depth=max_depth, random_state=0).fit(X, y - F)
                    F += lr * tree.predict(X)
                    trees.append(tree)
                return f0, trees


            def boost_predict(model, X, lr=0.1):
                f0, trees = model
                return f0 + lr * sum(t.predict(X) for t in trees)
        """),
        "hints_ru": [
            "Первая модель предсказывает одно число для всех объектов. Какое число даёт наименьшую MSE? Что тогда должно исправлять следующее дерево?",
            "Градиентный бустинг для MSE: начальное предсказание `F₀` — среднее `y`. Каждое дерево учится на остатках `y − F` — это антиградиент MSE. Шаг `lr` уменьшает вклад дерева, чтобы ансамбль не переобучался.",
            "1) `f0 = y.mean()`, `F = np.full(len(y), f0)`. 2) `n_estimators` раз: дерево `fit(X, y - F)`, затем `F += lr * tree.predict(X)`, сохраните дерево. 3) Верните `(f0, trees)`. 4) `boost_predict`: `f0 + lr * сумма tree.predict(X)` по всем деревьям.",
        ],
    },
    "ex-w5-sql": {
        "title": "SQL: LEFT JOIN и агрегаты",
        "statement_ru": d("""\
            Таблицы `employees(id, name, dept, salary, manager_id)` и `projects(id, title, owner_id, budget)`.
            Запишите в `QUERY` запрос: для **каждого** сотрудника — `name` и суммарный бюджет его проектов
            (0, если проектов нет). Сортировка: по бюджету по убыванию, затем по имени.

            Проекты: `RAG` (Анна, 50), `Ranker` (Борис, 30), `Site` (Глеб, 20), `ETL` (Борис, 10)."""),
        "starter_code": "QUERY = \"\"\"\nSELECT e.name\nFROM employees e\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                expected = [("Анна", 50), ("Борис", 40), ("Глеб", 20), ("Вера", 0), ("Дина", 0), ("Егор", 0)]
                assert [tuple(r[:2]) for r in rows] == expected, f"получилось {rows}"

            def test_left_join():
                """Сотрудники без проектов не потерялись — LEFT JOIN"""
                assert "left" in QUERY.lower()
            '''),
        "ref": "QUERY = \"\"\"\nSELECT e.name, COALESCE(SUM(p.budget), 0) AS total\nFROM employees e\nLEFT JOIN projects p ON p.owner_id = e.id\nGROUP BY e.id\nORDER BY total DESC, e.name\n\"\"\"\n",
        "hints_ru": [
            "Нужен каждый сотрудник, даже без проектов. Какой результат даст обычный `JOIN` для сотрудника, у которого нет ни одного проекта?",
            "`LEFT JOIN projects` сохраняет сотрудников без пары: поля проекта будут `NULL`. `SUM` по группе из одних `NULL` даёт `NULL`, а не 0. `COALESCE(x, 0)` заменяет `NULL` на 0.",
            "1) `SELECT e.name, COALESCE(SUM(p.budget), 0) AS total`. 2) `FROM employees e LEFT JOIN projects p ON p.owner_id = e.id`. 3) `GROUP BY e.id` — по id, а не по имени: имена могут совпасть. 4) `ORDER BY total DESC, e.name`.",
        ],
    },
}
