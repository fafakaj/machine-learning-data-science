"""Week 7 content: FastAPI, Pydantic, Docker, CI, git, Linux."""

from textwrap import dedent as d

QUIZZES = {
    "q-w7-api": {
        "title": "FastAPI и Pydantic",
        "questions": [
            {"type": "choice", "q": "Клиент прислал в `/predict` строку вместо числа. Что вернёт FastAPI с Pydantic-моделью запроса?",
             "options": ["500 Internal Server Error", "422 Unprocessable Entity с описанием, какое поле не прошло валидацию", "200 и пустой ответ", "404"],
             "answer": 1},
            {"type": "choice", "q": "`@app.get(\"/items/{item_id}\")` и функция `def read(item_id: int, q: str | None = None)`. Чем являются `item_id` и `q`?",
             "options": ["Оба — тело запроса", "`item_id` — параметр пути, `q` — необязательный query-параметр (`?q=…`)", "Оба — заголовки", "`q` — параметр пути"],
             "answer": 1},
            {"type": "choice", "q": "Где загружать ML-модель в сервисе на FastAPI?",
             "options": ["Внутри обработчика при каждом запросе", "Один раз при старте приложения (lifespan) и хранить в памяти", "В браузере клиента", "В Dockerfile через RUN"],
             "answer": 1},
            {"type": "choice", "q": "Зачем `response_model` у эндпоинта?",
             "options": ["Ускоряет модель", "Валидирует и фильтрует ответ, описывает схему в OpenAPI (/docs)", "Нужен для GET", "Шифрует ответ"], "answer": 1},
            {"type": "choice", "q": "Обработчик `async def` вызывает тяжёлый синхронный `model.predict` (CPU 2 с). Что произойдёт под нагрузкой?",
             "options": ["Всё параллельно", "Цикл событий блокируется — другие запросы ждут. Лучше обычный `def` (FastAPI запустит его в пуле потоков) или отдельный воркер",
                         "Запрос отменится", "Модель ускорится"], "answer": 1},
            {"type": "choice", "q": "Как тестировать FastAPI-приложение в pytest без запуска сервера?",
             "options": ["Только вручную через curl", "`TestClient(app)` и `client.post(\"/predict\", json=...)`", "Нельзя", "Через Docker"], "answer": 1},
        ],
    },
    "q-w7-docker": {
        "title": "Docker и docker-compose",
        "questions": [
            {"type": "choice", "q": "Образ и контейнер:",
             "options": ["Одно и то же", "Образ — неизменяемый шаблон из слоёв; контейнер — запущенный экземпляр образа со своим записываемым слоем", "Контейнер — это файл Dockerfile", "Образ — это виртуальная машина"],
             "answer": 1},
            {"type": "choice", "q": "Почему в Dockerfile сначала `COPY requirements.txt` и `RUN pip install`, а потом `COPY . .`?",
             "options": ["Так требует синтаксис", "Кэш слоёв: при изменении кода зависимости не переустанавливаются", "Чтобы образ был больше", "Без разницы"],
             "answer": 1},
            {"type": "choice", "q": "Разница `RUN` и `CMD`:",
             "options": ["`RUN` выполняется при сборке образа, `CMD` — команда по умолчанию при запуске контейнера", "Одно и то же", "`CMD` при сборке", "`RUN` только в compose"],
             "answer": 0},
            {"type": "choice", "q": "Сервис `api` в docker-compose обращается к базе из сервиса `db`. Какой хост указать?",
             "options": ["localhost", "`db` — имя сервиса в сети compose", "IP хоста", "0.0.0.0"], "answer": 1},
            {"type": "choice", "q": "Контейнер удалили. Что стало с файлами, которые он писал не в volume?",
             "options": ["Сохранились в образе", "Пропали вместе с записываемым слоем контейнера", "Попали в Git", "Переехали в volume"], "answer": 1},
            {"type": "choice", "q": "`docker run -p 8000:80 img` означает:",
             "options": ["порт 8000 контейнера → 80 хоста", "порт 8000 хоста → порт 80 контейнера", "два контейнера", "лимит памяти"], "answer": 1},
        ],
    },
    "q-w7-git": {
        "title": "git, GitHub Actions, Linux",
        "questions": [
            {"type": "choice", "q": "`git reset --soft HEAD~1`:",
             "options": ["Удаляет изменения последнего коммита", "Отменяет последний коммит, изменения остаются в индексе (staged)", "Отменяет коммит, изменения в рабочей папке не в индексе", "Пушит на сервер"],
             "answer": 1, "explain": "`--mixed` (по умолчанию) — изменения остаются, но не в индексе. `--hard` — изменения удаляются."},
            {"type": "choice", "q": "Нужно отменить коммит, который уже в общей ветке `main`:",
             "options": ["`git reset --hard` и `push --force`", "`git revert <sha>` — новый коммит с обратными изменениями, история не переписывается", "Удалить репозиторий", "`git rebase -i`"],
             "answer": 1},
            {"type": "choice", "q": "`git rebase main` на своей ветке делает:",
             "options": ["Слияние с коммитом слияния", "Переносит ваши коммиты поверх свежего `main` — история линейная, хэши коммитов меняются", "Удаляет ветку", "Пушит ветку"],
             "answer": 1, "explain": "Поэтому не делайте rebase ветки, которую уже используют другие."},
            {"type": "choice", "q": "Типичный CI для ML-сервиса на push:",
             "options": ["Только деплой", "lint (ruff) → тесты (pytest) → сборка Docker-образа", "Обучение модели на 10 ч", "Ничего"], "answer": 1},
            {"type": "choice", "q": "Команда `ps aux | grep uvicorn | wc -l` выводит:",
             "options": ["PID процесса", "число строк с «uvicorn» в списке процессов (включая сам grep)", "лог uvicorn", "ошибку"], "answer": 1},
            {"type": "choice", "q": "`chmod +x run.sh` делает:",
             "options": ["Удаляет файл", "Даёт право на выполнение", "Меняет владельца", "Шифрует файл"], "answer": 1},
        ],
    },
}

