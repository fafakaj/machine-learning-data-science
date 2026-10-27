---
title: uv — работа с проектами
source: Документация uv, руководство «Working on projects»
original: https://docs.astral.sh/uv/guides/projects/
kind: перевод
license: MIT / Apache-2.0, Astral
---
uv управляет Python-проектами. Проект описывает свои зависимости в файле `pyproject.toml`.

## Новый проект

Создайте проект командой `uv init`:

```console
$ uv init hello-world
$ cd hello-world
```

Или создайте проект в текущей папке:

```console
$ mkdir hello-world
$ cd hello-world
$ uv init
```

uv создаст такие файлы и папки:

```text
├── .git/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── src
    └── hello_world
        └── __init__.py
```

В `pyproject.toml` есть точка входа `hello-world`. Она ведёт на простую программу «Hello world» в `__init__.py`. Запустите её через `uv run`:

```console
$ uv run hello-world
Hello from hello-world!
```

## Структура проекта

Проект состоит из нескольких важных частей. Вместе они позволяют uv управлять проектом.

Кроме файлов от `uv init`, uv создаст в корне проекта виртуальное окружение и файл `uv.lock`. Это случится при первой команде проекта: `uv run`, `uv sync` или `uv lock`.

Полный список выглядит так:

```text
.
├── .git/
├── .venv/
│   ├── bin
│   ├── lib
│   └── pyvenv.cfg
├── .gitignore
├── .python-version
├── README.md
├── src
│   └── hello_world
│       └── __init__.py
├── pyproject.toml
└── uv.lock
```

### pyproject.toml

`pyproject.toml` хранит метаданные проекта:

```toml
[project]
name = "hello-world"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
  { name = "ferris", email = "ferris@example.org" }
]
requires-python = ">=3.14"
dependencies = []

[project.scripts]
hello-world = "hello_world:main"

[build-system]
requires = ["uv_build>=0.13.6,<0.14"]
build-backend = "uv_build"
```

В этом файле вы указываете зависимости и сведения о проекте: описание, лицензию. Файл можно править вручную или командами `uv add` и `uv remove` из терминала.

> Совет. Подробнее о формате — в официальном [руководстве по pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

В этом же файле задаются настройки самого uv — в разделе `[tool.uv]`.

### .python-version

Файл `.python-version` хранит версию Python по умолчанию для проекта. По нему uv выбирает версию Python, когда создаёт виртуальное окружение проекта.

### .venv

Папка `.venv` — виртуальное окружение проекта. Это окружение Python, изолированное от остальной системы. Сюда uv ставит зависимости проекта.

### uv.lock

`uv.lock` — кроссплатформенный lock-файл с точной информацией о зависимостях проекта. `pyproject.toml` задаёт общие требования. А lock-файл хранит точные версии, которые выбрал uv и которые установлены в окружении проекта.

Добавьте этот файл в систему контроля версий. Тогда установка будет одинаковой и воспроизводимой на всех компьютерах.

`uv.lock` — читаемый файл TOML. Но им управляет uv, и вручную его править не нужно.

## Зависимости

Добавьте зависимость в `pyproject.toml` командой `uv add`. Она также обновит lock-файл и окружение проекта:

```console
$ uv add requests
```

Можно указать ограничение версии или другой источник:

```console
$ # Ограничение версии
$ uv add 'requests==2.31.0'

$ # Зависимость из git
$ uv add git+https://github.com/psf/requests
```

Если вы переходите с `requirements.txt`, добавьте все зависимости из него флагом `-r`:

```console
$ # Все зависимости из requirements.txt
$ uv add -r requirements.txt -c constraints.txt
```

Удалить пакет — `uv remove`:

```console
$ uv remove requests
```

Обновить пакет — `uv lock` с флагом `--upgrade-package`:

```console
$ uv lock --upgrade-package requests
```

Флаг `--upgrade-package` пытается обновить пакет до последней совместимой версии. Остальной lock-файл не меняется.

> Для учебных проектов: зависимости для разработки (pytest, ruff) добавляйте с флагом `--dev`: `uv add --dev pytest ruff`. *(Примечание переводчика.)*

## Версия пакета

Команда `uv version` показывает версию вашего пакета:

```console
$ uv version
hello-world 0.7.0
```

Версия без имени пакета — опция `--short`:

```console
$ uv version --short
0.7.0
```

Версия в формате JSON — опция `--output-format json`:

```console
$ uv version --output-format json
{
    "package_name": "hello-world",
    "version": "0.7.0",
    "commit_info": null
}
```

## Запуск команд

`uv run` запускает любой скрипт или команду в окружении проекта.

Перед каждым `uv run` uv проверяет две вещи:

- lock-файл соответствует `pyproject.toml`;
- окружение соответствует lock-файлу.

Так проект всегда синхронизирован, и вручную ничего делать не нужно. `uv run` гарантирует: команда работает в окружении со всеми нужными зависимостями точных версий.

> Примечание. По умолчанию `uv run` не удаляет из окружения лишние пакеты (которых нет в lock-файле).

Пример с `flask`:

```console
$ uv add flask
$ uv run -- flask run -p 3000
```

Или запуск скрипта:

```python
# example.py
# Нужна зависимость проекта
import flask

print("hello world")
```

```console
$ uv run example.py
```

Другой способ — вручную обновить окружение через `uv sync`, активировать его и запускать команды.

macOS и Linux:

```console
$ uv sync
$ source .venv/bin/activate
$ flask run -p 3000
$ python example.py
```

Windows:

```console
PS> uv sync
PS> .venv\Scripts\activate
PS> flask run -p 3000
PS> python example.py
```

> Примечание. Без `uv run` окружение должно быть активно. Способ активации зависит от оболочки и платформы.

## Сборка дистрибутивов

`uv build` собирает дистрибутивы проекта: исходный (sdist) и бинарный (wheel).

По умолчанию `uv build` собирает проект из текущей папки и кладёт результат в подпапку `dist/`:

```console
$ uv build
$ ls dist/
hello_world-0.1.0-py3-none-any.whl
hello_world-0.1.0.tar.gz
```

## Что дальше

Подробнее о проектах в uv — на странице [Projects](https://docs.astral.sh/uv/concepts/projects/) и в [справочнике команд](https://docs.astral.sh/uv/reference/cli/#uv).
