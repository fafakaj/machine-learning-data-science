---
title: Jupyter — с чего начать
source: Документация Project Jupyter, «Try Jupyter» и «Running the Notebook»
original: https://docs.jupyter.org/en/latest/start/index.html
kind: перевод
license: BSD-3-Clause, Project Jupyter
---
Здесь описано несколько способов начать работу с самыми популярными инструментами экосистемы Jupyter.

## Попробовать в браузере, без установки

**Try Jupyter** ([try.jupyter.org](https://try.jupyter.org)) — сайт, где можно попробовать Jupyter Notebook без установки. На нём есть ядра для нескольких языков: Julia, R, C++, Scheme, Ruby.

На сайте Try Jupyter вы получаете временный сервер Jupyter на mybinder.org. Им можно пользоваться, пока не закроете вкладку браузера.

На этом сайте можно попробовать основные интерактивные интерфейсы, которые создало сообщество Jupyter.

### Классический интерфейс Notebook

*Classic Notebook* — интерфейс в виде документа. В нём вы создаёте, смотрите и выполняете код в блокноте Jupyter.

Он состоит из двух экранов:

- **Notebook Dashboard** (панель блокнотов) — список блокнотов, файлов и папок;
- **Notebook Editor** (редактор блокнота) — ячейки с кодом и текстом.

### Интерфейс JupyterLab

*JupyterLab* — более расширяемый и гибкий интерфейс для сложной работы. В одном окне можно открыть блокноты, терминал, текстовые файлы и просмотр данных рядом друг с другом.

## Следующий шаг: установить Jupyter у себя

Если Jupyter понравился, установите его на компьютер по [руководству по установке](https://docs.jupyter.org/en/latest/install.html).

> В проекте на uv удобно так: `uv add --dev jupyterlab`, затем `uv run jupyter lab`. Так Jupyter работает в окружении проекта и видит все его зависимости. *(Примечание переводчика.)*

## Запуск блокнота

*(Перевод страницы «Running the Notebook».)*

### Основные шаги

1. Запустите сервер блокнотов из командной строки:

```console
jupyter notebook
```

2. Блокнот откроется в браузере.

### Запуск сервера

Когда Jupyter Notebook установлен, можно запустить сервер блокнотов. Откройте командную строку (Terminal в Mac и Linux, Command Prompt в Windows) и выполните:

```console
jupyter notebook
```

В терминал будет выведена информация о сервере, в том числе адрес веб-приложения (по умолчанию `http://localhost:8888`):

```console
$ jupyter notebook
[I 08:58:24.417 NotebookApp] Serving notebooks from local directory: /Users/catherine
[I 08:58:24.417 NotebookApp] 0 active kernels
[I 08:58:24.417 NotebookApp] The Jupyter Notebook is running at: http://localhost:8888/
[I 08:58:24.417 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```

Потом откроется браузер по умолчанию с этим адресом.

В браузере вы увидите панель блокнотов (Notebook Dashboard). Она показывает блокноты, файлы и подпапки той папки, где запущен сервер. Обычно сервер запускают в самой верхней папке с блокнотами. Часто это домашняя папка.

### Опции командной строки

Открыть конкретный блокнот (в запущенном сервере, а если сервера нет — запустить его):

```console
jupyter notebook notebook.ipynb
```

Запустить на другом порту. По умолчанию сервер занимает порт 8888. Если порт занят, сервер ищет следующий свободный. Порт можно задать вручную, например 9999:

```console
jupyter notebook --port 9999
```

Запустить сервер, не открывая браузер:

```console
jupyter notebook --no-browser
```

Справка по всем опциям сервера:

```console
jupyter notebook --help
```
