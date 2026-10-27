---
title: Как языковая модель выбирает следующее слово — сэмплирование, temperature, top-k, top-p
source: Блог Hugging Face, Patrick von Platen, «How to generate text: using different decoding methods for language generation with Transformers» (ред. 2023)
original: https://huggingface.co/blog/how-to-generate
kind: пересказ
license: Пересказ разделов Sampling, Top-K и Top-p своими словами. Примеры кода и вывода — из статьи.
---
Языковая модель на каждом шаге выдаёт распределение вероятностей следующего слова (токена): P(w | w₁, …, wₜ₋₁). Способ выбрать слово из этого распределения называют **методом декодирования**. От него сильно зависит качество текста — наравне с архитектурой модели и объёмом данных.

В статье сначала разобраны детерминированные методы: **жадный поиск** (на каждом шаге брать самое вероятное слово) и **beam search** (держать несколько лучших цепочек). Их общая беда в открытой генерации — повторы и скучный текст. Ниже пересказ второй половины статьи: случайные методы.

Все примеры используют GPT-2 и начало фразы «I enjoy walking with my cute dog»:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")
# токен конца текста служит токеном-заполнителем, чтобы не было предупреждений
model = AutoModelForCausalLM.from_pretrained(
    "openai-community/gpt2", pad_token_id=tokenizer.eos_token_id
)
model_inputs = tokenizer("I enjoy walking with my cute dog", return_tensors="pt")
```

## Сэмплирование

В простейшем виде сэмплирование — это случайный выбор следующего слова **по его вероятности**:

wₜ ~ P(w | w₁:ₜ₋₁)

Слово с вероятностью 0,5 выпадет примерно в половине случаев, слово с вероятностью 0,01 — в одном случае из ста. Генерация перестаёт быть *детерминированной*: при каждом запуске текст разный.

В `transformers` сэмплирование включает `do_sample=True`. Чтобы получить «чистое» сэмплирование, отключим top-k (о нём ниже) через `top_k=0`. Зерно случайности фиксируем, чтобы результат повторялся:

```python
from transformers import set_seed
set_seed(42)

sample_output = model.generate(
    **model_inputs,
    max_new_tokens=40,
    do_sample=True,
    top_k=0
)
print(tokenizer.decode(sample_output[0], skip_special_tokens=True))
```

```text
I enjoy walking with my cute dog for the rest of the day, but this had me staying in an unusual room and not going on nights out with friends (which will always be wondered for a mere minute or so at this point).
```

На первый взгляд текст нормальный, но при чтении он бессвязный и не похож на человеческий. Это главная проблема чистого сэмплирования: иногда выпадают маловероятные, «странные» слова, и текст уходит в бессмыслицу.

### Temperature

Приём против этого — сделать распределение **острее**: вероятные слова ещё вероятнее, маловероятные — ещё менее вероятны. Для этого логиты делят на **температуру** T перед softmax:

P(wᵢ) = exp(zᵢ / T) / Σⱼ exp(zⱼ / T)

- T < 1 — распределение острее, текст предсказуемее;
- T = 1 — исходное распределение модели;
- T > 1 — распределение площе, текст разнообразнее и «безумнее».

Пример с `temperature=0.6`:

```python
set_seed(42)

sample_output = model.generate(
    **model_inputs,
    max_new_tokens=40,
    do_sample=True,
    top_k=0,
    temperature=0.6,
)
```

```text
I enjoy walking with my cute dog, but I don't like to chew on it. I like to eat it and not chew on it. I like to be able to walk with my dog."
So how did you decide
```

Странных сочетаний меньше, текст чуть связнее. Но если устремить T к нулю, сэмплирование превращается в жадный поиск — и возвращаются его проблемы (повторы).

## Top-K

Сэмплирование **top-K** предложили Fan и соавторы (2018). Идея простая и сильная:

1. оставить только K самых вероятных следующих слов;
2. перераспределить вероятность между ними (нормировать, чтобы сумма снова была 1);
3. выбрать слово из этих K.

Этот метод использовала GPT-2, и это одна из причин её успеха в генерации историй.

Пусть K = 6. На шаге, где распределение плоское (много примерно равных вариантов), 6 лучших слов покрывают, например, только около двух третей вероятности. На шаге, где распределение острое, 6 слов покрывают почти всю вероятность. Зато странные кандидаты из «хвоста» распределения отсекаются.

Пример с `top_k=50`:

```python
set_seed(42)

