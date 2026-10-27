"""Week 8 content: neural networks, backprop, optimizers, normalization."""

from textwrap import dedent as d

QUIZZES = {
    "q-w8-nn": {
        "title": "Нейрон, активации, loss, backprop, цикл обучения",
        "questions": [
            {"type": "expr", "q": "Производная сигмоиды σ(x) = 1/(1 + e^(−x)). Запишите через x (можно через σ(x) как sigma(x))",
             "vars": ["x"], "ref": "exp(-x)/(1+exp(-x))**2", "domain": [[-3, 3]], "explain": "σ'(x) = σ(x)(1 − σ(x))."},
            {"type": "choice", "q": "Почему без нелинейных активаций MLP бесполезен?",
             "options": ["Медленно учится", "Композиция линейных слоёв — снова линейная функция: глубина ничего не даёт", "Нужна для GPU", "Не бывает"],
             "answer": 1},
            {"type": "choice", "q": "Почему ReLU вытеснила сигмоиду в скрытых слоях?",
             "options": ["Красивее", "Сигмоида насыщается: при больших |x| производная ≈ 0, градиент затухает; у ReLU производная 1 при x > 0", "ReLU гладкая", "Сигмоида не дифференцируема"],
             "answer": 1},
            {"type": "number", "q": "L = (w·x − y)², w = 2, x = 3, y = 4. Чему равен ∂L/∂w?",
             "answer": 2 * (2 * 3 - 4) * 3, "tol": 1e-9, "explain": "2(wx − y)·x = 2·2·3 = 12."},
            {"type": "vector", "q": "Softmax + cross-entropy: p = [0,7; 0,2; 0,1], верный класс — 0. Градиент loss по логитам?",
             "answer": [-0.3, 0.2, 0.1], "tol": 1e-6, "labels": ["z₀", "z₁", "z₂"], "explain": "∂L/∂z = p − onehot."},
            {"type": "choice", "q": "Зачем `optimizer.zero_grad()` в каждой итерации?",
             "options": ["Обнуляет веса", "PyTorch накапливает (суммирует) градиенты в `.grad`; без обнуления шаг использует сумму градиентов прошлых батчей",
                         "Ускоряет GPU", "Сохраняет модель"], "answer": 1},
            {"type": "choice", "q": "Правильный порядок в цикле обучения PyTorch:",
             "options": ["step → backward → zero_grad → forward", "zero_grad → forward → loss → backward → step", "forward → step → backward", "backward → forward → step"],
             "answer": 1},
            {"type": "choice", "q": "Для многоклассовой классификации в PyTorch `nn.CrossEntropyLoss` принимает:",
             "options": ["вероятности после softmax", "сырые логиты (softmax внутри) и индексы классов", "one-hot и вероятности", "только два класса"], "answer": 1},
        ],
    },
    "q-w8-optim": {
        "title": "SGD, Adam, AdamW, learning rate, нормализация, dropout, RNN",
        "questions": [
            {"type": "choice", "q": "Чем Adam отличается от SGD?",
             "options": ["Ничем", "Хранит скользящие средние градиента (m) и его квадрата (v): у каждого параметра свой эффективный шаг", "Не использует градиент", "Только для CNN"],
             "answer": 1},
            {"type": "choice", "q": "Чем AdamW отличается от Adam с L2?",
             "options": ["Ничем", "Weight decay применяется к весам напрямую, отдельно от адаптивного шага (decoupled) — регуляризация работает как задумано",
                         "AdamW без моментов", "AdamW для RNN"], "answer": 1},
            {"type": "choice", "q": "Loss прыгает и растёт до NaN с первых шагов. Первое, что проверить:",
             "options": ["Добавить слоёв", "Слишком большой learning rate", "Слишком маленький батч", "Мало эпох"], "answer": 1},
            {"type": "choice", "q": "Зачем warmup learning rate в начале обучения трансформеров?",
             "options": ["Для красоты", "Статистики Adam ещё неточны, большие шаги в начале дестабилизируют обучение", "Чтобы прогреть GPU", "Снижает память"],
             "answer": 1},
            {"type": "choice", "q": "BatchNorm и LayerNorm:",
             "options": ["Одно и то же", "BatchNorm нормирует по батчу для каждого признака (зависит от батча, разное поведение в train/eval); LayerNorm — по признакам каждого объекта отдельно",
                         "LayerNorm только для CNN", "BatchNorm без параметров"], "answer": 1},
            {"type": "number", "q": "Dropout p = 0,2 при обучении (inverted dropout). На сколько умножаются оставшиеся активации?",
             "answer": 1.25, "tol": 1e-9, "explain": "1/(1 − p): так матожидание сохраняется, а в eval dropout просто выключен."},
            {"type": "choice", "q": "Почему трансформер заменил RNN/LSTM?",
             "options": ["RNN не умеют в текст", "RNN обрабатывает токены последовательно (не параллелится) и плохо держит дальние зависимости; attention видит все позиции сразу",
                         "LSTM слишком мало параметров", "Трансформер меньше"], "answer": 1},
        ],
    },
}

