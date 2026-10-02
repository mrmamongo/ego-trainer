"""XL-O-26 — Аукцион и истечение объявлений (новый код).

Реализуй AuctionHouse с create, bid и settle. Объявление имеет id, seller,
item, ends_at. Ставка должна быть выше текущей, продавец не может ставить
сам, средства резервируются. settle после ends_at выбирает победителя,
перечисляет деньги продавцу и возвращает резерв проигравшим. Повторный settle
идемпотентен и возвращает прежний результат.
"""

class AuctionHouse:
    def __init__(self):
        self.auctions = {}
        self.wallets = {}

    def create(self, auction_id, seller, item, ends_at):
        # TODO: реализовать создание объявления
        raise NotImplementedError

    def bid(self, auction_id, bidder, amount, now):
        # TODO: реализовать ставку и резервирование средств
        raise NotImplementedError

    def settle(self, auction_id, now):
        # TODO: реализовать завершение и возвраты
        raise NotImplementedError
