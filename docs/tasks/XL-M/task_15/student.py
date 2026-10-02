"""XL-M-15 — Агрегируй параллельные результаты (новый код).

Агент запускает несколько sub-агентов параллельно.
Каждый возвращает {"id": ..., "status": "ok"/"fail",
"value": ...}. Реализуй aggregate(results):
- Верни {"ok": [...values], "failed": [...ids],
  "summary": {"total": N, "ok": K, "fail": M}}
- Порядок ok-списка — как в results.
- Если results пуст — всё нули.

Пример:
    aggregate([
        {"id": "a", "status": "ok", "value": 10},
        {"id": "b", "status": "fail", "value": 0},
        {"id": "c", "status": "ok", "value": 20},
    ]) == {
        "ok": [10, 20], "failed": ["b"],
        "summary": {"total": 3, "ok": 2, "fail": 1},
    }
"""


def aggregate(results):
    # TODO: реализовать агрегацию
    raise NotImplementedError


if __name__ == "__main__":
    print(aggregate([
        {"id": "a", "status": "ok", "value": 10},
        {"id": "b", "status": "fail", "value": 0},
        {"id": "c", "status": "ok", "value": 20},
    ]))
