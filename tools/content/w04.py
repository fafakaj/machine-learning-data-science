"""Week 4: ML basics (E2–E8) and SQL."""

from textwrap import dedent as d

SQL_SETUP = d("""\
    import sqlite3

    def make_db():
        db = sqlite3.connect(":memory:")
        db.executescript('''
            CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, manager_id INTEGER);
            INSERT INTO employees VALUES
                (1, 'Анна', 'ML', 300, NULL), (2, 'Борис', 'ML', 200, 1), (3, 'Вера', 'ML', 200, 1),
                (4, 'Глеб', 'Web', 150, NULL), (5, 'Дина', 'Web', 120, 4), (6, 'Егор', 'Data', 180, NULL);
            CREATE TABLE projects (id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, budget INTEGER);
            INSERT INTO projects VALUES (1, 'RAG', 1, 50), (2, 'Ranker', 2, 30), (3, 'Site', 4, 20), (4, 'ETL', 2, 10);
        ''')
        return db

    def run(query):
        return make_db().execute(query).fetchall()
""")

QUIZZES = {
    "q-w4-ml1": {
        "title": "Train/val/test, переобучение (E2), bias–variance, регуляризация (E6)",
        "questions": [
            {"type": "choice", "q": "Зачем нужна отдельная тестовая выборка, если есть валидационная?",
             "options": ["Она не нужна", "На валидации подбирают гиперпараметры и модель, поэтому оценка на ней оптимистична; тест — честная финальная оценка",
                         "Тест нужен для обучения", "Валидация нужна только для нейросетей"],
             "answer": 1, "explain": "Каждый выбор по валидации — это немного «обучения» на ней."},
            {"type": "choice", "q": "E2. Ошибка на train 0,02, на val 0,30. Что это и что делать?",
             "options": ["Недообучение — усложнить модель", "Переобучение — регуляризация, больше данных, проще модель, ранняя остановка", "Всё хорошо", "Утечка данных — удалить train"],
             "answer": 1, "explain": "Большой разрыв train/val — признак высокой дисперсии (variance)."},
            {"type": "choice", "q": "Высокий bias (смещение) — это когда…",
             "options": ["Модель слишком сложная", "Модель слишком простая и ошибается одинаково на train и val", "Данные несбалансированы", "Много выбросов"],
             "answer": 1, "explain": "Например, линейная модель для сильно нелинейной зависимости."},
            {"type": "choice", "q": "E6. Чем L1-регуляризация отличается от L2 по эффекту на веса?",
             "options": ["Ничем", "L1 зануляет часть весов (отбор признаков), L2 равномерно уменьшает веса, не обнуляя", "L2 зануляет веса", "L1 увеличивает веса"],
             "answer": 1, "explain": "У |w| производная не зависит от величины веса — малые веса доходят до нуля. У w² сила тяги пропорциональна весу."},
            {"type": "number", "q": "Градиентный спуск для f(w) = (w − 3)², w₀ = 0, lr = 0,25. Чему равно w после одного шага?", "answer": 1.5, "tol": 1e-9,
             "explain": "f′(w) = 2(w − 3) = −6; w₁ = 0 − 0,25·(−6) = 1,5."},
            {"type": "choice", "q": "Что будет при слишком большом learning rate?",
             "options": ["Обучение медленнее, но стабильно", "Шаги перепрыгивают минимум, лосс скачет или растёт (расходимость)", "Модель переобучится", "Ничего"],
             "answer": 1, "explain": "Для (w − 3)² при lr > 1 каждый шаг увеличивает расстояние до минимума."},
            {"type": "choice", "q": "Логистическая регрессия выдаёт…",
             "options": ["Класс напрямую", "Вероятность класса: σ(w·x + b); обучается минимизацией log loss", "Расстояние до центра", "Число соседей"],
             "answer": 1, "explain": "Порог 0,5 — отдельное решение, его можно двигать под метрику."},
        ],
    },
    "q-w4-ml2": {
        "title": "Метрики (E3), кросс-валидация (E4), утечки (E7), kNN и k-means (E8)",
        "questions": [
            {"type": "vector", "q": "E3. TP = 40, FP = 10, FN = 20, TN = 930. Найдите precision, recall, accuracy", "answer": [0.8, 40 / 60, 0.97], "tol": 1e-3,
             "labels": ["precision", "recall", "accuracy"], "explain": "P = 40/50, R = 40/60, Acc = 970/1000. Высокая accuracy при редком классе мало что значит."},
            {"type": "number", "q": "F1 для precision = 0,8 и recall = 2/3", "answer": 2 * 0.8 * (2 / 3) / (0.8 + 2 / 3), "tol": 1e-3,
             "explain": "F1 = 2PR/(P + R) ≈ 0,727 — гармоническое среднее, тянется к меньшему."},
            {"type": "choice", "q": "Мошенничество — 0,1% транзакций. Какая метрика плохая?",
             "options": ["Accuracy", "PR-AUC", "Recall при фиксированной precision", "F1"], "answer": 0,
             "explain": "Модель «всегда не мошенник» даёт 99,9% accuracy и бесполезна."},
            {"type": "choice", "q": "ROC-AUC = 0,5 означает:", "options": ["Идеальная модель", "Модель ранжирует не лучше случайной", "Модель всегда ошибается", "Половина объектов верна"],
             "answer": 1, "explain": "AUC — вероятность, что случайный положительный объект получит скор выше случайного отрицательного."},
            {"type": "choice", "q": "E4. Зачем StratifiedKFold вместо KFold?",
             "options": ["Он быстрее", "Сохраняет долю классов в каждом фолде — важно при дисбалансе", "Для регрессии", "Перемешивает признаки"],
             "answer": 1, "explain": "Иначе в фолде может почти не оказаться редкого класса, и оценка будет шумной."},
            {"type": "multi", "q": "E7. Что из этого — утечка данных?",
             "options": ["StandardScaler.fit на всём датасете до разбиения", "Признак «дата возврата товара» для предсказания возврата",
                         "Стандартизация внутри Pipeline с cross_val_score", "Случайное разбиение временного ряда (будущее попадает в train)"],
             "answers": [0, 1, 3], "explain": "Pipeline обучает скейлер только на train-фолде — это правильный путь."},
            {"type": "choice", "q": "E8. Чем kNN отличается от k-means?",
             "options": ["Это одно и то же", "kNN — обучение с учителем (классификация/регрессия по k соседям), k-means — кластеризация без учителя (k центров)",
                         "k-means — классификация", "kNN строит k кластеров"],
             "answer": 1, "explain": "Совпадает только буква k, и смысл у неё разный: число соседей против числа кластеров."},
        ],
    },
    "q-w4-sql": {
        "title": "SQL: SELECT, WHERE, GROUP BY, HAVING, ORDER BY (G1)",
        "questions": [
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name FROM employees WHERE salary >= 200 ORDER BY name\"))",
             "explain": "WHERE фильтрует строки до группировки; ORDER BY сортирует результат."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT dept, COUNT(*), MAX(salary) FROM employees GROUP BY dept ORDER BY dept\"))",
             "explain": "GROUP BY схлопывает строки в группы; в SELECT — только ключи группировки и агрегаты."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT dept FROM employees GROUP BY dept HAVING AVG(salary) > 150 ORDER BY dept\"))",
             "explain": "HAVING фильтрует **группы** после агрегации. Web: (150 + 120)/2 = 135 — отсеян."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT COUNT(manager_id), COUNT(*) FROM employees\"))",
             "explain": "COUNT(столбец) не считает NULL, COUNT(*) считает все строки."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name FROM employees WHERE manager_id = NULL\"), run(\"SELECT COUNT(*) FROM employees WHERE manager_id IS NULL\"))",
             "explain": "Сравнение с NULL через `=` всегда даёт NULL (не TRUE). Нужно `IS NULL`."},
            {"type": "choice", "q": "Порядок логического выполнения частей запроса:",
             "options": ["SELECT → FROM → WHERE → GROUP BY", "FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT", "WHERE → FROM → SELECT", "ORDER BY → SELECT → FROM"],
             "answer": 1, "explain": "Поэтому псевдоним из SELECT нельзя использовать в WHERE, но можно в ORDER BY."},
        ],
    },
    "q-w4-checkpoint": {
        "title": "Контрольная точка 22.11: части B, D, E входного теста",
        "questions": [
            {"type": "output", "code": "def f(x, acc=[]):\n    acc.append(x)\n    return len(acc)\n\nprint(f(1), f(2), f(3, []), f(4))", "explain": "B1 снова: общий список у вызовов без acc."},
            {"type": "output", "code": "nums = [1, 2, 3]\ngen = (n * 2 for n in nums)\nnums.append(4)\nprint(list(gen))",
             "explain": "Генератор ленивый: он читает список при итерации, когда там уже 4 элемента."},
            {"type": "choice", "q": "B7: 8 потоков, CPU-тяжёлый чистый Python. Ускорение?", "options": ["≈8×", "≈1× (GIL)", "≈2×", "Замедление в 8 раз"], "answer": 1},
            {"type": "expr", "q": "D1: ∂/∂w от L = (wx + b − y)²", "vars": ["w", "x", "b", "y"], "ref": "2*(w*x + b - y)*x", "domain": [[-2, 2]] * 4,
             "explain": "Цепное правило: 2(ŷ − y) · ∂ŷ/∂w = 2(ŷ − y)·x. Это градиент MSE для одного объекта."},
            {"type": "number", "q": "D3: prior 0,02, чувствительность 0,9, специфичность 0,9. P(болен | +)?", "answer": 0.018 / (0.018 + 0.098), "tol": 2e-3},
            {"type": "number", "q": "D4: Var(3X), если Var X = 2", "answer": 18, "tol": 1e-9, "explain": "Var(aX) = a²·Var X."},
            {"type": "choice", "q": "E2: train-ошибка высокая и val-ошибка такая же высокая. Это…", "options": ["переобучение", "недообучение (высокий bias)", "утечка", "норма"], "answer": 1},
            {"type": "choice", "q": "E6: какой регуляризатор даст разреженные веса?", "options": ["L2", "L1", "Dropout", "BatchNorm"], "answer": 1},
            {"type": "choice", "q": "E7: подбор порога классификации по тестовой выборке — это…", "options": ["правильно", "утечка: тест перестаёт быть честной оценкой", "регуляризация", "кросс-валидация"], "answer": 1},
        ],
    },
    "q-w4-oral": {
        "title": "Мок №1 с другом: Python + основы ML (вопросы для интервьюера)",
        "oral": True,
        "questions": [
            {"type": "text", "q": "Объясните переобучение. Как его заметить и какие 4 способа борьбы вы знаете?",
             "model": "Модель запоминает шум train: ошибка train низкая, val высокая. Борьба: регуляризация (L1/L2), больше данных/аугментация, проще модель, ранняя остановка, dropout (для сетей), кросс-валидация для честной оценки."},
            {"type": "text", "q": "Почему accuracy плоха при дисбалансе? Какие метрики выбрать и почему?",
             "model": "Константная модель получает высокую accuracy. Precision/recall/F1, PR-AUC, ROC-AUC; выбор зависит от цены ошибок FP и FN."},
            {"type": "text", "q": "Что такое утечка данных? Два примера и как защититься.",
             "model": "Информация из теста/будущего попадает в обучение. Примеры: скейлер на всём датасете, признак из будущего, случайный сплит временного ряда, дубликаты в train и test. Защита: Pipeline, временной сплит, GroupKFold, аудит признаков."},
            {"type": "text", "q": "Выведите градиент MSE для линейной регрессии и опишите шаг градиентного спуска.",
             "model": "L = (1/n)Σ(Xw − y)²; ∇w = (2/n)Xᵀ(Xw − y). Шаг: w ← w − lr·∇w. Для b: (2/n)Σ(ŷ − y)."},
        ],
    },
}

