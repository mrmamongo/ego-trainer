from ego.testing import case

HELP = (
    'Команды:\n'
    'add <сумма> <категория> — записать расход\n'
    'total — сколько потрачено\n'
    'help — эта справка\n'
    'exit — выйти'
)

# --- прошлые шаги: сценарии PX01–PX02 должны работать как раньше ---

@case(
    args=(["add 120 кафе", "add 80 еда", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — еда', 'Всего: 200 ₽'],
    description='прошлый шаг: add и total',
    level="smoke",
)

@case(
    args=(["total"],),
    expected=['Всего: 0 ₽'],
    description='прошлый шаг: пустой итог',
    level="full",
)

@case(
    args=(["help"],),
    expected=[HELP],
    description='прошлый шаг: справка',
    level="full",
)

# --- новый шаг: проверка суммы и категории ---

@case(
    args=(["add 0 кафе"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='ноль — не расход',
    level="smoke",
)

@case(
    args=(["add abc кафе"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='не число',
    level="smoke",
)

@case(
    args=(["add 120"],),
    expected=['Укажи категорию'],
    description='нет категории',
    level="smoke",
)

@case(
    args=(["add"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='нет ни суммы, ни категории',
    level="full",
)

@case(
    args=(["add -50 кафе"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='минус — не цифра',
    level="full",
)

@case(
    args=(["add 12.5 кафе"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='дробная сумма',
    level="full",
)

@case(
    args=(["add 0", "add abc", "add 30", "total"],),
    expected=[
        'Сумма должна быть целым числом больше нуля',
        'Сумма должна быть целым числом больше нуля',
        'Укажи категорию',
        'Всего: 0 ₽',
    ],
    description='ошибки не записывают расход',
    level="full",
)

@case(
    args=(["add 0 кафе", "add 50 кафе", "total"],),
    expected=['Сумма должна быть целым числом больше нуля', 'Записал: 50 ₽ — кафе', 'Всего: 50 ₽'],
    description='после ошибки можно записать правильный расход',
    level="full",
)

def task_px03_session(lines):
    ...
