---
title: Ruff — учебник
source: Документация Ruff, «Tutorial»
original: https://docs.astral.sh/ruff/tutorial/
kind: перевод
license: MIT, Astral
---
Этот учебник показывает, как подключить к проекту линтер и форматтер Ruff. Подробный обзор настроек — в разделе [Configuring Ruff](https://docs.astral.sh/ruff/configuration/).

## Начало

Создадим проект с помощью [uv](https://docs.astral.sh/uv/):

```console
$ uv init --lib numbers
```

Команда создаёт проект с такой структурой:

```text
numbers
  ├── README.md
  ├── pyproject.toml
  └── src
      └── numbers
          ├── __init__.py
          └── py.typed
```

Перейдите в папку проекта:

```console
$ cd numbers
```

Очистим автоматически созданный `src/numbers/__init__.py` и создадим `src/numbers/calculate.py` с таким кодом:

```python
from typing import Iterable

import os


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(
        num for num in numbers
        if num % 2 == 0
    )
```

Добавим Ruff в проект:

```console
$ uv add --dev ruff
```

Запустим линтер Ruff по проекту через `uv run ruff check`:

```console
$ uv run ruff check
src/numbers/calculate.py:3:8: F401 [*] `os` imported but unused
Found 1 error.
[*] 1 fixable with `--fix`.
```

> Примечание. Вместо `uv run` можно активировать виртуальное окружение проекта (`source .venv/bin/activate` в Linux и macOS, `.venv\Scripts\activate` в Windows) и запускать `ruff check` напрямую.

Ruff нашёл неиспользуемый импорт — частую ошибку в коде Python. Ruff считает эту ошибку «исправимой», поэтому её можно исправить автоматически командой `ruff check --fix`:

```console
$ uv run ruff check --fix
Found 1 error (1 fixed, 0 remaining).
```

`git diff` покажет изменение:

```diff
--- a/src/numbers/calculate.py
+++ b/src/numbers/calculate.py
@@ -1,7 +1,5 @@
 from typing import Iterable

-import os
-

def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(
        num for num in numbers
        if num % 2 == 0
    )
```

По умолчанию Ruff проверяет текущую папку. Можно передать конкретные пути:

```console
$ uv run ruff check src/numbers/calculate.py
```

Проект проходит `ruff check`. Теперь запустим форматтер Ruff через `ruff format`:

```console
$ uv run ruff format
1 file reformatted
```

`git diff` показывает: вызов `sum` переформатирован, чтобы влезть в предел длины строки по умолчанию — 88 символов:

```diff
--- a/src/numbers/calculate.py
+++ b/src/numbers/calculate.py
@@ -3,7 +3,4 @@ from typing import Iterable

 def sum_even_numbers(numbers: Iterable[int]) -> int:
     """Given an iterable of integers, return the sum of all even numbers in the iterable."""
-    return sum(
-        num for num in numbers
-        if num % 2 == 0
-    )
+    return sum(num for num in numbers if num % 2 == 0)
```

До сих пор мы использовали настройки Ruff по умолчанию. Теперь посмотрим, как их изменить.

## Настройка

Для каждого файла Python Ruff ищет первый файл `pyproject.toml`, `ruff.toml` или `.ruff.toml` в папке файла или в любой родительской папке.

Добавим в файл настроек в корне проекта такие строки.

Вариант для `pyproject.toml`:

```toml
[tool.ruff]
# Максимальная длина строки — 79.
line-length = 79

[tool.ruff.lint]
# Добавить правило line-too-long. По умолчанию Ruff не включает правила,
# которые пересекаются с форматтером (например, Black), но правило можно
# включить явно.
extend-select = ["E501"]
```

Вариант для `ruff.toml`:

```toml
# Максимальная длина строки — 79.
line-length = 79

[lint]
# Добавить правило line-too-long.
extend-select = ["E501"]
```

Запустим Ruff снова. Теперь он проверяет длину строки с пределом 79:

```console
$ uv run ruff check
src/numbers/calculate.py:5:80: E501 Line too long (90 > 79)
Found 1 error.
```

Полный список настроек — в разделе [Settings](https://docs.astral.sh/ruff/settings/). Для нашего проекта важно указать минимальную поддерживаемую версию Python.

`pyproject.toml`:

```toml
[project]
# Поддержка Python 3.10+.
requires-python = ">=3.10"

[tool.ruff]
# Максимальная длина строки — 79.
line-length = 79

[tool.ruff.lint]
# Добавить правило line-too-long.
extend-select = ["E501"]
```

`ruff.toml`:

```toml
# Поддержка Python 3.10+.
target-version = "py310"
# Максимальная длина строки — 79.
line-length = 79

[lint]
# Добавить правило line-too-long.
extend-select = ["E501"]
```

### Выбор правил

Ruff поддерживает [больше 900 правил](https://docs.astral.sh/ruff/rules/) из более чем 50 встроенных плагинов. Нужный набор правил зависит от проекта: одни правила слишком строгие, другие относятся к конкретному фреймворку и так далее.

По умолчанию Ruff включает правила из категорий `F`, `E`, `B`, `UP`, `RUF` и многих других. Он не включает стилистические правила, которые пересекаются с форматтером (`ruff format` или [Black](https://github.com/psf/black)).

Если вы впервые подключаете линтер, **набор правил по умолчанию — хорошее начало**. Без всякой настройки он находит много частых ошибок, например неиспользуемые импорты. Полный список — в разделе [Default Rules](https://docs.astral.sh/ruff/default-rules/).

> К учебному плану: правило `B006` находит изменяемое значение по умолчанию (`def f(x=[])`), правило `B023` — функцию в цикле, которая читает переменную цикла (`[lambda: i for i in range(3)]`). *(Примечание переводчика.)*

Если вы переходите на Ruff с другого линтера, включите правила, равные прежним. Например, чтобы включить правила pyupgrade, настройте файл так.

`pyproject.toml`:

```toml
[project]
requires-python = ">=3.10"

[tool.ruff.lint]
extend-select = [
  "UP",  # pyupgrade
]
```

`ruff.toml`:

```toml
target-version = "py310"

[lint]
extend-select = [
  "UP",  # pyupgrade
]
```

Запустим Ruff снова. Теперь он применяет правила pyupgrade. В частности, он отмечает устаревший `typing.Iterable` вместо `collections.abc.Iterable`:

```console
$ uv run ruff check
src/numbers/calculate.py:1:1: UP035 [*] Import from `collections.abc` instead: `Iterable`
Found 1 error.
[*] 1 fixable with `--fix`.
```

Со временем можно включать новые правила. Например, потребовать docstring у всех функций.

`pyproject.toml`:

```toml
[project]
requires-python = ">=3.10"

[tool.ruff.lint]
extend-select = [
  "UP",  # pyupgrade
  "D",   # pydocstyle
]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

`ruff.toml`:

```toml
target-version = "py310"

[lint]
extend-select = [
  "UP",  # pyupgrade
  "D",   # pydocstyle
]

[lint.pydocstyle]
convention = "google"
```

Запустим Ruff снова. Теперь он применяет правила pydocstyle:

```console
$ uv run ruff check
src/numbers/__init__.py:1:1: D104 Missing docstring in public package
src/numbers/calculate.py:1:1: UP035 [*] Import from `collections.abc` instead: `Iterable`
  |
1 | from typing import Iterable
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP035
  |
  = help: Import from `collections.abc`

src/numbers/calculate.py:1:1: D100 Missing docstring in public module
Found 3 errors.
[*] 1 fixable with `--fix`.
```

### Как игнорировать ошибки

Любое правило можно отключить для строки комментарием `# noqa`. Например, отключим правило `UP035` для импорта `Iterable`:

```python
from typing import Iterable  # noqa: UP035


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(num for num in numbers if num % 2 == 0)
```

`ruff check` больше не отмечает импорт `Iterable`:

```console
$ uv run ruff check
src/numbers/__init__.py:1:1: D104 Missing docstring in public package
src/numbers/calculate.py:1:1: D100 Missing docstring in public module
Found 2 errors.
```

Чтобы отключить правило для всего файла, добавьте строку `# ruff: noqa: {код}` в любое место файла, лучше в начало:

```python
# ruff: noqa: UP035
from typing import Iterable


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(num for num in numbers if num % 2 == 0)
```

Подробнее — в разделе [Error suppression](https://docs.astral.sh/ruff/linter/#error-suppression).

### Новое правило в старом коде

Когда вы включаете новое правило в существующем коде, бывает удобно пропустить все *старые* нарушения и проверять правило только в новом коде.

Для этого есть флаг `--add-noqa`: он добавляет `# noqa` в каждую строку с нарушением. Вместе с флагом `--select` он добавит `# noqa` ко всем текущим нарушениям `UP035`:

```console
$ uv run ruff check --select UP035 --add-noqa .
Added 1 noqa directive.
```

`git diff` покажет:

```diff
--- a/numbers/src/numbers/calculate.py
+++ b/numbers/src/numbers/calculate.py
@@ -1,4 +1,4 @@
-from typing import Iterable
+from typing import Iterable  # noqa: UP035
```

Чтобы вместо этого добавить комментарии `# ruff: ignore[...]`, используйте флаг `--add-ignore`. В режиме preview `--add-ignore` пишет понятные имена правил вместо кодов.

## Интеграции

Учебник показал командную строку Ruff. Ruff можно запускать и как хук [pre-commit](https://pre-commit.com) через [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Версия Ruff.
  rev: v0.17.3
  hooks:
    # Запуск линтера.
    - id: ruff-check
    # Запуск форматтера.
    - id: ruff-format
```

Ruff также встраивается в редакторы кода — см. раздел [Editors](https://docs.astral.sh/ruff/editors/).
