"""Задача J3: Truncate истории под лимит токенов

Блок: XL-K — Агенты и тул-коллы
Сложность: hard
Тип: написать новый код
Темы: контекстное окно, системный промпт, история сообщений, агенты

== УСЛОВИЕ ==

У агента есть системный промпт, история сообщений и лимит токенов.
Нужно уместить системный промпт + историю в лимит, выкидывая самые
СТАРЫЕ сообщения из истории (системный промпт трогать НЕЛЬЗЯ).

Подсчёт токенов упрощённый:
  - системный промпт: ceil(len(content) / 4) + 2 служебных токена
  - сообщение user/assistant: ceil(len(content) / 4) + 2 служебных токена

Функция возвращает системный промпт, обрезанную историю и статистику.

== АРГУМЕНТЫ ==

- system_prompt — строка, системный промпт (обязателен, всегда в начале)
- messages — список dict: [{"role": "user"|"assistant", "content": str}, ...]
- max_tokens — целое, максимум токенов для всего (system + history)

== ВОЗВРАЩАЕТ ==

Dict:
  {
    "messages": list,       # обрезанная история (подсписок с конца)
    "used_tokens": int,     # токены system_prompt + messages
    "dropped": int          # сколько сообщений выкинули
  }

== ПРАВИЛА ==

- Системный промпт НЕ обрезается — он всегда присутствует в результате.
- Выкинутые сообщения — с НАЧАЛА списка messages.
- used_tokens = сумма токенов(возвращённые messages).
- Если system_prompt сам по себе > max_tokens — messages будет пустым,
  used_tokens всё равно считается по system_prompt.

== ПРИМЕР ==

  messages = [
      {"role": "system", "content": "a" * 40},    # 10 + 2 = 12 токенов
      {"role": "user", "content": "a" * 40},     # 10 + 2 = 12 токенов
      {"role": "assistant", "content": "ok"},     # 1 + 2 = 3 токена
  ]
  truncate_history(messages, 30)
  # -> {
  #     "messages": [{"role": "system", "content": "a" * 40}, {"role": "user", "content": "a" * 40}, {"role": "assistant", "content": "ok"}],
  #     "used_tokens": 12 + 12 + 3 = 27,
  #     "dropped": 0,
  #   }
"""


def task_xlj3_truncate_history(messages, max_tokens):
    # ТВОЙ КОД ЗДЕСЬ
    pass
