"""Week 3: probability and statistics, NumPy, pandas, Bash."""

from textwrap import dedent as d

QUIZZES = {
    "q-w3-prob": {
        "title": "Вероятность, условная вероятность, Байес (D3), матожидание и дисперсия (D4)",
        "questions": [
            {"type": "number", "q": "Бросаем два кубика. Вероятность, что сумма равна 7?", "answer": 1 / 6, "tol": 1e-3,
             "explain": "Благоприятных исходов 6 из 36: (1,6), (2,5), … (6,1)."},
            {"type": "number", "q": "P(A) = 0,3, P(B) = 0,5, A и B независимы. Найдите P(A и B)", "answer": 0.15, "tol": 1e-6,
             "explain": "Для независимых событий P(A∩B) = P(A)·P(B)."},
            {"type": "number", "q": "P(A ∪ B), если P(A) = 0,3, P(B) = 0,5, P(A ∩ B) = 0,1", "answer": 0.7, "tol": 1e-6,
             "explain": "Формула включений-исключений: 0,3 + 0,5 − 0,1."},
            {"type": "number", "q": "D3. Болезнью болеет 1% людей. Тест находит болезнь у 99% больных (чувствительность) и даёт ложную тревогу у 5% здоровых. Тест положительный. Вероятность, что человек болен?",
             "answer": 0.0099 / (0.0099 + 0.0495), "tol": 2e-3,
             "explain": "Байес: P(Б|+) = 0,99·0,01 / (0,99·0,01 + 0,05·0,99) ≈ 0,167. Большинство положительных — здоровые: болезнь редкая (низкая априорная вероятность)."},
            {"type": "number", "q": "D4. X — результат броска честного кубика. E[X] = ?", "answer": 3.5, "tol": 1e-6, "explain": "(1+2+…+6)/6 = 3,5."},
            {"type": "number", "q": "D4. Var[X] для броска кубика", "answer": 35 / 12, "tol": 1e-3,
             "explain": "E[X²] = 91/6; Var = E[X²] − (E[X])² = 91/6 − 12,25 = 35/12 ≈ 2,917."},
            {"type": "number", "q": "X и Y независимы, Var X = 4, Var Y = 9. Var(2X − Y) = ?", "answer": 25, "tol": 1e-6,
             "explain": "Var(aX + bY) = a²Var X + b²Var Y для независимых: 4·4 + 1·9 = 25. Минус не вычитает дисперсию."},
            {"type": "choice", "q": "Что означает E[X + Y] = E[X] + E[Y]?",
             "options": ["Верно только для независимых X и Y", "Верно всегда (линейность матожидания)", "Верно только для нормальных", "Неверно"],
             "answer": 1, "explain": "Линейность матожидания не требует независимости. А вот Var(X + Y) = Var X + Var Y — требует некоррелированности."},
        ],
    },
    "q-w3-stats": {
        "title": "Распределения, ЦПТ, гипотезы, p-value (D5)",
        "questions": [
            {"type": "choice", "q": "Какое распределение у числа успехов в n независимых испытаниях с вероятностью p?",
             "options": ["Пуассона", "Биномиальное", "Равномерное", "Экспоненциальное"], "answer": 1, "explain": "Bin(n, p): E = np, Var = np(1 − p)."},
            {"type": "choice", "q": "Центральная предельная теорема утверждает:",
             "options": ["Любые данные распределены нормально", "Среднее n независимых одинаково распределённых величин с конечной дисперсией при больших n примерно нормально",
                         "Медиана равна среднему", "Дисперсия выборки равна дисперсии генеральной совокупности"],
             "answer": 1, "explain": "Отсюда нормальные доверительные интервалы для средних и z-тесты в A/B (неделя 6)."},
            {"type": "number", "q": "Стандартное отклонение величины — 10. Стандартная ошибка среднего по n = 100 наблюдениям?", "answer": 1, "tol": 1e-6,
             "explain": "SE = σ/√n = 10/10 = 1. Чтобы уменьшить SE вдвое, нужно в 4 раза больше данных."},
            {"type": "choice", "q": "D5. p-value = 0,03. Что это значит?",
             "options": ["Вероятность, что нулевая гипотеза верна, — 3%", "Если H₀ верна, вероятность получить результат не менее экстремальный, чем наблюдаемый, — 3%",
                         "Эффект равен 3%", "С вероятностью 97% альтернатива верна"],
             "answer": 1, "explain": "p-value — вероятность данных при H₀, а не вероятность H₀ при данных. Частая ошибка на собеседованиях."},
            {"type": "choice", "q": "Уровень значимости α = 0,05. Что такое ошибка I рода?",
             "options": ["Не заметить реальный эффект", "Найти эффект, которого нет (отвергнуть верную H₀)", "Ошибка в коде", "Слишком маленькая выборка"],
             "answer": 1, "explain": "α — допустимая частота ошибок I рода. Ошибка II рода (β) — пропустить реальный эффект; мощность = 1 − β."},
            {"type": "number", "q": "Монету бросили 10 раз, выпало 9 орлов или больше. Вероятность этого у честной монеты (одностороннее p-value)?", "answer": 11 / 1024, "tol": 1e-3,
             "explain": "P(X ≥ 9) = (C(10,9) + C(10,10))/2¹⁰ = 11/1024 ≈ 0,0107."},
            {"type": "choice", "q": "Проверили 20 гипотез с α = 0,05, все H₀ верны. Сколько «значимых» результатов ожидаем?",
             "options": ["0", "1", "5", "20"], "answer": 1, "explain": "20 · 0,05 = 1. Проблема множественных сравнений; поправка Бонферрони — α/k."},
        ],
    },
    "q-w3-numpy": {
        "title": "NumPy: векторизация и broadcasting",
        "questions": [
            {"type": "output", "code": "import numpy as np\na = np.arange(6).reshape(2, 3)\nprint(a.shape, a.sum(axis=0), a.sum(axis=1))",
             "explain": "`axis=0` — схлопнуть строки (сумма по столбцам), `axis=1` — схлопнуть столбцы."},
            {"type": "output", "code": "import numpy as np\na = np.array([[1], [2], [3]])\nb = np.array([10, 20])\nprint((a + b).shape)\nprint(a + b)",
             "explain": "Broadcasting: (3, 1) и (2,) → (3, 1) и (1, 2) → (3, 2). Измерения сравниваются справа; размер 1 растягивается."},
            {"type": "output", "code": "import numpy as np\ntry:\n    np.ones((3, 2)) + np.ones(3)\nexcept ValueError:\n    print(\"не совместимы\")",
             "explain": "Справа: 2 против 3 — ни одно не равно 1. Нужно `np.ones(3)[:, None]` → (3, 1)."},
            {"type": "output", "code": "import numpy as np\na = np.arange(5)\nb = a[1:4]\nb[0] = 100\nprint(a)",
             "explain": "Срез NumPy — **view**, а не копия (в отличие от списков Python!). Изменение видно в исходном массиве. Нужна копия — `.copy()`."},
            {"type": "output", "code": "import numpy as np\na = np.array([3, -1, 4, -1, 5])\nprint(a[a > 0], (a > 0).mean())",
             "explain": "Булева маска выбирает элементы; среднее булевого массива — доля True."},
            {"type": "output", "code": "import numpy as np\nx = np.array([1.0, 2.0, 3.0])\nprint(x @ x, np.outer(x, x).shape)",
             "explain": "`@` для двух векторов — скалярное произведение; `outer` даёт матрицу n×n."},
            {"type": "output", "code": "import numpy as np\nprint(np.array([1, 2, 3]).dtype, (np.array([1, 2, 3]) / 2).dtype, np.array([1, 2.5]).dtype)",
             "explain": "Деление `/` всегда даёт float; массив с одним float целиком становится float64."},
            {"type": "choice", "q": "Почему `np.sum(a)` в сотни раз быстрее `sum(a)` в цикле Python на массиве из 10⁶ чисел?",
             "options": ["NumPy использует GPU", "Цикл идёт в C над непрерывным буфером одного типа, без Python-объекта на каждый элемент", "NumPy кэширует ответ", "Python sum многопоточный"],
             "answer": 1, "explain": "Это и есть векторизация: вынести цикл из Python в скомпилированный код."},
        ],
    },
    "q-w3-pandas": {
        "title": "pandas: groupby, merge, pivot",
        "questions": [
            {"type": "output", "code": "import pandas as pd\ndf = pd.DataFrame({\"city\": [\"A\", \"B\", \"A\", \"B\", \"A\"], \"sales\": [1, 2, 3, 4, 5]})\nprint(df.groupby(\"city\")[\"sales\"].sum().to_dict())",
             "explain": "`groupby` + агрегация: split → apply → combine."},
            {"type": "output", "code": "import pandas as pd\ndf = pd.DataFrame({\"g\": [\"x\", \"x\", \"y\"], \"v\": [1, 3, 10]})\nprint(df.groupby(\"g\")[\"v\"].agg([\"mean\", \"count\"]).loc[\"x\"].tolist())",
             "explain": "`agg` со списком функций даёт по столбцу на каждую."},
            {"type": "output", "code": "import pandas as pd\nusers = pd.DataFrame({\"id\": [1, 2, 3], \"name\": [\"ann\", \"bob\", \"cid\"]})\norders = pd.DataFrame({\"user_id\": [1, 1, 3], \"total\": [10, 20, 5]})\nm = users.merge(orders, left_on=\"id\", right_on=\"user_id\", how=\"left\")\nprint(len(m), m[\"total\"].isna().sum())",
             "explain": "LEFT join сохраняет всех пользователей: у ann 2 заказа (2 строки), у bob нет заказов (NaN), у cid 1. Итого 4 строки, один NaN."},
            {"type": "output", "code": "import pandas as pd\ndf = pd.DataFrame({\"d\": [\"пн\", \"пн\", \"вт\"], \"p\": [\"a\", \"b\", \"a\"], \"n\": [1, 2, 3]})\nt = df.pivot_table(index=\"d\", columns=\"p\", values=\"n\", aggfunc=\"sum\", fill_value=0)\nprint(t.loc[\"вт\", \"b\"], t.loc[\"пн\", \"b\"])",
             "explain": "pivot_table разворачивает значения столбца `p` в колонки; пустые ячейки — `fill_value`."},
            {"type": "output", "code": "import pandas as pd\ndf = pd.DataFrame({\"a\": [1, 2, 3]})\nsub = df[df[\"a\"] > 1]\nsub = sub.assign(b=sub[\"a\"] * 10)\nprint(df.columns.tolist(), sub[\"b\"].tolist())",
             "explain": "Фильтр создаёт новый объект; `assign` возвращает копию с новым столбцом. Исходный df не меняется."},
            {"type": "choice", "q": "Чем `df.loc[...]` отличается от `df.iloc[...]`?",
             "options": ["Ничем", "loc — по меткам индекса и названиям столбцов, iloc — по целочисленным позициям", "loc быстрее", "iloc только для строк"],
             "answer": 1, "explain": "После фильтрации индекс не 0..n−1, поэтому `df.loc[0]` и `df.iloc[0]` могут вернуть разные строки."},
        ],
    },
    "q-w3-bash": {
        "title": "Bash: grep, find, пайпы (G4)",
        "questions": [
            {"type": "choice", "q": "Как найти все `.py` файлы в текущей папке и подпапках?",
             "options": ["`ls *.py`", "`find . -name \"*.py\"`", "`grep .py`", "`cat *.py`"], "answer": 1, "explain": "`ls *.py` смотрит только текущую папку."},
            {"type": "choice", "q": "Что делает `grep -rn \"TODO\" src/`?",
             "options": ["Удаляет строки TODO", "Рекурсивно ищет «TODO» в src/ и печатает имя файла и номер строки", "Считает файлы", "Ищет только в именах файлов"],
             "answer": 1, "explain": "`-r` — рекурсивно, `-n` — номера строк, `-i` — без учёта регистра, `-l` — только имена файлов."},
            {"type": "choice", "q": "Команда `cat log.txt | grep ERROR | wc -l` выводит:",
             "options": ["Все ошибки", "Число строк с ERROR", "Число слов в файле", "Первую ошибку"], "answer": 1,
             "explain": "Пайп `|` передаёт stdout одной команды на stdin следующей."},
            {"type": "choice", "q": "Как получить 5 самых частых значений в первом столбце CSV без заголовка?",
             "options": ["`cut -d, -f1 data.csv | sort | uniq -c | sort -rn | head -5`", "`head -5 data.csv`", "`sort data.csv | head -5`", "`uniq data.csv | head -5`"],
             "answer": 0, "explain": "`uniq -c` считает только **соседние** повторы — поэтому сначала `sort`."},
            {"type": "choice", "q": "Чем `>` отличается от `>>`?", "options": ["Ничем", "`>` перезаписывает файл, `>>` дописывает в конец", "`>>` — ошибка", "`>` — для ошибок"],
             "answer": 1, "explain": "`2>` перенаправляет stderr; `2>&1` — stderr туда же, куда stdout."},
        ],
    },
    "q-w3-oral": {
        "title": "Вопросы вслух: неделя 3",
        "oral": True,
        "questions": [
            {"type": "text", "q": "Объясните формулу Байеса на примере теста на болезнь. Почему при точном тесте положительный результат может значить «скорее здоров»?",
             "model": "P(болен | +) = P(+ | болен)·P(болен) / P(+). Если болезнь редкая, ложных тревог среди огромного числа здоровых больше, чем истинных срабатываний среди немногих больных."},
            {"type": "text", "q": "Что такое p-value и чем оно НЕ является?",
             "model": "Вероятность получить такой же или более экстремальный результат, если H₀ верна. Это не вероятность того, что H₀ верна, и не размер эффекта."},
            {"type": "text", "q": "Что такое broadcasting в NumPy? Приведите пример с формами.",
             "model": "Правило совмещения массивов разной формы: измерения сравниваются справа, размер 1 растягивается. (3, 1) + (1, 4) → (3, 4); (n, d) − (d,) вычитает среднее из каждой строки."},
            {"type": "text", "q": "Расскажите о вашем хакатоне за 3 минуты: задача, данные, метрика, что сделала команда, что сделали вы.",
             "model": "Структура: задача и бизнес-смысл → данные (размер, признаки) → метрика и почему она → подход команды → ваш личный вклад конкретно → результат в цифрах (место, скор) → что сделали бы иначе."},
        ],
    },
}

