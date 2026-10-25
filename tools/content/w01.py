"""Week 1 content: quizzes and Python exercises.

Question types (see app/js/views/quiz.js):
    output  {code}                         answer = real stdout, computed at build time
    choice  {q, options, answer: index}
    multi   {q, options, answers: [index]}
    expr    {q, vars, ref, domain}         numeric comparison at random points of `domain`
    number  {q, answer, tol}
    vector  {q, answer: [..], tol, labels}
    text    {q, model}                     self-check: the student compares with the model answer
Every question may have "explain" (shown after the answer) and "source" (topic link).
"""

from textwrap import dedent as d

QUIZZES = {
    "q-w1-names": {
        "title": "Имена, ссылки, изменяемость, копии, B1, B2",
        "questions": [
            {"type": "output", "code": "a = [1, 2]\nb = a\nb.append(3)\nprint(a)",
             "explain": "`b = a` не копирует список: оба имени ссылаются на один объект."},
            {"type": "output", "code": "a = [1, 2]\nb = a[:]\nb.append(3)\nprint(a, b)",
             "explain": "Срез `a[:]` создаёт новый список (поверхностную копию)."},
            {"type": "output", "code": "x = [1]\ny = [1]\nprint(x == y, x is y)",
             "explain": "`==` сравнивает значения, `is` — объекты. Здесь два разных списка с равными значениями."},
            {"type": "output", "code": "a = [1]\nb = a\na += [2]\nprint(b)\na = a + [3]\nprint(b)",
             "explain": "`+=` для списка меняет объект на месте (это видно через `b`). `a + [3]` создаёт новый список и перепривязывает только `a`."},
            {"type": "output", "code": "t = (1, [2])\nt[1].append(3)\nprint(t)",
             "explain": "Кортеж неизменяем, но хранит ссылку на изменяемый список. Сам список менять можно."},
            {"type": "output", "code": "import copy\na = [[1], [2]]\nb = copy.copy(a)\nb[0].append(9)\nb.append([3])\nprint(a)",
             "explain": "`copy.copy` копирует только внешний список. Внутренние списки общие, поэтому `9` видно в `a`, а `[3]` — нет."},
            {"type": "output", "code": "import copy\na = [[1], [2]]\nb = copy.deepcopy(a)\nb[0].append(9)\nprint(a)",
             "explain": "`deepcopy` рекурсивно копирует вложенные объекты."},
            {"type": "output", "code": "def add(x, items=[]):\n    items.append(x)\n    return items\n\nprint(add(1))\nprint(add(2))",
             "explain": "B1. Значение по умолчанию вычисляется **один раз**, при выполнении `def`. Все вызовы без `items` делят один список."},
            {"type": "output", "code": "a = [[0] * 3] * 3\na[0][0] = 1\nprint(a)",
             "explain": "B2. Внешнее `* 3` копирует **ссылку** на одну и ту же строку три раза."},
            {"type": "choice", "q": "Как правильно исправить B1?",
             "options": ["`def add(x, items=list()):`", "`def add(x, items=None):` и внутри `if items is None: items = []`",
                         "`def add(x, items=[][:]):`", "Вызывать `add(1, [])` всегда"],
             "answer": 1, "explain": "`list()` и `[][:]` тоже вычисляются один раз при `def`. Нужен «пустой маркер» `None` и новый список внутри функции."},
            {"type": "choice", "q": "Как создать матрицу 3×3 из нулей без общих строк?",
             "options": ["`[[0] * 3] * 3`", "`[[0] * 3 for _ in range(3)]`", "`copy.copy([[0] * 3] * 3)`", "`list([[0] * 3] * 3)`"],
             "answer": 1, "explain": "Генератор списка выполняет `[0] * 3` заново на каждой итерации. `copy.copy` и `list` копируют только внешний список."},
            {"type": "text", "q": "Своими словами: что делает присваивание `b = a` в Python?",
             "model": "Привязывает имя `b` к тому же объекту, на который ссылается `a`. Объект не копируется. Имя — это ярлык на объект, а не «коробка» со значением."},
        ],
    },
    "q-w1-scopes": {
        "title": "Области видимости, замыкания, B3, аргументы, хэшируемость, B4",
        "questions": [
            {"type": "output", "code": "funcs = [lambda: i for i in range(3)]\nprint([f() for f in funcs])",
             "explain": "B3. Позднее связывание: лямбда ищет `i` в момент **вызова**. К этому моменту цикл закончился и `i == 2`."},
            {"type": "output", "code": "funcs = [lambda i=i: i for i in range(3)]\nprint([f() for f in funcs])",
             "explain": "Значение по умолчанию вычисляется при создании лямбды — здесь это полезно: каждая лямбда запоминает своё `i`."},
            {"type": "output", "code": "x = 1\n\ndef f():\n    print(x)\n    x = 2\n\ntry:\n    f()\nexcept UnboundLocalError:\n    print(\"UnboundLocalError\")",
             "explain": "Присваивание `x = 2` где угодно в теле делает `x` локальным для всей функции. `print(x)` читает локальное `x` до присваивания."},
            {"type": "output", "code": "def make_counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\n\nc = make_counter()\nc()\nc()\nprint(c())",
             "explain": "`nonlocal` разрешает менять переменную из внешней функции. Замыкание хранит `count` между вызовами."},
            {"type": "output", "code": "def f(*args, **kwargs):\n    print(args, kwargs)\n\nf(1, 2, a=3)",
             "explain": "`*args` собирает позиционные аргументы в кортеж, `**kwargs` — именованные в словарь."},
            {"type": "multi", "q": "Дана `def f(a, /, b, *, c): ...`. Какие вызовы работают?",
             "options": ["`f(1, 2, c=3)`", "`f(1, b=2, c=3)`", "`f(a=1, b=2, c=3)`", "`f(1, 2, 3)`"],
             "answers": [0, 1], "explain": "До `/` — только позиционные (`a=1` нельзя). После `*` — только именованные (`c` нельзя передать позиционно)."},
            {"type": "output", "code": "try:\n    d = {[1, 2]: \"x\"}\nexcept TypeError as e:\n    print(type(e).__name__)\nd = {(1, 2): \"x\"}\nprint(d[(1, 2)])",
             "explain": "Список изменяем, поэтому не hashable и не может быть ключом. Кортеж из hashable-элементов — может."},
            {"type": "output", "code": "try:\n    hash((1, [2]))\nexcept TypeError:\n    print(\"нельзя\")",
             "explain": "Кортеж hashable, только если hashable **все** его элементы."},
            {"type": "choice", "q": "Средняя сложность `x in s` для `list` и для `set` из n элементов:",
             "options": ["O(1) и O(1)", "O(n) и O(1)", "O(log n) и O(1)", "O(n) и O(log n)"], "answer": 1,
             "explain": "Список проверяется перебором. Множество — хэш-таблица: ищет по хэшу сразу нужную ячейку."},
            {"type": "choice", "q": "Почему поиск в `dict` в худшем случае O(n)?",
             "options": ["Python иногда сортирует словарь", "Много ключей с одинаковым хэшем (коллизии) — их приходится перебирать",
                         "Словарь хранит ключи в списке", "Из-за сборщика мусора"],
             "answer": 1, "explain": "Если хэши многих ключей совпадают (или попадают в одни ячейки), поиск сравнивает ключи по одному."},
            {"type": "text", "q": "B4: почему ключом `dict` может быть `tuple`, но не `list`? Какая сложность поиска по ключу в среднем и в худшем случае?",
             "model": "Ключ должен быть hashable: хэш не меняется, пока объект живёт. Список изменяем — его хэш мог бы измениться, поэтому `__hash__` у него нет. Кортеж из hashable-элементов hashable. Поиск: O(1) в среднем, O(n) в худшем (коллизии)."},
        ],
    },
    "q-w1-math1": {
        "title": "Производная и правила",
        "questions": [
            {"type": "choice", "q": "Что такое производная f′(x)?",
             "options": ["Значение функции в точке x", "Предел отношения малого сдвига выхода к малому сдвигу входа: (f(x+h) − f(x)) / h при h → 0",
                         "Площадь под графиком", "Разность f(x+1) − f(x)"],
             "answer": 1, "explain": "Производная — скорость изменения: насколько меняется выход на единицу малого сдвига входа."},
            {"type": "number", "q": "f(x) = x². Чему равен наклон касательной в точке x = 3?", "answer": 6, "tol": 1e-9,
             "explain": "f′(x) = 2x, f′(3) = 6."},
            {"type": "expr", "q": "Задача 1. Найдите f′(x) для f(x) = 3x⁴ − 5x² + 7x − 2", "vars": ["x"], "ref": "12*x**3 - 10*x + 7",
             "domain": [[-3, 3]], "explain": "Степенное правило: (xⁿ)′ = n·xⁿ⁻¹; производная константы — 0."},
            {"type": "expr", "q": "Задача 2. f(x) = √x + 1/x. Найдите f′(x)", "vars": ["x"], "ref": "1/(2*sqrt(x)) - 1/x**2",
             "domain": [[0.2, 5]], "explain": "√x = x^(1/2) → (1/2)x^(−1/2). 1/x = x^(−1) → −x^(−2)."},
            {"type": "expr", "q": "Задача 3. f(x) = x²·eˣ. Найдите f′(x)", "vars": ["x"], "ref": "exp(x)*(x**2 + 2*x)",
             "domain": [[-2, 2]], "explain": "Правило произведения: (uv)′ = u′v + uv′ = 2x·eˣ + x²·eˣ."},
            {"type": "expr", "q": "Задача 4. f(x) = x·ln x. Найдите f′(x)", "vars": ["x"], "ref": "log(x) + 1",
             "domain": [[0.2, 5]], "explain": "(x)′·ln x + x·(1/x) = ln x + 1."},
        ],
    },
    "q-w1-math2": {
        "title": "Цепное правило, сигмоида, частные производные, градиент",
        "questions": [
            {"type": "expr", "q": "Задача 5. f(x) = (3x + 1)⁵. Найдите f′(x)", "vars": ["x"], "ref": "15*(3*x + 1)**4",
             "domain": [[-1, 1]], "explain": "Цепное правило: внешняя производная 5u⁴, внутренняя (3x + 1)′ = 3."},
            {"type": "expr", "q": "Задача 6. f(x) = e^(−x²). Найдите f′(x)", "vars": ["x"], "ref": "-2*x*exp(-x**2)",
             "domain": [[-2, 2]], "explain": "Внешняя eᵘ, внутренняя −x² → −2x."},
            {"type": "expr", "q": "Задача 7. f(x) = ln(1 + x²). Найдите f′(x)", "vars": ["x"], "ref": "2*x/(1 + x**2)",
             "domain": [[-3, 3]], "explain": "(ln u)′ = u′/u."},
            {"type": "number", "q": "Задача 8. σ(x) = 1/(1 + e^(−x)), σ′ = σ(1 − σ). Чему равно σ′(0)?", "answer": 0.25, "tol": 1e-6,
             "explain": "σ(0) = 1/2, значит σ′(0) = 1/2 · 1/2 = 1/4."},
            {"type": "expr", "q": "Задача 9. g(w) = σ(2w + 1). Найдите g′(w). Можно писать `sigma(...)` или `σ(...)`.", "vars": ["w"],
             "ref": "2*sigma(2*w + 1)*(1 - sigma(2*w + 1))", "domain": [[-2, 2]],
             "explain": "Цепное правило: σ′(u)·u′ = σ(u)(1 − σ(u))·2. Это ровно то, что backprop делает в нейроне."},
            {"type": "expr", "q": "Задача 10 (D1). f(x, y) = x²y + 3y. Найдите ∂f/∂x", "vars": ["x", "y"], "ref": "2*x*y",
             "domain": [[-3, 3], [-3, 3]], "explain": "y — константа: (x²)′·y = 2xy; 3y по x — константа, производная 0."},
            {"type": "expr", "q": "Задача 10 (D1). f(x, y) = x²y + 3y. Найдите ∂f/∂y", "vars": ["x", "y"], "ref": "x**2 + 3",
             "domain": [[-3, 3], [-3, 3]], "explain": "x — константа: x²·(y)′ + 3 = x² + 3."},
            {"type": "vector", "q": "Задача 10. Найдите ∇f(1, 2) для f = x²y + 3y", "answer": [4, 4], "tol": 1e-6, "labels": ["∂f/∂x", "∂f/∂y"],
             "explain": "(2·1·2, 1² + 3) = (4, 4)."},
            {"type": "vector", "q": "Задача 11. f = x³y² − 4xy + y. Найдите ∇f(1, −1)", "answer": [7, -5], "tol": 1e-6, "labels": ["∂f/∂x", "∂f/∂y"],
             "explain": "∂f/∂x = 3x²y² − 4y → 3 + 4 = 7; ∂f/∂y = 2x³y − 4x + 1 → −2 − 4 + 1 = −5."},
            {"type": "vector", "q": "Задача 12. f = x·e^(yz). Найдите ∇f(2, 0, 3)", "answer": [1, 6, 0], "tol": 1e-6, "labels": ["∂f/∂x", "∂f/∂y", "∂f/∂z"],
             "explain": "(e^(yz), xz·e^(yz), xy·e^(yz)) в точке (2, 0, 3) = (1, 6, 0)."},
            {"type": "choice", "q": "Что показывает градиент функции в точке?",
             "options": ["Направление быстрейшего убывания", "Направление быстрейшего роста; длина — скорость роста", "Точку минимума", "Значение функции"],
             "answer": 1, "explain": "Поэтому градиентный спуск делает шаг **против** градиента: x ← x − lr·∇f."},
        ],
    },
    "q-w1-sunday": {
        "title": "Самопроверка недели: B1–B4, D1 и задачи 13–17",
        "questions": [
            {"type": "output", "code": "def add(x, items=[]):\n    items.append(x)\n    return items\n\nprint(add(1), add(2))",
             "explain": "Оба вызова возвращают один и тот же список. `print` вычисляет оба аргумента до печати и видит список уже после второго вызова."},
            {"type": "output", "code": "grid = [[0] * 2] * 2\ngrid[1][1] = 5\nprint(grid)", "explain": "B2: две ссылки на одну строку."},
            {"type": "output", "code": "fs = []\nfor i in range(3):\n    fs.append(lambda: i * 10)\nprint([f() for f in fs])",
             "explain": "B3 в цикле `for`: то же позднее связывание."},
            {"type": "text", "q": "B4 без подсказок: hashable, почему tuple можно, а list нельзя, сложность поиска в dict.",
             "model": "Hashable — хэш объекта не меняется за время жизни, есть `__hash__` и `__eq__`. tuple из hashable-элементов hashable; list изменяем — нет. Поиск O(1) в среднем, O(n) в худшем из-за коллизий."},
            {"type": "expr", "q": "D1 без подсказок: f = x²y + 3y, ∂f/∂x =", "vars": ["x", "y"], "ref": "2*x*y", "domain": [[-3, 3], [-3, 3]]},
            {"type": "expr", "q": "D1: ∂f/∂y =", "vars": ["x", "y"], "ref": "x**2 + 3", "domain": [[-3, 3], [-3, 3]]},
            {"type": "vector", "q": "Задача 13. f = x² + 3y², старт (1, 1), lr = 0,1. Новая точка после одного шага градиентного спуска?", "answer": [0.8, 0.4], "tol": 1e-6, "labels": ["x", "y"],
             "explain": "∇f = (2x, 6y) = (2, 6). (1, 1) − 0,1·(2, 6) = (0,8; 0,4)."},
            {"type": "number", "q": "Задача 13. Значение f в новой точке?", "answer": 1.12, "tol": 1e-6, "explain": "0,64 + 3·0,16 = 1,12 (было 4)."},
            {"type": "expr", "q": "Задача 14. z = x²y, x = t², y = 3t. Найдите dz/dt", "vars": ["t"], "ref": "15*t**4", "domain": [[-2, 2]],
             "explain": "z = t⁴·3t = 3t⁵ → 15t⁴. Через цепное правило: 2xy·2t + x²·3."},
            {"type": "vector", "q": "Задача 15. ŷ = wx + b, L = (1/n)Σ(ŷᵢ − yᵢ)², x = [1, 2, 3], y = [2, 4, 6], w = 1, b = 0. Найдите L, ∂L/∂w, ∂L/∂b", "answer": [14 / 3, -28 / 3, -4], "tol": 1e-3,
             "labels": ["L", "∂L/∂w", "∂L/∂b"], "explain": "Ошибки: −1, −2, −3. L = 14/3. ∂L/∂w = (2/n)Σ eᵢxᵢ = −28/3. ∂L/∂b = (2/n)Σ eᵢ = −4."},
            {"type": "vector", "q": "Задача 16. f = x³, x = 2, h = 0,01. Центральная разность и прямая разность:", "answer": [12.0001, 12.0601], "tol": 1e-3,
             "labels": ["центральная", "прямая"], "explain": "Центральная (f(x+h) − f(x−h))/2h точнее: ошибка O(h²) против O(h)."},
            {"type": "vector", "q": "Задача 17. e = (a + b)(b + 1), a = 2, b = 1. Найдите e, ∂e/∂a, ∂e/∂b", "answer": [6, 2, 5], "tol": 1e-6,
             "labels": ["e", "∂e/∂a", "∂e/∂b"], "explain": "c = a + b = 3, d = b + 1 = 2. ∂e/∂a = d = 2; ∂e/∂b = d + c = 5 (b входит в оба множителя)."},
        ],
    },
    "q-w1-oral": {
        "title": "Вопросы вслух (как на собеседовании)",
        "oral": True,
        "questions": [
            {"type": "text", "q": "Почему `print(add(1), add(2))` в одной строке печатает `[1, 2] [1, 2]`, а в двух строках — `[1]` и `[1, 2]`?",
             "model": "Оба вызова возвращают один и тот же список. `print` сначала вычисляет оба аргумента, поэтому печатает список уже после второго вызова."},
            {"type": "text", "q": "Чем `a = a + [x]` отличается от `a += [x]`, если до этого было `b = a`?",
             "model": "`a + [x]` создаёт новый список и перепривязывает `a`; `b` остаётся старым. `a += [x]` меняет список на месте (`__iadd__`), изменение видно через `b`."},
            {"type": "text", "q": "Почему `[[0]*3]*3` даёт общие строки, а `[[0]*3 for _ in range(3)]` — нет? Помогает ли `copy.copy`?",
             "model": "`* 3` повторяет ссылку на один объект. Генератор создаёт новый список на каждой итерации. `copy.copy` копирует только внешний список — строки остаются общими; нужен `deepcopy` или генератор."},
            {"type": "text", "q": "Почему лямбды в цикле возвращают последнее `i`? Назовите два исправления.",
             "model": "Замыкание хранит ссылку на переменную, значение читается при вызове. Исправления: `lambda i=i: i` (значение по умолчанию фиксирует текущее i) или фабрика `def make(i): return lambda: i` (новая область на каждый вызов)."},
            {"type": "text", "q": "Что такое hashable? Почему `(1, [2])` — не ключ? Откуда O(n) в худшем случае?",
             "model": "Хэш не меняется за время жизни, объект можно сравнить. Кортеж hashable, только если все элементы hashable; список — нет. O(n): коллизии хэшей, ключи сравниваются по одному."},
            {"type": "text", "q": "Что такое производная в терминах малых сдвигов? Объясните цепное правило без формул.",
             "model": "Во сколько раз выход меняется сильнее входа при очень малом сдвиге. Цепное правило: если x влияет на y, а y на z, то чувствительности перемножаются."},
            {"type": "text", "q": "Что показывает градиент? Посчитайте ∇(x²y + 3y) в (1, 2). Куда шагнёт градиентный спуск и почему со знаком минус?",
             "model": "Направление быстрейшего роста. ∇ = (2xy, x² + 3) = (4, 4). Спуск идёт против градиента, к уменьшению функции: (1, 2) − lr·(4, 4)."},
            {"type": "text", "q": "Two Sum: какой вопрос вы задаёте словарю и почему решение O(n), а не O(n²)?",
             "model": "«Видел ли я число target − x?» Проверка в словаре — O(1) в среднем, проход один → O(n). Перебор пар — O(n²)."},
        ],
    },
}

