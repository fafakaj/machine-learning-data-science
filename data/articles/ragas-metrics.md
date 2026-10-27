---
title: Метрики Ragas — Faithfulness и Context Recall
source: Документация Ragas, «Available metrics»: Faithfulness, Context Recall
original: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
kind: перевод
license: Apache-2.0, Exploding Gradients (Ragas).
---
Ragas — библиотека для оценки RAG-систем (поиск + генерация). Здесь переведены две метрики:

- **Faithfulness** (достоверность) — проверяет **генерацию**: не выдумывает ли ответ то, чего нет в найденном контексте;
- **Context Recall** (полнота контекста) — проверяет **поиск**: нашёл ли он всё нужное для правильного ответа.

## Faithfulness

Метрика **Faithfulness** показывает, насколько ответ (`response`) согласован по фактам с найденным контекстом (`retrieved context`). Значение от 0 до 1. Чем выше, тем лучше.

Ответ **достоверный**, если каждое его утверждение подтверждается найденным контекстом.

Как считается:

1. Найти все утверждения в ответе.
2. Для каждого утверждения проверить, следует ли оно из найденного контекста.
3. Посчитать оценку по формуле:

Faithfulness = (число утверждений ответа, подтверждённых контекстом) / (общее число утверждений в ответе)

### Пример

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

# Настройка LLM
client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)

# Создаём метрику
scorer = Faithfulness(llm=llm)

# Оцениваем
result = await scorer.ascore(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967",
    retrieved_contexts=[
        "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
    ]
)
print(f"Faithfulness Score: {result.value}")
```

Вывод:

```text
Faithfulness Score: 1.0
```

Для синхронного кода вместо `.ascore()` есть метод `.score()` с теми же аргументами.

### Как это вычисляется — разбор

**Вопрос:** где и когда родился Эйнштейн?

**Контекст:** «Альберт Эйнштейн (родился 14 марта 1879 года) — физик-теоретик немецкого происхождения, один из величайших и самых влиятельных учёных всех времён».

**Ответ с высокой достоверностью:** «Эйнштейн родился в Германии 14 марта 1879 года».

**Ответ с низкой достоверностью:** «Эйнштейн родился в Германии 20 марта 1879 года».

Посчитаем Faithfulness для второго ответа.

**Шаг 1.** Разбить ответ на отдельные утверждения:

- утверждение 1: «Эйнштейн родился в Германии»;
- утверждение 2: «Эйнштейн родился 20 марта 1879 года».

**Шаг 2.** Для каждого утверждения проверить, следует ли оно из контекста:

- утверждение 1: да;
- утверждение 2: нет (в контексте 14 марта).

**Шаг 3.** Посчитать по формуле: Faithfulness = 1 / 2 = 0,5.

### Старый API метрик

Старый API будет объявлен устаревшим в версии 0.4 и удалён в версии 1.0. Для новых проектов используйте API выше.

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import Faithfulness

sample = SingleTurnSample(
        user_input="When was the first super bowl?",
        response="The first superbowl was held on Jan 15, 1967",
        retrieved_contexts=[
            "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
        ]
    )
scorer = Faithfulness(llm=evaluator_llm)
await scorer.single_turn_ascore(sample)
```

Вывод: `1.0`.

### Faithfulness с моделью HHEM-2.1-Open