EXERCISES = {
    "ex-w3-softmax": {
        "title": "Устойчивый softmax на NumPy",
        "statement_ru": d("""\
            Напишите `softmax(x, axis=-1)` для массива любой формы: `exp(x) / sum(exp(x))` вдоль оси `axis`.
            Требования:
            - без циклов Python (векторизация);
            - численно устойчиво: `softmax([1000, 1001])` не должен дать `nan` (вычтите максимум вдоль оси);
            - сумма вдоль `axis` равна 1."""),
        "starter_code": "import numpy as np\n\n\ndef softmax(x, axis=-1):\n    x = np.asarray(x, dtype=float)\n    return np.exp(x) / np.exp(x).sum()\n",
        "tests": d('''\
            import numpy as np

            def test_simple():
                """Известный ответ для [1, 2, 3]"""
                assert np.allclose(softmax([1.0, 2.0, 3.0]), [0.09003057, 0.24472847, 0.66524096])

            def test_stable():
                """Большие числа не дают nan"""
                out = softmax([1000.0, 1001.0])
                assert np.all(np.isfinite(out)), f"получилось {out}"
                assert np.allclose(out, [0.26894142, 0.73105858])

            def test_axis():
                """Работает по оси для матрицы"""
                x = np.array([[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]])
                out = softmax(x, axis=1)
                assert out.shape == (2, 3)
                assert np.allclose(out.sum(axis=1), 1)
                assert np.allclose(out[1], 1 / 3)
                assert np.allclose(softmax(x, axis=0).sum(axis=0), 1)

            def test_shift_invariant():
                """softmax(x + c) = softmax(x)"""
                x = np.random.default_rng(0).normal(size=(4, 5))
                assert np.allclose(softmax(x), softmax(x + 123.0))
            '''),
        "ref": d("""\
            import numpy as np


            def softmax(x, axis=-1):
                x = np.asarray(x, dtype=float)
                z = x - x.max(axis=axis, keepdims=True)
                e = np.exp(z)
                return e / e.sum(axis=axis, keepdims=True)
            """),
        "hints_ru": [
            "Посчитайте `np.exp(1000)`. Что получилось? Что будет с `softmax(x)`, если вычесть из всех элементов `x` одно и то же число?",
            "softmax не меняется при сдвиге всех элементов на константу. Вычтите максимум вдоль оси: самый большой показатель станет 0, переполнения нет. `keepdims=True` сохраняет ось размера 1, и broadcasting вычитает правильно для массива любой формы.",
            "1) `x = np.asarray(x, dtype=float)`. 2) `z = x - x.max(axis=axis, keepdims=True)`. 3) `e = np.exp(z)`. 4) Верните `e / e.sum(axis=axis, keepdims=True)`. Проверьте 2D-массив с `axis=0` и `axis=-1`.",
        ],
    },
    "ex-w3-pairwise": {
        "title": "Попарные расстояния через broadcasting",
        "statement_ru": d("""\
            Даны точки `X` формы `(n, d)` и `Y` формы `(m, d)`. Верните матрицу `D` формы `(n, m)`:
            `D[i, j]` — евклидово расстояние между `X[i]` и `Y[j]`. Без циклов Python.
            Это ядро kNN (неделя 4) и поиска ближайших эмбеддингов (неделя 9)."""),
        "starter_code": "import numpy as np\n\n\ndef pairwise_dist(X, Y):\n    pass\n",
        "tests": d('''\
            import numpy as np

            def brute(X, Y):
                return np.array([[np.sqrt(((x - y) ** 2).sum()) for y in Y] for x in X])

            def test_small():
                """Маленький пример"""
                X = np.array([[0.0, 0.0], [3.0, 4.0]])
                Y = np.array([[0.0, 0.0], [6.0, 8.0], [3.0, 0.0]])
                assert np.allclose(pairwise_dist(X, Y), [[0, 10, 3], [5, 5, 4]])

            def test_random_shape():
                """Случайные данные, разные n и m"""
                rng = np.random.default_rng(1)
                X, Y = rng.normal(size=(7, 3)), rng.normal(size=(5, 3))
                D = pairwise_dist(X, Y)
                assert D.shape == (7, 5)
                assert np.allclose(D, brute(X, Y))

            def test_no_python_loops_speed():
                """Векторизовано: 1000×1000 быстро"""
                import time
                rng = np.random.default_rng(2)
                X, Y = rng.normal(size=(1000, 16)), rng.normal(size=(1000, 16))
                t = time.perf_counter()
                pairwise_dist(X, Y)
                assert time.perf_counter() - t < 2.0, "слишком медленно — есть цикл Python?"
            '''),
        "ref": d("""\
            import numpy as np


            def pairwise_dist(X, Y):
                X = np.asarray(X, dtype=float)
                Y = np.asarray(Y, dtype=float)
                diff = X[:, None, :] - Y[None, :, :]
                return np.sqrt((diff ** 2).sum(axis=-1))
            """),
        "hints_ru": [
            "Для `D[i, j]` нужна разность `X[i] − Y[j]` для каждой пары. Какой формы массив хранит все эти разности сразу?",
            "Broadcasting: `X[:, None, :]` имеет форму (n, 1, d), `Y[None, :, :]` — (1, m, d). NumPy растягивает оси размера 1, и разность получает форму (n, m, d) без циклов.",
            "1) Приведите `X`, `Y` к `float`. 2) `diff = X[:, None, :] - Y[None, :, :]`. 3) Возведите в квадрат, сложите по последней оси, возьмите корень. Бонус для экономии памяти: ‖x−y‖² = ‖x‖² + ‖y‖² − 2x·y.",
        ],
    },
    "ex-w3-zscore": {
        "title": "Стандартизация признаков (как StandardScaler)",
        "statement_ru": d("""\
            Напишите класс `Standardizer`:
            - `fit(X)` — запомнить среднее и стандартное отклонение **каждого столбца** (`ddof=0`), вернуть `self`;
            - `transform(X)` — `(X − mean) / std`; если std столбца равен 0, вместо деления на 0 оставить столбец нулевым;
            - `fit_transform(X)`.

            Важно для недели 4 (утечки E7): статистики считаются только на том, что передали в `fit`."""),
        "starter_code": "import numpy as np\n\n\nclass Standardizer:\n    def fit(self, X):\n        pass\n\n    def transform(self, X):\n        pass\n\n    def fit_transform(self, X):\n        pass\n",
        "tests": d('''\
            import numpy as np

            def test_matches_sklearn():
                """Совпадает с sklearn StandardScaler"""
                from sklearn.preprocessing import StandardScaler
                X = np.random.default_rng(3).normal(5, 3, size=(50, 4))
                assert np.allclose(Standardizer().fit_transform(X), StandardScaler().fit_transform(X))

            def test_constant_column():
                """Константный столбец не даёт nan"""
                X = np.array([[1.0, 7.0], [3.0, 7.0]])
                out = Standardizer().fit_transform(X)
                assert np.all(np.isfinite(out)) and np.allclose(out[:, 1], 0)

            def test_train_stats_only():
                """transform использует статистики из fit"""
                train = np.array([[0.0], [2.0]])
                test = np.array([[4.0]])
                s = Standardizer().fit(train)
                assert np.allclose(s.transform(test), [[3.0]]), "среднее 1, std 1 — из train"
            '''),
        "ref": d("""\
            import numpy as np


            class Standardizer:
                def fit(self, X):
                    X = np.asarray(X, dtype=float)
                    self.mean_ = X.mean(axis=0)
                    std = X.std(axis=0)
                    self.scale_ = np.where(std == 0, 1.0, std)
                    return self

                def transform(self, X):
                    return (np.asarray(X, dtype=float) - self.mean_) / self.scale_

                def fit_transform(self, X):
                    return self.fit(X).transform(X)
            """),
        "hints_ru": [
            "Объект вызывает `fit` один раз, а `transform` — много раз и на других данных. Что тогда нужно запомнить в `fit`? Что делать со столбцом, где все значения одинаковые?",
            "Статистики по столбцам — `axis=0`; сохраните их в атрибутах (`mean_`, `scale_`). Для std = 0 подставьте 1 через `np.where`: константный столбец после вычитания среднего и так нулевой, деление на 1 его не меняет.",
            "1) `fit`: `mean_ = X.mean(axis=0)`; `std = X.std(axis=0)`; `scale_ = np.where(std == 0, 1.0, std)`; верните `self`. 2) `transform`: `(X - mean_) / scale_`. 3) `fit_transform`: `self.fit(X).transform(X)`.",
        ],
    },
    "ex-w3-bayes": {
        "title": "D3 в коде: апостериорная вероятность",
        "statement_ru": d("""\
            Напишите `posterior(prior, sensitivity, specificity, positive=True)` — вероятность болезни
            после результата теста.
            - `prior` — доля больных;
            - `sensitivity` — P(тест + | болен);
            - `specificity` — P(тест − | здоров).

            Для `positive=False` верните P(болен | тест −). Затем напишите `tests_needed(prior, sensitivity, specificity, target)` —
            сколько **независимых положительных** тестов подряд нужно, чтобы вероятность болезни стала ≥ `target`
            (апостериорная после одного теста — априорная для следующего)."""),
        "starter_code": "def posterior(prior, sensitivity, specificity, positive=True):\n    pass\n\n\ndef tests_needed(prior, sensitivity, specificity, target):\n    pass\n",
        "tests": d('''\
            def test_d3():
                """Пример D3: ≈ 0,1667"""
                assert abs(posterior(0.01, 0.99, 0.95) - 0.16666) < 1e-3

            def test_negative():
                """Отрицательный тест"""
                p = posterior(0.01, 0.99, 0.95, positive=False)
                assert abs(p - 0.0001063) < 1e-6, f"получилось {p}"

            def test_edge():
                """Идеальный тест"""
                assert posterior(0.3, 1.0, 1.0) == 1.0
                assert posterior(0.3, 1.0, 1.0, positive=False) == 0.0

            def test_repeat():
                """Повторные тесты"""
                assert tests_needed(0.01, 0.99, 0.95, 0.9) == 3
                assert tests_needed(0.5, 0.9, 0.9, 0.5) == 0
            '''),
        "ref": d("""\
            def posterior(prior, sensitivity, specificity, positive=True):
                if positive:
                    num = sensitivity * prior
                    den = num + (1 - specificity) * (1 - prior)
                else:
                    num = (1 - sensitivity) * prior
                    den = num + specificity * (1 - prior)
                return num / den


            def tests_needed(prior, sensitivity, specificity, target):
                n, p = 0, prior
                while p < target:
                    p = posterior(p, sensitivity, specificity)
                    n += 1
                return n
            """),
        "hints_ru": [
            "Тест положительный. Из каких двух групп людей может прийти положительный результат? Какая доля всех положительных тестов приходится на больных?",
            "Формула Байеса: P(болен | +) = P(+ | болен)·P(болен) / P(+). Знаменатель P(+) — сумма по двум группам: больные с верным тестом и здоровые с ложным, где P(+ | здоров) = 1 − specificity.",
            "1) `positive=True`: числитель `sensitivity * prior`, знаменатель — числитель плюс `(1 - specificity) * (1 - prior)`. 2) `positive=False`: числитель `(1 - sensitivity) * prior`, плюс `specificity * (1 - prior)`. 3) `tests_needed`: `n, p = 0, prior`; пока `p < target`: `p = posterior(p, ...)`, `n += 1`. Если `prior >= target` — ответ 0.",
        ],
    },
    "ex-w3-pandas": {
        "title": "pandas: отчёт по продажам",
        "statement_ru": d("""\
            Напишите `report(sales, products)`. `sales` — DataFrame со столбцами `product_id, qty, day`;
            `products` — `product_id, category, price`. Верните DataFrame:
            - одна строка на категорию, индекс — `category`, отсортирован по алфавиту;
            - столбцы `revenue` (сумма qty·price), `orders` (число строк продаж), `top_product` (product_id с наибольшей выручкой в категории;
              при равенстве — меньший id).

            Категории без продаж в отчёт не попадают."""),
        "starter_code": "import pandas as pd\n\n\ndef report(sales, products):\n    pass\n",
        "tests": d('''\
            import pandas as pd

            def data():
                products = pd.DataFrame({"product_id": [1, 2, 3, 4], "category": ["food", "food", "toys", "books"], "price": [10.0, 5.0, 7.0, 3.0]})
                sales = pd.DataFrame({"product_id": [1, 2, 2, 3, 2], "qty": [1, 2, 1, 4, 1], "day": [1, 1, 2, 2, 3]})
                return sales, products

            def test_shape_and_index():
                """Индекс и столбцы"""
                r = report(*data())
                assert list(r.index) == ["food", "toys"], f"индекс: {list(r.index)}"
                assert set(["revenue", "orders", "top_product"]) <= set(r.columns)

            def test_values():
                """Выручка, заказы, лучший товар"""
                r = report(*data())
                assert r.loc["food", "revenue"] == 30.0 and r.loc["toys", "revenue"] == 28.0
                assert r.loc["food", "orders"] == 4 and r.loc["toys", "orders"] == 1

            def test_top_product_tie():
                """При равной выручке — меньший id"""
                r = report(*data())
                assert r.loc["food", "top_product"] == 2, "у товаров 1 и 2 выручка 10 и 20 — лучший 2"
                products = pd.DataFrame({"product_id": [5, 6], "category": ["x", "x"], "price": [1.0, 1.0]})
                sales = pd.DataFrame({"product_id": [6, 5], "qty": [2, 2], "day": [1, 1]})
                assert report(sales, products).loc["x", "top_product"] == 5
            '''),
        "ref": d("""\
            import pandas as pd


            def report(sales, products):
                df = sales.merge(products, on="product_id")
                df["revenue"] = df["qty"] * df["price"]
                by_cat = df.groupby("category").agg(revenue=("revenue", "sum"), orders=("revenue", "size"))
                per_product = df.groupby(["category", "product_id"], as_index=False)["revenue"].sum()
                per_product = per_product.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
                top = per_product.drop_duplicates("category").set_index("category")["product_id"]
                by_cat["top_product"] = top
                return by_cat.sort_index()
            """),
        "hints_ru": [
            "Категория и цена лежат в `products`, а количество — в `sales`. Что нужно сделать с таблицами до того, как считать выручку по категориям?",
            "`merge` по `product_id` соединяет таблицы. Потом `groupby('category').agg(...)` с именованной агрегацией даёт `revenue` и `orders` за один вызов. Для `top_product` нужна выручка на уровне пары (категория, товар).",
            "1) `df = sales.merge(products, on=\"product_id\")`; `df[\"revenue\"] = qty * price`. 2) `agg(revenue=(\"revenue\", \"sum\"), orders=(\"revenue\", \"size\"))`. 3) Выручка по `[\"category\", \"product_id\"]`, сортировка: категория ↑, выручка ↓, id ↑; `drop_duplicates(\"category\")`. 4) Присоедините `top_product` и `sort_index()`.",
        ],
    },
}
