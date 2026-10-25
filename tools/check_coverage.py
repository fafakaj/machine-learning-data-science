"""Coverage check: every topic of plan_3_months.md (section 4) has a step in data/plan.json.

How it works:
1. The script cuts the bullets of each week out of plan_3_months.md and splits them into fragments
   (by commas, semicolons, full stops, "vs").
2. COVER maps plan terms to evidence. Each term must occur in that week's bullet text,
   so the table cannot drift away from the plan.
3. Every fragment must contain a term (or be on the IGNORE list: sources, notes). Every term's evidence
   must exist in that week of plan.json:
       t:<topic id>     a theory step or a practice item with this source topic
       p:<number>       a LeetCode step with this problem
       q:<quiz id>      a quiz or oral step;  x:<exercise id>  an exercise step
       s:<text>         a step title or practice item that contains the text
Run: python3 app/tools/check_coverage.py
"""

import json
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
PLAN_MD = APP.parent / "plan_3_months.md"

# Month 1 practice runs on the site (the user chose that over a GitHub repo), so its evidence is site exercises.
COVER = {
    1: {
        "Two Sum": ["p:1"], "Contains Duplicate": ["p:217"], "Valid Anagram": ["p:242"], "Best Time to Buy": ["p:121"],
        "типы": ["t:w1-python-mutability"], "изменяемость": ["t:w1-python-mutability", "q:q-w1-names"],
        "ссылки": ["t:w1-python-mutability"], "`is` vs `==`": ["t:w1-python-mutability"], "deepcopy": ["t:w1-python-copy"],
        "аргументы по умолчанию (B1)": ["t:w1-python-default-args", "x:ex-w1-b1"], "списки списков (B2)": ["t:w1-python-list-of-lists", "x:ex-w1-b2"],
        "области видимости": ["t:w1-python-scopes", "q:q-w1-scopes"], "замыкания": ["t:w1-python-closures", "x:ex-w1-counter"],
        "позднее связывание (B3)": ["t:w1-python-late-binding", "x:ex-w1-b3"], "kwargs": ["t:w1-python-args-kwargs", "x:ex-w1-args"],
        "сложность `list`": ["t:w1-python-complexity"], "хэшируемость (B4)": ["t:w1-python-hashable", "x:ex-w1-freeze"],
        "производная": ["t:w1-math-derivative", "q:q-w1-math1"], "частная производная": ["t:w1-math-partial-gradient"],
        "градиент (D1)": ["t:w1-math-partial-gradient", "x:ex-w1-numgrad"], "цепное правило": ["t:w1-math-chain-rule", "q:q-w1-math2"],
        "Essence of calculus": ["t:w1-math-3b1b-calc-1", "t:w1-math-3b1b-calc-2", "t:w1-math-3b1b-calc-3", "t:w1-math-3b1b-calc-4"],
        "ml-notebooks": ["q:q-w1-tools", "x:ex-w1-tests"], "uv": ["t:w1-tools-uv"], "ruff": ["t:w1-tools-ruff"], "pytest": ["t:w1-tools-pytest"],
        "GitHub Actions": ["t:w1-tools-github-actions"], "ловушки B1–B3": ["x:ex-w1-tests"],
        "B1–B4 и D1 без подсказок": ["q:q-w1-sunday"], "Все верно": ["q:q-w1-sunday"],
    },
    2: {
        "Valid Palindrome": ["p:125"], "Two Sum II": ["p:167"], "Merge Sorted Array": ["p:88"], "Move Zeroes": ["p:283"],
        "Majority Element": ["p:169"],
        "итераторы и генераторы (B5)": ["t:w2-python-iterators-generators", "q:q-w2-gen", "x:ex-w2-fib"],
        "декораторы (B6)": ["t:w2-python-decorators", "x:ex-w2-timer", "x:ex-w2-retry"],
        "контекстные менеджеры": ["t:w2-python-context-managers", "x:ex-w2-ctx"], "исключения": ["t:w2-python-exceptions"],
        "@classmethod": ["t:w2-python-classmethod-staticmethod", "q:q-w2-oop"], "MRO": ["t:w2-python-mro-super"],
        "`super()`": ["t:w2-python-mro-super"], "dunder-методы (B8)": ["t:w2-python-dunder", "x:ex-w2-vector"],
        "`dataclasses`": ["t:w2-python-dataclasses", "x:ex-w2-dataclass"], "GIL": ["t:w2-python-gil-concurrency", "q:q-w2-gil"],
        "`threading`": ["t:w2-python-gil-concurrency"], "`multiprocessing`": ["t:w2-python-gil-concurrency"],
        "`asyncio` (B7)": ["t:w2-python-gil-concurrency"],
        "векторы": ["t:w2-math-la-ch1", "q:q-w2-linalg1"], "матрицы": ["t:w2-math-la-ch3"], "умножение как преобразование": ["t:w2-math-la-ch4"],
        "собственные векторы": ["t:w2-math-la-ch14", "q:q-w2-linalg2"],
        "Essence of linear algebra": ["t:w2-math-la-ch1", "t:w2-math-la-ch5", "t:w2-math-la-ch9"],
        "декоратор `timer`": ["x:ex-w2-timer"], "генератор Фибоначчи": ["x:ex-w2-fib"], "свой контекстный менеджер": ["x:ex-w2-ctx"],
        "класс с dunder-методами": ["x:ex-w2-vector"], "С тестами": ["x:ex-w2-timer", "x:ex-w2-fib", "x:ex-w2-ctx", "x:ex-w2-vector"],
        "потоки vs процессы": ["q:q-w2-bench"], "Замер": ["q:q-w2-bench"], "задаче с ожиданием": ["q:q-w2-bench"],
        "декоратор с нуля за 10 мин": ["x:ex-w2-deco10"], "результат замера потоков (B7)": ["q:q-w2-bench"],
    },
    3: {
        "Valid Parentheses": ["p:20"], "Binary Search": ["p:704"], "Climbing Stairs": ["p:70"], "Reverse Linked List": ["p:206"],
        "вероятность": ["t:w3-math-probability"], "условная вероятность": ["t:w3-math-conditional-bayes"],
        "Байес (D3)": ["t:w3-math-conditional-bayes", "x:ex-w3-bayes"], "матожидание и дисперсия (D4)": ["t:w3-math-expectation-variance"],
        "распределения": ["t:w3-math-distributions"], "ЦПТ": ["t:w3-math-clt"], "гипотезы": ["t:w3-math-hypotheses-pvalue"],
        "p-value (D5)": ["t:w3-math-hypotheses-pvalue", "q:q-w3-stats"],
        "NumPy (векторизация": ["t:w3-tools-numpy", "x:ex-w3-softmax"], "broadcasting": ["t:w3-tools-numpy-broadcasting", "x:ex-w3-pairwise"],
        "numpy-100": ["s:numpy-100"], "pandas": ["t:w3-tools-pandas", "x:ex-w3-pandas"], "`groupby`": ["q:q-w3-pandas"],
        "`merge`": ["q:q-w3-pandas"], "`pivot`": ["q:q-w3-pandas"], "matplotlib": ["t:w3-tools-matplotlib-seaborn"],
        "Jupyter": ["t:w3-tools-jupyter"], "Bash": ["t:w3-tools-bash", "q:q-w3-bash"], "`grep`": ["q:q-w3-bash"], "`find`": ["q:q-w3-bash"],
        "пайпы (G4)": ["q:q-w3-bash"],
        "разберите один ваш хакатон": ["s:Разбор хакатона"], "EDA": ["x:ex-w3-eda"],
        "задача": ["s:Задача: что нужно"], "метрика": ["s:Метрика: как оценивали"],
        "что сделала команда": ["s:Что сделала команда"], "что сделали вы": ["s:Что сделали вы лично"],
        "D3 и D5 без подсказок": ["q:q-w3-prob", "q:q-w3-stats"], "хакатон за 3 минуты": ["s:хакатон за 3 минуты"],
    },
    4: {
        "Longest Substring": ["p:3"], "Contains Duplicate II": ["p:219"], "Ransom Note": ["s:#383 уже на неделе 1"], "учебник Яндекса по ML": ["t:w4-ml-intro"],
        "SQLBolt": ["t:w4-sql-basics", "q:q-w4-sql", "x:ex-w4-sql"], "LeetCode SQL 50": ["x:ex-w4-sql-select", "x:ex-w4-sql-null", "x:ex-w4-sql-join", "x:ex-w4-sql-case", "x:ex-w4-sql"],
        "что такое ML": ["t:w4-ml-intro"], "train/val/test": ["t:w4-ml-train-val-test-overfitting"],
        "переобучение (E2)": ["t:w4-ml-train-val-test-overfitting", "q:q-w4-ml1"], "bias–variance": ["t:w4-ml-bias-variance"],
        "линейная регрессия": ["t:w4-ml-linear-regression", "x:ex-w4-linreg"], "градиентный спуск": ["t:w4-math-gradient-descent"],
        "логистическая регрессия": ["t:w4-ml-logistic-regression", "x:ex-w4-logreg"], "регуляризация L1/L2 (E6)": ["t:w4-ml-regularization"],
        "метрики (E3)": ["t:w4-ml-metrics", "x:ex-w4-metrics"], "кросс-валидация и StratifiedKFold (E4)": ["t:w4-ml-cross-validation", "x:ex-w4-kfold"],
        "утечки (E7)": ["t:w4-ml-leakage", "q:q-w4-ml2"], "kNN vs k-means (E8)": ["t:w4-ml-knn-vs-kmeans"],
        "регрессия на NumPy": ["x:ex-w4-linreg", "x:ex-w4-logreg"], "веса со `sklearn`": ["x:ex-w4-linreg", "x:ex-w4-logreg"],
        "тест «ваши веса": ["x:ex-w4-linreg", "x:ex-w4-logreg"], "Мок №1": ["q:q-w4-oral"], "Python + основы ML": ["q:q-w4-oral"],
    },
    5: {
        "Merge Intervals": ["p:56"], "Group Anagrams": ["p:49"], "Top K Frequent": ["p:347"], "JOIN": ["t:w5-sql-join-groupby"],
        "решающие деревья": ["t:w5-ml-decision-trees"], "Random Forest": ["t:w5-ml-bagging-rf"],
        "бэггинг vs бустинг (E5)": ["t:w5-ml-bagging-vs-boosting"], "градиентный бустинг": ["t:w5-ml-gradient-boosting"],
        "CatBoost / LightGBM / XGBoost": ["t:w5-ml-boosting-libraries"], "Ансамбли": ["t:w5-ml-stacking"], "стекинг": ["t:w5-ml-stacking"],
        "Kaggle Playground": ["s:Kaggle Playground"], "EDA": ["s:EDA:"], "бейзлайн sklearn": ["s:Бейзлайн `sklearn`"],
        "CatBoost": ["s:CatBoost с K-Fold"], "первая отправка": ["s:Первая отправка"], "место на лидерборде": ["s:место на лидерборде"],
        "CV-скор и лидерборд": ["s:CV-скор и лидерборд"],
    },
    6: {
        "Product of Array": ["p:238"], "3Sum": ["p:15"], "Linked List Cycle": ["p:141"], "оконные функции": ["t:w6-sql-window"],
        "Optuna": ["t:w6-ml-optuna", "s:Optuna для"], "K-Fold на практике": ["s:на K-Fold"], "SHAP": ["t:w6-ml-feature-importance-shap", "s:SHAP: топ-10"],
        "кластеризация (k-means": ["t:w6-ml-clustering"], "DBSCAN": ["t:w6-ml-clustering"], "PCA": ["t:w6-ml-pca"],
        "A/B-тесты": ["t:w6-ab-tests"], "мощность": ["t:w6-ab-tests"], "Продуктовые метрики": ["t:w6-product-metrics"],
        "ценообразование": ["t:w6-pricing"], "p-value": ["t:w6-ab-tests"], "MLflow": ["t:w6-tools-mlflow", "s:MLflow"], "Финальная отправка": ["s:Финальная отправка"],
        "топ-50%": ["s:Топ-50%"],
    },
    7: {
        "Invert Binary Tree": ["p:226"], "Maximum Depth": ["p:104"], "Same Tree": ["p:100"],
        "FastAPI": ["t:w7-fastapi"], "Pydantic": ["t:w7-pydantic"], "образ vs контейнер (G3)": ["t:w7-docker-image-container"],
        "docker-compose": ["t:w7-docker-compose"], "GitHub Actions (lint": ["t:w7-github-actions-ci", "s:lint, test, build"],
        "rebase": ["t:w7-git-rebase-reset"], "git": ["t:w7-git-rebase-reset"], "`reset` (G2)": ["t:w7-git-rebase-reset"], "Linux-основы": ["t:w7-linux-basics"],
        "`/predict`": ["s:/predict"], "Dockerfile": ["s:Dockerfile"], "CI": ["s:GitHub Actions: lint"], "README с таблицей моделей": ["s:README с таблицей моделей"],
        "DECISIONS.md": ["s:DECISIONS.md"], "Релиз v1.0": ["s:Релиз v1.0"], "резюме v1": ["t:w7-career-resume", "s:Резюме v1"],
        "разобранным хакатоном": ["s:разобранный хакатон"], "hh.ru и LinkedIn": ["s:hh.ru и LinkedIn"], "друг запускает проект по README": ["s:Друг запускает проект по README"],
    },
    8: {
        "Level Order Traversal": ["p:102"], "Validate BST": ["p:98"], "Kth Largest Element": ["p:215"],
        "нейрон": ["t:w8-dl-neuron-mlp-activations"], "MLP": ["t:w8-dl-neuron-mlp-activations"], "функции активации": ["t:w8-dl-neuron-mlp-activations"],
        "loss": ["t:w8-dl-loss"], "backprop (F1)": ["t:w8-dl-backprop"], "zero_grad": ["t:w8-pytorch-training-loop"],
        "SGD/Adam/AdamW": ["t:w8-dl-optimizers"], "learning rate": ["t:w8-dl-learning-rate"], "BatchNorm/LayerNorm": ["t:w8-dl-normalization"],
        "dropout": ["t:w8-dl-dropout"], "RNN/LSTM": ["t:w8-dl-rnn-lstm"], "почему их заменил трансформер": ["t:w8-dl-rnn-lstm"],
        "Zero to Hero": ["t:w8-karpathy-micrograd", "t:w8-karpathy-makemore"], "micrograd": ["s:micrograd с нуля"],
        "Trainer на PyTorch": ["s:Trainer на PyTorch"], "Fashion-MNIST": ["s:Fashion-MNIST"], "torch.autograd": ["s:tests/test_micrograd.py"],
        "Мок №2": ["s:Мок №2"], "классический ML + Проект №1": ["s:классический ML + Проект №1"],
    },
    9: {
        "Number of Islands": ["p:200"], "Flood Fill": ["p:733"], "Coin Change": ["p:322"],
        "свёртки": ["t:w9-dl-cnn"], "ResNet": ["t:w9-dl-resnet"], "transfer learning": ["t:w9-dl-transfer-learning"],
        "эмбеддинги и косинусное сходство": ["t:w9-embeddings-cosine"], "CLIP": ["t:w9-clip"], "BPE (F4)": ["t:w9-bpe-tokenization"], "токенизация": ["t:w9-bpe-tokenization"],
        "timm": ["t:w9-tools-timm", "s:Fine-tune модели из `timm`"], "BPE с нуля": ["s:tests/test_bpe.py"], "GPT Tokenizer": ["t:w9-bpe-tokenization"],
        "5 в неделю": ["s:5 откликов"], "ваш BPE совпадает с эталоном": ["s:tests/test_bpe.py"],
    },
    10: {
        "House Robber": ["p:198"], "Course Schedule": ["p:207"],
        "attention (F3)": ["t:w10-attention"], "softmax(QKᵀ/√d)·V": ["t:w10-attention"], "маска": ["t:w10-attention-mask-multihead"],
        "multi-head": ["t:w10-attention-mask-multihead"], "позиционное кодирование": ["t:w10-positional-encoding"],
        "encoder (BERT)": ["t:w10-bert-vs-gpt"], "decoder": ["t:w10-bert-vs-gpt"], "KV-кэш": ["t:w10-kv-cache"], "temperature": ["t:w10-sampling"], "top-k": ["t:w10-sampling"],
        "top-p": ["t:w10-sampling"], "Let's build GPT": ["t:w10-karpathy-gpt"], "Illustrated Transformer": ["t:w10-3b1b-transformers", "t:w10-attention"],
        "nanoGPT + KV-кэш": ["s:nanoGPT + KV-кэш"], "TF-IDF + LogReg": ["t:w10-baseline-tfidf", "s:TF-IDF + LogReg"],
        "rubert-tiny2": ["t:w10-baseline-rubert-tiny2"], "scaled_dot_product_attention": ["s:tests/test_attention.py"],
    },
    11: {
        "Medium по пройденным темам": ["p:33", "p:153", "p:739", "p:39", "p:300"],
        "fine-tuning": ["t:w11-sft-fine-tuning"], "SFT": ["t:w11-sft-fine-tuning"], "LoRA и QLoRA (F5)": ["t:w11-lora-qlora"],
        "память обучения": ["t:w11-training-memory"], "градиенты": ["t:w11-training-memory"], "Adam": ["t:w11-training-memory"], "смешанная точность": ["t:w11-mixed-precision"], "BF16": ["t:w11-mixed-precision"],
        "gradient checkpointing": ["t:w11-training-memory"], "квантизация (INT8": ["t:w11-quantization"], "NF4": ["t:w11-quantization"],
        "GGUF": ["t:w11-quantization"], "размер KV-кэша": ["t:w11-training-memory"], "батчинг": ["t:w11-inference-batching-vllm"],
        "vLLM": ["t:w11-inference-batching-vllm"], "LoRA и QLoRA для Qwen": ["s:LoRA и QLoRA для Qwen"],
        "llama.cpp": ["s:llama.cpp"], "Таблица: F1": ["s:Таблица: F1"], "Релиз v1.0": ["s:релиз v1.0"],
        "пиковая память": ["s:Пиковая память"], "Мок №3": ["s:Мок №3"],
    },
    12: {
        "смешанные Easy/Medium": ["p:155", "p:875", "p:19", "p:74", "p:53"],
        "RAG (F6)": ["t:w12-rag-overview"], "чанкинг": ["t:w12-rag-chunking"], "эмбеддинги": ["t:w12-semantic-search"],
        "векторная БД (HNSW": ["t:w12-vector-db-hnsw"], "гибридный поиск": ["t:w12-hybrid-search"], "реранкер": ["t:w12-reranker"],
        "tool calling": ["t:w12-tool-calling"], "агенты": ["t:w12-agents"], "MCP": ["t:w12-mcp"], "оценка RAG": ["t:w12-rag-evaluation"],
        "NDCG": ["t:w12-ranking-metrics"], "MRR": ["t:w12-ranking-metrics"], "RAG-агент": ["s:RAG-агент"],
        "30 вопросов": ["s:30 вопросов"], "Recall@5": ["s:Recall@5"],
    },
    13: {
        "каждый хакатон и каждый проект": ["t:w13-star", "s:Каждый хакатон и проект"], "что сделал бы иначе": ["s:что сделал бы иначе"],
        "3 мин на рассказ": ["s:3 мин на рассказ"], "диктофон": ["s:диктофон"],
        "секция 1": ["s:Мок секции 1"], "секция 2": ["s:Мок секции 2"], "2 задачи": ["s:2 задачи + вопросы по Python"],
        "вопросы по Python": ["s:2 задачи + вопросы по Python"], "Резюме v2": ["s:Резюме v2"],
        "Обновите сайт": ["s:Обновите сайт"], "ваш вклад и метрики": ["s:ваш вклад и метрики"], "test_week0.md": ["s:test_week0.md"],
    },
}