sample_output = model.generate(
    **model_inputs,
    max_new_tokens=40,
    do_sample=True,
    top_k=50
)
```

```text
I enjoy walking with my cute dog for the rest of the day, but this time it was hard for me to figure out what to do with it. (One reason I asked this for a few months back is that I had a
```

Пожалуй, это самый «человеческий» текст из всех примеров.

Слабое место top-K: число слов K **фиксировано** и не подстраивается под форму распределения.

- Если распределение плоское, K может отрезать разумные варианты — модель теряет творческую свободу.
- Если распределение острое, в K могут попасть явно неподходящие слова — модель рискует написать бессмыслицу.

Это наблюдение привело Holtzman и соавторов (2019) к методу top-p.

## Top-p (nucleus, «ядерное» сэмплирование)

Top-p выбирает не K лучших слов, а **наименьший набор слов, суммарная вероятность которых больше p**. Потом вероятность перераспределяется внутри этого набора и слово выбирается из него.

Размер набора теперь **меняется сам**:

- если следующее слово трудно предсказать (распределение плоское), в набор попадает много слов;
- если слово легко предсказать (распределение острое), хватает двух-трёх слов.

Например, при p = 0,92 в одном шаге набор может состоять из 9 слов, а в другом — из 3: этого достаточно, чтобы набрать 92 % вероятности.

Top-p включается так: `0 < top_p < 1`:

```python
set_seed(42)

sample_output = model.generate(
    **model_inputs,
    max_new_tokens=40,
    do_sample=True,
    top_p=0.92,
    top_k=0
)
```

```text
I enjoy walking with my cute dog for the rest of the day, but this had me staying in an unusual room and not going on nights out with friends (which will always be my yearning for such a spacious screen on my desk
```

## Top-K и top-p вместе

В теории top-p элегантнее, но на практике оба метода работают хорошо. Их можно сочетать: top-K отрезает совсем маловероятные слова, а top-p даёт гибкость внутри оставшихся.

Чтобы получить несколько независимых вариантов, задайте `num_return_sequences > 1`:

```python
set_seed(42)

sample_outputs = model.generate(
    **model_inputs,
    max_new_tokens=40,
    do_sample=True,
    top_k=50,
    top_p=0.95,
    num_return_sequences=3,
)
for i, sample_output in enumerate(sample_outputs):
    print("{}: {}".format(i, tokenizer.decode(sample_output, skip_special_tokens=True)))
```

```text
0: I enjoy walking with my cute dog for the rest of the day, but this time it was hard for me to figure out what to do with it. When I finally looked at this for a few moments, I immediately thought, "
1: I enjoy walking with my cute dog. The only time I felt like walking was when I was working, so it was awesome for me. I didn't want to walk for days. I am really curious how she can walk with me
2: I enjoy walking with my cute dog (Chama-I-I-I-I-I), and I really enjoy running. I play in a little game I play with my brother in which I take pictures of our houses.
```

## Выводы статьи

- В открытой генерации top-p и top-K обычно дают более гладкий текст, чем жадный поиск и beam search.
- Есть данные, что повторы у жадного поиска и beam search вызваны в основном самой моделью (тем, как её обучали), а не методом декодирования (Welleck и др., 2019). И top-K, и top-p тоже иногда повторяются (Welleck и др., 2020).
- Если изменить цель обучения модели, beam search по оценкам людей может давать текст глаже, чем top-p.
- Универсального лучшего метода нет: проверяйте, что работает в вашей задаче. Все методы доступны в `transformers` — см. [обзор стратегий декодирования](https://huggingface.co/docs/transformers/generation_strategies#decoding-strategies).

## Шпаргалка

| Метод | Параметры в `generate` | Что делает |
|---|---|---|
| Жадный поиск | `do_sample=False` (по умолчанию) | всегда самое вероятное слово |
| Чистое сэмплирование | `do_sample=True, top_k=0` | случайно по вероятностям модели |
| Temperature | `temperature=T` | T < 1 — острее и скучнее, T > 1 — площе и разнообразнее |
| Top-K | `top_k=K` | выбор только из K лучших слов |
| Top-p | `top_p=p`, `0 < p < 1` | выбор из минимального набора слов с суммой вероятностей ≥ p |
