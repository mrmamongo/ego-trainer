from ego.testing import case

HELP = (
    'Команды:\n'
    'add <сумма> <категория> — записать расход\n'
    'total — сколько потрачено\n'
    'report — отчёт по категориям\n'
    'help — эта справка\n'
    'exit — выйти'
)

# --- прошлые шаги: сценарии PX01–PX03 должны работать как раньше ---

@case(
    args=(["add 120 кафе", "add 80 еда", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — еда', 'Всего: 200 ₽'],
    description='прошлый шаг: add и total',
    level="smoke",
)

@case(
    args=(["add 0 кафе", "add 120"],),
    expected=['Сумма должна быть целым числом больше нуля', 'Укажи категорию'],
    description='прошлый шаг: проверки add',
    level="full",
)

@case(
    args=(["help"],),
    expected=[HELP],
    description='прошлый шаг: справка с новой строкой report',
    level="full",
)

# --- новый шаг: report ---

@case(
    args=(["report"],),
    expected=['Расходов пока нет'],
    description='отчёт без расходов',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 80 еда", "report"],),
    expected=[
        'Записал: 120 ₽ — кафе',
        'Записал: 80 ₽ — еда',
        'кафе: 120 ₽\nеда: 80 ₽\nИтого: 200 ₽',
    ],
    description='отчёт по двум категориям',
    level="smoke",
)

@case(
    args=(["add 150 кафе", "add 80 такси", "report"],),
    expected=['Записал: 150 ₽ — кафе', 'Записал: 80 ₽ — такси', 'кафе: 150 ₽\nтакси: 80 ₽\nИтого: 230 ₽'],
    description='отчёт из условия',
    level="smoke",
)

@case(
    args=(["add 100 кафе", "add 50 еда", "add 30 кафе", "report"],),
    expected=[
        'Записал: 100 ₽ — кафе',
        'Записал: 50 ₽ — еда',
        'Записал: 30 ₽ — кафе',
        'кафе: 130 ₽\nеда: 50 ₽\nИтого: 180 ₽',
    ],
    description='одна категория несколько раз',
    level="full",
)

@case(
    args=(["add 80 еда", "add 150 кафе", "report"],),
    expected=['Записал: 80 ₽ — еда', 'Записал: 150 ₽ — кафе', 'еда: 80 ₽\nкафе: 150 ₽\nИтого: 230 ₽'],
    description='порядок первого появления',
    level="full",
)

@case(
    args=(["add 40 дом", "report"],),
    expected=['Записал: 40 ₽ — дом', 'дом: 40 ₽\nИтого: 40 ₽'],
    description='одна категория',
    level="full",
)

@case(
    args=(["add 0 кафе", "report"],),
    expected=['Сумма должна быть целым числом больше нуля', 'Расходов пока нет'],
    description='ошибка не добавляет строку в отчёт',
    level="full",
)

@case(
    args=(["add 120 кафе", "total", "add 80 еда", "report", "report"],),
    expected=[
        'Записал: 120 ₽ — кафе',
        'Всего: 120 ₽',
        'Записал: 80 ₽ — еда',
        'кафе: 120 ₽\nеда: 80 ₽\nИтого: 200 ₽',
        'кафе: 120 ₽\nеда: 80 ₽\nИтого: 200 ₽',
    ],
    description='повторный report даёт тот же отчёт',
    level="full",
)

def task_px04_session(lines):
    ...
