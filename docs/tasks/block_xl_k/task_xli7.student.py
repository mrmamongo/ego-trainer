"""Задача I7: Sliding window для RAG — улучши код -- переписать на нормальную: overlap должен быть по словам, а не по символам

Блок: XL-K — LLM-токенайзер
Сложность: bug
Тип: улучши код (добавь функционал)
Темы: RAG, chunking, sliding window, обработка текста

== УСЛОВИЕ ==

Функция chunk_text ниже разбивает текст на куски (чанки) фиксированной
длины с перекрытием — для RAG (retrieval-augmented generation).

Проблема: чанки режут текст посередине слова. Нужно улучшить:
  1) Если граница чанка попадает ВНУТРЬ слова (символы до и после — не
     пробелы) — сдвинуть границу ВЛЕВО до ближайшего пробела.
  2) Если граница попадает на пробел — оставить как есть.
  3) Добавь docstring с описанием контракта.

== АРГУМЕНТЫ ==

- text — строка
- chunk_size — целое, длина одного чанка
- overlap — целое, перекрытие соседних чанков (overlap < chunk_size)

== ВОЗВРАЩАЕТ ==

Список строк — чанки текста.

== ПРАВИЛА ==

- Первый чанк всегда с позиции 0.
- Каждый следующий начинается с (конец предыдущего - overlap).
- Если граница режет слово — сдвигаем влево до пробела.
- Хвост текста, короче chunk_size, — тоже чанк (если не пустой).

== ПРИМЕР ==

  chunk_text("hello world foo bar", 10, 3)
  # -> ["hello worl", "l foo bar"]  (граница сдвинута с 10 до 6, где пробел)
"""


def chunk_text(text, chunk_size, overlap):
    """Разбивает текст на чанки длины chunk_size с перекрытием overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def task_xli7_chunk_text(text, chunk_size, overlap):
    # Вызови улучшенный chunk_text с «мягкими» границами по условию
    return chunk_text(text, chunk_size, overlap)
