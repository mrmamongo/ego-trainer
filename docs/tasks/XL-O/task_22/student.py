"""XL-O-22 — Marketplace-фильтры и пагинация (правка).

Реализуй search_market(items, viewer_id, name=None, min_level=None,
max_price=None, limit=20, cursor=None). Исключи объявления viewer_id,
отфильтруй параметры, отсортируй по price, затем id для стабильности.
Верни {'items': [...], 'next_cursor': ...}; cursor — последний id из
предыдущей страницы. Не мутируй объявления.
"""


def search_market(items, viewer_id, name=None, min_level=None, max_price=None, limit=20, cursor=None):
    # TODO: реализовать стабильную курсорную пагинацию
    raise NotImplementedError