# Fragments that are not study topics: sources, notes, time limits, examples.
IGNORE = [
    "Источник", "подсказка в разборе", "гл. 1–4", "гл. 1–9", "первые 40", "Cosmohackathon", "3 место", "Пересоберите", "своими руками",
    "Запишите", "данные", "C2", "C3", "Medium", "Easy", "все уроки", "5 задач", "GROUP BY", "HAVING", "первые главы",
    "с нуля", "Сравните", "проходит", "30 мин", "выберите", "расходятся не сильно", "стретч", "база из недели 3", "идея",
    "Тесты", "на CPU-задаче", "`time.sleep`", "Объясните", "Все верно", "решите", "Профили", "без подсказок", "RTX 4050",
    "на малом датасете", "Karpathy", "Jay Alammar", "Q", "K", "V", "G1", "F2", "LLM", "Проект №3", "гл", "1–4", "1–9", "например",
    "test", "build", "веса", "LeetCode", "Python", "Математика", "Практика", "Проверка", "Инструменты", "Теория", "SQL",
    "Проект №1", "Карьера", "Рассказы", "Моки", "Шпаргалка", "plan_v2", "раздел 5",
    "веса + градиенты + Adam", "FP16", "инференс", "память", "токенов/с", "±20%", "с Claude", "упрощённо", "письма HR",
    "Поиск и RecSys", "метрики ранжирования", "малая версия", "до и после", "повышает", "по 25 мин", "задача → данные",
    "подход", "что сделал я", "результат в цифрах", "2 задачи + вопросы по Python", "с другом", "начните откликаться",
    "стажировки и Junior", "Проектом №1", "без подсказок", "Принцип", "видео 1–2", "Kaggle —", "CV-скор", "Проект №2",
    "бейзлайны", "INT8", "Таблица", "F1", "SHAP и feature importance", "feature importance", "друг запускает",
    "copy", "`list`", "`dict`", "`set`", "`*args`", "ООП", "@staticmethod", "Ансамбли", "место", "B1–B3", "репозиторий",
]


