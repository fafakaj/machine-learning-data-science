---
title: Gradient checkpointing — экономия памяти на активациях
source: Документация Hugging Face Transformers, «Gradient checkpointing»
original: https://huggingface.co/docs/transformers/grad_checkpointing
kind: перевод
license: Apache-2.0, Hugging Face
---
Обычно прямой проход сохраняет все промежуточные активации, чтобы обратный проход их использовал. Но размер активаций растёт с размером батча и длиной последовательности.

**Gradient checkpointing** сохраняет только некоторые активации, а остальные выбрасывает. Тогда обратный проход заново вычисляет часть активаций, когда они нужны.

```text
Обычное обучение:
  Прямой:    [L1]→[L2]→[L3]→[L4]   (сохранить ВСЕ активации)
  Обратный:  ←везде берёт сохранённые активации

Gradient checkpointing:
  Прямой:    [L1]→[L2]→[L3]→[L4]   (сохранить только в контрольных точках, остальное выбросить)
  Обратный:  ←дойдя до L2, заново считает L2→L3, использует и выбрасывает
```

Обучение обычно медленнее: обратный проход пересчитывает выброшенные активации. Зато памяти под активации нужно меньше.

Включается параметром `gradient_checkpointing=True`.

> Совет. Сочетайте с [gradient accumulation](https://huggingface.co/docs/transformers/grad_accumulation), чтобы сэкономить ещё больше памяти.

```python
from transformers import TrainingArguments

args = TrainingArguments(
    ...,
    gradient_checkpointing=True,
)
```

## Частичный checkpointing

Полный gradient checkpointing пересчитывает каждый слой, который это поддерживает. Если у запуска есть запас памяти, отмечайте меньше слоёв: часть экономии памяти вы обменяете на скорость.

Интервал задаёт параметр `every_n_layers` в `PreTrainedModel.gradient_checkpointing_enable`.

```text
every_n_layers=2

Прямой:    вход  -> [L1] -> [L2] -> [L3] -> [L4] -> [L5] -> [L6]
                      CP    храним    CP    храним    CP    храним

Обратный:  выход <- [L6] <- [L5] <- [L4] <- [L3] <- [L2] <- [L1]
                   храним  пересчёт храним  пересчёт храним  пересчёт
```

(CP — контрольная точка, checkpoint.)

При `every_n_layers=2` контрольными становятся первый слой и далее каждый второй. Такие слои выбрасывают активации при прямом проходе и пересчитывают их при обратном. Остальные слои держат активации в памяти.

```python
model.gradient_checkpointing_enable(every_n_layers=2)
```

По умолчанию `every_n_layers=1`: контрольный каждый слой. При больших значениях контрольными становятся первый слой и затем каждый n-й, а остальные слои хранят активации. Например, `every_n_layers=2` отмечает слои 1, 3, 5 и т. д. Считаются только модули, унаследованные от `GradientCheckpointingLayer`. Другие модули с поддержкой checkpointing остаются включены.

Чтобы использовать частичный checkpointing с `Trainer`, задайте `every_n_layers` в `gradient_checkpointing_kwargs`:

```python
from transformers import TrainingArguments

args = TrainingArguments(
    ...,
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"every_n_layers": 4},
)
```

## Выгрузка сохранённых активаций в память CPU

Gradient checkpointing держит на GPU по одной активации на каждый контрольный слой. На длинных последовательностях это тоже много: примерно `слои × длина × ширина × байт_на_элемент`.

Параметр `offload` хранит эти активации в закреплённой (pinned) памяти CPU. Цена — копирование с GPU на CPU при прямом проходе и обратно при обратном.

```python
from transformers import TrainingArguments

args = TrainingArguments(
    ...,
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"offload": True},
)
```

Обе копии идут в потоке вычислений, поэтому шаг становится медленнее ради экономии памяти. Используйте это, когда иначе обучение не помещается в память, а не для ускорения.

## Что дальше

- [GPU memory usage](https://huggingface.co/docs/transformers/model_memory_anatomy) — что занимает память GPU при обучении (есть перевод в этой же теме плана).
- [Mixed precision training](https://huggingface.co/docs/transformers/mixed_precision_training) — меньше памяти и быстрее обучение за счёт пониженной точности.
