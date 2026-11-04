def task_mo02_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | class Playlist:
    #   2 |     def __init__(self, tracks):
    #   3 |         self.tracks = tracks
    #   4 |     def __len__(self):
    #   5 |         return len(self.tracks)
    #   6 |     def __getitem__(self, index):
    #   7 |         return self.tracks[index]
    #   8 | p = Playlist(["rock", "jazz", "pop"])
    #   9 | n = len(p)
    #  10 | first = p[0]
    #  11 | last = p[-1]
    #  12 | letter = p[1][0]
    #  13 | try:
    #  14 |     p[3]
    #  15 |     status = "ok"
    #  16 | except IndexError:
    #  17 |     status = "нет трека"
    #  18 | empty = len(Playlist([]))
    #
    # n: значение n (строка 9)
    # first: значение first (строка 10)
    # last: значение last (строка 11)
    # letter: значение letter (строка 12): первая буква второго трека
    # status: значение status после блока try (строки 13-17)
    # empty: значение empty (строка 18)

    n = None
    first = None
    last = None
    letter = None
    status = None
    empty = None

    # Ниже ничего не меняй: это рамка для проверки.
    return n, first, last, letter, status, empty
