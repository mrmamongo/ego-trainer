"""XL-M-01 — Исправь парсер XML-ответа LLM (баг: XML-инъекция).

Модель возвращает XML-ответ вида <thinking>...</thinking><answer>...</answer>.
Парсер должен извлечь содержимое тегов, но не экранирует пользовательский
текст внутри answer. Если пользовательский текст содержит <tag>, парсер
ломается или интерпретирует его как новый тег.

Исправь extract_xml_fields(text): верни словарь {"thinking": ..., "answer": ...},
где значение answer — это текст БЕЗ интерпретации вложенных тегов,
т.е. символы < и > в пользовательском тексте должны остаться как есть.

Примеры:
    extract_xml_fields("<thinking>ok</thinking><answer>5 < 10</answer>")
    == {"thinking": "ok", "answer": "5 < 10"}
    extract_xml_fields("<thinking></thinking><answer>a < b > c</answer>")
    == {"thinking": "", "answer": "a < b > c"}
"""

import re


def extract_xml_fields(text):
    # Намеренная ошибка: greedy match и неэкранированный user-текст
    thinking = re.search(r"<thinking>(.*)</thinking>", text).group(1)
    answer = re.search(r"<answer>(.*)</answer>", text).group(1)
    return {"thinking": thinking, "answer": answer}


if __name__ == "__main__":
    print(extract_xml_fields("<thinking>ok</thinking><answer>5 < 10</answer>"))
