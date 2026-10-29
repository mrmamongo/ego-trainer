def task_pr11_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Account:
    #   2 |     def __init__(self, balance):
    #   3 |         self._balance = balance
    #   4 |         self._nickname = "счёт"
    #   5 |     @property
    #   6 |     def balance(self):
    #   7 |         return self._balance
    #   8 |     @property
    #   9 |     def nickname(self):
    #  10 |         return self._nickname
    #  11 |     @nickname.setter
    #  12 |     def nickname(self, value):
    #  13 |         self._nickname = value
    #  14 |     def deposit(self, amount):
    #  15 |         self._balance = self._balance + amount
    #  16 | a = Account(100)
    #  17 | a.nickname = "зарплата"
    #  18 | n = a.nickname
    #  19 | try:
    #  20 |     a.balance = 500
    #  21 |     r1 = "записали"
    #  22 | except AttributeError:
    #  23 |     r1 = "запрет"
    #  24 | b = a.balance
    #  25 | a.deposit(20)
    #  26 | c = a.balance
    #  27 | d = a.balance - Account(30).balance
    #
    # nick: значение n (строка 18)
    # attempt: значение r1 после try/except (строки 19-23): "записали" или "запрет"
    # before: значение b (строка 24)
    # after: значение c (строка 26)
    # diff: значение d (строка 27)

    nick = None
    attempt = None
    before = None
    after = None
    diff = None

    # Ниже ничего не меняй: это рамка для проверки.
    return nick, attempt, before, after, diff