EXERCISES = {
    "ex-w8-micrograd": {
        "title": "micrograd: класс Value с обратным проходом",
        "statement_ru": d("""\
            Напишите класс `Value` (как micrograd Karpathy): скаляр `data`, градиент `grad`.
            Нужны операции `+`, `*` (в том числе с обычными числами слева и справа), `**` (степень — число),
            `tanh()`, `relu()` и `backward()` (топологическая сортировка + цепное правило).

            Тест сверяет градиенты с численными (конечные разности)."""),
        "starter_code": "import math\n\n\nclass Value:\n    def __init__(self, data, _children=()):\n        self.data = data\n        self.grad = 0.0\n\n    def backward(self):\n        pass\n",
        "tests": d('''\
            import math

            def f(a, b, c):
                return ((a * b + c) ** 2 + (a + 1).tanh() * 3 - (b * c).relu() * 2 if hasattr(a, "relu") else
                        (a * b + c) ** 2 + math.tanh(a + 1) * 3 - max(0, b * c) * 2)

            def test_simple():
                """d(a·b)/da = b"""
                a, b = Value(2.0), Value(-3.0)
                out = a * b
                out.backward()
                assert out.data == -6.0 and a.grad == -3.0 and b.grad == 2.0

            def test_reuse():
                """Узел используется дважды — градиенты складываются"""
                a = Value(3.0)
                out = a * a + a
                out.backward()
                assert abs(a.grad - 7.0) < 1e-12

            def test_numeric():
                """Сложное выражение: градиенты = конечные разности"""
                x = dict(a=0.7, b=-1.3, c=0.4)
                vs = {k: Value(v) for k, v in x.items()}
                out = vs["a"] * vs["b"] + vs["c"]
                out = out ** 2 + (vs["a"] + 1).tanh() * 3 + (vs["b"] * vs["c"]).relu() * (-2)
                out.backward()
                h = 1e-6
                for k in x:
                    up = dict(x); up[k] += h
                    dn = dict(x); dn[k] -= h
                    g = (f(**up) - f(**dn)) / (2 * h)
                    assert abs(vs[k].grad - g) < 1e-5, (k, vs[k].grad, g)

            def test_radd():
                """Число слева: 2 + v и 3 * v"""
                v = Value(1.5)
                out = 2 + v * 3
                out.backward()
                assert out.data == 6.5 and v.grad == 3.0
            '''),
        "ref": d("""\
            import math


            class Value:
                def __init__(self, data, _children=()):
                    self.data = data
                    self.grad = 0.0
                    self._prev = set(_children)
                    self._backward = lambda: None

                def __add__(self, other):
                    other = other if isinstance(other, Value) else Value(other)
                    out = Value(self.data + other.data, (self, other))

                    def _backward():
                        self.grad += out.grad
                        other.grad += out.grad
                    out._backward = _backward
                    return out

                def __mul__(self, other):
                    other = other if isinstance(other, Value) else Value(other)
                    out = Value(self.data * other.data, (self, other))

                    def _backward():
                        self.grad += other.data * out.grad
                        other.grad += self.data * out.grad
                    out._backward = _backward
                    return out

                def __pow__(self, k):
                    out = Value(self.data ** k, (self,))

                    def _backward():
                        self.grad += k * self.data ** (k - 1) * out.grad
                    out._backward = _backward
                    return out

                def tanh(self):
                    t = math.tanh(self.data)
                    out = Value(t, (self,))

                    def _backward():
                        self.grad += (1 - t * t) * out.grad
                    out._backward = _backward
                    return out

                def relu(self):
                    out = Value(max(0.0, self.data), (self,))

                    def _backward():
                        self.grad += (self.data > 0) * out.grad
                    out._backward = _backward
                    return out

                __radd__ = __add__
                __rmul__ = __mul__

                def __neg__(self):
                    return self * -1

                def __sub__(self, other):
                    return self + (-other)

                def backward(self):
                    order, seen = [], set()

                    def build(v):
                        if v not in seen:
                            seen.add(v)
                            for c in v._prev:
                                build(c)
                            order.append(v)
                    build(self)
                    self.grad = 1.0
                    for v in reversed(order):
                        v._backward()
        """),
        "hints_ru": [
            "Выражение `(a * b + c).tanh()` — цепочка простых операций. Что нужно запомнить в каждом промежуточном результате, чтобы потом пройти цепочку назад?",
            "Каждая операция создаёт новый `Value` с детьми `_prev` и замыканием `_backward`. Замыкание добавляет (`+=`) вклад в `grad` детей по цепному правилу. `+=` нужен: одно значение может участвовать в выражении несколько раз. Для `2 + v` и `3 * v` нужны `__radd__` и `__rmul__`; число превращайте в `Value`.",
            "1) `__add__`: `out.grad` идёт обоим детям. 2) `__mul__`: `self.grad += other.data * out.grad` и наоборот. 3) `__pow__`: `k * data**(k-1)`; `tanh`: `1 - t²`; `relu`: `data > 0`. 4) `backward`: DFS строит топологический порядок, `self.grad = 1`, затем `_backward()` в обратном порядке.",
        ],
    },
    "ex-w8-adam": {
        "title": "Шаг оптимизатора Adam на NumPy",
        "statement_ru": d("""\
            Напишите `adam_step(w, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8)` → `(w_new, m_new, v_new)`.
            `t` — номер шага, начиная с 1. Формулы:
            `m = b1·m + (1−b1)·g`, `v = b2·v + (1−b2)·g²`, `m̂ = m/(1−b1ᵗ)`, `v̂ = v/(1−b2ᵗ)`,
            `w = w − lr·m̂/(√v̂ + eps)`. Не меняйте входные массивы на месте."""),
        "starter_code": "import numpy as np\n\n\ndef adam_step(w, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8):\n    pass\n",
        "tests": d('''\
            import numpy as np

            def test_first_step():
                """Первый шаг: размер ≈ lr для каждого параметра, против знака градиента"""
                w = np.array([1.0, -2.0, 3.0]); g = np.array([0.5, -10.0, 1e-3])
                w1, m1, v1 = adam_step(w, g, np.zeros(3), np.zeros(3), 1, lr=0.1)
                assert np.allclose(w - w1, 0.1 * np.sign(g), atol=1e-4)
                assert np.allclose(m1, 0.1 * g) and np.allclose(v1, 0.001 * g ** 2)

            def test_converges():
                """200 шагов на f(w) = Σ(w − 3)² приводят к w ≈ 3"""
                w = np.zeros(4); m = np.zeros(4); v = np.zeros(4)
                for t in range(1, 1001):
                    w, m, v = adam_step(w, 2 * (w - 3), m, v, t, lr=0.05)
                assert np.allclose(w, 3, atol=1e-2), w

            def test_pure():
                """Входные массивы не меняются"""
                w = np.ones(2); g = np.ones(2); m = np.zeros(2); v = np.zeros(2)
                adam_step(w, g, m, v, 1)
                assert np.array_equal(w, np.ones(2)) and np.array_equal(m, np.zeros(2))
            '''),
        "ref": d("""\
            import numpy as np


            def adam_step(w, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8):
                m = b1 * m + (1 - b1) * g
                v = b2 * v + (1 - b2) * g ** 2
                m_hat = m / (1 - b1 ** t)
                v_hat = v / (1 - b2 ** t)
                return w - lr * m_hat / (np.sqrt(v_hat) + eps), m, v
        """),
        "hints_ru": [
            "На первом шаге `m` и `v` начинаются с нулей. Насколько тогда `m = b1·m + (1−b1)·g` меньше реального градиента? Что нужно сделать с этим смещением?",
            "Поправка смещения: делите `m` на `1 − b1ᵗ` и `v` на `1 − b2ᵗ`. На первом шаге это даёт `m̂ = g`, `v̂ = g²`, и шаг ≈ `lr` на каждый параметр. Новые массивы создавайте выражениями `m = b1 * m + ...`: `m *= b1` изменит вход на месте.",
            "1) `m = b1 * m + (1 - b1) * g`. 2) `v = b2 * v + (1 - b2) * g ** 2`. 3) `m_hat = m / (1 - b1 ** t)`, `v_hat = v / (1 - b2 ** t)`. 4) `w_new = w - lr * m_hat / (np.sqrt(v_hat) + eps)`. 5) Верните `(w_new, m, v)`.",
        ],
    },
}
