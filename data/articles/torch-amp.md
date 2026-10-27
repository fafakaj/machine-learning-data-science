---
title: torch.amp — автоматическая смешанная точность
source: Документация PyTorch 2.14, «Automatic Mixed Precision package — torch.amp»
original: https://docs.pytorch.org/docs/2.14/amp.html
kind: перевод
license: BSD-3-Clause, PyTorch Contributors
---
`torch.amp` даёт удобные средства для **смешанной точности** (mixed precision). Часть операций работает в `torch.float32` (`float`), а часть — в типе пониженной точности: `torch.float16` (`half`) или `torch.bfloat16`.

Некоторые операции, например линейные слои и свёртки, в пониженной точности работают намного быстрее. Другим, например операциям свёртки (reduction: сумма, softmax), часто нужен динамический диапазон `float32`. Смешанная точность старается подобрать каждой операции подходящий тип.

Обычно «автоматическое обучение в смешанной точности» с `torch.float16` использует вместе `torch.autocast` и `torch.amp.GradScaler`. Но они независимы, и их можно использовать по отдельности. Например, на CPU с типом `torch.bfloat16` обучение и инференс используют только `torch.autocast`.

> Внимание. `torch.cuda.amp.autocast(args...)` и `torch.cpu.amp.autocast(args...)` устарели. Пишите `torch.amp.autocast("cuda", args...)` или `torch.amp.autocast("cpu", args...)`. Так же `torch.cuda.amp.GradScaler(args...)` и `torch.cpu.amp.GradScaler(args...)` устарели — пишите `torch.amp.GradScaler("cuda", args...)` или `torch.amp.GradScaler("cpu", args...)`.

> Внимание. При сочетании AMP и `torch.compile`: по умолчанию настройка `torch._functorch.config.backward_pass_autocast` равна `"same_as_forward"`. Это значит, что скомпилированный обратный проход идёт в том же контексте autocast, что и прямой. Если вы следуете рекомендованной схеме AMP и вызываете backward вне autocast, поставьте для скомпилированной части значение `"off"`.

## Autocast

`torch.autocast(device_type, dtype=None, enabled=True, cache_enabled=None)`

Экземпляры `autocast` работают как контекстные менеджеры или декораторы. Внутри таких участков кода операции выполняются в типе, который autocast выбирает для каждой операции отдельно. Это ускоряет работу и сохраняет точность. Какой тип у какой операции — см. раздел «Справочник операций» ниже.

Правила:

- При входе в участок с autocast тензоры могут быть любого типа.
- Не вызывайте `half()` или `bfloat16()` у модели или входов: autocast сам всё сделает.
- `autocast` должен оборачивать только **прямой проход** сети, включая подсчёт потерь. Обратный проход внутри autocast не рекомендуется.
- Операции обратного прохода выполняются в том же типе, что autocast выбрал для соответствующих операций прямого прохода.

Пример для CUDA:

```python
# Модель и оптимизатор в точности по умолчанию
model = Net().cuda()
optimizer = optim.SGD(model.parameters(), ...)

for input, target in data:
    optimizer.zero_grad()

    # Autocast для прямого прохода (модель + потери)
    with torch.autocast(device_type="cuda"):
        output = model(input)
        loss = loss_fn(output, target)

    # Выход из контекста до backward()
    loss.backward()
    optimizer.step()
```

`autocast` можно использовать и как декоратор, например у метода `forward` модели:

```python
class AutocastModel(nn.Module):
    ...
    @torch.autocast(device_type="cuda")
    def forward(self, input):
        ...
```

Дробные тензоры, созданные внутри autocast, могут иметь тип `float16`. Если потом, вне autocast, смешать их с тензорами другого типа, возможна ошибка несовпадения типов. Тогда приведите тензоры из участка autocast обратно к `float32` (или другому нужному типу). Если тензор уже `float32`, приведение ничего не стоит.

```python
# Тензоры в типе по умолчанию (здесь float32)
a_float32 = torch.rand((8, 8), device="cuda")
b_float32 = torch.rand((8, 8), device="cuda")
c_float32 = torch.rand((8, 8), device="cuda")
d_float32 = torch.rand((8, 8), device="cuda")

with torch.autocast(device_type="cuda"):
    # torch.mm — в списке операций, которые autocast выполняет во float16.
    # Входы float32, но операция идёт во float16 и даёт float16.
    # Вручную приводить типы не нужно.
    e_float16 = torch.mm(a_float32, b_float32)
    # Смешанные типы входов тоже работают
    f_float16 = torch.mm(d_float32, e_float16)

# После autocast: f_float16.float(), чтобы умножать на d_float32
g_float32 = torch.mm(d_float32, f_float16.float())
```

Пример обучения на CPU:

```python
model = Net()
optimizer = optim.SGD(model.parameters(), ...)

for epoch in epochs:
    for input, target in data:
        optimizer.zero_grad()

        # Прямой проход с autocast
        with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
            output = model(input)
            loss = loss_fn(output, target)

        loss.backward()
        optimizer.step()
```

