---
title: timm — быстрый старт
source: Документация Hugging Face, timm, «Quickstart»
original: https://huggingface.co/docs/timm/quickstart
kind: перевод
license: Apache-2.0, Hugging Face / Ross Wightman
---
Этот быстрый старт — для разработчиков, которые готовы сразу перейти к коду. Он показывает, как встроить `timm` в обучение своей модели.

Сначала установите `timm`:

```console
pip install timm
```

## Загрузка предобученной модели

Предобученные модели загружает функция `create_model()`. Загрузим предобученную модель `mobilenetv3_large_100`:

```python
>>> import timm
>>> m = timm.create_model('mobilenetv3_large_100', pretrained=True)
>>> m.eval()
```

> Примечание. Модель PyTorch возвращается в режиме обучения. Если нужна модель для предсказаний (инференса), вызовите `.eval()`.

## Список моделей с предобученными весами

Модели из `timm` перечисляет функция `list_models()`. С `pretrained=True` она вернёт только модели, для которых есть предобученные веса.

```python
>>> import timm
>>> from pprint import pprint
>>> model_names = timm.list_models(pretrained=True)
>>> pprint(model_names)
[
    'adv_inception_v3',
    'cspdarknet53',
    'cspresnext50',
    'densenet121',
    'densenet161',
    'densenet169',
    'densenet201',
    'densenetblur121d',
    'dla34',
    'dla46_c',
]
```

Можно искать модели по шаблону имени:

```python
>>> import timm
>>> from pprint import pprint
>>> model_names = timm.list_models('*resne*t*')
>>> pprint(model_names)
[
    'cspresnet50',
    'cspresnet50d',
    'cspresnet50w',
    'cspresnext50',
    ...
]
```

## Дообучение предобученной модели

Любую предобученную модель можно дообучить (fine-tune): достаточно заменить классификатор, то есть последний слой.

```python
>>> model = timm.create_model('mobilenetv3_large_100', pretrained=True, num_classes=NUM_FINETUNE_CLASSES)
```

