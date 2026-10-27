"""The 13-week plan as data: week -> day -> steps. tools/build_plan.py validates it and writes data/plan.json.

Day template (plan_3_months.md, section 1):
    mon, tue, thu, fri  2.5 h: LeetCode (new problem + review of an old one), theory, quiz, Anki
    wed                 buffer: catch up or rest
    sat                 5 h: practice / project, the 5th problem
    sun                 5 h: review hour, project, questions aloud

LeetCode: new problems p1..p5 go to mon, tue, thu, fri, sat. Reviews ("solve again from scratch after 3 days"):
mon -> previous thu, tue -> previous fri, thu -> mon, fri -> tue, sun -> sat.
"""

START = "2026-10-26"
GITHUB_USER = "fafakaj"
REPO = "ml-notebooks"


def T(topic, do=None, check=None, goals=None, minutes=None, title=None, intro=None):
    s = {"type": "theory", "topic": topic}
    for k, v in (("do", do), ("check", check), ("goals", goals), ("minutes", minutes), ("title", title), ("intro", intro)):
        if v is not None:
            s[k] = v
    return s


def LC(pid, why=None):
    return {"type": "leetcode", "problem": pid, **({"why": why} if why else {})}


def R(pid):
    return {"type": "review", "problem": pid, "why": "Решите задачу заново с нуля, не открывая старое решение."}


def Q(quiz, why=None):
    return {"type": "quiz", "quiz": quiz, **({"why": why} if why else {})}


def ORAL(quiz, why=None):
    return {"type": "oral", "quiz": quiz, **({"why": why} if why else {})}


def EX(ex, minutes=20):
    return {"type": "exercise", "exercise": ex, "minutes": minutes}


def ANKI(deck="ML", intro=None):
    # The site brings new cards by the plan day of their theory (data/anki.json); deck is the Anki deck name.
    return {"type": "anki", "deck": deck, **({"intro": intro} if intro else {})}


def P(title, items, minutes, intro=None, goals=None):
    s = {"type": "practice", "title": title, "minutes": minutes, "items": items}
    if intro:
        s["intro"] = intro
    if goals:
        s["goals"] = goals
    return s


def I(text, topic=None, auto=None, write=False, rows=None):
    """A practice checklist item. write=True adds a text field on the site; the item is done once it is filled in."""
    it = {"text": text}
    if write:
        it["write"] = True
    if rows:
        it["rows"] = rows
    if topic:
        it["topic"] = topic
    if auto:
        it["auto"] = auto
    return it


def gh_repo(repo=REPO):
    return {"kind": "github-repo", "repo": repo}


def gh_file(path, repo=REPO):
    return {"kind": "github-file", "repo": repo, "path": path}


def gh_ci(repo=REPO):
    return {"kind": "github-ci", "repo": repo}


def OPT(text, topic=None):
    return {"text": text, **({"topic": topic} if topic else {})}


CI_ITEMS = [
    I("Запустите локально: `uv run ruff check && uv run ruff format --check && uv run pytest`. Всё зелёное."),
    I("Сделайте коммит и `git push`."),
    I("CI на GitHub зелёный (проверка по последнему запуску на `main`).", auto=gh_ci()),
]

LEETCODE_RULE = ("Решайте сами, без ИИ. Проверка здесь — автотесты на сайте. "
                 "Если застряли, откройте **одну** подсказку. После Accepted можно отправить то же решение на LeetCode.")

