---
title: Замыкания с поздним связыванием
source: The Hitchhiker’s Guide to Python, раздел «Common Gotchas»
original: https://docs.python-guide.org/writing/gotchas/#late-binding-closures
kind: перевод
license: CC BY-NC-SA 3.0, автор — Kenneth Reitz
---
Ещё один частый источник путаницы — то, как Python связывает переменные в замыканиях (и во внешней глобальной области).

## Что вы написали

```python
def create_multipliers():
    return [lambda x: i * x for i in range(5)]
```

## Что вы ожидали

```python
for multiplier in create_multipliers():
    print(multiplier(2))
```

Вы ожидали список из пяти функций. У каждой своя замкнутая переменная `i`, и функция умножает на неё аргумент:

```
0
2
4
6
8
```

## Что происходит на самом деле

```
8
8
8
8
8
```

Python создал пять функций, но все они умножают `x` на 4.

Замыкания в Python используют **позднее связывание** (late binding). Значения переменных замыкания ищутся в момент **вызова** внутренней функции.

Когда вызывается *любая* из функций, она ищет значение `i` во внешней области. К этому моменту цикл закончился, и в `i` осталось последнее значение — 4.

Особенно неприятно, что эту ловушку часто связывают с `lambda`. Это ошибка: функции из `lambda` ничем не особенны. Обычный `def` ведёт себя точно так же:

```python
def create_multipliers():
    multipliers = []
    for i in range(5):
        def multiplier(x):
            return i * x
        multipliers.append(multiplier)
    return multipliers
```

## Как сделать правильно

Самое общее решение похоже на трюк. Python вычисляет значения аргументов по умолчанию один раз, при создании функции (см. ловушку «изменяемые аргументы по умолчанию»). Поэтому аргумент по умолчанию сразу связывает замыкание с текущим значением:

```python
def create_multipliers():
    return [lambda x, i=i: i * x for i in range(5)]
```

Другой способ — `functools.partial`:

```python
from functools import partial
from operator import mul

def create_multipliers():
    return [partial(mul, i) for i in range(5)]
```

## Когда это не ловушка

Иногда такое поведение замыканий и нужно. Позднее связывание полезно во многих ситуациях. Но создание разных функций в цикле — как раз тот случай, где оно мешает.
