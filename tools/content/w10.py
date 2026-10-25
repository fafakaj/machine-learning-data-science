"""Week 10 content: attention, Transformer, KV cache, sampling."""

from textwrap import dedent as d

QUIZZES = {
    "q-w10-attn": {
        "title": "Attention (F3), маска, multi-head, позиции, BERT и GPT",
        "questions": [
            {"type": "choice", "q": "Q имеет форму (T, d), K — (T, d). Какой формы матрица QKᵀ?",
             "options": ["(d, d)", "(T, T): сходство каждой позиции с каждой", "(T, d)", "(1, T)"], "answer": 1},
            {"type": "choice", "q": "Зачем делить QKᵀ на √d?",
             "options": ["Для красоты", "При большом d скалярные произведения растут (дисперсия ~ d), softmax насыщается и градиенты почти нулевые",
                         "Чтобы сэкономить память", "Чтобы получить вероятности"], "answer": 1},
            {"type": "choice", "q": "Причинная (causal) маска в декодере:",
             "options": ["Обнуляет V", "Ставит −∞ в QKᵀ выше диагонали: позиция i не видит будущие j > i", "Удаляет паддинг", "Нужна только в BERT"],
             "answer": 1},
            {"type": "number", "q": "Multi-head attention, d_model = 512, без смещений. Сколько параметров в проекциях Q, K, V и выходной?",
             "answer": 4 * 512 * 512, "tol": 0, "explain": "4·d² — не зависит от числа голов: головы делят d на части."},
            {"type": "choice", "q": "Зачем позиционное кодирование?",
             "options": ["Ускоряет обучение", "Attention не знает порядок токенов (переставь — получишь те же выходы, переставленные); позиции нужно добавить явно", "Снижает память", "Для токенизации"],
             "answer": 1},
            {"type": "choice", "q": "BERT и GPT:",
             "options": ["Одно и то же", "BERT — энкодер, видит контекст с обеих сторон, учится восстанавливать маскированные токены; GPT — декодер, причинная маска, предсказывает следующий токен",
                         "GPT — энкодер", "BERT генерирует текст лучше"], "answer": 1},
        ],
    },
    "q-w10-gen": {
        "title": "KV-кэш, temperature, top-k, top-p",
        "questions": [
            {"type": "choice", "q": "Что хранит KV-кэш и зачем?",
             "options": ["Веса модели", "K и V всех прошлых токенов в каждом слое: на новом шаге считаем Q, K, V только для нового токена", "Логиты", "Градиенты"],
             "answer": 1},
            {"type": "number", "q": "KV-кэш (FP16): 24 слоя, 16 голов по 64, контекст 2048, батч 1. Сколько МиБ? (2·слои·головы·d_head·T·2 байта)",
             "answer": 2 * 24 * 16 * 64 * 2048 * 2 / 2**20, "tol": 0.5},
            {"type": "choice", "q": "Temperature → 0 при сэмплировании даёт:",
             "options": ["Случайный текст", "Жадный выбор самого вероятного токена", "Пустой ответ", "Ошибку"], "answer": 1},
            {"type": "choice", "q": "Temperature = 2 делает распределение…",
             "options": ["острее", "площе: редкие токены выбираются чаще", "не меняет", "равным one-hot"], "answer": 1},
            {"type": "choice", "q": "top-p = 0,9 (nucleus):",
             "options": ["90 самых вероятных токенов", "Минимальный набор самых вероятных токенов с суммарной вероятностью ≥ 0,9; дальше перенормировка", "Случайные 90% словаря", "Порог 0,9 на каждый токен"],
             "answer": 1},
        ],
    },
}

