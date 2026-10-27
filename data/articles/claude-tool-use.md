---
title: Вызов инструментов (tool use) в Claude
source: Документация Claude (Anthropic), «Tool use with Claude»
original: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
kind: пересказ
license: Пересказ страницы своими словами. Примеры кода — из документации, комментарии переведены.
---
**Tool use** (другое название — **function calling**, вызов функций) позволяет модели вызывать функции. Функции описываете вы, или их даёт Anthropic.

Как это работает в общих чертах:

1. Вы передаёте модели список инструментов: имя, описание и схему аргументов.
2. Модель сама решает, нужен ли инструмент. Она смотрит на запрос пользователя и на описание инструмента.
3. Если нужен — модель возвращает **структурированный вызов**: имя инструмента и аргументы в JSON.
4. Вызов выполняет ваше приложение (**клиентские инструменты**) или Anthropic (**серверные инструменты**).

## Где выполняется инструмент

Главное отличие инструментов — где работает их код.

**Клиентские инструменты** работают в вашем приложении. Это ваши собственные функции и инструменты со схемой от Anthropic (например, `bash` и `text_editor`). Порядок такой:

- модель отвечает с `stop_reason: "tool_use"` и одним или несколькими блоками `tool_use`;
- ваш код выполняет операцию;
- ваш код отправляет модели блок `tool_result` с результатом.

**Серверные инструменты** (`web_search`, `web_fetch`, `code_execution`, `tool_search`) работают на инфраструктуре Anthropic. Вы сразу получаете результат, код-обработчик не нужен.

Пример с серверным инструментом — поиск в интернете:

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
    messages=[{"role": "user", "content": "What's the latest on the Mars rover?"}],
)
print(response.content)
```

Claude выполняет поиск у Anthropic и возвращает результаты со ссылками в том же ответе.

## Полный цикл для клиентского инструмента

Это главный пример страницы. Первый запрос описывает инструмент `get_weather`. Claude отвечает вызовом этого инструмента (блок `tool_use`). Ваш код узнаёт погоду. Второй запрос отправляет результат в блоке `tool_result`, и Claude пишет ответ.

```python
import json
import anthropic

client = anthropic.Anthropic()
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
        },
    }
]
messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]
# Claude отвечает блоком tool_use: имя инструмента и аргументы.
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=tools,
    # Не больше одного вызова инструмента за ход.
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)
tool_use = next(block for block in response.content if block.type == "tool_use")
print(f"Claude called {tool_use.name} with {json.dumps(tool_use.input)}")
# Выполняем инструмент и отправляем результат в блоке tool_result.
weather = "15 degrees Celsius, partly cloudy"  # здесь ваш запрос погоды
messages += [
    {"role": "assistant", "content": response.content},
    {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": tool_use.id, "content": weather}
        ],
    },
]
followup = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)
# Claude отвечает на исходный вопрос с учётом результата.
final_text = next(block for block in followup.content if block.type == "text")
print(final_text.text)
```

Вывод:

```text
Claude called get_weather with {"location": "San Francisco, CA"}
The current weather in San Francisco is 15 degrees Celsius with partly cloudy skies.
```

Обратите внимание на три детали:

- ответ модели (`response.content`) добавляется в историю как сообщение `assistant`;
- результат идёт в сообщении `user` в блоке `tool_result`;
- `tool_use_id` связывает результат с конкретным вызовом.

Если модель вызывает несколько инструментов сразу, это **параллельные вызовы** — у документации есть отдельная страница о них. Чтобы не писать этот цикл самому, есть **tool runner** в SDK: он сам выполняет ваши инструменты и отправляет результаты.

Для подключения к серверам MCP (Model Context Protocol) есть **MCP connector**.

## Когда Claude вызывает инструменты

По умолчанию `tool_choice` равен `{"type": "auto"}`. Тогда Claude на каждом ходе решает сам: вызвать инструмент или ответить сразу.

- **Вызывает инструмент**, если запрос подходит под описание инструмента и ответа ещё нет в контексте.
- **Отвечает сразу** на вопросы о стабильных знаниях, творческие задачи и обычные реплики разговора.

Эту границу можно сдвигать системным промптом:

- мягко больше вызовов: `"Use the tools to investigate before responding."`;
- сильнее: `"Always call a tool first before responding."`;
- осторожнее: `"Use your judgment about whether to call a tool or respond directly."`.

Чтобы **гарантировать** вызов инструмента, а не просить о нём в промпте, задайте параметр `tool_choice`.

**Если не хватает аргументов.** Иногда в запросе пользователя нет данных для обязательного параметра. Claude Opus скорее заметит это и переспросит. Claude Sonnet может переспросить, особенно если попросить его подумать перед вызовом. Но может и подставить правдоподобное значение сам.

Пример: инструмент `get_weather` требует `location`, а пользователь спрашивает просто «Какая погода?». Модель может придумать город:

```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "get_weather",
  "input": { "location": "New York, NY", "unit": "fahrenheit" }
}
```

Поведение не гарантировано, особенно при неоднозначных запросах и у менее сильных моделей.

## Какие бывают инструменты

**Ваши собственные инструменты.** Схему пишете вы, каждый вызов выполняет ваше приложение. Нужно:

- задать схему и хорошее описание, решить, когда модель их вызывает;
- разобрать блоки `tool_use`, сформировать `tool_result`, обработать ошибки.

**Клиентские инструменты со схемой Anthropic.** Схему публикует Anthropic и обучает на ней Claude. Выполняет вызовы всё равно ваше приложение. Примеры:

- память — хранение информации между разговорами в ваших файлах;
- bash — команды оболочки в постоянной сессии;
- текстовый редактор — просмотр и правка файлов;
- управление компьютером — скриншоты, мышь и клавиатура;
- браузер — переход по страницам и работа с ними.

**Серверные инструменты.** Работают у Anthropic, код-обработчик не нужен:

- поиск в интернете со ссылками на источники;
- загрузка страниц и PDF целиком;
- выполнение Python и Bash в песочнице;
- консультация более сильной модели-советника посреди генерации;
- поиск инструментов — работа с тысячами инструментов, которые загружаются по требованию;
- MCP connector — подключение к удалённым серверам MCP без отдельного клиента.

## Цена

Запрос с инструментами оплачивается за:

1. все входные токены, включая параметр `tools`;
2. выходные токены;
3. для серверных инструментов — дополнительно за использование (например, за каждый поиск).

Дополнительные токены дают:

- параметр `tools` — имена, описания и схемы инструментов;
- блоки `tool_use` в запросах и ответах;
- блоки `tool_result` в запросах.

Кроме того, при наличии `tools` API сам добавляет специальный системный промпт для работы с инструментами. Это ещё примерно 260–800 токенов в зависимости от модели и от `tool_choice` (`any` и `tool` дороже, чем `auto` и `none`). Точные числа — в таблице на странице оригинала.

Количество входных и выходных токенов каждого запроса видно в поле `usage` ответа.