EXERCISES = {
    "ex-w4-linreg": {
        "title": "Линейная регрессия на NumPy: градиентный спуск ≈ sklearn",
        "statement_ru": d("""\
            Напишите класс `LinReg(lr=0.1, n_iter=2000)`:
            - `fit(X, y)` — градиентный спуск по MSE для весов `coef_` (форма `(d,)`) и смещения `intercept_` (число);
            - `predict(X)` → `X @ coef_ + intercept_`.

            Градиент: `∂L/∂w = (2/n)·Xᵀ(ŷ − y)`, `∂L/∂b = (2/n)·Σ(ŷ − y)`. Без циклов по объектам
            (цикл только по итерациям). Тест сравнивает ваши веса с `sklearn.linear_model.LinearRegression`."""),
        "starter_code": "import numpy as np\n\n\nclass LinReg:\n    def __init__(self, lr=0.1, n_iter=2000):\n        self.lr = lr\n        self.n_iter = n_iter\n\n    def fit(self, X, y):\n        pass\n\n    def predict(self, X):\n        pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.linear_model import LinearRegression

            def data(seed=0, n=200, d=3):
                rng = np.random.default_rng(seed)
                X = rng.normal(size=(n, d))
                y = X @ np.array([1.5, -2.0, 0.5])[:d] + 3.0 + rng.normal(scale=0.1, size=n)
                return X, y

            def test_matches_sklearn():
                """Веса ≈ LinearRegression"""
                X, y = data()
                mine = LinReg().fit(X, y)
                ref = LinearRegression().fit(X, y)
                assert np.allclose(mine.coef_, ref.coef_, atol=1e-3), f"{mine.coef_} vs {ref.coef_}"
                assert abs(mine.intercept_ - ref.intercept_) < 1e-3

            def test_predict_shape():
                """predict возвращает (n,)"""
                X, y = data(1, n=50, d=2)
                m = LinReg().fit(X, y)
                assert m.predict(X).shape == (50,)

            def test_fit_returns_self():
                """fit возвращает self"""
                X, y = data(2, n=20, d=1)
                m = LinReg(n_iter=10)
                assert m.fit(X, y) is m
            '''),
        "ref": d("""\
            import numpy as np


            class LinReg:
                def __init__(self, lr=0.1, n_iter=2000):
                    self.lr = lr
                    self.n_iter = n_iter

                def fit(self, X, y):
                    X = np.asarray(X, dtype=float)
                    y = np.asarray(y, dtype=float)
                    n, d = X.shape
                    self.coef_ = np.zeros(d)
                    self.intercept_ = 0.0
                    for _ in range(self.n_iter):
                        err = X @ self.coef_ + self.intercept_ - y
                        self.coef_ -= self.lr * (2 / n) * (X.T @ err)
                        self.intercept_ -= self.lr * (2 / n) * err.sum()
                    return self

                def predict(self, X):
                    return np.asarray(X, dtype=float) @ self.coef_ + self.intercept_
            """),
        "hints_ru": [
            "Градиент показывает, куда растёт ошибка. Куда тогда нужно двигать веса на каждой итерации? Что нужно посчитать до градиента?",
            "Градиентный спуск в матричной форме: `err = ŷ − y`, `grad_w = (2/n)·Xᵀ·err` — вектор формы (d,) для всех весов сразу. Цикл Python нужен только по итерациям, не по объектам.",
            "1) `coef_ = np.zeros(d)`, `intercept_ = 0.0`. 2) `n_iter` раз: `err = X @ coef_ + intercept_ - y`; `coef_ -= lr * (2/n) * (X.T @ err)`; `intercept_ -= lr * (2/n) * err.sum()`. 3) `fit` возвращает `self`. 4) `predict`: `X @ coef_ + intercept_`.",
        ],
    },
    "ex-w4-logreg": {
        "title": "Логистическая регрессия на NumPy ≈ sklearn",
        "statement_ru": d("""\
            Напишите `LogReg(lr=0.5, n_iter=3000)` для бинарной классификации (метки 0/1):
            - `fit(X, y)` — градиентный спуск по log loss (без регуляризации);
            - `predict_proba(X)` → вероятности класса 1, форма `(n,)`;
            - `predict(X)` → 0/1 с порогом 0,5.

            Градиент log loss удивительно простой: `∂L/∂w = (1/n)·Xᵀ(p − y)`, где `p = σ(Xw + b)`.
            Тест сравнивает вероятности с `LogisticRegression(penalty=None)`."""),
        "starter_code": "import numpy as np\n\n\nclass LogReg:\n    def __init__(self, lr=0.5, n_iter=3000):\n        self.lr = lr\n        self.n_iter = n_iter\n",
        "tests": d('''\
            import numpy as np
            from sklearn.linear_model import LogisticRegression

            def data():
                rng = np.random.default_rng(4)
                X = rng.normal(size=(300, 2))
                logits = 1.2 * X[:, 0] - 0.8 * X[:, 1] + 0.3
                y = (rng.random(300) < 1 / (1 + np.exp(-logits))).astype(int)
                return X, y

            def test_proba_matches_sklearn():
                """Вероятности ≈ LogisticRegression(penalty=None)"""
                X, y = data()
                mine = LogReg().fit(X, y)
                ref = LogisticRegression(penalty=None).fit(X, y)
                diff = np.abs(mine.predict_proba(X) - ref.predict_proba(X)[:, 1]).max()
                assert diff < 1e-3, f"максимальная разница вероятностей {diff:.4f}"

            def test_predict_labels():
                """predict даёт 0/1"""
                X, y = data()
                pred = LogReg().fit(X, y).predict(X)
                assert set(np.unique(pred)) <= {0, 1}
                assert (pred == y).mean() > 0.7

            def test_stable_sigmoid():
                """Нет overflow на больших логитах"""
                import warnings
                X = np.array([[1000.0], [-1000.0]])
                m = LogReg(n_iter=1).fit(X, np.array([1, 0]))
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    p = m.predict_proba(X * 10)
                assert np.all(np.isfinite(p))
            '''),
        "ref": d("""\
            import numpy as np


            def sigmoid(z):
                out = np.empty_like(z, dtype=float)
                pos = z >= 0
                out[pos] = 1 / (1 + np.exp(-z[pos]))
                ez = np.exp(z[~pos])
                out[~pos] = ez / (1 + ez)
                return out


            class LogReg:
                def __init__(self, lr=0.5, n_iter=3000):
                    self.lr = lr
                    self.n_iter = n_iter

                def fit(self, X, y):
                    X = np.asarray(X, dtype=float)
                    y = np.asarray(y, dtype=float)
                    n, d = X.shape
                    self.coef_ = np.zeros(d)
                    self.intercept_ = 0.0
                    for _ in range(self.n_iter):
                        err = sigmoid(X @ self.coef_ + self.intercept_) - y
                        self.coef_ -= self.lr * (X.T @ err) / n
                        self.intercept_ -= self.lr * err.mean()
                    return self

                def predict_proba(self, X):
                    return sigmoid(np.asarray(X, dtype=float) @ self.coef_ + self.intercept_)

                def predict(self, X):
                    return (self.predict_proba(X) >= 0.5).astype(int)
            """),
        "hints_ru": [
            "Сравните с `LinReg`. Что меняется в прогнозе, если ответ — вероятность от 0 до 1? Посчитайте `np.exp(1000)`: где в сигмоиде это может случиться?",
            "Прогноз — `σ(Xw + b)`, градиент log loss — `Xᵀ(p − y)/n`, без двойки. Устойчивая сигмоида: для z ≥ 0 — `1/(1 + e^(−z))`, для z < 0 — `e^z/(1 + e^z)`. В обоих случаях показатель экспоненты ≤ 0, переполнения нет.",
            "1) `sigmoid(z)`: `out = np.empty_like(z, dtype=float)`; маска `pos = z >= 0`; заполните `out[pos]` и `out[~pos]` по двум формулам. 2) `fit`: как в `LinReg`, но `err = sigmoid(...) - y`, шаг `lr * X.T @ err / n` и `lr * err.mean()`. 3) `predict`: `(proba >= 0.5).astype(int)`.",
        ],
    },
    "ex-w4-metrics": {
        "title": "Метрики классификации с нуля ≈ sklearn",
        "statement_ru": d("""\
            Напишите функции для бинарных меток 0/1 (списки или массивы):
            - `confusion(y_true, y_pred)` → `(tp, fp, fn, tn)`;
            - `precision_recall_f1(y_true, y_pred)` → кортеж из трёх float (если знаменатель 0 — значение 0.0);
            - `roc_auc(y_true, scores)` — вероятность, что случайный положительный объект получит скор выше
              случайного отрицательного; ничьи считаются как 0,5."""),
        "starter_code": "import numpy as np\n\n\ndef confusion(y_true, y_pred):\n    pass\n\n\ndef precision_recall_f1(y_true, y_pred):\n    pass\n\n\ndef roc_auc(y_true, scores):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

            rng = np.random.default_rng(5)
            Y = rng.integers(0, 2, 200)
            P = np.where(rng.random(200) < 0.8, Y, 1 - Y)
            S = Y * 0.3 + rng.random(200)

            def test_confusion():
                """Матрица ошибок"""
                assert confusion([1, 1, 0, 0, 1], [1, 0, 1, 0, 1]) == (2, 1, 1, 1)

            def test_prf_vs_sklearn():
                """precision, recall, f1 ≈ sklearn"""
                p, r, f = precision_recall_f1(Y, P)
                assert np.allclose([p, r, f], [precision_score(Y, P), recall_score(Y, P), f1_score(Y, P)])

            def test_zero_division():
                """Нет положительных предсказаний — 0.0"""
                assert precision_recall_f1([1, 0], [0, 0]) == (0.0, 0.0, 0.0)

            def test_auc_vs_sklearn():
                """ROC-AUC ≈ sklearn, с ничьими"""
                assert abs(roc_auc(Y, S) - roc_auc_score(Y, S)) < 1e-9
                assert roc_auc([0, 1, 0, 1], [0.5, 0.5, 0.1, 0.9]) == roc_auc_score([0, 1, 0, 1], [0.5, 0.5, 0.1, 0.9])
            '''),
        "ref": d("""\
            import numpy as np


            def confusion(y_true, y_pred):
                t = np.asarray(y_true)
                p = np.asarray(y_pred)
                return (int(((t == 1) & (p == 1)).sum()), int(((t == 0) & (p == 1)).sum()),
                        int(((t == 1) & (p == 0)).sum()), int(((t == 0) & (p == 0)).sum()))


            def precision_recall_f1(y_true, y_pred):
                tp, fp, fn, _ = confusion(y_true, y_pred)
                p = tp / (tp + fp) if tp + fp else 0.0
                r = tp / (tp + fn) if tp + fn else 0.0
                f = 2 * p * r / (p + r) if p + r else 0.0
                return (float(p), float(r), float(f))


            def roc_auc(y_true, scores):
                t = np.asarray(y_true)
                s = np.asarray(scores, dtype=float)
                pos, neg = s[t == 1], s[t == 0]
                cmp = pos[:, None] - neg[None, :]
                return float(((cmp > 0).sum() + 0.5 * (cmp == 0).sum()) / (len(pos) * len(neg)))
            """),
        "hints_ru": [
            "Каждый объект попадает ровно в одну из четырёх клеток: истина 0/1 и прогноз 0/1. Как посчитать объекты одной клетки без цикла? Что такое AUC, если смотреть на пары объектов?",
            "Булевы маски NumPy: `((t == 1) & (p == 1)).sum()` даёт tp. Перед делением проверяйте знаменатель. AUC — доля пар (положительный, отрицательный), где у положительного скор выше; все пары даёт broadcasting.",
            "1) `confusion`: четыре маски, верните `int`. 2) `precision = tp / (tp + fp) if tp + fp else 0.0`; так же recall и F1. 3) `roc_auc`: `pos = s[t == 1]`, `neg = s[t == 0]`; `cmp = pos[:, None] - neg[None, :]`; `(cmp > 0).sum() + 0.5 * (cmp == 0).sum()`, делённое на `len(pos) * len(neg)`.",
        ],
    },
    "ex-w4-kfold": {
        "title": "Стратифицированный K-Fold своими руками",
        "statement_ru": d("""\
            Напишите `stratified_kfold(y, k, seed=0)` — список из `k` пар `(train_idx, val_idx)` (списки индексов):
            - каждый индекс ровно один раз попадает в валидацию;
            - train и val одной пары не пересекаются и вместе дают все индексы;
            - в каждом фолде доля каждого класса в val отличается от доли в `y` не больше чем на 1 объект
              (раскладывайте индексы каждого класса по фолдам по кругу после перемешивания)."""),
        "starter_code": "import random\n\n\ndef stratified_kfold(y, k, seed=0):\n    pass\n",
        "tests": d('''\
            from collections import Counter

            Y = [0] * 90 + [1] * 10

            def test_partition():
                """Валидационные части покрывают все индексы ровно один раз"""
                folds = stratified_kfold(Y, 5)
                assert len(folds) == 5
                seen = sorted(i for _, val in folds for i in val)
                assert seen == list(range(len(Y)))
                for train, val in folds:
                    assert not set(train) & set(val)
                    assert sorted(list(train) + list(val)) == list(range(len(Y)))

            def test_stratified():
                """В каждом фолде 2 объекта редкого класса"""
                for _, val in stratified_kfold(Y, 5):
                    assert Counter(Y[i] for i in val)[1] == 2, "редкий класс распределён неравномерно"

            def test_shuffled_and_seeded():
                """Перемешано, но воспроизводимо"""
                a = stratified_kfold(Y, 5, seed=1)
                b = stratified_kfold(Y, 5, seed=1)
                assert a == b
                assert sorted(a[0][1]) != list(range(18)), "индексы не перемешаны"
            '''),
        "ref": d("""\
            import random


            def stratified_kfold(y, k, seed=0):
                rng = random.Random(seed)
                folds = [[] for _ in range(k)]
                by_class = {}
                for i, label in enumerate(y):
                    by_class.setdefault(label, []).append(i)
                pos = 0
                for label in sorted(by_class):
                    idx = by_class[label][:]
                    rng.shuffle(idx)
                    for i in idx:
                        folds[pos % k].append(i)
                        pos += 1
                everything = set(range(len(y)))
                return [(sorted(everything - set(f)), f) for f in folds]
            """),
        "hints_ru": [
            "Как разложить индексы по `k` фолдам, чтобы в каждом фолде было почти одинаково объектов класса 0 и класса 1? Можно ли раскладывать все индексы вместе?",
            "Раскладывайте каждый класс отдельно: перемешайте индексы класса и раздавайте их по кругу `folds[pos % k]`. Раздача по кругу даёт разницу между фолдами не больше 1 объекта. Счётчик `pos` не сбрасывайте между классами.",
            "1) `rng = random.Random(seed)`; словарь `label → [индексы]`. 2) Для `label` в `sorted(...)`: копия индексов, `rng.shuffle`, раздача по кругу. 3) Для каждого фолда: `train = sorted(set(range(n)) - set(val))`. 4) Верните список пар `(train, val)`.",
        ],
    },
    "ex-w4-sql": {
        "title": "SQL: GROUP BY и HAVING (sqlite в браузере)",
        "statement_ru": d("""\
            Таблица `employees(id, name, dept, salary, manager_id)`. Запишите в переменную `QUERY` SQL-запрос:
            для каждого отдела, где **больше одного** сотрудника, вывести `dept`, число сотрудников и
            среднюю зарплату, отсортировать по средней зарплате по убыванию.

            Данные (те же, что в квизе):
            ```
            1 Анна  ML   300 NULL
            2 Борис ML   200 1
            3 Вера  ML   200 1
            4 Глеб  Web  150 NULL
            5 Дина  Web  120 4
            6 Егор  Data 180 NULL
            ```"""),
        "starter_code": "QUERY = \"\"\"\nSELECT dept\nFROM employees\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                assert [(r[0], r[1]) for r in rows] == [("ML", 3), ("Web", 2)], f"получилось {rows}"
                assert abs(rows[0][2] - 233.33) < 0.01 and abs(rows[1][2] - 135) < 0.01

            def test_uses_having():
                """Условие на группы — через HAVING"""
                assert "having" in QUERY.lower(), "фильтр по числу сотрудников делается в HAVING"
            '''),
        "ref": "QUERY = \"\"\"\nSELECT dept, COUNT(*) AS n, AVG(salary) AS avg_salary\nFROM employees\nGROUP BY dept\nHAVING COUNT(*) > 1\nORDER BY avg_salary DESC\n\"\"\"\n",
        "hints_ru": [
            "Нужна одна строка результата на отдел. Какая операция SQL собирает строки в группы? Где проверять условие «больше одного сотрудника»: до группировки или после?",
            "`GROUP BY dept` даёт группы; `COUNT(*)` и `AVG(salary)` считаются по группе. `WHERE` фильтрует строки до группировки, `HAVING` — группы после. Число сотрудников известно только после группировки, поэтому условие в `HAVING`.",
            "1) `SELECT dept, COUNT(*) AS n, AVG(salary) AS avg_salary FROM employees`. 2) `GROUP BY dept`. 3) `HAVING COUNT(*) > 1`. 4) `ORDER BY avg_salary DESC`.",
        ],
    },
}