def week_bullets():
    text = PLAN_MD.read_text()
    sec = text.split("## 4. План по неделям")[1].split("## 5.")[0]
    parts = re.split(r"\n#### Неделя (\d+)", sec)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        bullets = re.findall(r"^- (.*?)(?=^- |\Z|^#|^\*\*Контрольная)", body, re.S | re.M)
        out[int(parts[i])] = " ".join(" ".join(bullets).split())
    return out


def week_evidence(week):
    ev = set()
    for day in week["days"]:
        for s in day["steps"]:
            texts = [s.get("title", ""), s.get("intro") or "", s.get("do") or ""]
            if s.get("topic"):
                ev.add(f"t:{s['topic']}")
            if s.get("problem"):
                ev.add(f"p:{s['problem']}")
            if s.get("quiz"):
                ev.add(f"q:{s['quiz']}")
            if s.get("exercise"):
                ev.add(f"x:{s['exercise']}")
            for it in s.get("items", []):
                texts.append(it["text"])
                if it.get("topic"):
                    ev.add(f"t:{it['topic']}")
                if it.get("auto", {}).get("path"):
                    texts.append(it["auto"]["path"])
            ev.add("s:" + "\n".join(texts))
        for o in day.get("optional", []):
            ev.add("s:" + o["text"])
    return ev


