from ego.testing import case

HELP = (
    'Команды:\n'
    'add <сумма> <категория> — записать расход\n'
    'total — сколько потрачено\n'
    'report — отчёт по категориям\n'
    'undo — отменить последний расход\n'
    'help — эта справка\n'
    'exit — выйти'
)

# --- прошлые шаги: сценарии PX01–PX04 должны работать как раньше ---

@case(
    args=(["add 120 кафе", "add 80 еда", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — еда', 'Всего: 200 ₽'],
    description='прошлый шаг: add и total',
    level="smoke",
)

@case(
    args=(["add 150 кафе", "add 80 такси", "report"],),
    expected=['Записал: 150 ₽ — кафе', 'Записал: 80 ₽ — такси', 'кафе: 150 ₽\nтакси: 80 ₽\nИтого: 230 ₽'],
    description='прошлый шаг: отчёт',
    level="smoke",
)

@case(
    args=(["report"],),
    expected=['Расходов пока нет'],
    description='прошлый шаг: пустой отчёт',
    level="full",
)

@case(
    args=(["add 0 кафе"],),
    expected=['Сумма должна быть целым числом больше нуля'],
    description='прошлый шаг: проверка суммы',
    level="full",
)

@case(
    args=(["help"],),
    expected=[HELP],
    description='прошлый шаг: справка с новой строкой undo',
    level="full",
)

# --- новый шаг: undo ---

@case(
    args=(["undo"],),
    expected=['Нечего отменять'],
    description='отменять нечего',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "undo"],),
    expected=['Записал: 120 ₽ — кафе', 'Отменил: 120 ₽ — кафе'],
    description='отмена одного расхода',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 80 такси", "undo"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — такси', 'Отменил: 80 ₽ — такси'],
    description='отменяется последний',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 80 такси", "undo", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — такси', 'Отменил: 80 ₽ — такси', 'Всего: 120 ₽'],
    description='после отмены итог меньше',
    level="full",
)

@case(
    args=(["add 120 кафе", "undo", "undo"],),
    expected=['Записал: 120 ₽ — кафе', 'Отменил: 120 ₽ — кафе', 'Нечего отменять'],
    description='вторая отмена не работает',
    level="full",
)

@case(
    args=(["add 120 кафе", "add 80 такси", "undo", "report"],),
    expected=[
        'Записал: 120 ₽ — кафе',
        'Записал: 80 ₽ — такси',
        'Отменил: 80 ₽ — такси',
        'кафе: 120 ₽\nИтого: 120 ₽',
    ],
    description='отменённая категория пропадает из отчёта',
    level="full",
)

@case(
    args=(["add 0 кафе", "undo"],),
    expected=['Сумма должна быть целым числом больше нуля', 'Нечего отменять'],
    description='ошибочный add нечего отменять',
    level="full",
)

def task_px05_session(lines):
    ...