EXERCISES = {
    "ex-w1-b1": {
        "title": "B1: исправьте значение по умолчанию",
        "statement_ru": d("""\
            Функция `add(x, items=...)` добавляет `x` в список `items` и возвращает его.
            Если список не передан, функция должна начинать с **нового** пустого списка.
            Сейчас в шаблоне ловушка B1. Исправьте её, не меняя поведение для переданного списка."""),
        "starter_code": "def add(x, items=[]):\n    items.append(x)\n    return items\n",
        "tests": d('''\
            def test_fresh_list():
                """Два вызова без items не делят список"""
                assert add(1) == [1]
                assert add(2) == [2], "второй вызов видит список первого вызова"

            def test_given_list():
                """Переданный список меняется на месте"""
                box = [0]
                result = add(5, box)
                assert result is box, "нужно вернуть тот же список, а не копию"
                assert box == [0, 5]

            def test_default_is_none():
                """Значение по умолчанию — неизменяемый маркер"""
                import inspect
                default = inspect.signature(add).parameters["items"].default
                assert default is None, f"по умолчанию сейчас {default!r}; используйте None"
            '''),
        "ref": "def add(x, items=None):\n    if items is None:\n        items = []\n    items.append(x)\n    return items\n",
        "hints_ru": [
            "Вызовите `add(1)`, потом `add(2)`. Почему второй результат содержит `1`? В какой момент Python создаёт список `[]` из строки `def`?",
            "Значение по умолчанию вычисляется один раз, при выполнении `def`. Поэтому изменяемый объект там общий для всех вызовов. Нужен неизменяемый маркер «аргумент не передан» — `None`.",
            "1) В сигнатуре поставьте `items=None`. 2) В начале тела: если `items is None`, создайте новый пустой список. 3) Дальше код без изменений. Переданный список меняйте на месте и возвращайте его же.",
        ],
    },
    "ex-w1-b2": {
        "title": "B2: матрица без общих строк",
        "statement_ru": d("""\
            Напишите `make_grid(rows, cols, fill=0)`: вернуть список из `rows` строк, в каждой
            `cols` значений `fill`. Строки должны быть **независимыми**: изменение одной строки
            не меняет другие."""),
        "starter_code": "def make_grid(rows, cols, fill=0):\n    return [[fill] * cols] * rows\n",
        "tests": d('''\
            def test_shape():
                """Размер и значения"""
                g = make_grid(2, 3, 7)
                assert g == [[7, 7, 7], [7, 7, 7]]

            def test_independent_rows():
                """Строки — разные объекты"""
                g = make_grid(3, 3)
                g[0][0] = 1
                assert g == [[1, 0, 0], [0, 0, 0], [0, 0, 0]], f"после g[0][0] = 1 получилось {g}"
                assert len({id(row) for row in g}) == 3, "строки ссылаются на один и тот же список"

            def test_empty():
                """Ноль строк или столбцов"""
                assert make_grid(0, 5) == []
                assert make_grid(2, 0) == [[], []]
            '''),
        "ref": "def make_grid(rows, cols, fill=0):\n    return [[fill] * cols for _ in range(rows)]\n",
        "hints_ru": [
            "Создайте сетку шаблоном и поменяйте один элемент первой строки. Почему поменялись все строки? Что именно копирует внешнее `* rows`?",
            "`[row] * rows` повторяет ссылку на один и тот же список. Генератор списка выполняет выражение заново на каждой итерации. Так каждая строка — новый объект.",
            "1) Строка — `[fill] * cols`. Внутреннее `*` здесь безопасно: числа неизменяемы. 2) Создайте строку внутри генератора списка по `range(rows)`. 3) Проверьте `rows = 0`: ответ `[]`.",
        ],
    },
    "ex-w1-b3": {
        "title": "B3: фабрика множителей",
        "statement_ru": d("""\
            Напишите `make_multipliers(n)`: вернуть список из `n` функций. Функция с номером `i`
            умножает аргумент на `i`: `make_multipliers(3)[2](10) == 20`.
            Шаблон показывает ловушку позднего связывания."""),
        "starter_code": "def make_multipliers(n):\n    return [lambda x: i * x for i in range(n)]\n",
        "tests": d('''\
            def test_each_function_keeps_its_i():
                """Каждая функция помнит своё i"""
                fs = make_multipliers(4)
                got = [f(10) for f in fs]
                assert got == [0, 10, 20, 30], f"получилось {got}: все функции видят последнее i?"

            def test_one_argument():
                """Функцию вызывают с одним аргументом"""
                import inspect
                f = make_multipliers(2)[1]
                assert f(7) == 7
                assert len([p for p in inspect.signature(f).parameters.values() if p.default is inspect.Parameter.empty]) == 1

            def test_zero():
                """n = 0 — пустой список"""
                assert make_multipliers(0) == []
            '''),
        "ref": "def make_multipliers(n):\n    def make(i):\n        return lambda x: i * x\n    return [make(i) for i in range(n)]\n",
        "hints_ru": [
            "Запустите шаблон: все функции умножают на одно число. Когда лямбда читает `i`: при создании или при вызове? Чему равно `i` после цикла?",
            "Позднее связывание: замыкание хранит имя `i`, а не его значение. Значение нужно «заморозить» в момент создания функции. Есть два способа: значение по умолчанию или отдельная функция-фабрика.",
            "1) Напишите внутреннюю `make(i)`, которая возвращает `lambda x: i * x`. Каждый вызов `make` создаёт свою область видимости. 2) Верните `[make(i) for i in range(n)]`. Другой способ: `lambda x, i=i: i * x`.",
        ],
    },
    "ex-w1-counter": {
        "title": "Замыкание со счётчиком (nonlocal)",
        "statement_ru": d("""\
            Напишите `make_counter(start=0, step=1)`. Она возвращает функцию без аргументов.
            Каждый вызов функции возвращает следующее значение: `start + step`, `start + 2·step`, …
            Глобальные переменные использовать нельзя: два счётчика не должны мешать друг другу."""),
        "starter_code": "def make_counter(start=0, step=1):\n    def tick():\n        start += step\n        return start\n    return tick\n",
        "tests": d('''\
            def test_counts():
                """Значения идут по шагу"""
                c = make_counter()
                assert [c(), c(), c()] == [1, 2, 3]

            def test_start_step():
                """start и step"""
                c = make_counter(10, 5)
                assert [c(), c()] == [15, 20]

            def test_independent():
                """Два счётчика независимы"""
                a, b = make_counter(), make_counter(100)
                a(); a()
                assert b() == 101
                assert a() == 3
            '''),
        "ref": "def make_counter(start=0, step=1):\n    value = start\n    def tick():\n        nonlocal value\n        value += step\n        return value\n    return tick\n",
        "hints_ru": [
            "Запустите шаблон. Какую ошибку вы видите? Вспомните вопрос квиза вторника: что делает присваивание имени внутри функции?",
            "Присваивание `value += step` внутри `tick` делает `value` локальным именем `tick`. Объявление `nonlocal value` говорит Python: это имя из внешней функции. Каждый вызов `make_counter` создаёт свою переменную, поэтому счётчики не мешают друг другу.",
            "1) В `make_counter`: `value = start`. 2) Внутри `tick`: `nonlocal value`, затем `value += step`, затем верните `value`. 3) `make_counter` возвращает `tick` без скобок. Первый вызов даёт `start + step`.",
        ],
    },
    "ex-w1-freeze": {
        "title": "B4: сделать значение hashable",
        "statement_ru": d("""\
            Напишите `freeze(obj)`: превратить вложенную структуру в hashable-значение, чтобы его
            можно было сделать ключом `dict`. Правила:
            - `list` и `tuple` → `tuple` (элементы тоже замораживаются);
            - `set` → `frozenset`;
            - `dict` → `frozenset` пар `(ключ, freeze(значение))`;
            - остальное (`int`, `str`, `None`, …) — как есть."""),
        "starter_code": "def freeze(obj):\n    pass\n",
        "tests": d('''\
            def test_list():
                """Список → кортеж"""
                assert freeze([1, [2, 3]]) == (1, (2, 3))

            def test_set_and_dict():
                """set → frozenset, dict → frozenset пар"""
                assert freeze({1, 2}) == frozenset({1, 2})
                assert freeze({"a": [1]}) == frozenset({("a", (1,))})

            def test_hashable():
                """Результат можно положить в dict"""
                key = freeze({"x": [1, {2, 3}], "y": ({"z": None},)})
                d = {key: "ok"}
                assert d[freeze({"y": ({"z": None},), "x": [1, {3, 2}]})] == "ok"

            def test_scalars():
                """Простые значения не меняются"""
                assert freeze(5) == 5 and freeze("s") == "s" and freeze(None) is None
            '''),
        "ref": d("""\
            def freeze(obj):
                if isinstance(obj, (list, tuple)):
                    return tuple(freeze(x) for x in obj)
                if isinstance(obj, (set, frozenset)):
                    return frozenset(freeze(x) for x in obj)
                if isinstance(obj, dict):
                    return frozenset((k, freeze(v)) for k, v in obj.items())
                return obj
            """),
        "hints_ru": [
            "Внутри списка может лежать словарь, внутри словаря — множество. Сколько уровней вложенности нужно обработать? Можно ли решить задачу для внешнего уровня, если внутренние уже «заморожены»?",
            "Рекурсия по типу объекта: `freeze` вызывает себя для каждого элемента. Тип проверяйте через `isinstance`. База рекурсии — неизменяемые значения (`int`, `str`, `None`): их верните как есть.",
            "1) `list` или `tuple` → `tuple` из `freeze(x)` для каждого `x`. 2) `set` или `frozenset` → `frozenset` из замороженных элементов. 3) `dict` → `frozenset` пар `(k, freeze(v))`. 4) Иначе верните `obj`.",
        ],
    },
    "ex-w1-args": {
        "title": "Аргументы: позиционные, именованные, *args, **kwargs",
        "statement_ru": d("""\
            Напишите `describe(name, /, *tags, sep=", ", **attrs)` — функцию, которая возвращает строку.
            - `name` — только позиционный;
            - `tags` — любое число дополнительных позиционных аргументов;
            - `sep` — только именованный, по умолчанию `", "`;
            - `attrs` — любые другие именованные аргументы.

            Формат: `name`, затем `[tag1, tag2]` (через `sep`), если теги есть, затем `{k=v, …}`
            (через `sep`, ключи по алфавиту), если есть attrs. Части разделяются одним пробелом.
            Пример: `describe("cat", "cute", "small", age=3)` → `"cat [cute, small] {age=3}"`."""),
        "starter_code": "def describe(name, tags, sep, attrs):\n    pass\n",
        "tests": d('''\
            def test_plain():
                """Только имя"""
                assert describe("cat") == "cat"

            def test_tags_and_attrs():
                """Теги и атрибуты"""
                assert describe("cat", "cute", "small", age=3) == "cat [cute, small] {age=3}"
                assert describe("x", b=2, a=1) == "x {a=1, b=2}"

            def test_sep_keyword_only():
                """sep только именованный"""
                assert describe("x", "a", "b", sep="|") == "x [a|b]"
                assert describe("x", "|") == "x [|]", "второй позиционный аргумент — это тег, а не sep"

            def test_name_positional_only():
                """name нельзя передать по имени"""
                try:
                    describe(name="cat")
                except TypeError:
                    return
                raise AssertionError("describe(name=...) должен падать с TypeError")
            '''),
        "ref": d("""\
            def describe(name, /, *tags, sep=", ", **attrs):
                parts = [name]
                if tags:
                    parts.append("[" + sep.join(tags) + "]")
                if attrs:
                    parts.append("{" + sep.join(f"{k}={v}" for k, v in sorted(attrs.items())) + "}")
                return " ".join(parts)
            """),
        "hints_ru": [
            "Посмотрите Tutorial 4.9.3–4.9.5. Какие символы в сигнатуре делают аргумент «только позиционным» и «только именованным»?",
            "`/` после `name` запрещает передать `name` по имени. Всё, что стоит после `*tags`, становится только именованным — поэтому `sep` после `*tags` уже только именованный. `**attrs` собирает остальные именованные аргументы в словарь.",
            "1) Сигнатура: `name, /, *tags, sep=\", \", **attrs`. 2) `parts = [name]`. 3) Теги есть — добавьте `\"[\" + sep.join(tags) + \"]\"`. 4) attrs есть — пары `k=v` из `sorted(attrs.items())` через `sep` в фигурных скобках. 5) Верните `\" \".join(parts)`.",
        ],
    },
    "ex-w1-numgrad": {
        "title": "Численный градиент (мост к backprop)",
        "statement_ru": d("""\
            Напишите `num_grad(f, point, h=1e-5)`. `f` принимает список чисел и возвращает число.
            Верните список частных производных в точке `point` по **центральной разности**:
            `(f(x + h·eᵢ) − f(x − h·eᵢ)) / (2h)` для каждой координаты `i`.
            Не меняйте переданный список `point`."""),
        "starter_code": "def num_grad(f, point, h=1e-5):\n    pass\n",
        "tests": d('''\
            import math

            def close(a, b, tol=1e-4):
                return len(a) == len(b) and all(abs(x - y) < tol for x, y in zip(a, b))

            def test_d1():
                """D1: ∇(x²y + 3y) в (1, 2) ≈ (4, 4)"""
                g = num_grad(lambda p: p[0] ** 2 * p[1] + 3 * p[1], [1.0, 2.0])
                assert close(g, [4, 4]), f"получилось {g}"

            def test_three_vars():
                """∇(x·e^(yz)) в (2, 0, 3) ≈ (1, 6, 0)"""
                g = num_grad(lambda p: p[0] * math.exp(p[1] * p[2]), [2.0, 0.0, 3.0])
                assert close(g, [1, 6, 0]), f"получилось {g}"

            def test_point_unchanged():
                """Точка не меняется"""
                p = [1.0, 2.0]
                num_grad(lambda q: q[0] + q[1], p)
                assert p == [1.0, 2.0], f"point изменился: {p}"

            def test_central_not_forward():
                """Центральная разность точнее прямой"""
                g = num_grad(lambda p: p[0] ** 3, [2.0], h=0.01)
                assert abs(g[0] - 12.0001) < 1e-6, f"для x³ в x=2 при h=0.01 ждём 12.0001, получилось {g[0]}"
            '''),
        "ref": d("""\
            def num_grad(f, point, h=1e-5):
                grad = []
                for i in range(len(point)):
                    plus = list(point)
                    minus = list(point)
                    plus[i] += h
                    minus[i] -= h
                    grad.append((f(plus) - f(minus)) / (2 * h))
                return grad
            """),
        "hints_ru": [
            "Частная производная по координате `i` показывает, как меняется `f`, если двигать только эту координату. Что делать с остальными координатами?",
            "Центральная разность: сдвиньте координату `i` на `+h` и на `−h`, остальные оставьте. Сдвиги делайте на копиях `list(point)`: список изменяемый, и сдвиг на месте испортит `point` (тема понедельника).",
            "1) `grad = []`. 2) Для каждого `i`: `plus = list(point)`, `minus = list(point)`; `plus[i] += h`; `minus[i] -= h`. 3) `grad.append((f(plus) - f(minus)) / (2 * h))`. 4) Верните `grad`.",
        ],
    },
}