Пример инференса на CPU:

```python
model = Net().eval()

with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
    for input in data:
        # Прямой проход с autocast
        output = model(input)
```

Ошибка несовпадения типов *внутри* участка autocast — это баг PyTorch; о нём стоит сообщить разработчикам.

Внутри участка autocast можно сделать вложенный участок `autocast(enabled=False)`. Это полезно, чтобы принудительно выполнить часть кода в нужном типе: вы явно управляете типом. Входы из внешнего участка нужно сначала привести к этому типу:

```python
with torch.autocast(device_type="cuda"):
    e_float16 = torch.mm(a_float32, b_float32)
    with torch.autocast(device_type="cuda", enabled=False):
        # e_float16.float(), чтобы операция шла во float32
        # (e_float16 создан внутри autocast)
        f_float32 = torch.mm(c_float32, e_float16.float())

    # Снова внутри autocast приводить типы не нужно:
    # torch.mm опять идёт во float16 и даёт float16.
    g_float16 = torch.mm(d_float32, f_float32)
```

Состояние autocast своё у каждого потока. Чтобы autocast работал в новом потоке, вызовите контекстный менеджер или декоратор в этом потоке. Это важно для `torch.nn.DataParallel` и `torch.nn.parallel.DistributedDataParallel`, когда в одном процессе больше одного GPU.

Параметры:

- **device_type** (str, обязательный) — тип устройства: `'cuda'`, `'cpu'`, `'mtia'`, `'maia'`, `'xpu'`, `'hpu'`. Это тот же тип, что в атрибуте `type` у `torch.device`, то есть его можно взять из `tensor.device.type`.
- **enabled** (bool) — включать ли autocast в этом участке. По умолчанию `True`.
- **dtype** (torch.dtype) — тип для операций в autocast. Если `None`, берётся значение по умолчанию из `get_autocast_dtype()`: `torch.float16` для CUDA и `torch.bfloat16` для CPU.
- **cache_enabled** (bool) — включать ли внутренний кэш весов autocast. По умолчанию `True`.

Для своих функций autograd (подклассов `torch.autograd.Function`) есть декораторы:

- `torch.amp.custom_fwd(fwd=None, *, device_type, cast_inputs=None)` — для метода `forward`. Если `cast_inputs` не `None`, то внутри autocast входные дробные тензоры приводятся к этому типу, а `forward` выполняется с выключенным autocast. Если `None`, операции внутри `forward` идут с текущим состоянием autocast.
- `torch.amp.custom_bwd(bwd=None, *, device_type)` — для метода `backward`. Гарантирует, что `backward` выполняется в том же состоянии autocast, что и `forward`.

## Масштабирование градиентов (Gradient Scaling)

Если у операции в прямом проходе входы `float16`, то и градиенты этой операции в обратном проходе будут `float16`. Маленькие по модулю градиенты могут не уместиться в `float16`. Они обнулятся (это называют «исчезновением», underflow), и обновление соответствующих параметров потеряется.

Чтобы этого избежать, **масштабирование градиентов** умножает потери на коэффициент и запускает обратный проход по увеличенным потерям. Тогда все градиенты в сети тоже умножаются на этот коэффициент. Они становятся больше по модулю и не обнуляются.

Перед тем как оптимизатор обновит параметры, градиент каждого параметра (атрибут `.grad`) нужно разделить обратно на коэффициент. Тогда коэффициент не влияет на learning rate.

Типичный цикл с `GradScaler` *(пример добавлен при переводе; так же он устроен в официальных примерах AMP)*:

```python
scaler = torch.amp.GradScaler("cuda")

for input, target in data:
    optimizer.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        output = model(input)
        loss = loss_fn(output, target)

    scaler.scale(loss).backward()  # обратный проход по увеличенным потерям
    scaler.step(optimizer)         # делит градиенты обратно; пропускает шаг, если есть inf/NaN
    scaler.update()                # подстраивает коэффициент на следующую итерацию
```

> Примечание. AMP с fp16 подходит не каждой модели! Например, большинство моделей, предобученных в bf16, не умещаются в диапазон fp16 (максимум 65504). У них градиенты не исчезают, а переполняются. Тогда коэффициент может стать меньше 1, чтобы вернуть градиенты в диапазон fp16. Можно ожидать, что коэффициент всегда больше 1, но GradScaler этого не гарантирует ради производительности. Если при AMP/fp16 в потерях или градиентах появляются NaN, проверьте, что модель совместима с fp16.

## Справочник операций autocast

### Какие операции подходят

Операции во `float64` и в недробных типах (целые числа, bool) не подходят: они выполняются в своём типе, включён autocast или нет.

