---
title: PyTorch — оптимизация параметров модели
source: PyTorch Tutorials, «Learn the Basics», урок «Optimizing Model Parameters»
original: https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
kind: перевод
license: BSD-3-Clause, PyTorch Contributors
---
У нас есть модель и данные. Пора обучить, проверить и протестировать модель: оптимизировать её параметры на наших данных.

Обучение — итеративный процесс. На каждой итерации модель:

1. делает предсказание (догадку о выходе);
2. считает ошибку предсказания (*loss*);
3. собирает производные ошибки по своим параметрам (см. прошлый урок про autograd);
4. **оптимизирует** параметры градиентным спуском.

Подробно этот процесс показан в [видео 3Blue1Brown про обратное распространение](https://www.youtube.com/watch?v=tIeHLnjs5U8).

## Код из прошлых уроков

Загрузим код из уроков «Datasets & DataLoaders» и «Build Model»:

```python
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
)

test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
)

train_dataloader = DataLoader(training_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

model = NeuralNetwork()
```

## Гиперпараметры

Гиперпараметры — настраиваемые параметры, которые управляют процессом оптимизации. От их значений зависят обучение модели и скорость сходимости.

Зададим гиперпараметры обучения:

- **число эпох** — сколько раз пройти по всему набору данных;
- **размер батча** — сколько примеров проходит через сеть до обновления параметров;
- **learning rate** (скорость обучения) — насколько сильно менять параметры на каждом батче или эпохе. Малое значение — медленное обучение. Большое — непредсказуемое поведение при обучении.

```python
learning_rate = 1e-3
batch_size = 64
epochs = 5
```

## Цикл оптимизации

Когда гиперпараметры заданы, модель обучают и оптимизируют в цикле. Одна итерация цикла оптимизации называется **эпохой**.

Эпоха состоит из двух частей:

- **цикл обучения** — проход по обучающей выборке, параметры приближаются к оптимальным;
- **цикл проверки (валидации или теста)** — проход по тестовой выборке, чтобы понять, растёт ли качество модели.

Сначала кратко разберём понятия цикла обучения.

### Функция потерь

Необученная сеть на обучающих данных, скорее всего, ответит неверно. **Функция потерь** (loss function) измеряет, насколько полученный результат отличается от целевого значения. Именно её мы минимизируем при обучении. Чтобы посчитать потери, модель делает предсказание по входу примера, и предсказание сравнивается с настоящей меткой.

Частые функции потерь:

- `nn.MSELoss` (среднеквадратичная ошибка) — для регрессии;
- `nn.NLLLoss` (отрицательное логарифмическое правдоподобие) — для классификации;
- `nn.CrossEntropyLoss` — объединяет `nn.LogSoftmax` и `nn.NLLLoss`.

Передадим логиты (сырые выходы) модели в `nn.CrossEntropyLoss`. Она нормализует логиты и посчитает ошибку предсказания.

```python
# Функция потерь
loss_fn = nn.CrossEntropyLoss()
```

### Оптимизатор

Оптимизация — подстройка параметров модели, чтобы на каждом шаге обучения уменьшать ошибку. **Алгоритм оптимизации** задаёт, как именно это делать. Здесь используем стохастический градиентный спуск (SGD).

Вся логика оптимизации спрятана в объекте `optimizer`. Здесь это SGD. В PyTorch есть и [другие оптимизаторы](https://pytorch.org/docs/stable/optim.html), например Adam и RMSProp: они лучше подходят для других моделей и данных.

Оптимизатор создают так: передают ему параметры модели, которые нужно обучать, и гиперпараметр learning rate.

```python
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
```

Внутри цикла обучения оптимизация идёт в три шага:

1. `optimizer.zero_grad()` — обнулить градиенты параметров модели. По умолчанию градиенты **складываются**. Чтобы не посчитать их дважды, их явно обнуляют на каждой итерации.
2. `loss.backward()` — обратное распространение ошибки. PyTorch записывает градиент потерь по каждому параметру.
3. `optimizer.step()` — изменить параметры по градиентам, собранным при обратном проходе.

## Полная реализация

Напишем `train_loop` — цикл с кодом оптимизации, и `test_loop` — проверку качества модели на тестовых данных.

```python
def train_loop(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    # Режим обучения: важно для слоёв batch normalization и dropout.
    # Здесь не обязательно, но так правильно.
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        # Предсказание и потери
        pred = model(X)
        loss = loss_fn(pred, y)

        # Обратное распространение
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * batch_size + len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


def test_loop(dataloader, model, loss_fn):
    # Режим оценки: важно для слоёв batch normalization и dropout.
    # Здесь не обязательно, но так правильно.
    model.eval()
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0

    # torch.no_grad(): при проверке градиенты не считаются.
    # Это экономит вычисления и память для тензоров с requires_grad=True.
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()

    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")
```

> Обратите внимание на порядок в `train_loop`: `backward()`, затем `step()`, затем `zero_grad()`. Это то же самое, что `zero_grad()` в начале итерации: важно лишь, чтобы градиенты обнулялись между шагами. *(Примечание переводчика.)*

Создадим функцию потерь и оптимизатор и передадим их в `train_loop` и `test_loop`. Можно увеличить число эпох и посмотреть, как растёт качество модели.

```python
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

epochs = 10
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train_loop(train_dataloader, model, loss_fn, optimizer)
    test_loop(test_dataloader, model, loss_fn)
print("Done!")
```

Вывод (сокращён: показаны первая и последняя эпохи):

```text
Epoch 1
-------------------------------
loss: 2.311237  [   64/60000]
loss: 2.295860  [ 6464/60000]
loss: 2.278365  [12864/60000]
...
loss: 2.164147  [57664/60000]
Test Error:
 Accuracy: 46.8%, Avg loss: 2.158507

...

Epoch 10
-------------------------------
loss: 0.838284  [   64/60000]
loss: 0.908002  [ 6464/60000]
loss: 0.678949  [12864/60000]
...
loss: 0.790809  [57664/60000]
Test Error:
 Accuracy: 70.5%, Avg loss: 0.792417

Done!
```

За 10 эпох точность на тесте выросла с 46,8 % до 70,5 %, а средние потери упали с 2,16 до 0,79.
