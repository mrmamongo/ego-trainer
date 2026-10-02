"""Задача I3: BPE merge — улучши код

Блок: XL-K — LLM-токенайзер
Сложность: easy
Тип: улучши код (добавь функционал)
Темы: BPE, валидация входных данных, робастность

== УСЛОВИЕ ==

Функция merge_pair ниже заменяет ВСЕ вхождения пары (a, b) в каждом
предложении на один новый токен new_token. Она работает, но хрупкая.

Твоя задача — улучшить её:
  1) Если new_token — пустая строка, НЕ заменять пару, а оставить как есть
     (сейчас silently «съедает» оба токена).
  2) Если new_token совпадает с a или b — породит бесконечный цикл
     при внешнем использовании — в этом случае кидать ValueError.


== АРГУМЕНТЫ ==

- sentences — список списков строк
- pair — tuple (a, b) — какую пару искать
- new_token — строка, на что заменять

== ВОЗВРАЩАЕТ ==

Новый список предложений с применённым слиянием (не мутирует вход).

== ПРАВИЛА ==

- Вход не мутируется: работаем с копией.
- Замена идёт по всем вхождениям пары в каждом предложении.
- Пустой new_token → вернуть копию входа без изменений.
- new_token == a или new_token == b → ValueError.

== ПРИМЕР ==

  merge_pair([["t", "h", "e"]], ("t", "h"), "th")
  # -> [["th", "e"]]

  merge_pair([["t", "h"]], ("t", "h"), "")
  # -> [["t", "h"]]  (пустой new_token — без изменений)

  merge_pair([["t", "h"]], ("t", "h"), "t")
  # -> ValueError  (new_token == a)
"""


def merge_pair(sentences, pair, new_token):
    """Заменяет все вхождения пары (a, b) на new_token в каждом предложении."""
    a, b = pair
    result = []
    for sent in sentences:
        new_sent = []
        i = 0
        while i < len(sent):
            if i + 1 < len(sent) and sent[i] == a and sent[i + 1] == b:
                new_sent.append(new_token)
                i += 2
            else:
                new_sent.append(sent[i])
                i += 1
        result.append(new_sent)
    return result


def task_xli3_merge_pair(sentences, pair, new_token):
    # Вызови улучшенный merge_pair, добавив валидацию по условию
    return merge_pair(sentences, pair, new_token)
