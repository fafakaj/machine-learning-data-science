"""Week 6 content: Optuna, K-Fold, SHAP, clustering, PCA, A/B tests, window functions."""

from textwrap import dedent as d

from .w04 import SQL_SETUP

QUIZZES = {
    "q-w6-tuning": {
        "title": "Optuna, K-Fold на практике, SHAP и feature importance",
        "questions": [
            {"type": "choice", "q": "Что Optuna делает по умолчанию (сэмплер TPE)?",
             "options": ["Перебирает всю сетку", "Подбирает следующие параметры по результатам прошлых попыток (байесовская оптимизация)",
                         "Берёт параметры по умолчанию", "Обучает нейросеть"], "answer": 1},
            {"type": "choice", "q": "Зачем pruning в Optuna?",
             "options": ["Удаляет признаки", "Рано останавливает бесперспективные попытки по промежуточным метрикам", "Сжимает модель", "Удаляет выбросы"],
             "answer": 1},
            {"type": "choice", "q": "Подбор гиперпараметров на всех данных, а затем отчёт CV-скора с теми же фолдами. Что не так?",
             "options": ["Всё верно", "Скор оптимистичен: параметры подогнаны под эти фолды. Нужен отложенный тест или вложенная CV",
                         "Нужно больше деревьев", "CV не нужна"], "answer": 1},
            {"type": "choice", "q": "Out-of-fold (OOF) предсказания — это…",
             "options": ["предсказания на тесте", "предсказание для каждого объекта от модели, которая не видела его при обучении",
                         "предсказания на обучении", "случайные предсказания"], "answer": 1},
            {"type": "number", "q": "SHAP: базовое значение модели 0,3, SHAP-значения признаков объекта: +0,25, −0,1, +0,05. Предсказание модели для объекта?",
             "answer": 0.5, "tol": 1e-9, "explain": "SHAP аддитивен: base + Σ φᵢ = f(x)."},
            {"type": "choice", "q": "Почему impurity-based feature importance в деревьях может обманывать?",
             "options": ["Она всегда точна", "Завышает важность признаков с большим числом уникальных значений (например, id); permutation importance или SHAP надёжнее",
                         "Работает только для линейных моделей", "Не зависит от данных"], "answer": 1},
        ],
    },
    "q-w6-unsup": {
        "title": "Кластеризация (k-means, DBSCAN) и PCA",
        "questions": [
            {"type": "choice", "q": "Что минимизирует k-means?",
             "options": ["Число кластеров", "Сумму квадратов расстояний от точек до центра их кластера (inertia)", "Энтропию", "Расстояние между центрами"],
             "answer": 1},
            {"type": "choice", "q": "Какие кластеры k-means находит плохо?",
             "options": ["Шарообразные одного размера", "Вытянутые, вложенные (кольца) и разной плотности", "Хорошо разделённые", "Любые находит одинаково"],
             "answer": 1, "explain": "Для произвольной формы подходит DBSCAN: кластер — область высокой плотности."},
            {"type": "choice", "q": "DBSCAN пометил точку меткой −1. Это…",
             "options": ["первый кластер", "шум: точка не попала ни в одну плотную область", "ошибка", "центр кластера"], "answer": 1},
            {"type": "choice", "q": "Почему перед k-means и PCA обычно стандартизируют признаки?",
             "options": ["Не нужно", "Оба метода опираются на расстояния/дисперсии: признак в больших единицах иначе доминирует", "Для скорости", "Чтобы убрать пропуски"],
             "answer": 1},
            {"type": "number", "q": "PCA: собственные значения ковариационной матрицы 4, 1, 0. Какую долю дисперсии объясняет первая компонента?",
             "answer": 0.8, "tol": 1e-9},
            {"type": "choice", "q": "Главные компоненты PCA — это…",
             "options": ["случайные направления", "ортогональные направления максимальной дисперсии: собственные векторы ковариационной матрицы (правые сингулярные векторы центрированной X)",
                         "исходные признаки", "центры кластеров"], "answer": 1},
        ],
    },
    "q-w6-ab": {
        "title": "A/B-тесты, продуктовые метрики, ценообразование",
        "questions": [
            {"type": "choice", "q": "p-value = 0,03 в A/B-тесте означает:",
             "options": ["вероятность, что B лучше, — 97%", "если разницы на самом деле нет, то результат такой же или более экстремальный случился бы с вероятностью 3%",
                         "вероятность ошибки — 3%", "эффект равен 3%"], "answer": 1},
            {"type": "choice", "q": "Мощность теста (power) — это…",
             "options": ["вероятность найти эффект, если он действительно есть (1 − β)", "уровень значимости α", "размер эффекта", "число пользователей"], "answer": 0},
            {"type": "number", "q": "MDE уменьшили в 2 раза (хотим ловить вдвое меньший эффект). Во сколько раз вырастет нужный размер выборки?",
             "answer": 4, "tol": 1e-9, "explain": "n ∝ 1/MDE²."},
            {"type": "choice", "q": "Аналитик смотрит на p-value каждый день и останавливает тест, как только p < 0,05. Что не так?",
             "options": ["Всё верно", "Подглядывание (peeking): реальная доля ложных срабатываний становится сильно выше 5%", "Нужно смотреть раз в час", "p-value не меняется"],
             "answer": 1},
            {"type": "choice", "q": "Что такое guardrail-метрика?",
             "options": ["Главная метрика теста", "Метрика, которая не должна ухудшиться (время загрузки, отток), даже если целевая растёт", "Метрика дизайна", "Число пользователей"],
             "answer": 1},
            {"type": "choice", "q": "Ценовая эластичность спроса −2. Цену подняли на 1%. Что примерно с объёмом продаж?",
             "options": ["+2%", "−2%", "−0,5%", "Не изменится"], "answer": 1},
        ],
    },
    "q-w6-sql": {
        "title": "SQL: оконные функции",
        "questions": [
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name, salary, RANK() OVER (ORDER BY salary DESC) FROM employees ORDER BY salary DESC, name\"))",
             "explain": "RANK даёт одинаковый ранг равным значениям и пропускает следующий номер."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name, DENSE_RANK() OVER (ORDER BY salary DESC) FROM employees ORDER BY salary DESC, name\"))",
             "explain": "DENSE_RANK не пропускает номера."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name, dept, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name) FROM employees ORDER BY dept, 3\"))",
             "explain": "PARTITION BY нумерует строки отдельно в каждой группе, но не схлопывает их (в отличие от GROUP BY)."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT id, SUM(salary) OVER (ORDER BY id) FROM employees ORDER BY id\"))",
             "explain": "Накопительная сумма: окно от начала до текущей строки."},
            {"type": "output", "code": SQL_SETUP + "print(run(\"SELECT name, salary - LAG(salary) OVER (ORDER BY id) FROM employees ORDER BY id\"))",
             "explain": "LAG берёт значение из предыдущей строки; для первой строки — NULL."},
        ],
    },
}

