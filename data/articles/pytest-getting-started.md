---
title: pytest — начало работы
source: Документация pytest, «Get Started»
original: https://docs.pytest.org/en/stable/getting-started.html
kind: перевод
license: MIT
---
## Установка pytest

Ставьте `pytest` в виртуальное окружение, а не в Python операционной системы.

1. Создайте виртуальное окружение и установите в него `pytest` удобным инструментом.

**venv и pip.** Они входят в Python. Некоторые дистрибутивы Linux ставят их отдельно (например, `python3-venv` в Debian и Ubuntu).

```console
python3 -m venv .venv
source .venv/bin/activate   # в Windows: .venv\Scripts\activate
pip install -U pytest
```

**uv.** [uv](https://docs.astral.sh/uv/) сам создаёт виртуальное окружение проекта и управляет им. В папке с `pyproject.toml` (его создаёт `uv init`) выполните:

```console
uv add --dev pytest
```

Команды `pytest` на этой странице запускайте с префиксом `uv run`, например `uv run pytest`. Тогда они работают в окружении проекта.

**virtualenv.** [virtualenv](https://virtualenv.pypa.io/en/stable/index.html) — более быстрая и гибкая замена `venv`:

```console
virtualenv .venv
source .venv/bin/activate   # в Windows: .venv\Scripts\activate
pip install -U pytest
```

2. Проверьте, что установлена нужная версия:

```console
$ pytest --version
pytest 9.2.0
```

## Первый тест

Создайте файл `test_sample.py` с функцией и тестом:

```python
# файл test_sample.py
def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5
```

Запустите тест:

```console
$ pytest
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
rootdir: /home/sweet/project
collected 1 item

test_sample.py F                                                     [100%]

================================= FAILURES =================================
_______________________________ test_answer ________________________________

    def test_answer():
>       assert func(3) == 5
E       assert 4 == 5
E        +  where 4 = func(3)

test_sample.py:6: AssertionError
========================= short test summary info ==========================
FAILED test_sample.py::test_answer - assert 4 == 5
============================ 1 failed in 0.12s =============================
```

`[100%]` — общий прогресс выполнения всех тестов. После прогона pytest показывает отчёт об ошибке: `func(3)` не возвращает `5`.

> Примечание. Ожидания в тесте проверяйте обычной инструкцией `assert`. pytest умно показывает промежуточные значения выражения в `assert`. Поэтому не нужны многочисленные методы в стиле JUnit (`assertEqual` и т. п.).

## Несколько тестов

`pytest` запускает все файлы вида `test_*.py` или `*_test.py` в текущей папке и её подпапках. В целом он следует [стандартным правилам поиска тестов](https://docs.pytest.org/en/stable/explanation/goodpractices.html#test-discovery).

## Проверка, что код бросает исключение

Используйте помощник `pytest.raises`:

```python
# файл test_sysexit.py
import pytest


def f():
    raise SystemExit(1)


def test_mytest():
    with pytest.raises(SystemExit):
        f()
```

Запустите тест в «тихом» режиме отчёта:

```console
$ pytest -q test_sysexit.py
.                                                                    [100%]
1 passed in 0.12s
```

> Примечание. Флаг `-q` / `--quiet` делает вывод коротким в этом и следующих примерах.

## Группа тестов в классе

Когда тестов много, их удобно сгруппировать в класс. В pytest это просто:

```python
# файл test_class.py
class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")
```

`pytest` находит тесты по своим правилам, поэтому найдёт обе функции с префиксом `test_`. Наследоваться ни от чего не нужно. Но имя класса должно начинаться с `Test`, иначе класс будет пропущен. Запустите модуль, передав имя файла:

```console
$ pytest -q test_class.py
.F                                                                   [100%]
================================= FAILURES =================================
____________________________ TestClass.test_two ____________________________

self = <test_class.TestClass object at 0xdeadbeef0001>

    def test_two(self):
        x = "hello"
>       assert hasattr(x, "check")
E       AssertionError: assert False
E        +  where False = hasattr('hello', 'check')

test_class.py:8: AssertionError
========================= short test summary info ==========================
FAILED test_class.py::TestClass::test_two - AssertionError: assert False
1 failed, 1 passed in 0.12s
```

Первый тест прошёл, второй упал. Промежуточные значения в `assert` помогают понять причину ошибки.

Группировка тестов в классы полезна:

- для порядка в тестах;
- чтобы общие фикстуры были только у тестов этого класса;
- чтобы метки на уровне класса применялись ко всем его тестам.

Учтите: у каждого теста свой экземпляр класса. Если бы тесты делили один экземпляр, это сильно мешало бы изоляции тестов и поощряло плохие практики. Пример:

```python
# файл test_class_demo.py
class TestClassDemoInstance:
    value = 0

    def test_one(self):
        self.value = 1
        assert self.value == 1

    def test_two(self):
        assert self.value == 1
```

```console
$ pytest -k TestClassDemoInstance -q
.F                                                                   [100%]
================================= FAILURES =================================
______________________ TestClassDemoInstance.test_two ______________________

self = <test_class_demo.TestClassDemoInstance object at 0xdeadbeef0002>

    def test_two(self):
>       assert self.value == 1
E       assert 0 == 1
E        +  where 0 = <test_class_demo.TestClassDemoInstance object at 0xdeadbeef0002>.value

test_class_demo.py:9: AssertionError
========================= short test summary info ==========================
FAILED test_class_demo.py::TestClassDemoInstance::test_two - assert 0 == 1
1 failed, 1 passed in 0.12s
```

Атрибуты, заданные на уровне класса, — это *атрибуты класса*. Они общие для всех тестов.

## Сравнение дробных чисел: pytest.approx

В `pytest` есть помощники, которые упрощают тесты. Например, `pytest.approx()` сравнивает дробные числа с маленькими ошибками округления:

```python
# файл test_approx.py
import pytest


def test_sum():
    assert (0.1 + 0.2) == pytest.approx(0.3)
```

Не нужно вручную задавать допуск или вызывать `math.isclose`. Это работает с числами, списками и массивами NumPy.

## Уникальная временная папка для теста

`pytest` даёт встроенные фикстуры (аргументы функции) для разных ресурсов, например уникальной временной папки:

```python
# файл test_tmp_path.py
def test_needsfiles(tmp_path):
    print(tmp_path)
    assert 0
```

Укажите имя `tmp_path` в сигнатуре теста. Перед вызовом теста `pytest` найдёт фикстуру и создаст ресурс — временную папку, уникальную для каждого запуска теста:

```console
$ pytest -q test_tmp_path.py
F                                                                    [100%]
================================= FAILURES =================================
_____________________________ test_needsfiles ______________________________

tmp_path = PosixPath('PYTEST_TMPDIR/test_needsfiles0')

    def test_needsfiles(tmp_path):
        print(tmp_path)
>       assert 0
E       assert 0

test_tmp_path.py:3: AssertionError
--------------------------- Captured stdout call ---------------------------
PYTEST_TMPDIR/test_needsfiles0
========================= short test summary info ==========================
FAILED test_tmp_path.py::test_needsfiles - assert 0
1 failed in 0.12s
```

Список встроенных фикстур показывает команда:

```console
pytest --fixtures   # встроенные и ваши фикстуры
```

Фикстуры с `_` в начале имени эта команда показывает только с опцией `-v`.

## Что читать дальше

- [How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html) — примеры запуска из командной строки;
- [How to mark test functions with attributes](https://docs.pytest.org/en/stable/how-to/mark.html) — метки `pytest.mark`, в том числе `parametrize`;
- [Fixtures reference](https://docs.pytest.org/en/stable/reference/fixtures.html) — фикстуры;
- [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) — окружения и структура тестов.