[HHEM-2.1-Open от Vectara](https://vectara.com/blog/hhem-2-1-a-better-hallucination-detection-model/) — модель-классификатор (T5), обученная находить галлюцинации в тексте LLM. Её можно использовать на шаге 2, когда утверждения сверяются с контекстом. Модель бесплатная, маленькая и открытая, поэтому экономна в продакшене.

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import FaithfulnesswithHHEM

sample = SingleTurnSample(
        user_input="When was the first super bowl?",
        response="The first superbowl was held on Jan 15, 1967",
        retrieved_contexts=[
            "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
        ]
    )
scorer = FaithfulnesswithHHEM(llm=evaluator_llm)
await scorer.single_turn_ascore(sample)
```

Аргумент `device` задаёт устройство, `batch_size` — размер батча. По умолчанию модель работает на CPU с батчем 10:

```python
my_device = "cuda:0"
my_batch_size = 10

scorer = FaithfulnesswithHHEM(device=my_device, batch_size=my_batch_size)
await scorer.single_turn_ascore(sample)
```

## Context Recall

**Context Recall** показывает, сколько релевантных документов (или фрагментов информации) поиск успешно нашёл. Метрика следит, чтобы **важное не потерялось**. Чем выше recall, тем меньше релевантных документов пропущено.

Раз метрика про «ничего не пропустить», для неё всегда нужен **эталон**, с которым сравнивают.

Версия на основе LLM использует эталонный ответ (`reference`) вместо эталонных контекстов (`reference_contexts`). Так проще: размечать эталонные контексты очень долго. Эталонный ответ разбивается на утверждения. Для каждого утверждения проверяется, подтверждается ли оно найденным контекстом. В идеале подтверждаются все.

Формула:

Context Recall = (число утверждений эталона, подтверждённых найденным контекстом) / (общее число утверждений в эталоне)

### Пример

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextRecall

# Настройка LLM
client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)

# Создаём метрику
scorer = ContextRecall(llm=llm)

# Оцениваем
result = await scorer.ascore(
    user_input="Where is the Eiffel Tower located?",
    retrieved_contexts=["Paris is the capital of France."],
    reference="The Eiffel Tower is located in Paris."
)
print(f"Context Recall Score: {result.value}")
```

Вывод:

```text
Context Recall Score: 1.0
```

Для синхронного кода есть метод `.score()` с теми же аргументами.

### Context Recall на основе LLM (старый API)

Старый API будет объявлен устаревшим в версии 0.4 и удалён в версии 1.0.

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import LLMContextRecall

sample = SingleTurnSample(
    user_input="Where is the Eiffel Tower located?",
    response="The Eiffel Tower is located in Paris.",
    reference="The Eiffel Tower is located in Paris.",
    retrieved_contexts=["Paris is the capital of France."],
)

context_recall = LLMContextRecall(llm=evaluator_llm)
await context_recall.single_turn_ascore(sample)
```

Вывод: `1.0`.

### Context Recall без LLM

Метрика `NonLLMContextRecall` использует найденные контексты (`retrieved_contexts`) и эталонные контексты (`reference_contexts`). Значение от 0 до 1, чем выше, тем лучше. Релевантность найденного контекста определяется строковым сравнением без LLM. В качестве меры расстояния подходит любая метрика без LLM.

Формула:

Context Recall = (число найденных релевантных контекстов) / (общее число эталонных контекстов)

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import NonLLMContextRecall

sample = SingleTurnSample(
    retrieved_contexts=["Paris is the capital of France."],
    reference_contexts=["Paris is the capital of France.", "The Eiffel Tower is one of the most famous landmarks in Paris."]
)

context_recall = NonLLMContextRecall()
await context_recall.single_turn_ascore(sample)
```

Вывод: `0.5` — найден 1 из 2 эталонных контекстов.

### Context Recall по ID

`IDBasedContextRecall` сравнивает не тексты, а **идентификаторы** документов: найденные (`retrieved_context_ids`) и эталонные (`reference_context_ids`). Это просто и быстро, если у документов есть уникальные ID. Подходят строковые и целые ID. Значение от 0 до 1.

Формула:

Context Recall по ID = (число эталонных ID среди найденных) / (общее число эталонных ID)

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import IDBasedContextRecall

sample = SingleTurnSample(
    retrieved_context_ids=["doc_1", "doc_2", "doc_3"],
    reference_context_ids=["doc_1", "doc_4", "doc_5", "doc_6"]
)

id_recall = IDBasedContextRecall()
await id_recall.single_turn_ascore(sample)
```

Вывод: `0.25` — из 4 эталонных документов найден только `doc_1`.
