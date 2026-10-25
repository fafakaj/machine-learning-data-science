"""Week 9 content: CNN, ResNet, transfer learning, embeddings, CLIP, BPE."""

from textwrap import dedent as d

QUIZZES = {
    "q-w9-cv": {
        "title": "Свёртки, ResNet, transfer learning",
        "questions": [
            {"type": "number", "q": "Вход 32×32, ядро 5×5, stride 1, padding 0. Размер выхода по одной стороне?", "answer": 28, "tol": 0,
             "explain": "(W − K + 2P)/S + 1 = (32 − 5)/1 + 1 = 28."},
            {"type": "number", "q": "Вход 224×224, ядро 7×7, stride 2, padding 3. Размер выхода по стороне?", "answer": 112, "tol": 0,
             "explain": "⌊(224 − 7 + 6)/2⌋ + 1 = 112 — первый слой ResNet."},
            {"type": "number", "q": "Conv2d(in=3, out=64, kernel=3) со смещением. Сколько параметров?", "answer": 3 * 64 * 9 + 64, "tol": 0,
             "explain": "C_in·C_out·K·K + C_out = 1728 + 64 = 1792. Не зависит от размера картинки."},
            {"type": "choice", "q": "Зачем skip-соединения (x + F(x)) в ResNet?",
             "options": ["Уменьшают число параметров", "Градиент проходит напрямую через сложение — можно обучать очень глубокие сети; слою легко выучить «почти тождество»",
                         "Заменяют свёртки", "Нужны для цвета"], "answer": 1},
            {"type": "choice", "q": "Мало данных (500 картинок), предобученная ResNet. Лучшая стратегия:",
             "options": ["Обучать с нуля", "Заморозить основу, обучить новую голову; потом разморозить верхние слои с маленьким learning rate",
                         "Обучать все слои с большим lr", "Удалить свёртки"], "answer": 1},
            {"type": "choice", "q": "Почему свёртка лучше полносвязного слоя для картинок?",
             "options": ["Она медленнее", "Общие веса по всей картинке (мало параметров) и локальность: один детектор узора работает в любом месте", "Работает без GPU", "Не нужна нелинейность"],
             "answer": 1},
        ],
    },
    "q-w9-emb": {
        "title": "Эмбеддинги, косинусное сходство, CLIP, BPE (F4)",
        "questions": [
            {"type": "number", "q": "Косинусное сходство векторов a = (1, 0, 1) и b = (1, 1, 0)?", "answer": 0.5, "tol": 1e-9,
             "explain": "a·b = 1; |a| = |b| = √2; 1/2."},
            {"type": "choice", "q": "Векторы нормированы (|v| = 1). Тогда косинусное сходство равно…",
             "options": ["евклидову расстоянию", "скалярному произведению", "нулю", "сумме координат"], "answer": 1,
             "explain": "Поэтому в векторных БД часто нормируют эмбеддинги и ищут по dot product."},
            {"type": "choice", "q": "Как обучают CLIP?",
             "options": ["Классификация 1000 классов", "Контрастивно: эмбеддинги картинки и её подписи сближают, чужих пар — отдаляют", "Генерация картинок", "Обучение без текста"],
             "answer": 1, "explain": "Отсюда zero-shot: сравнить картинку с текстами «фото кошки», «фото собаки»."},
            {"type": "choice", "q": "F4. Один шаг обучения BPE:",
             "options": ["Удалить редкие слова", "Найти самую частую пару соседних токенов и заменить её новым токеном", "Разбить текст по пробелам", "Отсортировать словарь"],
             "answer": 1},
            {"type": "choice", "q": "Почему токенизация по байтам (byte-level BPE) не знает «неизвестных слов» (UNK)?",
             "options": ["Словарь бесконечный", "Любой текст раскладывается на 256 базовых байтов, а слияния только укрупняют токены", "Удаляет неизвестное", "Использует словарь Википедии"],
             "answer": 1},
            {"type": "choice", "q": "Почему LLM плохо считают буквы в слове «strawberry»?",
             "options": ["Мало параметров", "Модель видит токены (куски слова), а не отдельные буквы", "Нет английского", "Из-за temperature"], "answer": 1},
        ],
    },
}

