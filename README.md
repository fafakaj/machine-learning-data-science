# Machine Learning / Data Science

Учебная дорожка: 13 недель от Python и математики до ML, LLM и RAG.
Сайт: https://fafakaj.github.io/machine-learning-data-science/

- План разбит на недели и блоки. Сайт показывает один шаг «сейчас».
- Задачи LeetCode и упражнения на Python проверяются прямо в браузере (Pyodide).
- Квизы, повторение по карточкам (удобно с телефона), журнал прогресса.
- Прогресс хранится в аккаунте (секретный gist), вход по паролю.

## Quiz ML

Викторина по Python для телефона: https://fafakaj.github.io/machine-learning-data-science/quiz.html

- 11 тем: сложность и методы `list`, `dict`, `set`, `str`; оценка сложности кода; параллелизм (что выбрать и теория).
- В каждой теме три режима: «Умные 10» (коробки Лейтнера), «Случайные 10», «Каталог». «Свой набор» — 20 вопросов из выбранных тем.
- После ответа — разбор: почему верно, в чём ошибка выбранного варианта, разбор остальных вариантов, источник.
- Ярлык на главный экран и работа без сети (`quiz.webmanifest`, `quiz-sw.js`). Прогресс — в том же аккаунте, ключ `pyquiz`.
- Банк вопросов — `tools/pyquiz/`. Сборка проверяет каждый ответ: покрытие всех методов, `assert` на CPython, таблицу TimeComplexity, замер сложности.

## Запуск у себя

```
python3 server.py --open
```

Без сервера (локально) прогресс пишется в `../logs/progress.json`.

## Сборка данных

```
bash tools/build_all.sh            # квизы, упражнения, план, покрытие плана
bash tools/build_all.sh --problems # + задачи (≈ 4 мин)
python3 tools/build_pyquiz.py      # банк Quiz ML (≈ 1 мин), входит в build_all.sh
python3 tools/test_pyquiz_checks.py # тесты проверок банка
node --test tests/unit/            # юнит-тесты: коробки Лейтнера, проверка ответа
bash tests/run_e2e.sh              # проверки в браузере (Playwright)
```