def has(ev, item):
    if item.startswith("s:"):
        needle = item[2:]
        return any(e.startswith("s:") and needle in e for e in ev)
    return item in ev


def main():
    plan = json.loads((APP / "data" / "plan.json").read_text())
    bullets = week_bullets()
    errors = []
    n_terms = 0
    # Problems that are planned in another week on purpose.
    moved = {"s:#383 уже на неделе 1": any(s.get("problem") == 383 for d in plan["weeks"][0]["days"] for s in d["steps"])}
    for w in plan["weeks"]:
        n = w["n"]
        text = bullets[n]
        ev = week_evidence(w)
        terms = COVER.get(n, {})
        for term, evidence in terms.items():
            n_terms += 1
            if term not in text:
                errors.append(f"неделя {n}: термина «{term}» нет в тексте плана (таблица COVER устарела)")
            for item in evidence:
                if item in moved:
                    if not moved[item]:
                        errors.append(f"неделя {n}: {term}: {item}")
                    continue
                if not has(ev, item):
                    errors.append(f"неделя {n}: «{term}» — нет шага {item}")
        # Every fragment of the plan text must be covered by a term or ignored.
        for frag in re.split(r",|;|\. |\.$|\bvs\b|\+|\(|\)|:|\*\*", text):
            frag = frag.strip(" .–-—/")
            if len(frag) < 2:
                continue
            # Short ignore words (Q, K, G1, гл) must match the whole fragment.
            if any(t in frag or frag in t for t in terms) or any(i == frag if len(i) < 4 else i in frag for i in IGNORE):
                continue
            errors.append(f"неделя {n}: фрагмент плана без шага: «{frag}»")
    print(f"Покрытие плана: недель {len(plan['weeks'])}, терминов плана {n_terms}, ошибок {len(errors)}")
    for e in errors:
        print("  -", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
