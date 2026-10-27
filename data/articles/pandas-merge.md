---
title: pandas — объединение таблиц через merge
source: Документация pandas, «Merge, join, concatenate and compare», раздел merge()
original: https://pandas.pydata.org/docs/user_guide/merging.html#merge
kind: перевод
license: BSD-3-Clause, pandas Development Team
---
pandas даёт несколько способов объединять и сравнивать `Series` и `DataFrame`:

- `concat()` — склеить несколько `Series` или `DataFrame` по общему индексу или столбцу;
- `DataFrame.join()` — объединить несколько `DataFrame` по столбцам;
- `DataFrame.combine_first()` — заполнить пропуски значениями из той же позиции другой таблицы;
- `merge()` — объединить два `Series` или `DataFrame` как JOIN в SQL;
- `merge_ordered()` — объединить по упорядоченной оси;
- `merge_asof()` — объединить по ближайшему, а не точному совпадению ключей;
- `Series.compare()` и `DataFrame.compare()` — показать различия значений двух объектов.

Ниже перевод раздела про `merge()`.

## merge()

`merge()` выполняет объединения, как в реляционных базах данных (SQL). Если вы знаете SQL, но новичок в pandas, посмотрите [сравнение с SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#compare-with-sql-join).

### Типы объединения

`merge()` реализует обычные для SQL виды объединения:

- **один к одному**: объединить два `DataFrame` по индексам, где значения уникальны;
- **многие к одному**: объединить уникальный индекс с одним или несколькими столбцами другого `DataFrame`;
- **многие ко многим**: объединить столбцы со столбцами.

> Примечание. Когда объединяются столбцы со столбцами (возможно, «многие ко многим»), индексы переданных `DataFrame` **отбрасываются**.

При объединении **многие ко многим**: если комбинация ключей встречается больше одного раза в обеих таблицах, результат содержит **декартово произведение** соответствующих строк.

```python
left = pd.DataFrame(
    {
        "key": ["K0", "K1", "K2", "K3"],
        "A": ["A0", "A1", "A2", "A3"],
        "B": ["B0", "B1", "B2", "B3"],
    }
)
right = pd.DataFrame(
    {
        "key": ["K0", "K1", "K2", "K3"],
        "C": ["C0", "C1", "C2", "C3"],
        "D": ["D0", "D1", "D2", "D3"],
    }
)
result = pd.merge(left, right, on="key")
```

```text
  key   A   B   C   D
0  K0  A0  B0  C0  D0
1  K1  A1  B1  C1  D1
2  K2  A2  B2  C2  D2
3  K3  A3  B3  C3  D3
```

Аргумент `how` задаёт, какие ключи попадут в результат. Если комбинации ключей **нет** в левой или правой таблице, значения в результате будут `NA` (пропуск). Варианты `how` и их имена в SQL:

| Метод merge | Имя в SQL | Что делает |
|---|---|---|
| `left` | `LEFT OUTER JOIN` | только ключи левой таблицы |
| `right` | `RIGHT OUTER JOIN` | только ключи правой таблицы |
| `outer` | `FULL OUTER JOIN` | объединение ключей обеих таблиц |
| `inner` | `INNER JOIN` | пересечение ключей обеих таблиц |
| `cross` | `CROSS JOIN` | декартово произведение строк обеих таблиц |

Пример с двумя ключами:

```python
left = pd.DataFrame(
    {
        "key1": ["K0", "K0", "K1", "K2"],
        "key2": ["K0", "K1", "K0", "K1"],
        "A": ["A0", "A1", "A2", "A3"],
        "B": ["B0", "B1", "B2", "B3"],
    }
)
right = pd.DataFrame(
    {
        "key1": ["K0", "K1", "K1", "K2"],
        "key2": ["K0", "K0", "K0", "K0"],
        "C": ["C0", "C1", "C2", "C3"],
        "D": ["D0", "D1", "D2", "D3"],
    }
)
```

`how="left"`:

```python
pd.merge(left, right, how="left", on=["key1", "key2"])
```

```text
  key1 key2   A   B    C    D
0   K0   K0  A0  B0   C0   D0
1   K0   K1  A1  B1  NaN  NaN
2   K1   K0  A2  B2   C1   D1
3   K1   K0  A2  B2   C2   D2
4   K2   K1  A3  B3  NaN  NaN
```

`how="right"`:

```python
pd.merge(left, right, how="right", on=["key1", "key2"])
```

```text
  key1 key2    A    B   C   D
0   K0   K0   A0   B0  C0  D0
1   K1   K0   A2   B2  C1  D1
2   K1   K0   A2   B2  C2  D2
3   K2   K0  NaN  NaN  C3  D3
```

`how="outer"`:

```python
pd.merge(left, right, how="outer", on=["key1", "key2"])
```

```text
  key1 key2    A    B    C    D
0   K0   K0   A0   B0   C0   D0
1   K0   K1   A1   B1  NaN  NaN
2   K1   K0   A2   B2   C1   D1
3   K1   K0   A2   B2   C2   D2
4   K2   K0  NaN  NaN   C3   D3
5   K2   K1   A3   B3  NaN  NaN
```

`how="inner"`:

```python
pd.merge(left, right, how="inner", on=["key1", "key2"])
```

```text
  key1 key2   A   B   C   D
0   K0   K0  A0  B0  C0  D0
1   K1   K0  A2  B2  C1  D1
2   K1   K0  A2  B2  C2  D2
```

`how="cross"` — каждая строка слева с каждой строкой справа (4 × 4 = 16 строк):

```python
pd.merge(left, right, how="cross")
```

```text
   key1_x key2_x   A   B key1_y key2_y   C   D
0      K0     K0  A0  B0     K0     K0  C0  D0
1      K0     K0  A0  B0     K1     K0  C1  D1
2      K0     K0  A0  B0     K1     K0  C2  D2
3      K0     K0  A0  B0     K2     K0  C3  D3
4      K0     K1  A1  B1     K0     K0  C0  D0
..    ...    ...  ..  ..    ...    ...  ..  ..
15     K2     K1  A3  B3     K2     K0  C3  D3

[16 rows x 8 columns]
```

`Series` можно объединить с `DataFrame`, если у `Series` есть `MultiIndex`, а имена его уровней совпадают со столбцами `DataFrame`. Ещё можно перед объединением превратить `Series` в `DataFrame` через `Series.reset_index()`:

```python
df = pd.DataFrame({"Let": ["A", "B", "C"], "Num": [1, 2, 3]})
ser = pd.Series(
    ["a", "b", "c", "d", "e", "f"],
    index=pd.MultiIndex.from_arrays(
        [["A", "B", "C"] * 2, [1, 2, 3, 4, 5, 6]], names=["Let", "Num"]
    ),
)
pd.merge(df, ser.reset_index(), on=["Let", "Num"])
```

```text
  Let  Num  0
0   A    1  a
1   B    2  b
2   C    3  c
```

Внешнее объединение (`outer`) с повторяющимися ключами:

```python
left = pd.DataFrame({"A": [1, 2], "B": [2, 2]})
right = pd.DataFrame({"A": [4, 5, 6], "B": [2, 2, 2]})
pd.merge(left, right, on="B", how="outer")
```

```text
   A_x  B  A_y
0    1  2    4
1    1  2    5
2    1  2    6
3    2  2    4
4    2  2    5
5    2  2    6
```

> Внимание. Объединение по повторяющимся ключам сильно увеличивает размер результата и может переполнить память.

### Проверка уникальности ключей

Аргумент `validate` проверяет, уникальны ли ключи объединения. Проверка идёт до объединения. Она защищает от переполнения памяти и неожиданных повторов ключей.

```python
left = pd.DataFrame({"A": [1, 2], "B": [1, 2]})
right = pd.DataFrame({"A": [4, 5, 6], "B": [2, 2, 2]})
pd.merge(left, right, on="B", how="outer", validate="one_to_one")
```

```text
MergeError: Merge keys are not unique in right dataset; not a one-to-one merge
Duplicates in right:
  B
 2
 2 ...
```

Допустим, вы знаете о повторах в правом `DataFrame`, но хотите убедиться, что в левом их нет. Тогда используйте `validate="one_to_many"` — исключения не будет:

```python
pd.merge(left, right, on="B", how="outer", validate="one_to_many")
```

```text
   A_x  B  A_y
0    1  1  NaN
1    2  2  4.0
2    2  2  5.0
3    2  2  6.0
```

### Индикатор происхождения строки

`merge()` принимает аргумент `indicator`. Если он равен `True`, в результат добавляется категориальный столбец `_merge` со значениями:

| Откуда строка | Значение `_merge` |
|---|---|
| ключ только в левой таблице | `left_only` |
| ключ только в правой таблице | `right_only` |
| ключ в обеих таблицах | `both` |

```python
df1 = pd.DataFrame({"col1": [0, 1], "col_left": ["a", "b"]})
df2 = pd.DataFrame({"col1": [1, 2, 2], "col_right": [2, 2, 2]})
pd.merge(df1, df2, on="col1", how="outer", indicator=True)
```

```text
   col1 col_left  col_right      _merge
0     0        a        NaN   left_only
1     1        b        2.0        both
2     2      NaN        2.0  right_only
3     2      NaN        2.0  right_only
```

Если передать в `indicator` строку, она станет именем столбца-индикатора:

```python
pd.merge(df1, df2, on="col1", how="outer", indicator="indicator_column")
```

```text
   col1 col_left  col_right indicator_column
0     0        a        NaN        left_only
1     1        b        2.0             both
2     2      NaN        2.0       right_only
3     2      NaN        2.0       right_only
```

### Столбцы с одинаковыми именами

Аргумент `suffixes` принимает кортеж или список строк. Они добавляются к одинаковым именам столбцов из входных `DataFrame`, чтобы столбцы результата различались:

```python
left = pd.DataFrame({"k": ["K0", "K1", "K2"], "v": [1, 2, 3]})
right = pd.DataFrame({"k": ["K0", "K0", "K3"], "v": [4, 5, 6]})
pd.merge(left, right, on="k")
```

```text
    k  v_x  v_y
0  K0    1    4
1  K0    1    5
```

```python
pd.merge(left, right, on="k", suffixes=("_l", "_r"))
```

```text
    k  v_l  v_r
0  K0    1    4
1  K0    1    5
```