EXERCISES = {
    "ex-w9-conv2d": {
        "title": "Свёртка conv2d на NumPy ≈ scipy",
        "statement_ru": d("""\
            Напишите `conv2d(x, w, stride=1, padding=0)` для одного канала: `x` — `(H, W)`, `w` — `(K, K)`.
            Как в нейросетях, это **кросс-корреляция** (ядро не переворачивается). Padding — нулями.
            Размер выхода: `(H − K + 2P)//S + 1`.

            Тест сравнивает с `scipy.signal.correlate2d(..., mode="valid")`."""),
        "starter_code": "import numpy as np\n\n\ndef conv2d(x, w, stride=1, padding=0):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from scipy.signal import correlate2d

            rng = np.random.default_rng(9)
            x = rng.normal(size=(9, 11))
            w = rng.normal(size=(3, 3))

            def test_valid():
                """stride 1, без padding ≈ scipy"""
                assert np.allclose(conv2d(x, w), correlate2d(x, w, mode="valid"))

            def test_padding():
                """padding 1 сохраняет размер"""
                y = conv2d(x, w, padding=1)
                assert y.shape == x.shape
                assert np.allclose(y, correlate2d(np.pad(x, 1), w, mode="valid"))

            def test_stride():
                """stride 2"""
                y = conv2d(x, w, stride=2, padding=1)
                assert y.shape == ((9 - 3 + 2) // 2 + 1, (11 - 3 + 2) // 2 + 1)
                assert np.allclose(y, correlate2d(np.pad(x, 1), w, mode="valid")[::2, ::2])
            '''),
        "ref": d("""\
            import numpy as np


            def conv2d(x, w, stride=1, padding=0):
                x = np.pad(np.asarray(x, dtype=float), padding)
                k = w.shape[0]
                oh = (x.shape[0] - k) // stride + 1
                ow = (x.shape[1] - k) // stride + 1
                out = np.empty((oh, ow))
                for i in range(oh):
                    for j in range(ow):
                        out[i, j] = (x[i * stride:i * stride + k, j * stride:j * stride + k] * w).sum()
                return out
        """),
        "hints_ru": [
            "Ядро `K × K` скользит по картинке с шагом `stride`. Сколько позиций у ядра по одной стороне? Как padding меняет это число?",
            "Сначала добавьте нули по краям `np.pad(x, padding)`. Тогда размер выхода по стороне — `(H_pad − K) // stride + 1`. Каждый выходной элемент — поэлементное произведение окна и ядра, просуммированное. Ядро не переворачивайте: это кросс-корреляция.",
            "1) `x = np.pad(x, padding)`. 2) `oh`, `ow` по формуле. 3) Для каждого `(i, j)`: окно `x[i*s : i*s+K, j*s : j*s+K]`; `out[i, j] = (окно * w).sum()`. 4) Верните `out`. Проверьте `stride = 2` и `padding = 1`.",
        ],
    },
    "ex-w9-cosine": {
        "title": "Поиск по эмбеддингам: косинусное сходство и top-k",
        "statement_ru": d("""\
            1. `cosine_matrix(A, B)` — матрица косинусных сходств строк `A` `(n, d)` и строк `B` `(m, d)` → `(n, m)`. Без циклов.
            2. `top_k(query, docs, k)` — индексы `k` документов с наибольшим сходством с вектором `query`,
               по убыванию сходства."""),
        "starter_code": "import numpy as np\n\n\ndef cosine_matrix(A, B):\n    pass\n\n\ndef top_k(query, docs, k):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

            rng = np.random.default_rng(2)
            A = rng.normal(size=(5, 8)); B = rng.normal(size=(7, 8))

            def test_matrix():
                """Матрица ≈ sklearn cosine_similarity"""
                assert np.allclose(cosine_matrix(A, B), cosine_similarity(A, B))

            def test_scale_invariant():
                """Сходство не зависит от длины векторов"""
                assert np.allclose(cosine_matrix(3 * A, B), cosine_matrix(A, B))

            def test_top_k():
                """top-k по убыванию сходства"""
                docs = np.array([[1, 0], [0, 1], [1, 1], [-1, 0]], dtype=float)
                assert list(top_k(np.array([1.0, 0.2]), docs, 3)) == [0, 2, 1]
            '''),
        "ref": d("""\
            import numpy as np


            def cosine_matrix(A, B):
                A = np.asarray(A, dtype=float)
                B = np.asarray(B, dtype=float)
                An = A / np.linalg.norm(A, axis=1, keepdims=True)
                Bn = B / np.linalg.norm(B, axis=1, keepdims=True)
                return An @ Bn.T


            def top_k(query, docs, k):
                sims = cosine_matrix(np.asarray(query)[None, :], docs)[0]
                return np.argsort(-sims)[:k]
        """),
        "hints_ru": [
            "Косинус угла — скалярное произведение, делённое на длины векторов. Что станет с формулой, если заранее сделать длину каждого вектора равной 1?",
            "Нормируйте строки: `A / np.linalg.norm(A, axis=1, keepdims=True)`. После нормировки косинусное сходство — просто скалярное произведение, и вся матрица — одно умножение `An @ Bn.T` без циклов.",
            "1) `cosine_matrix`: нормируйте `A` и `B`, верните `An @ Bn.T`. 2) `top_k`: сделайте из `query` матрицу `(1, d)` через `[None, :]`, возьмите строку 0 результата. 3) `np.argsort(-sims)[:k]` — индексы по убыванию сходства.",
        ],
    },
    "ex-w9-bpe": {
        "title": "BPE-токенизатор с нуля (как у Karpathy)",
        "statement_ru": d("""\
            Байтовый BPE. Текст → байты UTF-8 (числа 0–255).
            - `get_stats(ids)` → `dict` пара → сколько раз встречается подряд (пересечения считаются: в `aaa` пара `(a, a)` — 2 раза);
            - `merge(ids, pair, idx)` — заменить вхождения `pair` слева направо (без пересечений) на `idx`;
            - `train(text, n_merges)` → список слияний `[(pair, idx), ...]`, `idx` = 256, 257, …;
              на каждом шаге берётся самая частая пара (при равенстве — та, что встретилась раньше);
            - `encode(text, merges)` и `decode(ids, merges)`."""),
        "starter_code": "def get_stats(ids):\n    pass\n\n\ndef merge(ids, pair, idx):\n    pass\n\n\ndef train(text, n_merges):\n    pass\n\n\ndef encode(text, merges):\n    pass\n\n\ndef decode(ids, merges):\n    pass\n",
        "tests": d('''\
            TEXT = "aaabdaaabac aaabdaaabac — привет, привет!"

            def test_stats_and_merge():
                """get_stats и merge"""
                assert get_stats([1, 1, 1, 2]) == {(1, 1): 2, (1, 2): 1}
                assert merge([1, 1, 1, 2], (1, 1), 9) == [9, 1, 2]

            def test_first_merge():
                """Первое слияние — пара «aa»"""
                merges = train("aaabdaaabac", 3)
                assert merges[0] == ((97, 97), 256)
                assert [m[1] for m in merges] == [256, 257, 258]

            def test_roundtrip():
                """decode(encode(t)) == t, токенов меньше, чем байтов"""
                merges = train(TEXT, 10)
                ids = encode(TEXT, merges)
                assert decode(ids, merges) == TEXT
                assert len(ids) < len(TEXT.encode())

            def test_new_text():
                """Новый текст с теми же слияниями"""
                merges = train(TEXT, 10)
                for t in ["привет aaab", "", "zzz"]:
                    assert decode(encode(t, merges), merges) == t
            '''),
        "ref": d("""\
            def get_stats(ids):
                counts = {}
                for pair in zip(ids, ids[1:]):
                    counts[pair] = counts.get(pair, 0) + 1
                return counts


            def merge(ids, pair, idx):
                out, i = [], 0
                while i < len(ids):
                    if i + 1 < len(ids) and (ids[i], ids[i + 1]) == pair:
                        out.append(idx)
                        i += 2
                    else:
                        out.append(ids[i])
                        i += 1
                return out


            def train(text, n_merges):
                ids = list(text.encode("utf-8"))
                merges = []
                for k in range(n_merges):
                    stats = get_stats(ids)
                    if not stats:
                        break
                    pair = max(stats, key=stats.get)
                    idx = 256 + k
                    ids = merge(ids, pair, idx)
                    merges.append((pair, idx))
                return merges


            def encode(text, merges):
                ids = list(text.encode("utf-8"))
                for pair, idx in merges:
                    ids = merge(ids, pair, idx)
                return ids


            def decode(ids, merges):
                vocab = {i: bytes([i]) for i in range(256)}
                for (a, b), idx in merges:
                    vocab[idx] = vocab[a] + vocab[b]
                return b"".join(vocab[i] for i in ids).decode("utf-8")
        """),
        "hints_ru": [
            "BPE раз за разом склеивает самую частую соседнюю пару в новый токен. Какие три действия тогда нужны: что посчитать, что выбрать, что заменить?",
            "Пары — `zip(ids, ids[1:])`, частоты — словарь. `max(stats, key=stats.get)` при равенстве даёт первую пару: словарь хранит порядок вставки. `merge` идёт слева направо без пересечений: совпала пара — пишем `idx` и прыгаем на 2, иначе на 1.",
            "1) `train`: `ids = list(text.encode(\"utf-8\"))`; `n_merges` раз — статистика, самая частая пара, `idx = 256 + k`, `merge`, запишите `(pair, idx)`; пустая статистика — стоп. 2) `encode`: применяйте слияния в порядке обучения. 3) `decode`: словарь `idx → bytes` (от 0 до 255 — один байт, новые — склейка двух), `b\"\".join(...).decode(\"utf-8\")`.",
        ],
    },
}