EXERCISES = {
    "ex-w7-validate": {
        "title": "Валидация запроса /predict (как Pydantic)",
        "statement_ru": d("""\
            Без FastAPI потренируйте логику эндпоинта. Напишите `handle_predict(payload: dict) -> (status, body)`:
            - нужны поля `age` (int, 0–120) и `income` (int или float, ≥ 0), `city` — необязательная строка;
            - `bool` — не число (как в Pydantic strict-режиме);
            - ошибка → `(422, {"detail": [{"loc": [<поле>], "msg": <текст>}, ...]})` — **все** ошибки сразу, в порядке `age`, `income`, `city`;
            - успех → `(200, {"score": round(0.01 * age + 0.001 * income, 3)})`."""),
        "starter_code": "def handle_predict(payload):\n    pass\n",
        "tests": d('''\
            def locs(body):
                return [e["loc"][0] for e in body["detail"]]

            def test_ok():
                """Верный запрос — 200 и score"""
                assert handle_predict({"age": 30, "income": 1000}) == (200, {"score": 1.3})
                assert handle_predict({"age": 30, "income": 10.5, "city": "Москва"})[0] == 200

            def test_missing():
                """Нет поля — 422"""
                status, body = handle_predict({"age": 30})
                assert status == 422 and locs(body) == ["income"]

            def test_types_and_ranges():
                """Неверный тип и диапазон — все ошибки сразу"""
                status, body = handle_predict({"age": "30", "income": -1, "city": 5})
                assert status == 422 and locs(body) == ["age", "income", "city"]
                assert all(isinstance(e["msg"], str) and e["msg"] for e in body["detail"])

            def test_bool_is_not_int():
                """True — не возраст"""
                assert handle_predict({"age": True, "income": 1})[0] == 422
                assert handle_predict({"age": 121, "income": 1})[0] == 422
            '''),
        "ref": d("""\
            def handle_predict(payload):
                errors = []

                def is_num(v, kinds):
                    return isinstance(v, kinds) and not isinstance(v, bool)

                age = payload.get("age")
                if "age" not in payload:
                    errors.append({"loc": ["age"], "msg": "обязательное поле"})
                elif not is_num(age, int) or not 0 <= age <= 120:
                    errors.append({"loc": ["age"], "msg": "целое число от 0 до 120"})
                income = payload.get("income")
                if "income" not in payload:
                    errors.append({"loc": ["income"], "msg": "обязательное поле"})
                elif not is_num(income, (int, float)) or income < 0:
                    errors.append({"loc": ["income"], "msg": "неотрицательное число"})
                if "city" in payload and not isinstance(payload["city"], str):
                    errors.append({"loc": ["city"], "msg": "строка"})
                if errors:
                    return 422, {"detail": errors}
                return 200, {"score": round(0.01 * age + 0.001 * income, 3)}
        """),
        "hints_ru": [
            "Клиент отправил запрос с тремя ошибками. Сколько раз ему придётся исправлять запрос, если вы вернёте только первую ошибку? Чему равно `isinstance(True, int)`?",
            "Копите ошибки в списке и возвращайте 422 один раз в конце. `bool` — подкласс `int` в Python, поэтому `True` прошёл бы проверку на число; исключайте его явно: `isinstance(v, int) and not isinstance(v, bool)`.",
            "1) `errors = []`. 2) `age`: нет поля — ошибка «обязательное поле»; не целое или вне 0–120 — другая ошибка. 3) `income`: так же, число `int`/`float`, ≥ 0. 4) `city`: есть, но не `str` — ошибка. 5) `errors` не пуст — `(422, {\"detail\": errors})`; иначе `(200, {\"score\": round(...)})`. Порядок проверок задаёт порядок ошибок.",
        ],
    },
}
