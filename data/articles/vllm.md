---
title: vLLM — быстрый инференс и сервер для LLM
source: Документация vLLM, главная страница и «Quickstart»
original: https://docs.vllm.ai/en/latest/getting_started/quickstart.html
kind: перевод
license: Apache-2.0, vLLM project. Установка для AMD, Intel, TPU, Ascend и Mac сокращена до ссылок.
---
## Что такое vLLM

vLLM — быстрая и простая библиотека для инференса и сервинга (обслуживания запросов) больших языковых моделей.

Её создали в Sky Computing Lab Калифорнийского университета в Беркли. Сейчас это один из самых активных open-source проектов в области ИИ: в нём больше 2000 участников из десятков университетов и компаний.

Почему vLLM быстрый:

- высокая пропускная способность сервинга (throughput) — одна из лучших среди открытых решений;
- эффективное управление памятью для ключей и значений внимания (KV-кэш) с помощью [**PagedAttention**](https://blog.vllm.ai/2023/06/20/vllm.html);
- **непрерывный батчинг** (continuous batching) входящих запросов, chunked prefill (обработка длинного промпта по частям), кэш префиксов;
- быстрое выполнение модели через CUDA/HIP graphs;
- квантование: FP8, MXFP8/MXFP4, NVFP4, INT8, INT4, GPTQ/AWQ, GGUF и [другие](https://docs.vllm.ai/en/latest/features/quantization/index.html);
- оптимизированные ядра внимания: FlashAttention, FlashInfer, FlashMLA, Triton и другие;
- спекулятивное декодирование (n-gram, suffix, EAGLE, DFlash);
- автоматическая генерация ядер и преобразования графа через `torch.compile`;
- раздельные (disaggregated) prefill, decode и encode.

Почему vLLM гибкий и удобный:

- работает с популярными моделями Hugging Face без доработок;
- разные алгоритмы декодирования: *параллельное сэмплирование*, *beam search* и другие;
- тензорный, конвейерный (pipeline), data-, expert- и context-параллелизм для распределённого инференса;
- потоковый вывод (streaming);
- структурированный вывод через xgrammar или guidance;
- вызов инструментов (tool calling) и парсеры рассуждений;
- сервер с API, совместимым с OpenAI, а также Anthropic Messages API и gRPC;
- много адаптеров LoRA одновременно;
- GPU NVIDIA и AMD, CPU x86/ARM/PowerPC, а через плагины — Google TPU, Intel Gaudi, Huawei Ascend, Apple Silicon и другие.

vLLM поддерживает больше 200 архитектур моделей с Hugging Face:

- LLM только с декодером (Llama, Qwen, Gemma);
- модели со смесью экспертов, MoE (Mixtral, DeepSeek-V3, Qwen-MoE, GPT-OSS);
- гибридные модели с вниманием и пространством состояний (Mamba, Qwen3.5);
- мультимодальные модели (LLaVA, Qwen-VL, Pixtral);
- модели эмбеддингов и поиска (E5-Mistral, GTE, ColBERT);
- модели наград и классификации (Qwen-Math).

Что почитать дальше:

- [пост о запуске vLLM](https://blog.vllm.ai/2023/06/20/vllm.html) — введение в PagedAttention;
- [статья о vLLM](https://arxiv.org/abs/2309.06180) (SOSP 2023);
- [как непрерывный батчинг даёт в 23 раза больший throughput и снижает медианную задержку](https://www.anyscale.com/blog/continuous-batching-llm-inference) — Cade Daniel и др.

## Быстрый старт

Это руководство показывает два способа работы с vLLM:

- офлайн-инференс батчами;
- онлайн-сервинг.

### Требования

- ОС: Linux.
- Python: от 3.11 до 3.14.

> На macOS vLLM работает через [vLLM-Metal](https://github.com/vllm-project/vllm-metal) с ускорением на GPU Apple Silicon.

### Установка (NVIDIA CUDA)

На GPU NVIDIA vLLM ставится через pip. Рекомендуем [uv](https://docs.astral.sh/uv/) — очень быстрый менеджер окружений Python. Установите `uv`, потом создайте окружение и поставьте vLLM:

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
vllm download-kernels
```

`vllm download-kernels` ставит заранее собранные ядра. Без этой команды vLLM скачивает и компилирует их при запуске, и на GPU Hopper и новее это занимает несколько минут.

Флаг `--torch-backend=auto` (или переменная `UV_TORCH_BACKEND=auto`) говорит `uv` выбрать нужную сборку PyTorch по версии драйвера CUDA. Чтобы задать сборку явно, укажите, например, `--torch-backend=cu126`.

Ещё один удобный способ — `uv run --with`. Он запускает команды вроде `vllm serve` без постоянного окружения:

```bash
uv run --with vllm vllm --help
```

Можно использовать и conda:

```bash
conda create -n myenv python=3.12 -y
conda activate myenv
pip install --upgrade uv
uv pip install vllm --torch-backend=auto
```

Для AMD ROCm, Intel GPU, Google TPU, Ascend NPU и Apple Silicon см. [руководство по установке](https://docs.vllm.ai/en/latest/getting_started/installation/).

### Офлайн-инференс батчами

После установки можно генерировать текст для списка промптов сразу (офлайн-инференс батчами). Полный скрипт: [examples/basic/offline_inference/basic.py](https://github.com/vllm-project/vllm/blob/main/examples/basic/offline_inference/basic.py).

Первая строка импортирует два класса:

- `LLM` — главный класс для офлайн-инференса на движке vLLM;
- `SamplingParams` — параметры сэмплирования.

```python
from vllm import LLM, SamplingParams
```

Дальше задаём список промптов и параметры генерации. Температура сэмплирования — `0.8`, вероятность для nucleus-сэмплирования (top-p) — `0.95`:

```python
prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
```

> Важно. По умолчанию vLLM берёт параметры сэмплирования, которые рекомендует автор модели: файл `generation_config.json` из репозитория модели на Hugging Face, если он есть. Обычно это лучший вариант, если `SamplingParams` не заданы. Чтобы использовать параметры vLLM по умолчанию, создайте `LLM` с `generation_config="vllm"`.

Класс `LLM` запускает движок vLLM и загружает модель [OPT-125M](https://arxiv.org/abs/2205.01068):

```python
llm = LLM(model="facebook/opt-125m")
```

> По умолчанию vLLM скачивает модели с Hugging Face. Чтобы брать модели с ModelScope, задайте переменную окружения `export VLLM_USE_MODELSCOPE=True` до запуска движка.

Самое интересное — генерация. Метод `llm.generate` ставит промпты в очередь движка и выполняет их с высокой пропускной способностью. Результат — список объектов `RequestOutput` со всеми выходными токенами:

```python
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

> `llm.generate` не применяет чат-шаблон модели к промпту. Для Instruct- или Chat-модели примените шаблон сами или вызовите `llm.chat` со списком сообщений в формате OpenAI.

Пример с чат-шаблоном:

```python
# чат-шаблон через токенизатор
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("/path/to/chat_model")
messages_list = [
    [{"role": "user", "content": prompt}]
    for prompt in prompts
]
texts = tokenizer.apply_chat_template(
    messages_list,
    tokenize=False,
    add_generation_prompt=True,
)
outputs = llm.generate(texts, sampling_params)

# или через чат-интерфейс
outputs = llm.chat(messages_list, sampling_params)
for idx, output in enumerate(outputs):
    prompt = prompts[idx]
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

### Онлайн-сервинг

vLLM можно запустить как сервер с протоколом OpenAI API. Тогда он заменяет OpenAI в любом приложении без изменения кода (drop-in replacement).

По умолчанию сервер слушает `http://localhost:8000`. Адрес задают аргументы `--host` и `--port`. Сейчас сервер держит одну модель и умеет, среди прочего, отдавать список моделей, chat completion и completion.

Запуск сервера с моделью [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct):

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct
```

> По умолчанию сервер берёт чат-шаблон из токенизатора. Ещё он применяет `generation_config.json` модели, если он есть. Чтобы это отключить, запустите сервер с `--generation-config vllm`.

Запросы идут в том же формате, что к OpenAI API. Например, список моделей:

```bash
curl http://localhost:8000/v1/models
```

Аргумент `--api-key` или переменная `VLLM_API_KEY` включает проверку ключа в заголовке. Можно передать несколько ключей — сервер примет любой. Это удобно для смены ключей.

#### OpenAI Completions API

Когда сервер запущен, отправьте промпт:

```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }'
```

Сервер совместим с OpenAI API, поэтому подходит и пакет `openai` для Python:

```python
from openai import OpenAI

# ключ и адрес API меняем на сервер vLLM
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    prompt="San Francisco is a",
)
print("Completion result:", completion)
```

#### OpenAI Chat Completions API

vLLM поддерживает и Chat Completions API. Чат — более живой способ общения с моделью: обмен репликами хранится в истории. Это полезно, когда нужен контекст или подробные объяснения.

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
    }'
```

То же через пакет `openai`:

```python
from openai import OpenAI

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ],
)
print("Chat response:", chat_response)
```

### Бэкенды внимания

vLLM поддерживает несколько бэкендов для вычисления внимания на разных платформах. Он сам выбирает самый быстрый бэкенд, который подходит системе и модели.

Бэкенд можно задать вручную аргументом `--attention-backend`:

```bash
# онлайн-сервинг
vllm serve Qwen/Qwen2.5-1.5B-Instruct --attention-backend FLASH_ATTN

# офлайн-инференс
python script.py --attention-backend FLASHINFER
```

Некоторые варианты:

- NVIDIA CUDA: `FLASH_ATTN` или `FLASHINFER`;
- AMD ROCm: `TRITON_ATTN`, `ROCM_ATTN`, `ROCM_AITER_FA` и другие;
- Intel XPU: `FLASH_ATTN`, `TRITON_ATTN`, `TORCH_SDPA` и другие.

> FlashInfer ставится вместе с vLLM, но его собранные ядра — нет. Запускайте `vllm download-kernels` после установки или обновления vLLM.