EXERCISES = {
    "ex-w6-kmeans": {
        "title": "k-means (алгоритм Ллойда) ≈ sklearn",
        "statement_ru": d("""\
            Реализуйте `kmeans(X, centers, n_iter=100)`: алгоритм Ллойда со стартовыми центрами `centers`.
            Шаг: назначьте каждую точку ближайшему центру, затем пересчитайте центры как средние.
            Остановитесь, когда центры перестали меняться. Верните `(labels, centers, inertia)`.

            Тест сравнивает с `KMeans(init=centers, n_init=1)`."""),
        "starter_code": "import numpy as np\n\n\ndef kmeans(X, centers, n_iter=100):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.cluster import KMeans

            rng = np.random.default_rng(3)
            X = np.vstack([rng.normal(c, 0.6, size=(50, 2)) for c in ([0, 0], [4, 4], [0, 5])])
            init = X[[0, 60, 120]]

            def test_vs_sklearn():
                """Метки, центры и inertia ≈ sklearn"""
                labels, centers, inertia = kmeans(X, init.copy())
                sk = KMeans(n_clusters=3, init=init, n_init=1, algorithm="lloyd").fit(X)
                assert np.array_equal(labels, sk.labels_)
                assert np.allclose(centers, sk.cluster_centers_, atol=1e-6)
                assert abs(inertia - sk.inertia_) < 1e-6 * sk.inertia_

            def test_does_not_modify_input():
                """Стартовые центры не меняются на месте"""
                c = init.copy()
                kmeans(X, c)
                assert np.array_equal(c, init)
            '''),
        "ref": d("""\
            import numpy as np


            def kmeans(X, centers, n_iter=100):
                X = np.asarray(X, dtype=float)
                centers = np.array(centers, dtype=float)
                for _ in range(n_iter):
                    dist = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
                    labels = dist.argmin(1)
                    new = np.array([X[labels == k].mean(0) for k in range(len(centers))])
                    if np.allclose(new, centers):
                        centers = new
                        break
                    centers = new
                dist = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
                labels = dist.argmin(1)
                return labels, centers, float(dist.min(1).sum())
        """),
        "hints_ru": [
            "Алгоритм Ллойда повторяет два шага. Какой шаг зависит только от центров, а какой — только от назначений точек? Когда повторять больше не нужно?",
            "Шаг назначения: расстояния до всех центров сразу через broadcasting, форма `(n, k)`; `argmin` по оси 1 даёт метки. Шаг обновления: центр кластера — среднее его точек. Остановка — центры не изменились (`np.allclose`).",
            "1) Скопируйте центры: `np.array(centers, dtype=float)` — вход менять нельзя. 2) В цикле: `dist = ((X[:, None, :] - centers[None]) ** 2).sum(-1)`, `labels = dist.argmin(1)`, новые центры — средние. 3) Центры не изменились — `break`. 4) Пересчитайте `labels` по финальным центрам; `inertia = dist.min(1).sum()`.",
        ],
    },
    "ex-w6-pca": {
        "title": "PCA через SVD ≈ sklearn",
        "statement_ru": d("""\
            Реализуйте `pca(X, k)` через SVD центрированной матрицы. Верните `(Z, components, ratio)`:
            - `Z` — проекции, форма `(n, k)`;
            - `components` — `k` главных направлений, форма `(k, d)`;
            - `ratio` — доля объяснённой дисперсии каждой компоненты.

            Знак компоненты произволен, поэтому тест сравнивает модули."""),
        "starter_code": "import numpy as np\n\n\ndef pca(X, k):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.decomposition import PCA

            rng = np.random.default_rng(4)
            X = rng.normal(size=(100, 4)) @ rng.normal(size=(4, 4)) + 5

            def test_vs_sklearn():
                """Проекции и доли дисперсии ≈ sklearn"""
                Z, comps, ratio = pca(X, 2)
                sk = PCA(n_components=2).fit(X)
                assert Z.shape == (100, 2) and comps.shape == (2, 4)
                assert np.allclose(np.abs(Z), np.abs(sk.transform(X)), atol=1e-8)
                assert np.allclose(ratio, sk.explained_variance_ratio_)

            def test_orthonormal():
                """Компоненты ортонормированы"""
                _, comps, _ = pca(X, 3)
                assert np.allclose(comps @ comps.T, np.eye(3), atol=1e-10)
            '''),
        "ref": d("""\
            import numpy as np


            def pca(X, k):
                X = np.asarray(X, dtype=float)
                Xc = X - X.mean(0)
                U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
                var = S ** 2
                return Xc @ Vt[:k].T, Vt[:k], var[:k] / var.sum()
        """),
        "hints_ru": [
            "Главные направления ищут разброс точек вокруг среднего. Что нужно сделать с данными до разложения, чтобы среднее не исказило направления?",
            "Центрируйте `X` и сделайте SVD: `Xc = U·S·Vt`. Строки `Vt` — главные направления по убыванию важности. Дисперсия вдоль компоненты пропорциональна `S²`, поэтому доля объяснённой дисперсии — `S² / Σ S²`.",
            "1) `Xc = X - X.mean(0)`. 2) `U, S, Vt = np.linalg.svd(Xc, full_matrices=False)`. 3) `components = Vt[:k]`; `Z = Xc @ components.T`. 4) `var = S ** 2`; `ratio = var[:k] / var.sum()`. Знак компонент произвольный — это нормально.",
        ],
    },
    "ex-w6-ztest": {
        "title": "A/B: z-тест для двух конверсий и размер выборки",
        "statement_ru": d("""\
            1. `ztest(conv_a, n_a, conv_b, n_b)` — z-тест для разницы двух долей с общей (pooled) долей.
               Верните `(z, p_value)`, p-value двусторонний. `z > 0`, если B лучше.
            2. `sample_size(p, mde, alpha=0.05, power=0.8)` — сколько пользователей нужно **в каждую** группу,
               чтобы поймать абсолютный рост конверсии `mde` от базы `p`:
               `n = (z₁₋α/₂ + z_power)² · (p(1−p) + (p+mde)(1−p−mde)) / mde²`, округлить вверх.

            Квантили нормального распределения: `scipy.stats.norm.ppf`, хвост: `norm.sf`."""),
        "starter_code": "import math\nfrom scipy.stats import norm\n\n\ndef ztest(conv_a, n_a, conv_b, n_b):\n    pass\n\n\ndef sample_size(p, mde, alpha=0.05, power=0.8):\n    pass\n",
        "tests": d('''\
            import math

            def test_known_values():
                """200/2000 против 250/2000"""
                z, p = ztest(200, 2000, 250, 2000)
                assert abs(z - 2.50196) < 1e-4, z
                assert abs(p - 0.012351) < 1e-5, p

            def test_symmetry():
                """Перестановка групп меняет знак z, но не p-value"""
                z1, p1 = ztest(200, 2000, 250, 2000)
                z2, p2 = ztest(250, 2000, 200, 2000)
                assert abs(z1 + z2) < 1e-12 and abs(p1 - p2) < 1e-12

            def test_no_difference():
                """Одинаковые конверсии — z = 0, p = 1"""
                z, p = ztest(100, 1000, 100, 1000)
                assert abs(z) < 1e-12 and abs(p - 1) < 1e-12

            def test_sample_size():
                """Размер выборки: база 10%, MDE 1 п.п."""
                n = sample_size(0.10, 0.01)
                assert n == 14749, n
                assert sample_size(0.10, 0.005) > 3.5 * n
            '''),
        "ref": d("""\
            import math
            from scipy.stats import norm


            def ztest(conv_a, n_a, conv_b, n_b):
                pa, pb = conv_a / n_a, conv_b / n_b
                p = (conv_a + conv_b) / (n_a + n_b)
                se = math.sqrt(p * (1 - p) * (1 / n_a + 1 / n_b))
                z = (pb - pa) / se
                return z, float(2 * norm.sf(abs(z)))


            def sample_size(p, mde, alpha=0.05, power=0.8):
                z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
                return math.ceil(z ** 2 * (p * (1 - p) + (p + mde) * (1 - p - mde)) / mde ** 2)
        """),
        "hints_ru": [
            "Если A и B на самом деле не отличаются, какой одной долей лучше всего оценить конверсию? От чего зависит разброс разницы двух выборочных долей?",
            "z-тест с общей (pooled) долей: при нулевой гипотезе обе группы имеют одну долю `p = (conv_a + conv_b) / (n_a + n_b)`. Стандартная ошибка разницы — `sqrt(p(1−p)(1/n_a + 1/n_b))`. Двусторонний p-value учитывает оба хвоста: `2·norm.sf(|z|)`.",
            "1) `pa`, `pb`, общая `p`, `se`. 2) `z = (pb - pa) / se` — положительный, если B лучше. 3) Верните `(z, 2 * norm.sf(abs(z)))`. 4) `sample_size`: `z = norm.ppf(1 - alpha/2) + norm.ppf(power)`, подставьте в формулу, округлите вверх `math.ceil`.",
        ],
    },
    "ex-w6-sql": {
        "title": "SQL: топ-1 по зарплате в каждом отделе (окна)",
        "statement_ru": d("""\
            Запишите в `QUERY` запрос: для каждого отдела — сотрудник с максимальной зарплатой
            (при равенстве — первый по имени). Столбцы: `dept`, `name`, `salary`, сортировка по `dept`.
            Используйте оконную функцию `ROW_NUMBER() OVER (PARTITION BY …)`."""),
        "starter_code": "QUERY = \"\"\"\nSELECT dept, name, salary\nFROM employees\n\"\"\"\n",
        "tests": SQL_SETUP + d('''\

            def test_result():
                """Результат запроса"""
                rows = run(QUERY)
                assert rows == [("Data", "Егор", 180), ("ML", "Анна", 300), ("Web", "Глеб", 150)], f"получилось {rows}"

            def test_window():
                """Используется оконная функция"""
                assert "over" in QUERY.lower() and "partition" in QUERY.lower()
            '''),
        "ref": "QUERY = \"\"\"\nSELECT dept, name, salary FROM (\n    SELECT dept, name, salary,\n           ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name) AS rn\n    FROM employees\n)\nWHERE rn = 1\nORDER BY dept\n\"\"\"\n",
        "hints_ru": [
            "Нужен один лучший сотрудник в каждом отделе, но строки сотрудников не должны схлопываться в одну строку группы. Как пометить «первого» внутри отдела?",
            "Оконная функция `ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name)` нумерует сотрудников внутри каждого отдела, не схлопывая строки. Оконные функции считаются после `WHERE`, поэтому фильтр по номеру — только во внешнем запросе.",
            "1) Внутренний запрос: `dept, name, salary` и номер `AS rn`. 2) Внешний: `SELECT dept, name, salary FROM (...) WHERE rn = 1`. 3) `ORDER BY dept`. `name` в `ORDER BY` окна решает ничьи по зарплате.",
        ],
    },
}
