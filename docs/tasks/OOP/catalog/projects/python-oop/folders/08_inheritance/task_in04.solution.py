def task_in04_poly():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Notification:
    #   2 |     def __init__(self, to):
    #   3 |         self.to = to
    #   4 |     def send(self, text):
    #   5 |         return "уведомление: " + text
    #   6 | class Email(Notification):
    #   7 |     def send(self, text):
    #   8 |         return "email " + self.to + ": " + text
    #   9 | class Sms(Notification):
    #  10 |     def send(self, text):
    #  11 |         return "sms " + self.to + ": " + text[:5]
    #  12 | class Push(Notification):
    #  13 |     pass
    #  14 | items = [Email("a@x.ru"), Sms("+7900"), Push("app")]
    #  15 | log = []
    #  16 | for n in items:
    #  17 |     log.append(n.send("Привет, мир"))
    #  18 | a = len(log)
    #  19 | b = log[0]
    #  20 | c = log[1]
    #  21 | d = log[2]
    #  22 | e = log[1] == log[2]
    #
    # a_value: значение a (строка 18)
    # b_value: значение b (строка 19)
    # c_value: значение c (строка 20)
    # d_value: значение d (строка 21)
    # e_value: значение e, True или False (строка 22)

    a_value = 3
    b_value = 'email a@x.ru: Привет, мир'
    c_value = 'sms +7900: Приве'
    d_value = 'уведомление: Привет, мир'
    e_value = False

    # Ниже ничего не меняй: это рамка для проверки.
    return a_value, b_value, c_value, d_value, e_value
