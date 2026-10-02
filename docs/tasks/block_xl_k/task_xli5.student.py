"""Задача I5: Подсчёт токенов — упрощённый cl100k

Блок: XL-K — LLM-токенайзер
Сложность: pizdec
Тип: написать новый код
Темы: токенизация, эвристика, парсинг текста

== УСЛОВИЕ ==

Настоящий токенайзер cl100k_base у OpenAI — сложная модель BPE.
Твоя задача — написать упрощённую эвристику подсчёта токенов:

  - Английские слова: 1 токен на каждые 4 символа (ceil).
  - Числа: 1 токен на каждые 2 цифры (ceil).
  - Пунктуация (.,!?;:()[]{}'"—) — каждый знак 1 токен.
  - Пробелы — 0 токенов.
  - Всё остальное (не-ASCII, эмодзи) — 2 токена на символ.

== АРГУМЕНТЫ ==

- text — строка (может быть пустой)

== ВОЗВРАЩАЕТ ==

Целое число — оценочное количество токенов.

== ПРАВИЛА ==

- Пустая строка → 0.
- Слова разделяются пробелами; внутри слова могут быть буквы и цифры.
- Слово разбивается на максимальные подслова: буквы / цифры / прочее.
- Пунктуация считается отдельно от слов, даже если стоит вплотную.

== ПРИМЕР ==

  count_tokens_simple("Hello, world! 42")
  # -> "Hello"(2) + ","(1) + "world"(2) + "!"(1) + "42"(1) = 7
"""
from typing import Literal

def task_xli5_count_tokens_simple(text):
    # ТВОЙ КОД ЗДЕСЬ
    if len(text) == 0:
        return 0

    tokens = text.split(" ")
    tokens_count = 0

    ledge_counter = 0
    current_state: Literal["word", "number"] = "word"
    for word_token in tokens:
        for char_token in word_token:
            if not char_token.isalnum():
                ledge_counter = 0
                current_state = "word"
                tokens_count += 1
                continue

            if current_state == "word" and char_token.isdigit():
                    tokens_count += ledge_counter / 4
                    current_state = "number"
                    ledge_counter = 0
                    continue

            if current_state == "number" and not char_token.isdigit():
                    tokens_count += ledge_counter / 2
                    current_state = "word"
                    ledge_counter = 0
                    continue

            ledge_counter += 1
    return tokens_count
