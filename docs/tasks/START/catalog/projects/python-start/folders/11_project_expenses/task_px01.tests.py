from ego.testing import case

@case(
    args=(["add 120 кафе"],),
    expected=['Записал: 120 ₽ — кафе'],
    description='одна команда add',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 50 еда"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 50 ₽ — еда'],
    description='две категории подряд',
    level="smoke",
)

@case(
    args=(["total"],),
    expected=['Не понимаю команду. Напиши help.'],
    description='команда total ещё не знакома',
    level="smoke",
)

@case(
    args=(["  ADD   80  такси  "],),
    expected=['Записал: 80 ₽ — такси'],
    description='лишние пробелы и заглавные буквы',
    level="full",
)

@case(
    args=([],),
    expected=[],
    description='ни одной команды',
    level="full",
)

@case(
    args=([""],),
    expected=['Не понимаю команду. Напиши help.'],
    description='пустая строка',
    level="full",
)

@case(
    args=(["?", "add 30 кафе"],),
    expected=['Не понимаю команду. Напиши help.', 'Записал: 30 ₽ — кафе'],
    description='непонятная команда не мешает следующей',
    level="full",
)

@case(
    args=(["add 120 кафе", "add 30 кафе"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 30 ₽ — кафе'],
    description='одна категория дважды',
    level="full",
)

def task_px01_session(lines):
    ...
