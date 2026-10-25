# Machine Learning / Data Science

Учебная дорожка: 13 недель от Python и математики до ML, LLM и RAG.
Сайт: https://fafakaj.github.io/machine-learning-data-science/

- План разбит на недели и блоки. Сайт показывает один шаг «сейчас».
- Задачи LeetCode и упражнения на Python проверяются прямо в браузере (Pyodide).
- Квизы, повторение по карточкам (удобно с телефона), журнал прогресса.
- Прогресс хранится в аккаунте (секретный gist), вход по паролю.

## Запуск у себя

```
python3 server.py --open
```

Без сервера (локально) прогресс пишется в `../logs/progress.json`.

## Сборка данных

```
bash tools/build_all.sh            # квизы, упражнения, план, покрытие плана
bash tools/build_all.sh --problems # + задачи (≈ 4 мин)
bash tests/run_e2e.sh              # проверки в браузере (Playwright)
```