Подходят только операции, которые создают новый тензор (out-of-place), и методы тензоров. Варианты «на месте» (in-place) и вызовы с явным `out=...` разрешены внутри autocast, но autocast их не трогает. Например, внутри autocast `a.addmm(b, c)` может пройти через autocast, а `a.addmm_(b, c)` и `a.addmm(b, c, out=d)` — нет. Ради скорости и стабильности внутри autocast лучше использовать операции, которые создают новый тензор.

Операции с явным аргументом `dtype=...` не подходят: их выход будет в указанном `dtype`.

### Поведение операций на CUDA

Списки ниже описывают подходящие операции внутри autocast. Эти операции всегда идут через autocast: как часть `torch.nn.Module`, как функции или как методы `torch.Tensor`. Если функция есть в нескольких пространствах имён, autocast работает в любом из них.

Операции не из списков через autocast не идут: они выполняются в типе своих входов. Но если такая операция стоит после операций autocast, её тип тоже может измениться. Считается, что операции не из списка устойчивы во `float16`.

**Операции CUDA, которые autocast переводит во `float16`:**

`__matmul__`, `addbmm`, `addmm`, `addmv`, `addr`, `baddbmm`, `bmm`, `chain_matmul`, `multi_dot`, `conv1d`, `conv2d`, `conv3d`, `conv_transpose1d`, `conv_transpose2d`, `conv_transpose3d`, `GRUCell`, `linear`, `LSTMCell`, `matmul`, `mm`, `mv`, `prelu`, `RNNCell`

**Операции CUDA, которые autocast переводит во `float32`:**

`__pow__`, `__rdiv__`, `__rpow__`, `__rtruediv__`, `acos`, `asin`, `binary_cross_entropy_with_logits`, `cosh`, `cosine_embedding_loss`, `cdist`, `cosine_similarity`, `cross_entropy`, `cumprod`, `cumsum`, `dist`, `erfinv`, `exp`, `expm1`, `group_norm`, `hinge_embedding_loss`, `kl_div`, `l1_loss`, `layer_norm`, `log`, `log_softmax`, `log10`, `log1p`, `log2`, `margin_ranking_loss`, `mse_loss`, `multilabel_margin_loss`, `multi_margin_loss`, `nll_loss`, `norm`, `normalize`, `pdist`, `poisson_nll_loss`, `pow`, `prod`, `reciprocal`, `rsqrt`, `sinh`, `smooth_l1_loss`, `soft_margin_loss`, `softmax`, `softmin`, `softplus`, `sum`, `renorm`, `tan`, `triplet_margin_loss`

Видна закономерность: умножения матриц и свёртки — во `float16` (быстро), экспоненты, логарифмы, суммы, нормализации и функции потерь — во `float32` (нужен диапазон и точность).

**Операции CUDA, которые приводят входы к самому широкому типу.** Им не нужен конкретный тип для устойчивости, но у них несколько входов, и типы входов должны совпадать. Если все входы `float16`, операция идёт во `float16`. Если хоть один вход `float32`, autocast приводит все входы к `float32`:

`addcdiv`, `addcmul`, `atan2`, `bilinear`, `cross`, `dot`, `grid_sample`, `index_put`, `scatter_add`, `tensordot`

Некоторые операции не из списка (например, бинарные вроде `add`) сами приводят входы к общему типу. Если входы — смесь `float16` и `float32`, такие операции работают во `float32` и дают `float32`, независимо от autocast.

**Предпочитайте `binary_cross_entropy_with_logits` вместо `binary_cross_entropy`.** Обратный проход `torch.nn.functional.binary_cross_entropy` (и `torch.nn.BCELoss`) может дать градиенты, которые не помещаются во `float16`. Внутри autocast вход прямого прохода может быть `float16`, значит, и градиент должен помещаться во `float16`. Приведение входа к `float32` не помогает: в обратном проходе приведение обращается. Поэтому `binary_cross_entropy` и `BCELoss` внутри autocast бросают ошибку.

Во многих моделях перед бинарной кросс-энтропией стоит сигмоида. Объедините эти два слоя через `torch.nn.functional.binary_cross_entropy_with_logits` или `torch.nn.BCEWithLogitsLoss`. Они безопасны для autocast.

### Поведение операций на CPU и XPU

На CPU тип пониженной точности по умолчанию — `bfloat16`, и `float16` использует те же списки. Логика та же, что на CUDA:

- в `bfloat16` идут свёртки, умножения матриц (`mm`, `bmm`, `addmm`, `linear`, `matmul`, `baddbmm`, …), `prelu`, `scaled_dot_product_attention`;
- во `float32` идут функции потерь, пулинги в 3D, FFT, операции линейной алгебры (`inverse`, `svd`, `linalg_*`), `prod`, `quantile` и другие;
- к самому широкому типу приводят входы `cat`, `stack`, `index_copy`.

Для XPU (экспериментально) списки почти совпадают со списками CUDA. Полные списки для CPU и XPU — в [оригинале страницы](https://docs.pytorch.org/docs/2.14/amp.html#cpu-op-specific-behavior).
