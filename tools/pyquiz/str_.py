"""str: complexity (measured: the TimeComplexity wiki has no str table) and methods (checked by asserts)."""

from . import O1, OLOG, ON, ON2, ONLOG, STD

STR_SRC = STD + "#string-methods"
UNICODE_C = "https://github.com/python/cpython/blob/main/Objects/unicodeobject.c"
FASTSEARCH = "https://github.com/python/cpython/blob/main/Objects/stringlib/fastsearch.h"
NS = [20000, 40000, 80000, 160000, 320000]

TOPICS = [
    {"id": "str-o", "title": "str: сложность", "group": "Асимптотика и методы"},
    {"id": "str-m", "title": "str: методы", "group": "Асимптотика и методы"},
]

_IMM = "str в Python неизменяемая: любой метод, который «меняет» строку, создаёт новую и копирует в неё символы. "


def _t(setup, stmt, cls, ns=NS):
    return {"setup": setup, "stmt": stmt, "ns": ns, "cls": cls}


QUESTIONS = [
    # ------------------------------------------------------------------ complexity
    {
        "id": "str-o-len", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `len(s)` для строки из n символов?",
        "options": [ON, O1, OLOG, ONLOG], "answer": 1, "measure": _t("s = 'a' * n", "len(s)", "1"),
        "why": "Длина хранится в заголовке объекта строки и задаётся при создании (строка неизменяема, длина не меняется). len читает это поле.",
        "wrong": {
            "0": "Так было бы у строки C с нулём в конце (strlen). Строка Python знает свою длину заранее.",
            "2": "Ничего не ищется: длина — готовое число в объекте.",
            "3": "Никакой сортировки или перебора нет — только чтение поля.",
        },
        "src": [STD + "#text-sequence-type-str", UNICODE_C],
    },
    {
        "id": "str-o-index", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s[i]` для строки из n символов?",
        "options": [O1, ON, OLOG, "O(i)"], "answer": 0, "measure": _t("s = 'a' * n", "s[n // 2]", "1"),
        "why": "CPython хранит строку массивом символов одинаковой ширины: 1, 2 или 4 байта на символ (PEP 393). "
               "Поэтому адрес i-го символа вычисляется сразу, без прохода по строке, даже для кириллицы и эмодзи.",
        "wrong": {
            "1": "O(n) было бы при хранении в UTF-8 с переменной шириной символа. CPython выбирает одну ширину на всю строку.",
            "2": "Ничего не ищется: позиция считается одной формулой.",
            "3": "O(i) — снова переменная ширина символов, как в UTF-8. PEP 393 даёт одинаковую ширину.",
        },
        "src": ["https://peps.python.org/pep-0393/"],
    },
    {
        "id": "str-o-in", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько в типичном случае стоит `sub in s`, где `sub` — короткая строка (длина много меньше n)?",
        "options": [O1, OLOG, ON, ON2], "answer": 2, "measure": _t("s = 'a' * n", "'ab' in s", "n"),
        "why": "Поиск подстроки идёт по s слева направо (алгоритм fastsearch: смесь Бойера — Мура и Хорспула, для длинных образцов — двусторонний алгоритм). "
               "Если подстроки нет, приходится просмотреть всю s, поэтому O(n). Хеш-индекса по подстрокам у строки нет.",
        "wrong": {
            "0": "O(1) — у set и dict. У строки нет индекса подстрок, и её нужно просмотреть.",
            "1": "Бинарный поиск по строке невозможен: символы не упорядочены.",
            "3": "Наивный поиск мог бы дать O(n·m), но для короткой подстроки это всё равно O(n), а CPython к тому же пропускает куски строки.",
        },
        "src": [FASTSEARCH],
    },
    {
        "id": "str-o-join", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `''.join(parts)`, где суммарная длина частей — n?",
        "options": [ON, ON2, ONLOG, O1], "answer": 0, "measure": _t("parts = ['a'] * n", "''.join(parts)", "n"),
        "why": "join сначала проходит по частям и считает итоговую длину, потом один раз выделяет память и копирует символы. "
               "Каждый символ копируется ровно один раз — O(n). Поэтому join — правильный способ собрать строку из многих кусков.",
        "wrong": {
            "1": "O(n²) даёт наивная склейка res = res + part в цикле: каждая склейка копирует всё накопленное. join копирует один раз.",
            "2": "join не сортирует и не сравнивает части.",
            "3": "Нужно скопировать n символов, за константу не выйдет.",
        },
        "src": [STR_SRC + "#str.join"],
    },
    {
        "id": "str-o-concat-loop", "topic": "str-o", "type": "choice",
        "q": "Почему для сборки строки из n кусков советуют `''.join(parts)`, а не `s += part` в цикле?",
        "options": [
            "Строка неизменяема: += в общем случае копирует всё накопленное, это O(n²) на весь цикл; CPython иногда дописывает на месте, но это не гарантия",
            "+= не работает со строками",
            "join быстрее только для чисел",
            "Разницы нет: += в Python всегда O(1)",
        ],
        "answer": 0,
        "why": _IMM + "Поэтому s += part в общем случае создаёт новую строку длины |s| + |part|, и цикл копирует 1 + 2 + … + n символов — O(n²). "
               "CPython умеет дописывать на месте, если на строку нет других ссылок, но PEP 8 прямо просит не полагаться на это: в PyPy и в других случаях оптимизации нет.",
        "wrong": {
            "1": "+= для строк работает, вопрос только в скорости на длинных циклах.",
            "2": "join принимает только строки; числа сначала нужно превратить: ''.join(map(str, nums)).",
            "3": "O(1) для += не гарантировано: это деталь CPython, которая срабатывает не всегда.",
        },
        "src": ["https://peps.python.org/pep-0008/#programming-recommendations"],
    },
    {
        "id": "str-o-replace", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s.replace('a', 'b')` для строки из n символов?",
        "options": [O1, ON, ON2, OLOG], "answer": 1, "measure": _t("s = 'ab' * (n // 2)", "s.replace('a', 'c')", "n"),
        "why": _IMM + "replace находит вхождения за один проход и строит новую строку из n символов. Каждый символ просматривается и копируется константное число раз.",
        "wrong": {
            "0": "Даже если заменять нечего, строку нужно просмотреть, чтобы это узнать.",
            "2": "Каждая замена не копирует всю строку заново: результат собирается за один проход.",
            "3": "Логарифму неоткуда взяться: строка просматривается целиком.",
        },
        "src": [STR_SRC + "#str.replace"],
    },
    {
        "id": "str-o-split", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s.split(',')` для строки из n символов?",
        "options": [ON, ON2, ONLOG, O1], "answer": 0, "measure": _t("s = 'a,' * (n // 2)", "s.split(',')", "n"),
        "why": "split идёт по строке один раз, находит разделители и копирует куски в новые строки. Суммарно копируется не больше n символов, плюс создаётся список частей — O(n).",
        "wrong": {
            "1": "Каждый кусок копируется один раз, повторных проходов по строке нет.",
            "2": "O(n log n) — это сортировка, а split только режет строку по порядку, ничего не сравнивая.",
            "3": "Нужно найти все разделители — это проход по n символам.",
        },
        "src": [STR_SRC + "#str.split"],
    },
    {
        "id": "str-o-reverse", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s[::-1]`?",
        "options": [O1, OLOG, ON, ONLOG], "answer": 2, "measure": _t("s = 'a' * n", "s[::-1]", "n"),
        "why": _IMM + "Срез с шагом −1 создаёт новую строку и копирует в неё все n символов в обратном порядке.",
        "wrong": {
            "0": "Ленивое «представление» без копии дал бы reversed(s) — но это итератор, а не строка. Срез копирует.",
            "1": "Каждый символ нужно переписать, логарифм тут невозможен.",
            "3": "Разворот не сравнивает символы, сортировки нет.",
        },
        "src": [STD + "#common-sequence-operations"],
    },
    {
        "id": "str-o-eq", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько в худшем случае стоит `s == t` для двух разных объектов-строк длины n?",
        "options": [O1, ON, OLOG, ON2], "answer": 1,
        "measure": _t("s = 'a' * n; t = 'a' * (n - 1) + 'a'", "s == t", "n"),
        "why": "Если длины разные, ответ False сразу. Если длины равны, строки сравниваются посимвольно (memcmp), и для равных строк это проход по всем n символам. "
               "Сравнение одного и того же объекта (s == s) CPython сокращает до O(1) по идентичности.",
        "wrong": {
            "0": "O(1) — только когда сразу видно различие (разная длина или первый символ) или это один и тот же объект.",
            "2": "Сравнение идёт подряд, деления пополам нет.",
            "3": "Каждый символ сравнивается один раз, квадрата нет.",
        },
        "src": [UNICODE_C],
    },
    {
        "id": "str-o-hash-cached", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Строку `s` из n символов уже использовали как ключ dict. Сколько стоит повторный `hash(s)`?",
        "options": [ON, O1, OLOG, ONLOG], "answer": 1, "measure": _t("s = 'a' * n; hash(s)", "hash(s)", "1"),
        "why": "Первый hash(s) проходит по всем символам — O(n). Результат сохраняется в объекте строки (поле hash), ведь строка неизменяема. "
               "Повторные вызовы и поиск этой же строки в dict берут готовое число — O(1).",
        "wrong": {
            "0": "O(n) стоит только первый вызов. Потом хеш читается из кэша в объекте.",
            "2": "Хеш не ищется, а читается из поля объекта.",
            "3": "O(n log n) — сортировка. Хеш даже в первый раз считается одним проходом, а повторно вообще не считается.",
        },
        "src": [UNICODE_C],
    },
    {
        "id": "str-o-startswith", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s.startswith('ab')` для строки из n символов?",
        "options": [ON, O1, OLOG, "O(n·m)"], "answer": 1, "measure": _t("s = 'a' * n", "s.startswith('ab')", "1"),
        "why": "startswith сравнивает только начало s длиной с префикс. Остальные символы s не просматриваются, поэтому стоимость зависит от длины префикса, а не от n.",
        "wrong": {
            "0": "Просматривать всю строку не нужно: ответ ясен по первым len(prefix) символам.",
            "2": "Ничего не ищется пополам: сравнивается начало строки.",
            "3": "Произведение длин — у наивного поиска подстроки где угодно. Префикс сравнивается в одном месте.",
        },
        "src": [STR_SRC + "#str.startswith"],
    },
    {
        "id": "str-o-count", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s.count('a')` для строки из n символов?",
        "options": [O1, ON, ONLOG, OLOG], "answer": 1, "measure": _t("s = 'ab' * (n // 2)", "s.count('a')", "n"),
        "why": "Счётчики вхождений строка не хранит, поэтому count проходит всю строку и считает совпадения. Каждый символ смотрится константное число раз — O(n).",
        "wrong": {
            "0": "Готового счётчика в объекте строки нет, в отличие от длины.",
            "2": "O(n log n) — сортировка. count не переставляет символы, а только просматривает их подряд.",
            "3": "Вхождения могут быть где угодно, пропустить часть строки нельзя.",
        },
        "src": [STR_SRC + "#str.count"],
    },
    {
        "id": "str-o-upper", "topic": "str-o", "type": "choice", "mono": True,
        "q": "Сколько стоит `s.upper()`?",
        "options": [ON, O1, ON2, OLOG], "answer": 0, "measure": _t("s = 'a' * n", "s.upper()", "n"),
        "why": _IMM + "upper проходит по каждому символу, переводит его в верхний регистр и пишет в новую строку — O(n).",
        "wrong": {
            "1": "Строку нельзя изменить на месте, нужна новая строка из n символов.",
            "2": "Каждый символ обрабатывается один раз, вложенных проходов нет.",
            "3": "Нужно обработать все символы, логарифм невозможен.",
        },
        "src": [STR_SRC + "#str.upper"],
    },
    # ------------------------------------------------------------------ methods
    {
        "id": "str-m-rsplit", "topic": "str-m", "type": "input", "of": "str",
        "q": "Какой метод str режет строку по разделителю справа налево?",
        "code": "'a.b.c'.???('.', 1)\n# ['a.b', 'c']",
        "answer": ["rsplit"], "covers": ["str.rsplit"],
        "check": "assert 'a.b.c'.rsplit('.', 1) == ['a.b', 'c']",
        "why": "rsplit(sep, maxsplit) режет с правого края не больше maxsplit раз. Удобно, чтобы отделить расширение файла или последний компонент пути. "
               "Без maxsplit результат такой же, как у split.",
        "src": [STR_SRC + "#str.rsplit"],
    },
    {
        "id": "str-m-split-ws", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `' a  b '.split()` и что вернёт `' a  b '.split(' ')`?",
        "options": ["`['a', 'b']` и `['', 'a', '', 'b', '']`", "Оба `['a', 'b']`", "Оба `['', 'a', '', 'b', '']`", "`['a', 'b']` и `['a', 'b', '']`"],
        "answer": 0, "covers": ["str.split"],
        "check": "assert ' a  b '.split() == ['a', 'b'] and ' a  b '.split(' ') == ['', 'a', '', 'b', '']",
        "why": "Без аргумента split режет по любым пробельным символам, склеивает их подряд и выкидывает пустые куски по краям. "
               "С явным разделителем ' ' каждый пробел — граница, поэтому появляются пустые строки.",
        "wrong": {
            "1": "С явным разделителем пустые куски не выкидываются.",
            "2": "Без аргумента split работает «умно»: пустые куски не возвращает.",
            "3": "Пустая строка есть и в начале: строка начинается с пробела.",
        },
        "src": [STR_SRC + "#str.split"],
    },
    {
        "id": "str-m-splitlines", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'a\\nb\\n'.splitlines()` и что вернёт `'a\\nb\\n'.split('\\n')`?",
        "options": ["`['a', 'b']` и `['a', 'b', '']`", "Оба `['a', 'b']`", "Оба `['a', 'b', '']`", "`['a\\n', 'b\\n']` и `['a', 'b']`"],
        "answer": 0, "covers": ["str.splitlines"],
        "check": "assert 'a\\nb\\n'.splitlines() == ['a', 'b'] and 'a\\nb\\n'.split('\\n') == ['a', 'b', '']",
        "why": "splitlines режет по концам строк и не даёт лишнего пустого элемента после последнего \\n. split('\\n') видит разделитель в конце и добавляет пустую строку. "
               "splitlines понимает и \\r\\n, и \\r, поэтому подходит для текста из разных систем.",
        "wrong": {
            "1": "split('\\n') возвращает кусок после последнего разделителя, даже пустой.",
            "2": "splitlines не создаёт пустой элемент после завершающего перевода строки.",
            "3": "Переводы строк сохраняются только с keepends=True.",
        },
        "src": [STR_SRC + "#str.splitlines"],
    },
    {
        "id": "str-m-strip-set", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'xyhixyx'.strip('xy')`?",
        "options": ["`'hi'`", "`'hixyx'`", "`'xyhix'`", "`'xyhixyx'`"],
        "answer": 0, "covers": ["str.strip"],
        "check": "assert 'xyhixyx'.strip('xy') == 'hi'",
        "why": "Аргумент strip — набор символов, а не строка-префикс. С обоих концов срезаются все символы из набора {'x', 'y'}, пока не встретится другой символ.",
        "wrong": {
            "1": "strip работает с обоих концов, а не только слева.",
            "2": "strip срезает любые символы из набора, а не точное совпадение 'xy' один раз.",
            "3": "Края строки состоят из x и y, они удаляются.",
        },
        "src": [STR_SRC + "#str.strip"],
    },
    {
        "id": "str-m-lstrip-trap", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'https://shop.ru'.lstrip('https://')`?",
        "options": ["`'op.ru'`", "`'shop.ru'`", "`'hop.ru'`", "`'https://shop.ru'`"],
        "answer": 0, "covers": ["str.lstrip", "str.removeprefix"],
        "check": "assert 'https://shop.ru'.lstrip('https://') == 'op.ru' and 'https://shop.ru'.removeprefix('https://') == 'shop.ru'",
        "why": "lstrip принимает набор символов {h, t, p, s, :, /}. Он срезает слева всё из набора — в том числе 's' и 'h' из 'shop'. "
               "Чтобы убрать именно префикс, нужен removeprefix('https://') (Python 3.9+).",
        "wrong": {
            "1": "Так сработал бы removeprefix. lstrip не знает о «слове» https://, только о наборе символов.",
            "2": "'s' тоже в наборе: после '/' срезается и 's', и 'h'.",
            "3": "Символы набора есть в начале строки, поэтому что-то срежется.",
        },
        "src": [STR_SRC + "#str.lstrip"],
    },
    {
        "id": "str-m-rstrip-trap", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'report.txt'.rstrip('.txt')`?",
        "options": ["`'repor'`", "`'report'`", "`'report.'`", "`'report.txt'`"],
        "answer": 0, "covers": ["str.rstrip", "str.removesuffix"],
        "check": "assert 'report.txt'.rstrip('.txt') == 'repor' and 'report.txt'.removesuffix('.txt') == 'report'",
        "why": "rstrip('.txt') срезает справа любые символы из набора {'.', 't', 'x'}. После '.txt' следующий символ — 't' из 'report', он тоже в наборе. "
               "Остановка на 'r'. Для расширения нужен removesuffix('.txt').",
        "wrong": {
            "1": "'report' дал бы removesuffix('.txt'). rstrip продолжает срезать, пока символы есть в наборе.",
            "2": "'.' входит в набор {'.', 't', 'x'} и срезается, поэтому точки в конце не останется.",
            "3": "Конец строки состоит из символов набора, поэтому он срежется.",
        },
        "src": [STR_SRC + "#str.rstrip"],
    },
    {
        "id": "str-m-removesuffix", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом убрать из строки ровно суффикс '.csv', если он есть?",
        "code": "'data.csv'.???('.csv')\n# 'data'",
        "answer": ["removesuffix"], "covers": ["str.removesuffix"],
        "check": "assert 'data.csv'.removesuffix('.csv') == 'data' and 'data'.removesuffix('.csv') == 'data'",
        "why": "removesuffix (Python 3.9+) срезает суффикс, только если строка на него оканчивается, иначе возвращает строку без изменений. "
               "rstrip для этого не годится: он срезает набор символов.",
        "src": [STR_SRC + "#str.removesuffix"],
    },
    {
        "id": "str-m-removeprefix", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом убрать из строки ровно префикс 'test_', если он есть?",
        "code": "'test_login'.???('test_')\n# 'login'",
        "answer": ["removeprefix"], "covers": ["str.removeprefix"],
        "check": "assert 'test_login'.removeprefix('test_') == 'login'",
        "why": "removeprefix (Python 3.9+) срезает префикс целиком и только если он есть. lstrip('test_') срезал бы набор символов и испортил бы слово, например 'test_set' → ''.",
        "src": [STR_SRC + "#str.removeprefix"],
    },
    {
        "id": "str-m-find-index", "topic": "str-m", "type": "choice",
        "q": "Подстроки нет в строке. Что вернут `s.find(sub)` и `s.index(sub)`?",
        "options": ["`-1` и ValueError", "Оба `-1`", "`None` и `-1`", "ValueError и `-1`"],
        "answer": 0, "covers": ["str.find", "str.index"],
        "check": "assert 'abc'.find('z') == -1\ntry:\n    'abc'.index('z')\n    raise AssertionError\nexcept ValueError:\n    pass",
        "why": "find сообщает об отсутствии значением −1, index — исключением ValueError. Осторожно с −1: s[s.find(x)] без проверки возьмёт последний символ.",
        "wrong": {
            "1": "index никогда не возвращает −1, он бросает исключение.",
            "2": "find не возвращает None, а index не возвращает −1.",
            "3": "Наоборот: −1 возвращает find, а исключение ValueError бросает index.",
        },
        "src": [STR_SRC + "#str.find"],
    },
    {
        "id": "str-m-rfind-rindex", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'a.b.c'.rfind('.')` и что сделает `'abc'.rindex('.')`?",
        "options": ["`3` и ValueError", "`1` и `-1`", "`3` и `-1`", "`-3` и ValueError"],
        "answer": 0, "covers": ["str.rfind", "str.rindex"],
        "check": "assert 'a.b.c'.rfind('.') == 3\ntry:\n    'abc'.rindex('.')\n    raise AssertionError\nexcept ValueError:\n    pass",
        "why": "rfind ищет последнее вхождение, но индекс считается от начала строки: последняя точка — на позиции 3. "
               "rindex ведёт себя так же, но при отсутствии бросает ValueError, как index.",
        "wrong": {
            "1": "1 — позиция первой точки (find). rindex не возвращает −1.",
            "2": "rindex при отсутствии подстроки бросает ValueError, а не возвращает −1.",
            "3": "Индекс от rfind считается от начала, он не отрицательный.",
        },
        "src": [STR_SRC + "#str.rfind"],
    },
    {
        "id": "str-m-count", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'aaaa'.count('aa')`?",
        "options": ["`2`", "`3`", "`4`", "`1`"],
        "answer": 0, "covers": ["str.count"],
        "check": "assert 'aaaa'.count('aa') == 2",
        "why": "count считает непересекающиеся вхождения: после найденного 'aa' поиск продолжается за его концом. Поэтому 'aa' + 'aa' — два вхождения, а не три.",
        "wrong": {
            "1": "3 — число пересекающихся вхождений (позиции 0, 1, 2). count их не считает.",
            "2": "4 — число символов 'a'. Ищется подстрока 'aa'.",
            "3": "После первого вхождения поиск продолжается и находит второе.",
        },
        "src": [STR_SRC + "#str.count"],
    },
    {
        "id": "str-m-replace", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'aaa'.replace('a', 'b', 2)`?",
        "options": ["`'bba'`", "`'bbb'`", "`'abb'`", "Ошибка: лишний аргумент"],
        "answer": 0, "covers": ["str.replace"],
        "check": "assert 'aaa'.replace('a', 'b', 2) == 'bba'",
        "why": "Третий аргумент count ограничивает число замен. Замены идут слева направо, поэтому меняются два первых 'a'.",
        "wrong": {
            "1": "Все три 'a' заменились бы без третьего аргумента. count = 2 ограничивает замены двумя.",
            "2": "replace идёт слева направо, а не справа.",
            "3": "У replace есть необязательный третий аргумент count.",
        },
        "src": [STR_SRC + "#str.replace"],
    },
    {
        "id": "str-m-join-types", "topic": "str-m", "type": "choice",
        "q": "Что сделает `', '.join([1, 2])`?",
        "options": ["TypeError", "`'1, 2'`", "`'[1, 2]'`", "`', '`"],
        "answer": 0, "covers": ["str.join"],
        "check": "try:\n    ', '.join([1, 2])\n    raise AssertionError\nexcept TypeError:\n    pass\nassert ', '.join(map(str, [1, 2])) == '1, 2'",
        "why": "join склеивает только строки и не превращает числа в строки сам. Нужно явно: ', '.join(map(str, nums)). "
               "Метод вызывается у разделителя, а аргумент — итерируемый объект строк.",
        "wrong": {
            "1": "Так было бы после map(str, ...). Сам join типы не приводит.",
            "2": "join не вызывает str() у списка, он перебирает элементы.",
            "3": "Ошибка возникает на первом нестроковом элементе.",
        },
        "src": [STR_SRC + "#str.join"],
    },
    {
        "id": "str-m-partition", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'k=v=w'.partition('=')` и `'k=v=w'.rpartition('=')`?",
        "options": [
            "`('k', '=', 'v=w')` и `('k=v', '=', 'w')`",
            "`['k', 'v', 'w']` и `['k', 'v', 'w']`",
            "`('k', 'v=w')` и `('k=v', 'w')`",
            "`('k=v', '=', 'w')` и `('k', '=', 'v=w')`",
        ],
        "answer": 0, "covers": ["str.partition", "str.rpartition"],
        "check": "assert 'k=v=w'.partition('=') == ('k', '=', 'v=w') and 'k=v=w'.rpartition('=') == ('k=v', '=', 'w')",
        "why": "partition делит по первому вхождению, rpartition — по последнему. Оба всегда возвращают кортеж из трёх частей: до, разделитель, после. "
               "Удобно для разбора 'ключ=значение' без проверок длины.",
        "wrong": {
            "1": "Список всех частей дал бы split('='). partition делит только один раз.",
            "2": "Разделитель тоже входит в результат: кортеж из трёх частей.",
            "3": "Перепутаны: partition берёт первое вхождение, rpartition — последнее.",
        },
        "src": [STR_SRC + "#str.partition"],
    },
    {
        "id": "str-m-endswith-tuple", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'img.png'.endswith(('.jpg', '.png'))`?",
        "options": ["`True`", "`False`", "TypeError", "`'.png'`"],
        "answer": 0, "covers": ["str.endswith"],
        "check": "assert 'img.png'.endswith(('.jpg', '.png')) is True",
        "why": "endswith и startswith принимают кортеж вариантов и возвращают True, если подходит любой. Список не подойдёт — только кортеж.",
        "wrong": {
            "1": "Строка оканчивается на один из вариантов, '.png'.",
            "2": "Кортеж — допустимый аргумент. TypeError был бы для списка.",
            "3": "Метод возвращает bool, а не найденный вариант.",
        },
        "src": [STR_SRC + "#str.endswith"],
    },
    {
        "id": "str-m-startswith-case", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'Hello'.startswith('he')`?",
        "options": ["`False`", "`True`", "`0`", "ValueError"],
        "answer": 0, "covers": ["str.startswith"],
        "check": "assert 'Hello'.startswith('he') is False and 'Hello'.lower().startswith('he')",
        "why": "Сравнение учитывает регистр: 'H' и 'h' — разные символы. Без учёта регистра: s.casefold().startswith(prefix.casefold()).",
        "wrong": {
            "1": "startswith регистр не игнорирует: 'H' и 'h' — разные символы, совпадения нет.",
            "2": "startswith возвращает bool (True или False), а не позицию совпадения, как find.",
            "3": "Несовпадение — обычный результат False, не ошибка.",
        },
        "src": [STR_SRC + "#str.startswith"],
    },
    {
        "id": "str-m-digits", "topic": "str-m", "type": "choice",
        "q": "Что вернут для строки `'²'` методы `isdecimal()`, `isdigit()`, `isnumeric()`?",
        "options": ["`False`, `True`, `True`", "`True`, `True`, `True`", "`False`, `False`, `True`", "`False`, `False`, `False`"],
        "answer": 0, "covers": ["str.isdecimal", "str.isdigit", "str.isnumeric"],
        "check": "assert ('²'.isdecimal(), '²'.isdigit(), '²'.isnumeric()) == (False, True, True)\nassert '½'.isnumeric() and not '½'.isdigit()",
        "why": "Три уровня строгости. isdecimal — только десятичные цифры, годные для int(). isdigit добавляет надстрочные цифры вроде '²'. "
               "isnumeric добавляет дроби и прочие числовые символы: '½'. Для проверки перед int() берите isdecimal.",
        "wrong": {
            "1": "'²' не десятичная цифра: int('²') упадёт, поэтому isdecimal — False.",
            "2": "isdigit считает надстрочные цифры цифрами.",
            "3": "'²' — числовой символ, isnumeric и isdigit его принимают.",
        },
        "src": [STR_SRC + "#str.isdecimal"],
    },
    {
        "id": "str-m-alpha-alnum", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'abc123'.isalpha()` и `'abc123'.isalnum()`?",
        "options": ["`False` и `True`", "`True` и `True`", "`False` и `False`", "`True` и `False`"],
        "answer": 0, "covers": ["str.isalpha", "str.isalnum"],
        "check": "assert 'abc123'.isalpha() is False and 'abc123'.isalnum() is True",
        "why": "isalpha требует, чтобы все символы были буквами — цифры мешают. isalnum разрешает буквы и цифры вместе. Обе дают False для пустой строки.",
        "wrong": {
            "1": "Цифры не буквы, поэтому isalpha — False.",
            "2": "Буквы и цифры вместе как раз подходят для isalnum.",
            "3": "Наоборот: isalpha ложь из-за цифр, isalnum истина.",
        },
        "src": [STR_SRC + "#str.isalnum"],
    },
    {
        "id": "str-m-empty-checks", "topic": "str-m", "type": "choice",
        "q": "Что вернут для пустой строки `''.isascii()`, `''.isspace()`, `''.isprintable()`?",
        "options": ["`True`, `False`, `True`", "`False`, `False`, `False`", "`True`, `True`, `True`", "`False`, `True`, `False`"],
        "answer": 0, "covers": ["str.isascii", "str.isspace", "str.isprintable"],
        "check": "assert (''.isascii(), ''.isspace(), ''.isprintable()) == (True, False, True)\nassert not 'a\\tb'.isprintable()",
        "why": "isascii и isprintable спрашивают «нет ли плохих символов» — у пустой строки их нет, ответ True. isspace (как isalpha, isdigit) требует хотя бы один символ, "
               "поэтому для '' — False. А '\\t' и '\\n' непечатаемые: 'a\\tb'.isprintable() — False.",
        "wrong": {
            "1": "isascii и isprintable проверяют отсутствие неподходящих символов, у '' их нет.",
            "2": "isspace требует непустую строку, поэтому для '' он даёт False, а не True.",
            "3": "Всё наоборот: True дают isascii и isprintable.",
        },
        "src": [STR_SRC + "#str.isascii"],
    },
    {
        "id": "str-m-case-checks", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'abc1'.islower()` и `'123'.isupper()`?",
        "options": ["`True` и `False`", "`False` и `False`", "`True` и `True`", "`False` и `True`"],
        "answer": 0, "covers": ["str.islower", "str.isupper"],
        "check": "assert 'abc1'.islower() is True and '123'.isupper() is False",
        "why": "islower и isupper смотрят только на буквы с регистром, остальные символы им не мешают. Но нужна хотя бы одна такая буква: "
               "в '123' букв нет, поэтому isupper — False.",
        "wrong": {
            "1": "Цифра не мешает islower: проверяются только буквы.",
            "2": "В '123' нет ни одной буквы, а isupper требует хотя бы одну.",
            "3": "Наоборот: True даёт 'abc1'.islower(), а у '123' нет букв, и isupper — False.",
        },
        "src": [STR_SRC + "#str.islower"],
    },
    {
        "id": "str-m-title", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `\"they're bill's\".title()`?",
        "options": ["`\"They'Re Bill'S\"`", "`\"They're Bill's\"`", "`\"They're bill's\"`", "`\"THEY'RE BILL'S\"`"],
        "answer": 0, "covers": ["str.title"],
        "check": "assert \"they're bill's\".title() == \"They'Re Bill'S\"",
        "why": "title считает словом любую группу букв подряд. Апостроф разрывает слово, поэтому 're' и 's' тоже получают заглавную. "
               "Для текста лучше string.capwords или своё правило.",
        "wrong": {
            "1": "Так хотелось бы, но title не знает про апострофы.",
            "2": "Так работает capitalize: заглавная только у первого символа строки.",
            "3": "Все буквы заглавными делает upper(), а title меняет только первые буквы слов.",
        },
        "src": [STR_SRC + "#str.title"],
    },
    {
        "id": "str-m-istitle", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'Hello World'.istitle()` и `'Hello world'.istitle()`?",
        "options": ["`True` и `False`", "`True` и `True`", "`False` и `False`", "`False` и `True`"],
        "answer": 0, "covers": ["str.istitle"],
        "check": "assert 'Hello World'.istitle() and not 'Hello world'.istitle()",
        "why": "istitle требует, чтобы каждое слово начиналось с заглавной, а остальные буквы были строчными. В 'Hello world' второе слово со строчной.",
        "wrong": {
            "1": "'world' начинается со строчной, поэтому вторая строка не в title-регистре.",
            "2": "'Hello World' — ровно тот вид, что даёт title().",
            "3": "Перепутаны: True даёт 'Hello World', а у 'Hello world' второе слово со строчной.",
        },
        "src": [STR_SRC + "#str.istitle"],
    },
    {
        "id": "str-m-capitalize", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'hELLO wORLD'.capitalize()`?",
        "options": ["`'Hello world'`", "`'HELLO wORLD'`", "`'Hello World'`", "`'hello world'`"],
        "answer": 0, "covers": ["str.capitalize"],
        "check": "assert 'hELLO wORLD'.capitalize() == 'Hello world'",
        "why": "capitalize делает первый символ строки заглавным, а все остальные — строчными. Остальные слова не трогаются по отдельности: это не title.",
        "wrong": {
            "1": "capitalize переводит остальные символы в нижний регистр, а не оставляет как есть.",
            "2": "Заглавную букву в каждом слове даёт title(). capitalize меняет только первый символ строки.",
            "3": "Все строчные даёт lower(). capitalize делает первый символ заглавным.",
        },
        "src": [STR_SRC + "#str.capitalize"],
    },
    {
        "id": "str-m-swapcase", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'Привет'.swapcase()`?",
        "options": ["`'пРИВЕТ'`", "`'ПРИВЕТ'`", "`'привет'`", "`'Привет'`: кириллица не меняется"],
        "answer": 0, "covers": ["str.swapcase"],
        "check": "assert 'Привет'.swapcase() == 'пРИВЕТ'",
        "why": "swapcase меняет регистр каждой буквы на противоположный. Методы регистра работают по Unicode, поэтому кириллица обрабатывается так же, как латиница.",
        "wrong": {
            "1": "Все заглавные даёт upper(). swapcase сделал бы П строчной.",
            "2": "Все строчные даёт lower(). swapcase меняет и строчные на заглавные.",
            "3": "Строки Python — Unicode, кириллические буквы имеют регистр.",
        },
        "src": [STR_SRC + "#str.swapcase"],
    },
    {
        "id": "str-m-upper-len", "topic": "str-m", "type": "choice",
        "q": "Чему равно `len('ß'.upper())`?",
        "options": ["`2`", "`1`", "`0`", "Ошибка"],
        "answer": 0, "covers": ["str.upper"],
        "check": "assert 'ß'.upper() == 'SS' and len('ß'.upper()) == 2",
        "why": "У немецкой 'ß' нет одной заглавной пары, по правилам Unicode она становится 'SS'. Поэтому upper() может изменить длину строки — "
               "не стоит полагаться на равенство len(s) и len(s.upper()).",
        "wrong": {
            "1": "Длина сохранилась бы для большинства букв, но 'ß' превращается в два символа.",
            "2": "upper не удаляет символы: строка из одной буквы не может стать пустой.",
            "3": "Ошибки нет: Unicode знает правило для 'ß'.",
        },
        "src": [STR_SRC + "#str.upper"],
    },
    {
        "id": "str-m-casefold", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'Straße'.lower() == 'STRASSE'.lower()` и `'Straße'.casefold() == 'STRASSE'.casefold()`?",
        "options": ["`False` и `True`", "`True` и `True`", "`False` и `False`", "`True` и `False`"],
        "answer": 0, "covers": ["str.casefold", "str.lower"],
        "check": "assert ('Straße'.lower() == 'STRASSE'.lower()) is False and 'Straße'.casefold() == 'STRASSE'.casefold()",
        "why": "lower оставляет 'ß' как есть: 'straße' ≠ 'strasse'. casefold агрессивнее и превращает 'ß' в 'ss'. "
               "Для сравнения без учёта регистра берите casefold, для вывода — lower.",
        "wrong": {
            "1": "lower не меняет 'ß', поэтому строки не совпадут.",
            "2": "casefold как раз приводит 'ß' к 'ss', и строки совпадают.",
            "3": "Наоборот: lower строки не уравнивает, а casefold уравнивает через 'ss'.",
        },
        "src": [STR_SRC + "#str.casefold"],
    },
    {
        "id": "str-m-lower", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом перевести строку в нижний регистр для вывода?",
        "code": "'ПРИВЕТ'.???()\n# 'привет'",
        "answer": ["lower"], "covers": ["str.lower"],
        "check": "assert 'ПРИВЕТ'.lower() == 'привет'",
        "why": "lower возвращает новую строку в нижнем регистре. Для сравнения без учёта регистра лучше casefold: он обрабатывает особые случаи вроде 'ß'.",
        "src": [STR_SRC + "#str.lower"],
    },
    {
        "id": "str-m-center", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'ab'.center(6, '*')`?",
        "options": ["`'**ab**'`", "`'ab****'`", "`'****ab'`", "`'*ab*'`"],
        "answer": 0, "covers": ["str.center"],
        "check": "assert 'ab'.center(6, '*') == '**ab**'",
        "why": "center дополняет строку до длины width символом fillchar поровну с двух сторон. 6 − 2 = 4 символа: по два слева и справа.",
        "wrong": {
            "1": "'ab****' — это ljust(6, '*'): текст прижат влево, заполнитель справа.",
            "2": "'****ab' — это rjust(6, '*'): текст прижат вправо, заполнитель слева.",
            "3": "width — итоговая длина строки (6), а не число добавленных символов.",
        },
        "src": [STR_SRC + "#str.center"],
    },
    {
        "id": "str-m-ljust", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом дополнить строку точками справа до длины 6?",
        "code": "'ab'.???(6, '.')\n# 'ab....'",
        "answer": ["ljust"], "covers": ["str.ljust"],
        "check": "assert 'ab'.ljust(6, '.') == 'ab....'",
        "why": "ljust прижимает текст влево, то есть добавляет заполнитель справа до длины width. Если строка уже длиннее width, она возвращается как есть, без обрезки.",
        "src": [STR_SRC + "#str.ljust"],
    },
    {
        "id": "str-m-rjust-zfill", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'-7'.rjust(4, '0')` и `'-7'.zfill(4)`?",
        "options": ["`'00-7'` и `'-007'`", "`'-007'` и `'-007'`", "`'00-7'` и `'00-7'`", "`'-700'` и `'-007'`"],
        "answer": 0, "covers": ["str.rjust", "str.zfill"],
        "check": "assert '-7'.rjust(4, '0') == '00-7' and '-7'.zfill(4) == '-007'",
        "why": "rjust дописывает заполнитель слева и про знак не знает. zfill создан для чисел: нули встают после знака '-' или '+'. "
               "Для чисел ещё удобнее f'{n:04d}'.",
        "wrong": {
            "1": "rjust не учитывает знак, нули встают перед '-'.",
            "2": "zfill учитывает знак: нули идут после '-'.",
            "3": "rjust добавляет символы слева, а не справа.",
        },
        "src": [STR_SRC + "#str.zfill"],
    },
    {
        "id": "str-m-expandtabs", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'a\\tb'.expandtabs(4)`?",
        "options": ["`'a   b'` (3 пробела)", "`'a    b'` (4 пробела)", "`'a b'`", "`'a\\tb'` без изменений"],
        "answer": 0, "covers": ["str.expandtabs"],
        "check": "assert 'a\\tb'.expandtabs(4) == 'a   b'",
        "why": "Табуляция заменяется пробелами до следующей позиции, кратной tabsize. 'a' занимает позицию 0, следующая граница — 4, поэтому нужно 3 пробела.",
        "wrong": {
            "1": "Число пробелов зависит от текущей колонки: до границы 4 осталось 3.",
            "2": "Табуляция не превращается в один пробел, а дополняет до колонки.",
            "3": "expandtabs как раз заменяет табуляции пробелами, поэтому строка изменится.",
        },
        "src": [STR_SRC + "#str.expandtabs"],
    },
    {
        "id": "str-m-encode", "topic": "str-m", "type": "choice",
        "q": "Чему равно `len('я'.encode())`?",
        "options": ["`2`", "`1`", "`4`", "Ошибка: нужна кодировка"],
        "answer": 0, "covers": ["str.encode"],
        "check": "assert len('я'.encode()) == 2 and len('я') == 1",
        "why": "encode по умолчанию даёт UTF-8. Кириллица в UTF-8 занимает 2 байта, поэтому len(bytes) = 2, хотя len(str) = 1: длина строки считается в символах, а длина bytes — в байтах.",
        "wrong": {
            "1": "1 — длина строки в символах. После encode считаются байты.",
            "2": "4 байта в UTF-8 занимают эмодзи и редкие символы. Кириллица — 2.",
            "3": "Кодировка по умолчанию — UTF-8, аргумент не обязателен.",
        },
        "src": [STR_SRC + "#str.encode"],
    },
    {
        "id": "str-m-format", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'{0}{1}{0}'.format('a', 'b')`?",
        "options": ["`'aba'`", "`'ab'`", "`'abab'`", "IndexError"],
        "answer": 0, "covers": ["str.format"],
        "check": "assert '{0}{1}{0}'.format('a', 'b') == 'aba'",
        "why": "Число в поле {} — номер позиционного аргумента, и один аргумент можно подставить несколько раз. {0} = 'a', {1} = 'b'.",
        "wrong": {
            "1": "Поле {0} встречается дважды, 'a' подставляется дважды.",
            "2": "Подставляются ровно три поля, а не аргументы повторяются по кругу.",
            "3": "Номера 0 и 1 существуют: аргументов два.",
        },
        "src": [STR_SRC + "#str.format"],
    },
    {
        "id": "str-m-format-map", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом подставить в шаблон значения прямо из словаря, без распаковки `**d`?",
        "code": "d = {'x': 1, 'y': 2}\n'{x}-{y}'.???(d)\n# '1-2'",
        "answer": ["format_map"], "covers": ["str.format_map"],
        "check": "assert '{x}-{y}'.format_map({'x': 1, 'y': 2}) == '1-2'",
        "why": "format_map(mapping) берёт значения из отображения как есть. В отличие от format(**d), словарь не копируется, "
               "и можно передать подкласс dict с __missing__, чтобы задать значение для отсутствующих полей.",
        "src": [STR_SRC + "#str.format_map"],
    },
    {
        "id": "str-m-translate", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'hello'.translate(str.maketrans('el', 'ip', 'o'))`?",
        "options": ["`'hipp'`", "`'hippo'`", "`'hello'`", "`'hipl'`"],
        "answer": 0, "covers": ["str.translate", "str.maketrans"],
        "check": "assert 'hello'.translate(str.maketrans('el', 'ip', 'o')) == 'hipp'",
        "why": "maketrans строит таблицу: e → i, l → p, а символы третьего аргумента ('o') удаляются. translate применяет таблицу к каждому символу за один проход. "
               "Это быстрее цепочки replace для посимвольных замен.",
        "wrong": {
            "1": "Третий аргумент maketrans — символы на удаление, 'o' пропадает.",
            "2": "Таблица замен применилась, строка изменится.",
            "3": "Замена посимвольная: обе 'l' превращаются в 'p'.",
        },
        "src": [STR_SRC + "#str.maketrans", STR_SRC + "#str.translate"],
    },
    {
        "id": "str-m-isidentifier", "topic": "str-m", "type": "choice",
        "q": "Что вернут `'2x'.isidentifier()` и `'class'.isidentifier()`?",
        "options": ["`False` и `True`", "`False` и `False`", "`True` и `True`", "`True` и `False`"],
        "answer": 0, "covers": ["str.isidentifier"],
        "check": "assert not '2x'.isidentifier() and 'class'.isidentifier()",
        "why": "isidentifier проверяет только синтаксис имени: нельзя начинать с цифры. Ключевые слова синтаксически подходят, поэтому 'class' даёт True. "
               "Проверку на ключевое слово делает keyword.iskeyword.",
        "wrong": {
            "1": "Ключевые слова isidentifier не исключает — это делает keyword.iskeyword.",
            "2": "'2x' не может быть именем: имя в Python не начинается с цифры, поэтому первый ответ — False.",
            "3": "Перепутаны: False у '2x', True у 'class'.",
        },
        "src": [STR_SRC + "#str.isidentifier", "https://docs.python.org/3/library/keyword.html"],
    },
]

# Second batch: edge cases of split, find, count and replace; input questions for everyday methods.
QUESTIONS += [
    {
        "id": "str-m-split-maxsplit", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'a,b,c'.split(',', 1)`?",
        "options": ["`['a', 'b,c']`", "`['a,b', 'c']`", "`['a', 'b', 'c']`", "`['a']`"],
        "answer": 0, "covers": ["str.split"],
        "check": "assert 'a,b,c'.split(',', 1) == ['a', 'b,c']",
        "why": "Второй аргумент — maxsplit, наибольшее число разрезов. split режет слева, поэтому после одного разреза остаток 'b,c' идёт целиком. "
               "Так удобно отделять первое поле, например ключ от значения.",
        "wrong": {
            "1": "Так режет rsplit(',', 1): он начинает справа. split начинает слева.",
            "2": "Так было бы без maxsplit. Число 1 разрешает только один разрез.",
            "3": "maxsplit ограничивает разрезы, а не число частей в ответе. Остаток строки тоже попадает в список.",
        },
        "src": [STR_SRC + "#str.split"],
    },
    {
        "id": "str-m-join", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом склеить список строк через разделитель?",
        "code": "', '.???(['a', 'b', 'c'])\n# 'a, b, c'",
        "answer": ["join"], "covers": ["str.join"],
        "check": "assert ', '.join(['a', 'b', 'c']) == 'a, b, c'",
        "why": "join вызывают у разделителя, а список передают аргументом. Метод один раз считает итоговую длину и копирует части, "
               "поэтому он работает за O(n). Склейка через += в цикле может копировать строку много раз.",
        "src": [STR_SRC + "#str.join"],
    },
    {
        "id": "str-m-strip", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом убрать пробелы и переводы строк с обоих краёв строки?",
        "code": "'  hi\\n'.???()\n# 'hi'",
        "answer": ["strip"], "covers": ["str.strip"],
        "check": "assert '  hi\\n'.strip() == 'hi'",
        "why": "strip() без аргумента убирает с обоих краёв все пробельные символы: пробелы, табуляции, переводы строк. "
               "Середину строки он не трогает. Только левый край чистит lstrip, только правый — rstrip.",
        "src": [STR_SRC + "#str.strip"],
    },
    {
        "id": "str-m-replace-empty", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'abc'.replace('', '-')`?",
        "options": ["`'-a-b-c-'`", "`'abc'`", "`'a-b-c'`", "Ошибка ValueError"],
        "answer": 0, "covers": ["str.replace"],
        "check": "assert 'abc'.replace('', '-') == '-a-b-c-'",
        "why": "Пустая строка встречается в каждой позиции: перед каждым символом и в конце. В строке из 3 символов таких позиций 4. "
               "replace вставляет '-' в каждую из них.",
        "wrong": {
            "1": "Пустая подстрока находится везде, поэтому замены есть. Строка без изменений была бы при поиске отсутствующей подстроки.",
            "2": "Позиции есть и до первого символа, и после последнего. Их replace тоже заполняет.",
            "3": "Пустой образец для replace допустим, ошибки нет.",
        },
        "src": [STR_SRC + "#str.replace"],
    },
    {
        "id": "str-m-find-start", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'abcabc'.find('c', 3)`?",
        "options": ["`5`", "`2`", "`-1`", "`3`"],
        "answer": 0, "covers": ["str.find"],
        "check": "assert 'abcabc'.find('c', 3) == 5",
        "why": "Второй аргумент — индекс начала поиска. Поиск идёт с позиции 3, первое 'c' после неё стоит на индексе 5. "
               "Индекс в ответе считается от начала всей строки, а не от точки старта.",
        "wrong": {
            "1": "2 — индекс первого 'c' во всей строке. Но поиск начинается с индекса 3, и это 'c' пропускается.",
            "2": "-1 значит «не найдено». Второе 'c' есть дальше, на индексе 5.",
            "3": "3 — это точка старта, а не найденная позиция. Там стоит 'a'.",
        },
        "src": [STR_SRC + "#str.find"],
    },
    {
        "id": "str-m-count-empty", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'abc'.count('')`?",
        "options": ["`4`", "`0`", "`3`", "Ошибка ValueError"],
        "answer": 0, "covers": ["str.count"],
        "check": "assert 'abc'.count('') == 4",
        "why": "count считает непересекающиеся вхождения. Пустая строка входит в каждую позицию между символами и по краям. "
               "У строки длины n таких позиций n + 1, здесь 4.",
        "wrong": {
            "1": "Пустая подстрока есть в любой строке, даже в пустой: ''.count('') == 1.",
            "2": "Позиций на одну больше, чем символов: есть ещё позиция в самом конце.",
            "3": "Пустой образец допустим, count не бросает ошибку.",
        },
        "src": [STR_SRC + "#str.count"],
    },
    {
        "id": "str-m-upper", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом перевести строку в верхний регистр?",
        "code": "'Привет'.???()\n# 'ПРИВЕТ'",
        "answer": ["upper"], "covers": ["str.upper"],
        "check": "assert 'Привет'.upper() == 'ПРИВЕТ'",
        "why": "upper() возвращает новую строку, где все буквы заглавные. Он работает для любых алфавитов Unicode, не только для латиницы. "
               "Исходная строка не меняется.",
        "src": [STR_SRC + "#str.upper"],
    },
    {
        "id": "str-m-startswith", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом проверить, что строка начинается с заданного префикса?",
        "code": "'test_io.py'.???('test_')\n# True",
        "answer": ["startswith"], "covers": ["str.startswith"],
        "check": "assert 'test_io.py'.startswith('test_') and not 'io.py'.startswith('test_')",
        "why": "startswith(prefix) отвечает True или False. Он принимает и кортеж префиксов: s.startswith(('a', 'b')). "
               "Это понятнее и надёжнее, чем срез s[:5] == 'test_', где легко ошибиться в длине.",
        "src": [STR_SRC + "#str.startswith"],
    },
    {
        "id": "str-m-isspace", "topic": "str-m", "type": "choice",
        "q": "Что вернут `' \\t\\n'.isspace()` и `''.isspace()`?",
        "options": ["`True` и `False`", "`True` и `True`", "`False` и `False`", "`False` и `True`"],
        "answer": 0, "covers": ["str.isspace"],
        "check": "assert ' \\t\\n'.isspace() is True and ''.isspace() is False",
        "why": "isspace() отвечает True, если строка непустая и все её символы пробельные. Табуляция и перевод строки — тоже пробельные символы. "
               "Пустая строка даёт False: у неё нет ни одного символа.",
        "wrong": {
            "1": "Все методы is... для пустой строки возвращают False, кроме isascii.",
            "2": "\\t и \\n считаются пробельными символами, поэтому первая строка даёт True.",
            "3": "Ответы перепутаны: непустая строка из пробелов — True, пустая — False.",
        },
        "src": [STR_SRC + "#str.isspace"],
    },
    {
        "id": "str-m-zfill", "topic": "str-m", "type": "input", "of": "str",
        "q": "Каким методом дополнить строку с числом нулями слева до ширины 5?",
        "code": "'42'.???(5)\n# '00042'",
        "answer": ["zfill"], "covers": ["str.zfill"],
        "check": "assert '42'.zfill(5) == '00042' and '-42'.zfill(5) == '-0042'",
        "why": "zfill(width) добавляет нули слева до нужной ширины. Знак + или - он оставляет впереди: '-42'.zfill(5) == '-0042'. "
               "Если строка уже длиннее width, она возвращается как есть.",
        "src": [STR_SRC + "#str.zfill"],
    },
    {
        "id": "str-m-partition-missing", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'abc'.partition('=')`?",
        "options": ["`('abc', '', '')`", "`('', '', 'abc')`", "`['abc']`", "Ошибка ValueError"],
        "answer": 0, "covers": ["str.partition"],
        "check": "assert 'abc'.partition('=') == ('abc', '', '') and 'abc'.rpartition('=') == ('', '', 'abc')",
        "why": "partition всегда возвращает кортеж из трёх частей. Если разделителя нет, вся строка идёт в первую часть, а две другие пустые. "
               "Поэтому распаковка key, sep, value = s.partition('=') не падает, а проверка if sep показывает, был ли разделитель.",
        "wrong": {
            "1": "Так отвечает rpartition: при неудаче он кладёт строку в последнюю часть.",
            "2": "partition возвращает кортеж ровно из трёх строк, а не список. Список возвращает split.",
            "3": "Ошибку при отсутствии разделителя бросает index. partition возвращает пустые части.",
        },
        "src": [STR_SRC + "#str.partition"],
    },
    {
        "id": "str-m-encode-ascii", "topic": "str-m", "type": "choice",
        "q": "Что произойдёт при `'é'.encode('ascii')`?",
        "options": ["Исключение UnicodeEncodeError", "`b'e'`", "`b'?'`", "`b'\\xc3\\xa9'`"],
        "answer": 0, "covers": ["str.encode"],
        "check": "try:\n    'é'.encode('ascii')\n    raise AssertionError\nexcept UnicodeEncodeError:\n    pass\nassert 'é'.encode('ascii', 'replace') == b'?'",
        "why": "В ASCII только 128 символов, и 'é' среди них нет. По умолчанию encode работает в режиме errors='strict' и бросает UnicodeEncodeError. "
               "Другие режимы: 'replace' даёт b'?', 'ignore' выбрасывает символ.",
        "wrong": {
            "1": "encode не убирает диакритику сам. Для этого нужна нормализация unicodedata.normalize('NFKD', ...).",
            "2": "b'?' получится только с errors='replace'. По умолчанию режим строгий.",
            "3": "Это UTF-8: два байта для 'é'. Кодировку UTF-8 дал бы 'é'.encode() без аргумента.",
        },
        "src": [STR_SRC + "#str.encode", "https://docs.python.org/3/library/codecs.html#error-handlers"],
    },
    {
        "id": "str-m-format-align", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'{:>5}'.format('ab')`?",
        "options": ["`'   ab'`", "`'ab   '`", "`' ab  '`", "`'>>>ab'`"],
        "answer": 0, "covers": ["str.format"],
        "check": "assert '{:>5}'.format('ab') == '   ab' and '{:<5}'.format('ab') == 'ab   '",
        "why": "В спецификации формата > значит «выровнять вправо», 5 — ширина поля. Строка 'ab' занимает 2 места, слева добавляются 3 пробела. "
               "< выравнивает влево, ^ — по центру. Тот же синтаксис работает в f-строках: f'{x:>5}'.",
        "wrong": {
            "1": "Пробелы справа даёт выравнивание влево, '{:<5}'. Знак > прижимает текст к правому краю.",
            "2": "Пробелы с двух сторон даёт выравнивание по центру, '{:^5}'. Здесь знак >.",
            "3": "Знак > задаёт выравнивание, а не символ заполнения. Заполнитель ставят перед ним: '{:*>5}'.",
        },
        "src": ["https://docs.python.org/3/library/string.html#format-specification-mini-language"],
    },
    {
        "id": "str-m-splitlines-keepends", "topic": "str-m", "type": "choice",
        "q": "Что вернёт `'a\\nb'.splitlines(keepends=True)`?",
        "options": ["`['a\\n', 'b']`", "`['a', 'b']`", "`['a\\n', 'b\\n']`", "`['a', '\\n', 'b']`"],
        "answer": 0, "covers": ["str.splitlines"],
        "check": "assert 'a\\nb'.splitlines(keepends=True) == ['a\\n', 'b']",
        "why": "С keepends=True каждая строка сохраняет свой перевод строки. У последней строки перевода нет, поэтому 'b' остаётся без него. "
               "Так можно разбить текст и потом собрать его обратно через ''.join без потерь.",
        "wrong": {
            "1": "Это результат без keepends. Флаг как раз оставляет переводы строк.",
            "2": "splitlines не добавляет перевод строки туда, где его не было: после 'b' его нет.",
            "3": "Перевод строки остаётся частью своей строки, а не становится отдельным элементом.",
        },
        "src": [STR_SRC + "#str.splitlines"],
    },
]