Чтобы дообучить модель на своих данных, напишите цикл обучения PyTorch или адаптируйте [скрипт обучения](https://huggingface.co/docs/timm/training_script) из `timm` под свой набор данных.

## Предобученная модель как извлекатель признаков

Сеть менять не нужно. Вместо обычного `model(input)` вызовите у любой модели `model.forward_features(input)`. Этот вызов пропускает голову-классификатор и глобальный пулинг.

Подробнее — в руководстве [Feature Extraction](https://huggingface.co/docs/timm/feature_extraction).

```python
>>> import timm
>>> import torch
>>> x = torch.randn(1, 3, 224, 224)
>>> model = timm.create_model('mobilenetv3_large_100', pretrained=True)
>>> features = model.forward_features(x)
>>> print(features.shape)
torch.Size([1, 960, 7, 7])
```

## Преобразования картинок

Чтобы превратить картинку в правильный вход модели, используйте `timm.data.create_transform()` и передайте нужный модели `input_size`.

Функция вернёт общее преобразование с разумными настройками по умолчанию:

```python
>>> timm.data.create_transform((3, 224, 224))
Compose(
    Resize(size=256, interpolation=bilinear, max_size=None, antialias=None)
    CenterCrop(size=(224, 224))
    ToTensor()
    Normalize(mean=tensor([0.4850, 0.4560, 0.4060]), std=tensor([0.2290, 0.2240, 0.2250]))
)
```

У предобученных моделей есть свои преобразования: их применяли к картинкам при обучении. Если подать картинку с другим преобразованием, модель не поймёт, что видит!

Какие преобразования использовались для модели, видно в её `pretrained_cfg`:

```python
>>> model.pretrained_cfg
{'url': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mobilenetv3_large_100_ra-f55367f5.pth',
 'num_classes': 1000,
 'input_size': (3, 224, 224),
 'pool_size': (7, 7),
 'crop_pct': 0.875,
 'interpolation': 'bicubic',
 'mean': (0.485, 0.456, 0.406),
 'std': (0.229, 0.224, 0.225),
 'first_conv': 'conv_stem',
 'classifier': 'classifier',
 'architecture': 'mobilenetv3_large_100'}
```

Только настройки данных выделяет `timm.data.resolve_data_config()`:

```python
>>> timm.data.resolve_data_config(model.pretrained_cfg)
{'input_size': (3, 224, 224),
 'interpolation': 'bicubic',
 'mean': (0.485, 0.456, 0.406),
 'std': (0.229, 0.224, 0.225),
 'crop_pct': 0.875}
```

Передайте эти настройки в `timm.data.create_transform()` — получите преобразование, подходящее модели:

```python
>>> data_cfg = timm.data.resolve_data_config(model.pretrained_cfg)
>>> transform = timm.data.create_transform(**data_cfg)
>>> transform
Compose(
    Resize(size=256, interpolation=bicubic, max_size=None, antialias=None)
    CenterCrop(size=(224, 224))
    ToTensor()
    Normalize(mean=tensor([0.4850, 0.4560, 0.4060]), std=tensor([0.2290, 0.2240, 0.2250]))
)
```

> Примечание. Здесь настройки модели почти совпали с общими (отличается только интерполяция). Так бывает не всегда. Поэтому надёжнее строить преобразование по настройкам модели, как здесь, а не брать общее.

## Предсказание предобученной моделью

Соберём всё вместе и получим предсказание предобученной модели.

Сначала нужна картинка. Загрузим фото кошки из интернета:

```python
>>> import requests
>>> from PIL import Image
>>> from io import BytesIO
>>> url = 'https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/timm/cat.jpg'
>>> image = Image.open(requests.get(url, stream=True).raw)
>>> image
```

Снова создадим модель и преобразование. На этот раз сразу переведём модель в режим оценки:

```python
>>> model = timm.create_model('mobilenetv3_large_100', pretrained=True).eval()
>>> transform = timm.data.create_transform(
    **timm.data.resolve_data_config(model.pretrained_cfg)
)
```

Подготовим картинку для модели, пропустив её через преобразование:

```python
>>> image_tensor = transform(image)
>>> image_tensor.shape
torch.Size([3, 224, 224])
```

Передадим картинку модели и получим предсказания. Нужен `unsqueeze(0)`: модель ждёт измерение батча.

```python
>>> output = model(image_tensor.unsqueeze(0))
>>> output.shape
torch.Size([1, 1000])
```

Чтобы получить вероятности, применим к выходу softmax. Получится тензор формы `(num_classes,)`:

```python
>>> probabilities = torch.nn.functional.softmax(output[0], dim=0)
>>> probabilities.shape
torch.Size([1000])
```

Найдём 5 классов с наибольшей вероятностью через `torch.topk`:

```python
>>> values, indices = torch.topk(probabilities, 5)
>>> indices
tensor([281, 282, 285, 673, 670])
```

Посмотрим метки ImageNet для этих индексов — что предсказала модель:

```python
>>> IMAGENET_1k_URL = 'https://storage.googleapis.com/bit_models/ilsvrc2012_wordnet_lemmas.txt'
>>> IMAGENET_1k_LABELS = requests.get(IMAGENET_1k_URL).text.strip().split('\n')
>>> [{'label': IMAGENET_1k_LABELS[idx], 'value': val.item()} for val, idx in zip(values, indices)]
[{'label': 'tabby, tabby_cat', 'value': 0.5101025700569153},
 {'label': 'tiger_cat', 'value': 0.22490699589252472},
 {'label': 'Egyptian_cat', 'value': 0.1835290789604187},
 {'label': 'mouse, computer_mouse', 'value': 0.006752475164830685},
 {'label': 'motor_scooter, scooter', 'value': 0.004942195490002632}]
```

Модель уверенно видит кошку: три лучших класса — породы кошек (полосатая, тигровая, египетская).