WEEKS = [
    # ------------------------------------------------------------------ month 1
    {
        "title": "Python: модель данных. Производные",
        "short": "Python, производные",
        "goal": ("- Ловушки Python (общий список по умолчанию, `[[0] * 3] * 3`, `lambda` в цикле, hashable-ключи `dict`) и градиент f(x, y) = x²y + 3y — ответ без подсказок.\n"
                 "- 4 задачи LeetCode: #217 «Есть ли повтор», #242 «Анаграмма», #1 «Сумма двух», #121 «Купить и продать акцию».\n"
                 "- Тесты на три ловушки (на сайте) и квиз по uv, ruff, pytest, CI."),
        "days": {
            "mon": {
                "title": "Python I: имена, копии, изменяемые значения по умолчанию",
                "intro": "Порядок дня: LeetCode → теория → проверка → Anki. Anki — после теории: сначала поймите, потом запоминайте.",
                "steps": [
                    T("lc-bigo", minutes=10, intro="Перед первой задачей: как оценивать сложность алгоритма.",
                      goals=["оценить сложность цикла и вложенного цикла", "сказать, почему `x in set` — это O(1)"]),
                    LC(217),
                    T("w1-python-mutability", goals=["объяснить разницу `is` и `==`", "сказать, какие типы изменяемые"]),
                    T("w1-python-list-of-lists", do="Запустите `a = [[0]*3]*3; a[0][0] = 1` в Python Tutor и посмотрите на стрелки.",
                      goals=["объяснить, почему `[[0] * 3] * 3` даёт три ссылки на одну строку"]),
                    T("w1-python-copy", goals=["выбрать между `copy.copy` и `copy.deepcopy`"]),
                    T("w1-python-default-args",
                      do="Запишите своими словами 3 фразы: «имя — это…», «`*` для списка…», «default вычисляется…».",
                      goals=["объяснить, почему `def add(x, items=[])` делит один список между вызовами, и исправить через `None`"]),
                    Q("q-w1-names"),
                    EX("ex-w1-b1", 10),
                    EX("ex-w1-b2", 10),
                    ANKI("1 Python", "Пройдите новые карточки по темам дня: Python и оценка сложности."),
                ],
            },
            "tue": {
                "title": "Python II: области видимости, позднее связывание, аргументы, hashable",
                "steps": [
                    T("lc-hash-map", minutes=10, goals=["подсчитать частоты через `dict` и `Counter`"]),
                    LC(242),
                    T("w1-python-scopes", goals=["назвать правило LEGB", "объяснить `UnboundLocalError`"]),
                    T("w1-python-closures", goals=["написать замыкание с `nonlocal`"]),
                    T("w1-python-late-binding", do="Запустите в Python Tutor `funcs = [lambda: i for i in range(3)]; print([f() for f in funcs])`.",
                      goals=["объяснить, почему код печатает `[2, 2, 2]`, и исправить его"]),
                    T("w1-python-args-kwargs", goals=["читать сигнатуру с `/`, `*`, `*args`, `**kwargs`"]),
                    T("w1-python-hashable", goals=["объяснить, почему ключ `dict` должен быть hashable"]),
                    T("w1-python-complexity", do="Запишите своими словами: почему ключом `dict` может быть `tuple`, но не `list`, и какая сложность поиска по ключу.",
                      goals=["назвать сложность `in` для list, set, dict"]),
                    Q("q-w1-scopes"),
                    EX("ex-w1-b3", 10),
                    EX("ex-w1-args", 10),
                    EX("ex-w1-freeze", 10),
                    ANKI("1 Python"),
                ],
            },
            "wed": {
                "title": "Буфер",
                "intro": "Догоняйте или отдыхайте. Отдых — нормальный выбор. Если есть силы, выберите **одно** из списка по порядку.",
                "optional": [
                    OPT("Доделайте теорию пн или вт (долг — в списке слева)."),
                    OPT("wtfpython: «Beware of default mutable arguments!», «A tic-tac-toe where X wins», «Schrödinger's variable», «Hash brownies»."),
                    OPT("Повтор на русском: модель памяти Python.", "w1-python-mutability"),
                    OPT("5-я задача недели #383 «Записка из журнала» — в списке шагов."),
                ],
                "steps": [dict(LC(383), optional=True)],
            },
            "thu": {
                "title": "Математика I: производная и правила",
                "steps": [
                    LC(1),
                    R(217),
                    T("w1-math-3b1b-calc-1"),
                    T("w1-math-3b1b-calc-2", do="Запишите: «производная = отношение малого сдвига выхода к малому сдвигу входа»."),
                    T("w1-math-3b1b-calc-3", do="Выпишите правила: степень, сумма, `eˣ`, `ln x`."),
                    T("w1-math-derivative", goals=["взять производную многочлена, `eˣ`, `ln x`"]),
                    Q("q-w1-math1"),
                    ANKI("2 Математика", "Повторите карточки. Новые — по производной."),
                ],
            },
            "fri": {
                "title": "Математика II: цепное правило, частные производные, градиент",
                "steps": [
                    LC(121),
                    R(242),
                    T("w1-math-3b1b-calc-4"),
                    T("w1-math-chain-rule", goals=["взять производную сигмоиды через цепное правило"]),
                    T("w1-math-partial-gradient", goals=["посчитать градиент функции двух переменных"]),
                    Q("q-w1-math2"),
                    ANKI("2 Математика", "Повторите карточки. Новые — по цепному правилу и градиенту."),
                ],
            },
            "sat": {
                "title": "Практика: инструменты и тесты на ловушки",
                "intro": ("Вся практика — на сайте. Прочитайте про инструменты, ответьте на квиз и напишите тесты на три ловушки: общий список по умолчанию, общие строки матрицы, `lambda` в цикле. "
                          "Сайт проверит, что ваши тесты ловят ошибки."),
                "steps": [
                    T("w1-tools-uv", goals=["знать команды `uv init`, `uv add --dev`, `uv run`"]),
                    T("w1-tools-ruff", goals=["знать правила B006 (изменяемое значение по умолчанию) и B023 (`lambda` в цикле читает переменную цикла)"]),
                    T("w1-tools-pytest", goals=["писать тесты через `assert`", "понимать `parametrize`"]),
                    T("w1-tools-github-actions", goals=["читать простой `ci.yml`"]),
                    Q("q-w1-tools"),
                    EX("ex-w1-counter", 15),
                    EX("ex-w1-tests", 45),
                ],
            },
            "sun": {
                "title": "Повтор и вопросы вслух",
                "intro": "Начните с самопроверки, пока голова свежая.",
                "steps": [
                    Q("q-w1-sunday", "Это проверка недели: ловушки Python, градиент и градиентный спуск без подсказок. Цель — все ответы верны."),
                    EX("ex-w1-numgrad", 20),
                    P("Своими словами: почему ловушки работают так", minutes=30,
                      items=[
                          I("`def add(x, items=[])`: почему список по умолчанию общий для всех вызовов?", write=True),
                          I("Почему `[[0] * 3] * 3` даёт три одинаковые строки?", write=True),
                          I("`[lambda: i for i in range(3)]`: почему все lambda из цикла видят последнее значение?", write=True),
                      ]),
                    ORAL("q-w1-oral", "Отвечайте **вслух**, потом сверьте с образцом. Можно попросить Claude: «задай мне 5 вопросов по ловушкам Python (изменяемый default, список списков, lambda в цикле, hashable) и по градиенту»."),
                ],
            },
        },
    },
    {
        "title": "Python: функции и ООП. Линейная алгебра",
        "short": "ООП, линал",
        "goal": ("- Генераторы, декораторы, GIL, dunder-методы — объясняю без шпаргалки.\n"
                 "- Декоратор с нуля без подсказок.\n"
                 "- 3Blue1Brown «Essence of linear algebra», гл. 1–9.\n"
                 "- 5 задач: #125 «Палиндром», #167 «Сумма двух в отсортированном списке», #88 «Слить два отсортированных списка», #283 «Нули в конец», #169 «Элемент большинства»."),
        "days": {
            "mon": {
                "title": "Генераторы и декораторы",
                "steps": [
                    T("lc-two-pointers", minutes=10, goals=["узнать задачу на два указателя"]),
                    LC(125), R(1),
                    T("w2-python-iterators-generators", goals=["объяснить, чем генератор отличается от списка"]),
                    T("w2-python-decorators", goals=["написать декоратор с `functools.wraps`"]),
                    Q("q-w2-gen"),
                    EX("ex-w2-fib", 15),
                    ANKI(),
                ],
            },
            "tue": {
                "title": "Контекстные менеджеры и исключения",
                "steps": [
                    LC(167), R(121),
                    T("w2-python-context-managers", goals=["написать контекстный менеджер классом и через `contextlib`"]),
                    T("w2-python-exceptions", goals=["использовать `try/except/else/finally` и свои исключения"]),
                    Q("q-w2-deco"),
                    EX("ex-w2-timer", 15),
                    EX("ex-w2-ctx", 20),
                    ANKI(),
                ],
            },
            "wed": {"optional": [OPT("Доделайте долг пн–вт."), OPT("Упражнение «retry» с субботы — заранее.")]},
            "thu": {
                "title": "ООП и GIL",
                "steps": [
                    LC(88), R(125),
                    T("w2-python-classmethod-staticmethod"),
                    T("w2-python-mro-super", goals=["предсказать порядок MRO при множественном наследовании"]),
                    T("w2-python-dunder", goals=["сделать класс с `__repr__`, `__eq__`, `__add__`, `__len__`"]),
                    T("w2-python-dataclasses"),
                    Q("q-w2-oop"),
                    T("w2-python-gil-concurrency", goals=["выбрать между `threading`, `multiprocessing` и `asyncio`"]),
                    Q("q-w2-gil"),
                    EX("ex-w2-vector", 20),
                    ANKI(),
                ],
            },
            "fri": {
                "title": "Линейная алгебра I: векторы и матрицы (гл. 1–5)",
                "steps": [
                    LC(283), R(167),
                    T("w2-math-la-ch1"), T("w2-math-la-ch2"), T("w2-math-la-ch3"), T("w2-math-la-ch4"), T("w2-math-la-ch5"),
                    Q("q-w2-linalg1"),
                    ANKI(),
                ],
            },
            "sat": {
                "title": "Линейная алгебра II и практика",
                "steps": [
                    T("lc-majority", minutes=10),
                    LC(169),
                    T("w2-math-la-ch6"), T("w2-math-la-ch7"), T("w2-math-la-ch8"), T("w2-math-la-ch9"), T("w2-math-la-ch14"),
                    Q("q-w2-linalg2"),
                    EX("ex-w2-retry", 20),
                    EX("ex-w2-dataclass", 20),
                ],
            },
            "sun": {
                "title": "Повтор и проверка недели",
                "steps": [
                    R(169),
                    EX("ex-w2-deco10", 10),
                    Q("q-w2-bench", "Проверка недели: объясните замер потоков и процессов."),
                ],
            },
        },
    },
    {
        "title": "Теорвер, статистика, NumPy, pandas",
        "short": "Теорвер, NumPy",
        "goal": ("- Задачи на формулу Байеса (тест на болезнь) и на p-value — решаю без подсказок.\n"
                 "- NumPy: векторизация и broadcasting; pandas: groupby, merge, pivot.\n"
                 "- Разобран свой хакатон: EDA своими руками и рассказ на 3 минуты."),
        "days": {
            "mon": {
                "title": "Вероятность, Байес, матожидание",
                "steps": [
                    T("lc-stack", minutes=10), LC(20), R(88),
                    T("w3-math-probability"),
                    T("w3-math-conditional-bayes", goals=["решить задачу на формулу Байеса"]),
                    T("w3-math-expectation-variance", goals=["посчитать матожидание и дисперсию"]),
                    Q("q-w3-prob"),
                    EX("ex-w3-bayes", 15),
                    ANKI(),
                ],
            },
            "tue": {
                "title": "Распределения, ЦПТ, гипотезы",
                "steps": [
                    T("lc-binary-search", minutes=10), LC(704), R(283),
                    T("w3-math-distributions"), T("w3-math-clt"),
                    T("w3-math-hypotheses-pvalue", goals=["объяснить p-value одной фразой без ошибки"]),
                    Q("q-w3-stats"),
                    ANKI(),
                ],
            },
            "wed": {"optional": [OPT("Доделайте долг пн–вт."), OPT("NumPy-тренировка: `rougier/numpy-100`, задачи 1–40 (в Jupyter или в Python у себя).", "w3-tools-numpy")]},
            "thu": {
                "title": "NumPy: векторизация и broadcasting",
                "steps": [
                    T("lc-dp-1d", minutes=10), LC(70), R(20),
                    T("w3-tools-numpy"),
                    T("w3-tools-numpy-broadcasting", goals=["предсказать форму результата broadcasting"]),
                    Q("q-w3-numpy"),
                    EX("ex-w3-softmax", 15),
                    EX("ex-w3-pairwise", 15),
                    ANKI(),
                ],
            },
            "fri": {
                "title": "pandas, графики, Jupyter",
                "steps": [
                    T("lc-linked-list", minutes=10), LC(206), R(704),
                    T("w3-tools-pandas"), T("w3-tools-matplotlib-seaborn"), T("w3-tools-jupyter"),
                    Q("q-w3-pandas"),
                    EX("ex-w3-zscore", 15),
                    EX("ex-w3-pandas", 20),
                    ANKI(),
                ],
            },
            "sat": {
                "title": "Bash и EDA",
                "steps": [
                    LC(21),
                    T("w3-tools-bash"), Q("q-w3-bash"),
                    EX("ex-w3-eda", 40),
                    P("Разбор хакатона", minutes=90,
                      intro="Возьмите один ваш хакатон (например, Cosmohackathon, 3 место). Ответьте письменно здесь, своими словами.",
                      items=[
                          I("Задача: что нужно было сделать?", write=True, rows=3),
                          I("Данные: что было на входе, сколько, какие проблемы?", write=True, rows=3),
                          I("Метрика: как оценивали решение и почему именно так?", write=True, rows=3),
                          I("Что сделала команда?", write=True, rows=3),
                          I("Что сделали вы лично? Цифры: метрика до и после, место.", write=True, rows=3),
                      ]),
                ],
            },
            "sun": {
                "title": "Повтор, хакатон, вопросы вслух",
                "steps": [
                    R(21),
                    P("Хакатон за 3 минуты", minutes=30,
                      items=[
                          I("Расскажите хакатон за 3 минуты (другу или на диктофон): задача → данные → метрика → подход → ваш вклад → результат."),
                          I("Что бы вы сделали иначе сейчас?", write=True, rows=3),
                      ]),
                    ORAL("q-w3-oral"),
                ],
            },
        },
    },
    {
        "title": "Основы ML, SQL",
        "short": "Основы ML, SQL",
        "goal": ("- Линейная и логистическая регрессия на NumPy: веса ≈ `sklearn`.\n"
                 "- SQL: SQLBolt + 5 задач LeetCode SQL 50.\n"
                 "- Мок №1 с другом. Контрольная точка 22.11: части B, D, E теста ≥ 70%."),
        "days": {
            "mon": {
                "title": "Что такое ML, переобучение",
                "steps": [
                    T("lc-sliding-window", minutes=10), LC(3), R(70),
                    T("w4-ml-intro"),
                    T("w4-ml-train-val-test-overfitting", goals=["объяснить, зачем нужна валидационная выборка"]),
                    T("w4-ml-bias-variance"),
                    ANKI(),
                ],
            },
            "tue": {
                "title": "Линейная регрессия и градиентный спуск",
                "steps": [
                    LC(219), R(206),
                    T("w4-ml-linear-regression"), T("w4-math-gradient-descent"),
                    T("w4-ml-regularization", goals=["сравнить L1 и L2"]),
                    Q("q-w4-ml1"),
                    EX("ex-w4-linreg", 30),
                    ANKI(),
                ],
            },
            "wed": {"optional": [OPT("Доделайте долг пн–вт."), OPT("SQLBolt: уроки 1–6 заранее.", "w4-sql-basics")]},
            "thu": {
                "title": "Логистическая регрессия и метрики",
                "steps": [
                    LC(567), R(3),
                    T("w4-ml-logistic-regression"),
                    T("w4-ml-metrics", goals=["выбрать метрику для несбалансированных классов"]),
                    EX("ex-w4-logreg", 30),
                    EX("ex-w4-metrics", 20),
                    ANKI(),
                ],
            },
            "fri": {
                "title": "Кросс-валидация, утечки, kNN и k-means",
                "steps": [
                    LC(392), R(219),
                    T("w4-ml-cross-validation", goals=["объяснить StratifiedKFold"]),
                    T("w4-ml-leakage", goals=["найти утечку в пайплайне"]),
                    T("w4-ml-knn-vs-kmeans", goals=["отличить kNN от k-means"]),
                    Q("q-w4-ml2"),
                    EX("ex-w4-kfold", 20),
                    ANKI(),
                ],
            },
            "sat": {
                "title": "SQL",
                "steps": [
                    LC(205),
                    T("w4-sql-basics", do="Пройдите все уроки SQLBolt."),
                    Q("q-w4-sql"),
                    EX("ex-w4-sql-select", 10),
                    EX("ex-w4-sql-null", 10),
                    EX("ex-w4-sql-join", 15),
                    EX("ex-w4-sql-case", 15),
                    EX("ex-w4-sql", 15),
                ],
            },
            "sun": {
                "title": "Контрольная точка и мок №1",
                "steps": [
                    R(205),
                    Q("q-w4-checkpoint", "Контрольная точка месяца 1. Цель — ≥ 70% верно с первой попытки."),
                    ORAL("q-w4-oral", "Мок №1 с другом: Python + основы ML. Друг задаёт вопросы, вы отвечаете вслух."),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ month 2
    {
        "title": "Деревья, ансамбли, бустинг. Старт Проекта №1",
        "short": "Бустинг, Kaggle",
        "goal": ("- Объясняю бэггинг и бустинг, разницу CatBoost / LightGBM / XGBoost.\n"
                 "- Проект №1: Kaggle Playground, EDA, бейзлайн, CatBoost, первая отправка.\n"
                 "- SQL: 5 задач на JOIN, GROUP BY, HAVING."),
        "days": {
            "mon": {"title": "Решающие деревья", "steps": [
                T("lc-intervals", minutes=10), LC(56), R(567),
                T("w5-ml-decision-trees", goals=["посчитать Gini для разбиения"]), ANKI()]},
            "tue": {"title": "Random Forest, бэггинг и бустинг", "steps": [
                T("lc-group-anagrams", minutes=10), LC(49), R(392),
                T("w5-ml-bagging-rf"), T("w5-ml-bagging-vs-boosting", goals=["объяснить разницу бэггинга и бустинга"]), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт."), OPT("Выберите соревнование Kaggle Playground заранее.")]},
            "thu": {"title": "Градиентный бустинг", "steps": [
                T("lc-heap-top-k", minutes=10), LC(347), R(56),
                T("w5-ml-gradient-boosting"), ANKI()]},
            "fri": {"title": "CatBoost, LightGBM, XGBoost, стекинг", "steps": [
                LC(57), R(49),
                T("w5-ml-boosting-libraries"), T("w5-ml-stacking"), ANKI()]},
            "sat": {"title": "SQL и старт Проекта №1", "steps": [
                LC(435),
                T("w5-sql-join-groupby", do="Решите 5 задач LeetCode SQL 50 на JOIN, GROUP BY, HAVING."),
                P("Проект №1: EDA и бейзлайн", minutes=180,
                  intro="Проект №1 — табличные данные Kaggle Playground → прод. Отдельный публичный репозиторий.",
                  items=[
                      I("Выберите текущее соревнование Kaggle Playground. Создайте репозиторий проекта."),
                      I("EDA: целевая переменная, пропуски, категориальные признаки."),
                      I("Бейзлайн `sklearn` с честной кросс-валидацией. Запишите CV-скор."),
                  ])]},
            "sun": {"title": "Проект №1: CatBoost и первая отправка", "steps": [
                R(435),
                P("Проект №1: CatBoost", minutes=180,
                  items=[
                      I("CatBoost с K-Fold. Запишите CV-скор."),
                      I("Первая отправка на Kaggle. Запишите место на лидерборде."),
                      I("CV-скор и лидерборд расходятся не сильно? Если сильно — ищите утечку."),
                  ])]},
        },
    },
    {
        "title": "Подбор гиперпараметров, SHAP, A/B — основы",
        "short": "Optuna, SHAP, A/B",
        "goal": "- Проект №1: Optuna, K-Fold, SHAP, MLflow, финальная отправка.\n- **Kaggle — топ-50%** (стретч — топ-30%).\n- SQL: 5 задач на оконные функции.",
        "days": {
            "mon": {"title": "Optuna", "steps": [
                T("lc-prefix-suffix", minutes=10), LC(238), R(347), T("w6-ml-optuna"), ANKI()]},
            "tue": {"title": "Feature importance и SHAP", "steps": [
                T("lc-3sum", minutes=10), LC(15), R(57), T("w6-ml-feature-importance-shap"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "Кластеризация и PCA", "steps": [
                T("lc-fast-slow-pointers", minutes=10), LC(141), R(238),
                T("w6-ml-clustering"), T("w6-ml-pca"), ANKI()]},
            "fri": {"title": "A/B-тесты и продуктовые метрики", "steps": [
                LC(11), R(15),
                T("w6-ab-tests", goals=["объяснить p-value и мощность теста"]), T("w6-product-metrics"), T("w6-pricing"), ANKI()]},
            "sat": {"title": "SQL окна и MLflow", "steps": [
                LC(128),
                T("w6-sql-window", do="Решите 5 задач LeetCode SQL 50 на оконные функции."),
                T("w6-tools-mlflow"),
                P("Проект №1: Optuna и MLflow", minutes=150, items=[
                    I("Optuna для CatBoost / LightGBM на K-Fold."),
                    I("Логируйте эксперименты в MLflow."),
                ])]},
            "sun": {"title": "Проект №1: SHAP и финальная отправка", "steps": [
                R(128),
                P("Проект №1: финал на Kaggle", minutes=180, items=[
                    I("SHAP: топ-10 признаков и вывод в README."),
                    I("Финальная отправка. **Топ-50%** лидерборда (стретч — топ-30%). Запишите место."),
                ])]},
        },
    },
    {
        "title": "Проект №1 в прод. Резюме",
        "short": "Прод, резюме",
        "goal": "- Проект №1: `/predict`, Dockerfile, CI, README, `DECISIONS.md`, релиз v1.0.\n- Резюме v1, hh.ru, LinkedIn.\n- **Друг запускает проект по README** без подсказок.",
        "days": {
            "mon": {"title": "FastAPI", "steps": [
                T("lc-tree-dfs", minutes=10), LC(226), R(141), T("w7-fastapi"), ANKI()]},
            "tue": {"title": "Pydantic", "steps": [LC(104), R(11), T("w7-pydantic"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "Docker", "steps": [
                LC(100), R(226),
                T("w7-docker-image-container", goals=["объяснить разницу образа и контейнера"]), T("w7-docker-compose"), ANKI()]},
            "fri": {"title": "CI и git", "steps": [
                LC(572), R(104),
                T("w7-github-actions-ci"), T("w7-git-rebase-reset", goals=["объяснить `rebase` и три режима `reset`"]), ANKI()]},
            "sat": {"title": "Проект №1 в прод", "steps": [
                LC(543), T("w7-linux-basics"),
                P("Проект №1: API, Docker, CI", minutes=200, items=[
                    I("FastAPI `/predict` с Pydantic-схемой и тестом."),
                    I("Dockerfile. `docker run` отдаёт предсказание."),
                    I("GitHub Actions: lint, test, build образа."),
                    I("README с таблицей моделей, `DECISIONS.md`. Релиз v1.0."),
                ])]},
            "sun": {"title": "Резюме и проверка недели", "steps": [
                R(543), T("w7-career-resume"),
                P("Резюме и проверка", minutes=180, items=[
                    I("Резюме v1: Проект №1 и разобранный хакатон, с цифрами."),
                    I("Профили hh.ru и LinkedIn."),
                    I("**Друг запускает проект по README** без ваших подсказок."),
                ])]},
        },
    },
    {
        "title": "Нейросети и PyTorch",
        "short": "PyTorch",
        "goal": "- micrograd: градиенты = `torch.autograd`.\n- Trainer на PyTorch, Fashion-MNIST на RTX 4050.\n- Мок №2. Объясняю бустинг, переобучение и backprop без шпаргалки.",
        "days": {
            "mon": {"title": "Нейрон, MLP, loss", "steps": [
                T("lc-tree-bfs", minutes=10), LC(102), R(100),
                T("w8-dl-neuron-mlp-activations"), T("w8-dl-loss"), ANKI()]},
            "tue": {"title": "Backprop и micrograd", "steps": [
                T("lc-bst", minutes=10), LC(98), R(572),
                T("w8-dl-backprop", goals=["посчитать backprop для двух нейронов вручную"]), T("w8-karpathy-micrograd"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт."), OPT("Допишите micrograd.")]},
            "thu": {"title": "PyTorch: цикл обучения и оптимизаторы", "steps": [
                LC(215), R(102),
                T("w8-pytorch-training-loop", goals=["объяснить `zero_grad`, `backward`, `step`"]),
                T("w8-dl-optimizers"), T("w8-dl-learning-rate"), ANKI()]},
            "fri": {"title": "Нормализация, dropout, RNN", "steps": [
                LC(230), R(98),
                T("w8-dl-normalization"), T("w8-dl-dropout"), T("w8-dl-rnn-lstm"), ANKI()]},
            "sat": {"title": "micrograd и Trainer", "steps": [
                LC(1046), T("w8-karpathy-makemore"),
                P("micrograd и Trainer в ml-notebooks", minutes=180, items=[
                    I("micrograd с нуля. Тест: градиенты = `torch.autograd`.", auto=gh_file("tests/test_micrograd.py")),
                    I("Trainer на PyTorch: Fashion-MNIST на RTX 4050. Точность в README."),
                    *CI_ITEMS,
                ])]},
            "sun": {"title": "Мок №2 и контрольная точка", "steps": [
                R(1046),
                P("Мок №2 и контрольная точка 20.12", minutes=120, items=[
                    I("Мок №2 с другом: классический ML + Проект №1."),
                    I("Объясните вслух без шпаргалки: бустинг, переобучение, backprop."),
                ])]},
        },
    },
    # ------------------------------------------------------------------ month 3
    {
        "title": "CV, эмбеддинги, токенизация",
        "short": "CV, BPE",
        "goal": "- Fine-tune модели из `timm` на малом датасете.\n- BPE с нуля совпадает с эталоном.\n- Отклики: 5 в неделю.",
        "days": {
            "mon": {"title": "Свёртки", "steps": [
                T("lc-graph-bfs-dfs", minutes=10), LC(200), R(215), T("w9-dl-cnn"), ANKI()]},
            "tue": {"title": "ResNet и transfer learning", "steps": [
                LC(733), R(230), T("w9-dl-resnet"), T("w9-dl-transfer-learning"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "Эмбеддинги и CLIP", "steps": [
                T("lc-dp-coin-change", minutes=10), LC(322), R(200),
                T("w9-embeddings-cosine"), T("w9-clip"), ANKI()]},
            "fri": {"title": "Токенизация BPE", "steps": [
                LC(695), R(733), T("w9-bpe-tokenization", goals=["объяснить шаг слияния BPE"]), ANKI()]},
            "sat": {"title": "timm и BPE", "steps": [
                LC(994), T("w9-tools-timm"),
                P("Практика: timm и BPE", minutes=200, items=[
                    I("Fine-tune модели из `timm` на малом датасете (RTX 4050). Точность в README."),
                    I("BPE с нуля. Тест: совпадает с эталонным токенизатором на тестовом тексте.", auto=gh_file("tests/test_bpe.py")),
                    *CI_ITEMS,
                ])]},
            "sun": {"title": "Отклики и повтор", "steps": [
                R(994),
                P("Карьера: отклики", minutes=60, items=[I("5 откликов на стажировки и Junior. Запишите, куда.")])]},
        },
    },
    {
        "title": "Transformer и LLM изнутри. Старт Проекта №2",
        "short": "Transformer",
        "goal": "- Ваш attention ≈ `scaled_dot_product_attention`.\n- nanoGPT + KV-кэш.\n- Проект №2: бейзлайны TF-IDF + LogReg и `rubert-tiny2`.\n\nНовогодняя неделя — можно сдвинуть, но не пропускать.",
        "days": {
            "mon": {"title": "Attention", "steps": [
                LC(198), R(322), T("w10-attention", goals=["написать softmax(QKᵀ/√d)·V"]), ANKI()]},
            "tue": {"title": "Маска, multi-head, позиции", "steps": [
                T("lc-topological-sort", minutes=10), LC(207), R(695),
                T("w10-attention-mask-multihead"), T("w10-positional-encoding"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "BERT и GPT", "steps": [
                LC(213), R(198), T("w10-bert-vs-gpt"), T("w10-3b1b-transformers"), ANKI()]},
            "fri": {"title": "KV-кэш и сэмплирование", "steps": [
                LC(210), R(207), T("w10-kv-cache"), T("w10-sampling"), ANKI()]},
            "sat": {"title": "nanoGPT", "steps": [
                LC(62), T("w10-karpathy-gpt"),
                P("nanoGPT + KV-кэш", minutes=200, items=[
                    I("nanoGPT по видео Karpathy."),
                    I("Тест: ваш attention ≈ `F.scaled_dot_product_attention`.", auto=gh_file("tests/test_attention.py")),
                    I("KV-кэш: генерация с кэшем даёт те же токены, но быстрее."),
                    *CI_ITEMS,
                ])]},
            "sun": {"title": "Проект №2: бейзлайны", "steps": [
                R(62), T("w10-baseline-tfidf"), T("w10-baseline-rubert-tiny2"),
                P("Проект №2: бейзлайны", minutes=150, items=[
                    I("Датасет интентов (Bitext или русский). Репозиторий Проекта №2."),
                    I("TF-IDF + LogReg: F1 в таблицу."),
                    I("`rubert-tiny2` fine-tune: F1 в таблицу."),
                ])]},
        },
    },
    {
        "title": "Дообучение и эффективность",
        "short": "LoRA, квантизация",
        "goal": "- LoRA и QLoRA для Qwen ~0,5B.\n- Таблица инференса: F1, память, токенов/с. Релиз v1.0.\n- Пиковая память совпадает с расчётом ±20%. Мок №3 с Claude.",
        "days": {
            "mon": {"title": "Fine-tuning и SFT", "steps": [LC(33), R(213), T("w11-sft-fine-tuning"), ANKI()]},
            "tue": {"title": "LoRA и QLoRA", "steps": [LC(153), R(210), T("w11-lora-qlora", goals=["посчитать число параметров LoRA"]), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "Память обучения и точность", "steps": [
                LC(739), R(33), T("w11-training-memory"), T("w11-mixed-precision"), ANKI()]},
            "fri": {"title": "Квантизация", "steps": [LC(39), R(153), T("w11-quantization"), ANKI()]},
            "sat": {"title": "Проект №2: LoRA", "steps": [
                LC(300), T("w11-inference-batching-vllm"),
                P("Проект №2: LoRA и QLoRA", minutes=200, items=[
                    I("Посчитайте пиковую память обучения заранее (веса + градиенты + Adam)."),
                    I("LoRA и QLoRA для Qwen ~0,5B на RTX 4050. Пиковая память ±20% от расчёта."),
                ])]},
            "sun": {"title": "Проект №2: инференс и мок №3", "steps": [
                R(300),
                P("Проект №2: инференс и релиз", minutes=200, items=[
                    I("Инференс FP16 vs NF4 vs llama.cpp (GGUF). Таблица: F1, память, задержка, токенов/с."),
                    I("README, релиз v1.0."),
                    I("Мок №3 с Claude: секция 2 из письма HR, упрощённо."),
                ])]},
        },
    },
    {
        "title": "RAG и агенты",
        "short": "RAG, агенты",
        "goal": "- Проект №3: RAG-агент, малая версия. 30 вопросов.\n- Реранкер повышает Recall@5.",
        "days": {
            "mon": {"title": "RAG и чанкинг", "steps": [
                LC(155), R(739), T("w12-rag-overview"), T("w12-rag-chunking"), ANKI()]},
            "tue": {"title": "Семантический поиск и HNSW", "steps": [
                LC(875), R(39), T("w12-semantic-search"), T("w12-vector-db-hnsw"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "Гибридный поиск и реранкер", "steps": [
                LC(19), R(155), T("w12-hybrid-search"), T("w12-reranker"), ANKI()]},
            "fri": {"title": "Tool calling, агенты, MCP", "steps": [
                LC(74), R(875), T("w12-tool-calling"), T("w12-agents"), T("w12-mcp"), ANKI()]},
            "sat": {"title": "Проект №3: RAG", "steps": [
                LC(53), T("w12-rag-evaluation"), T("w12-ranking-metrics"),
                P("Проект №3: RAG-агент", minutes=180, items=[
                    I("Qdrant + эмбеддинги: индекс документации."),
                    I("30 вопросов с правильными чанками. Recall@5 без реранкера."),
                ])]},
            "sun": {"title": "Проект №3: реранкер и агент", "steps": [
                R(53),
                P("Проект №3: реранкер и агент", minutes=200, items=[
                    I("Реранкер. Recall@5 после — выше, чем до."),
                    I("Claude API + tool calling. README с таблицей метрик."),
                ])]},
        },
    },
    {
        "title": "Собеседования",
        "short": "Собеседования",
        "goal": "- Рассказ о каждом хакатоне и проекте — 3 мин, с цифрами.\n- Моки: секция 1 и секция 2.\n- Резюме v2. Повторный входной тест ≥ 80%.",
        "days": {
            "mon": {"title": "Рассказы по STAR", "steps": [
                LC(146), R(19), T("w13-star"),
                P("Рассказы о проектах", minutes=60, items=[
                    I("Каждый хакатон и проект: задача → данные → метрика → подход → что сделал я → результат в цифрах → что сделал бы иначе."),
                    I("3 мин на рассказ. Запишите на диктофон."),
                ]), ANKI()]},
            "tue": {"title": "Подготовка к собеседованию", "steps": [
                LC(5), R(74), T("w13-interview-prep"), ANKI()]},
            "wed": {"optional": [OPT("Доделайте долг пн–вт.")]},
            "thu": {"title": "ML-вопросы", "steps": [
                T("w13-ml-interview-questions"),
                {**LC(78)}, R(146), ANKI()]},
            "fri": {"title": "Резюме v2", "steps": [
                R(5),
                P("Резюме v2 и сайт", minutes=90, items=[
                    I("Резюме v2: все проекты с цифрами."),
                    I("Обновите сайт: в описании хакатонов — ваш вклад и метрики."),
                ]), ANKI()]},
            "sat": {"title": "Моки", "steps": [
                R(78),
                P("Моки секции 1 и 2", minutes=240, items=[
                    I("Мок секции 1 (2 задачи + вопросы по Python) с другом."),
                    I("Мок секции 2 (LLM) с Claude."),
                ])]},
            "sun": {"title": "Итоговая проверка", "steps": [
                P("Итоговые критерии 24.01", minutes=240,
                  intro="Раздел 5 плана. Отметьте только то, что выполнено по-честному.",
                  items=[
                      I("Перепройдите весь `test_week0.md`. ≥ 80% верно."),
                      I("LeetCode: ~60 задач; новые Easy за 15 мин — 80%, новые Medium за 30 мин — 50%."),
                      I("Kaggle Playground: топ-50%."),
                      I("Мок с живым человеком: ≥ 4/5 по вопросам уровня Junior."),
                      I("Проекты: друг запускает по README; тесты «с нуля vs библиотека» проходят."),
                      I("Anki: ≥ 85% верных повторений."),
                  ])]},
        },
    },
]

# A week is done in three blocks, not day by day: the user picks the days.
# Block 1 = mon + tue (+ the optional wed steps), block 2 = thu + fri, block 3 = sat + sun.
BLOCK_TITLES = [
    ["Python: имена, копии, области видимости", "Математика: производная и градиент", "Инструменты, тесты, самопроверка"],
    ["Генераторы, декораторы, исключения", "ООП, GIL, векторы и матрицы", "Линейная алгебра II, проверка недели"],
    ["Вероятность, статистика", "NumPy и pandas", "Bash, EDA, разбор хакатона"],
    ["Основы ML, линейная регрессия", "Логистическая регрессия, метрики, CV", "SQL, контрольная точка, мок №1"],
    ["Деревья, бэггинг и бустинг", "Градиентный бустинг, библиотеки", "SQL и старт Проекта №1"],
    ["Optuna и SHAP", "Кластеризация, PCA, A/B", "SQL-окна, MLflow, финал Kaggle"],
    ["FastAPI и Pydantic", "Docker, CI, git", "Проект №1 в прод, резюме"],
    ["Нейрон, loss, backprop", "PyTorch, оптимизаторы, нормализация", "micrograd, Trainer, мок №2"],
    ["Свёртки, ResNet", "Эмбеддинги, CLIP, BPE", "timm, BPE, отклики"],
    ["Attention, маска, позиции", "BERT и GPT, KV-кэш, сэмплирование", "nanoGPT, Проект №2"],
    ["Fine-tuning, LoRA", "Память, точность, квантизация", "Проект №2: LoRA и инференс"],
    ["RAG, чанкинг, поиск", "Реранкер, агенты, MCP", "Проект №3: RAG-агент"],
    ["Рассказы и подготовка", "ML-вопросы, резюме v2", "Моки и итоговая проверка"],
]
BLOCK_DAYS = [("mon", "tue", "wed"), ("thu", "fri"), ("sat", "sun")]
