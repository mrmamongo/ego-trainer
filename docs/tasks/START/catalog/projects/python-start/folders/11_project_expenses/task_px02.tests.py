from ego.testing import case, rules

HELP = (
    'Команды:\n'
    'add <сумма> <категория> — записать расход\n'
    'total — сколько потрачено\n'
    'help — эта справка\n'
    'exit — выйти'
)

# --- прошлый шаг: сценарии PX01 должны работать как раньше ---

@case(
    args=(["add 120 кафе"],),
    expected=['Записал: 120 ₽ — кафе'],
    description='прошлый шаг: одна команда add',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 50 еда"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 50 ₽ — еда'],
    description='прошлый шаг: две категории',
    level="full",
)

# --- новый шаг: total и help ---

@case(
    args=(["total"],),
    expected=['Всего: 0 ₽'],
    description='total без расходов',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 80 еда", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 80 ₽ — еда', 'Всего: 200 ₽'],
    description='total после двух расходов',
    level="smoke",
)

@case(
    args=(["help"],),
    expected=[HELP],
    description='справка по командам',
    level="smoke",
)

@case(
    args=(["add 120 кафе", "add 30 кафе", "total"],),
    expected=['Записал: 120 ₽ — кафе', 'Записал: 30 ₽ — кафе', 'Всего: 150 ₽'],
    description='одна категория дважды',
    level="full",
)

@case(
    args=(["total", "add 5 еда", "total"],),
    expected=['Всего: 0 ₽', 'Записал: 5 ₽ — еда', 'Всего: 5 ₽'],
    description='total до и после расхода',
    level="full",
)

@case(
    args=(["help", "add 40 такси", "total", "help"],),
    expected=[HELP, 'Записал: 40 ₽ — такси', 'Всего: 40 ₽', HELP],
    description='help не мешает другим командам',
    level="full",
)

@case(
    args=(["  TOTAL  "],),
    expected=['Всего: 0 ₽'],
    description='команда в любом регистре',
    level="full",
)

@case(
    args=([],),
    expected=[],
    description='ни одной команды',
    level="full",
)

@case(
    args=(["add 999 кафе", "total", "?", "total"],),
    expected=['Записал: 999 ₽ — кафе', 'Всего: 999 ₽', 'Не понимаю команду. Напиши help.', 'Всего: 999 ₽'],
    description='неизвестная команда не меняет сумму',
    level="full",
)


@rules(forbid_names=["sum"])

def task_px02_session(lines):
    ...