EXERCISES = {
    "ex-w10-attention": {
        "title": "Scaled dot-product attention с маской на NumPy",
        "statement_ru": d("""\
            Напишите `attention(Q, K, V, causal=False)` для форм `(T, d)`:
            `softmax(QKᵀ/√d)·V`, softmax по последней оси, численно устойчивый.
            При `causal=True` позиция `i` не видит позиции `j > i`.
            Верните `(out, weights)`."""),
        "starter_code": "import numpy as np\n\n\ndef attention(Q, K, V, causal=False):\n    pass\n",
        "tests": d('''\
            import numpy as np
            from scipy.special import softmax

            rng = np.random.default_rng(10)
            T, dk = 6, 8
            Q, K, V = (rng.normal(size=(T, dk)) for _ in range(3))

            def test_full():
                """Без маски ≈ формула"""
                out, w = attention(Q, K, V)
                ref = softmax(Q @ K.T / np.sqrt(dk), axis=-1)
                assert np.allclose(w, ref) and np.allclose(out, ref @ V)

            def test_causal():
                """Маска: будущие позиции имеют вес 0"""
                out, w = attention(Q, K, V, causal=True)
                assert np.allclose(np.triu(w, 1), 0)
                assert np.allclose(w.sum(-1), 1)
                assert np.allclose(out[0], V[0])

            def test_stable():
                """Большие значения не дают nan"""
                out, w = attention(Q * 1000, K * 1000, V)
                assert np.isfinite(out).all()
            '''),
        "ref": d("""\
            import numpy as np


            def attention(Q, K, V, causal=False):
                scores = Q @ K.T / np.sqrt(Q.shape[-1])
                if causal:
                    T = scores.shape[0]
                    scores = np.where(np.triu(np.ones((T, T), dtype=bool), 1), -np.inf, scores)
                scores = scores - scores.max(-1, keepdims=True)
                w = np.exp(scores)
                w /= w.sum(-1, keepdims=True)
                return w @ V, w
        """),
        "hints_ru": [
            "Вес `i → j` показывает, насколько позиция `i` смотрит на позицию `j`. Как посчитать все такие веса одним действием? Какое значение score сделает вес будущей позиции ровно нулём после softmax?",
            "Scores — `Q @ K.T / √d`: деление на `√d` удерживает дисперсию scores около 1, и softmax не насыщается. Каузальная маска ставит `-inf` выше диагонали: `exp(-inf) = 0`, поэтому будущие позиции получают вес 0. Устойчивый softmax вычитает максимум строки.",
            "1) `scores = Q @ K.T / np.sqrt(d)`. 2) Если `causal`: `np.where(np.triu(np.ones((T, T), bool), 1), -np.inf, scores)`. 3) Вычтите `scores.max(-1, keepdims=True)`, `exp`, разделите на сумму по строке. 4) Верните `(w @ V, w)`. Диагональ не маскируется, поэтому в строке всегда есть конечный score.",
        ],
    },
    "ex-w10-sampling": {
        "title": "Сэмплирование: temperature, top-k, top-p",
        "statement_ru": d("""\
            Напишите функции, которые из логитов (`np.ndarray` формы `(V,)`) делают распределение вероятностей:
            - `with_temperature(logits, t)` → softmax(logits / t);
            - `top_k_probs(logits, k)` → оставить `k` самых больших логитов, остальным вероятность 0, перенормировать;
            - `top_p_probs(logits, p)` → оставить минимальный набор самых вероятных токенов с суммой ≥ `p`, перенормировать."""),
        "starter_code": "import numpy as np\n\n\ndef with_temperature(logits, t):\n    pass\n\n\ndef top_k_probs(logits, k):\n    pass\n\n\ndef top_p_probs(logits, p):\n    pass\n",
        "tests": d('''\
            import numpy as np

            L = np.log(np.array([0.5, 0.3, 0.15, 0.05]))

            def test_temperature():
                """t = 1 — исходные вероятности; t → 0 — почти one-hot; t большое — почти равномерно"""
                assert np.allclose(with_temperature(L, 1), [0.5, 0.3, 0.15, 0.05])
                assert with_temperature(L, 0.01)[0] > 0.999
                assert np.allclose(with_temperature(L, 1000), 0.25, atol=1e-3)

            def test_top_k():
                """top-2"""
                assert np.allclose(top_k_probs(L, 2), [0.625, 0.375, 0, 0])

            def test_top_p():
                """top-p: 0,7 → два токена; 0,8 → два (сумма ровно 0,8); 0,81 → три"""
                assert np.allclose(top_p_probs(L, 0.7), [0.625, 0.375, 0, 0])
                assert np.allclose(top_p_probs(L, 0.81), [0.5 / 0.95, 0.3 / 0.95, 0.15 / 0.95, 0])
                assert np.allclose(top_p_probs(L, 1.0).sum(), 1)
            '''),
        "ref": d("""\
            import numpy as np


            def _softmax(z):
                z = z - z.max()
                e = np.exp(z)
                return e / e.sum()


            def with_temperature(logits, t):
                return _softmax(np.asarray(logits, dtype=float) / t)


            def top_k_probs(logits, k):
                logits = np.asarray(logits, dtype=float)
                keep = np.argsort(-logits)[:k]
                masked = np.full_like(logits, -np.inf)
                masked[keep] = logits[keep]
                return _softmax(masked)


            def top_p_probs(logits, p):
                probs = _softmax(np.asarray(logits, dtype=float))
                order = np.argsort(-probs)
                cum = np.cumsum(probs[order])
                n = int(np.searchsorted(cum, p - 1e-12)) + 1
                out = np.zeros_like(probs)
                out[order[:n]] = probs[order[:n]]
                return out / out.sum()
        """),
        "hints_ru": [
            "Все три функции в конце превращают числа в распределение. Какое общее действие у них есть? Как «выключить» токен, чтобы после этого действия его вероятность стала ровно 0?",
            "Один устойчивый `softmax` для всех функций. Температура делит логиты: `t < 1` делает распределение острее, `t > 1` — ровнее. top-k: логиты вне топа замените на `-inf`. top-p: отсортируйте вероятности по убыванию, кумулятивная сумма `np.cumsum` показывает, где набралось `p`.",
            "1) `_softmax(z)`: вычтите максимум, `exp`, нормировка. 2) `with_temperature`: `_softmax(logits / t)`. 3) `top_k_probs`: индексы `np.argsort(-logits)[:k]`, остальным `-inf`, softmax. 4) `top_p_probs`: `order = np.argsort(-probs)`; `n = searchsorted(cumsum, p) + 1`; оставьте `order[:n]`, перенормируйте. Небольшой допуск `p - 1e-12` защищает от ошибок округления.",
        ],
    },
}
