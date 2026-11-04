"""Этап 8: свои шаблоны `.` `^` `$` без модуля re (импорт и чёрный ящик)."""

from ego.testing import case, program, rules

LOG = (
    "INFO server started\n"
    "ERROR disk full\n"
    "INFO retry in 5s\n"
    "error: timeout\n"
    "WARN slow response\n"
    "ERROR disk full again\n"
    "INFO done\n"
    "\n"
    "note: ERROR is not at start\n"
)


@rules(
    forbid_imports=["re", "fnmatch"],
    messages={
        "re": "Модуль re запрещён: шаблоны разбираем сами",
        "fnmatch": "Модуль fnmatch тоже запрещён: шаблоны разбираем сами",
    },
)
@case(
    target="matcher.matches",
    args=("abc", "a.c"),
    expected=True,
    description="точка заменяет любой один символ",
)
def task_gr08_dot():
    ...


@case(
    target="matcher.matches",
    args=("abc", "^b"),
    expected=False,
    description="^ — шаблон должен стоять в начале строки",
)
def task_gr08_start():
    ...


@case(
    target="matcher.matches",
    args=("abc", "c$"),
    expected=True,
    description="$ — шаблон должен стоять в конце строки",
)
def task_gr08_end():
    ...


@case(
    target="matcher.matches",
    args=("abc", "^abc$"),
    expected=True,
    description="^ и $ вместе: шаблон равен всей строке",
)
def task_gr08_whole():
    ...


@case(
    target="matcher.matches",
    args=("ac", "a.c"),
    expected=False,
    description="точка — ровно один символ, не ноль",
    level="full",
)
def task_gr08_dot_not_zero():
    ...


@case(
    target="matcher.matches",
    args=("abbc", "a.c"),
    expected=False,
    description="точка — ровно один символ, не два",
    level="full",
)
def task_gr08_dot_not_two():
    ...


@case(
    target="matcher.matches",
    args=("a.c", "a.c"),
    expected=True,
    description="точка подходит и к самой точке",
    level="full",
)
def task_gr08_dot_matches_dot():
    ...


@case(
    target="matcher.matches",
    args=("a", "a."),
    expected=False,
    description="после `a` нет символа для точки",
    level="full",
)
def task_gr08_dot_needs_char():
    ...


@case(
    target="matcher.matches",
    args=("", "."),
    expected=False,
    description="в пустой строке нет ни одного символа",
    level="full",
)
def task_gr08_dot_empty_line():
    ...


@case(
    target="matcher.matches",
    args=("abab", "^b"),
    expected=False,
    description="^ не находит b в середине строки",
    level="full",
)
def task_gr08_start_middle():
    ...


@case(
    target="matcher.matches",
    args=("abab", "b$"),
    expected=True,
    description="$ находит b в самом конце, хотя раньше b тоже была",
    level="full",
)
def task_gr08_end_second_occurrence():
    ...


@case(
    target="matcher.matches",
    args=("cat", "ca$"),
    expected=False,
    description="`ca` есть в строке, но не в конце",
    level="full",
)
def task_gr08_end_not_at_end():
    ...


@case(
    target="matcher.matches",
    args=("", "^$"),
    expected=True,
    description="^$ подходит к пустой строке",
    level="full",
)
def task_gr08_blank_line():
    ...


@case(
    target="matcher.matches",
    args=("x", "^$"),
    expected=False,
    description="^$ не подходит к непустой строке",
    level="full",
)
def task_gr08_not_blank():
    ...


@case(
    target="matcher.matches",
    args=("abc", "^"),
    expected=True,
    description="один ^ подходит к любой строке",
    level="full",
)
def task_gr08_only_start():
    ...


@case(
    target="matcher.matches",
    args=("abc", "$"),
    expected=True,
    description="один $ подходит к любой строке",
    level="full",
)
def task_gr08_only_end():
    ...


@case(
    target="matcher.matches",
    args=("ab", "^.b$"),
    expected=True,
    description="все три особых символа в одном шаблоне",
    level="full",
)
def task_gr08_all_three():
    ...


@case(
    target="matcher.matches",
    args=("abc", "^.$"),
    expected=False,
    description="^.$ подходит только к строке из одного символа",
    level="full",
)
def task_gr08_one_char_line():
    ...


@case(
    target="matcher.matches",
    args=("a^b", "a^b"),
    expected=True,
    description="^ не в начале шаблона — обычный символ",
    level="full",
)
def task_gr08_caret_literal():
    ...


@case(
    target="matcher.matches",
    args=("a$b", "a$b"),
    expected=True,
    description="$ не в конце шаблона — обычный символ",
    level="full",
)
def task_gr08_dollar_literal():
    ...


@case(
    target="matcher.matches",
    args=("cat dog", "t d"),
    expected=True,
    description="шаблон без особых символов работает как раньше",
    level="full",
)
def task_gr08_plain():
    ...


@program(
    argv=["^ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="main.py: ^ERROR — только строки, начинающиеся с ERROR",
)
def task_gr08_run_start():
    ...


@program(
    argv=["done$", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="INFO done",
    match="exact",
    expected_exit=0,
    description="main.py: done$ — строки, оканчивающиеся на done",
)
def task_gr08_run_end():
    ...


@program(
    argv=["-n", "-i", "^error", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="2:ERROR disk full\n4:error: timeout\n6:ERROR disk full again",
    match="exact",
    expected_exit=0,
    description="main.py: ^ вместе с -i и -n",
)
def task_gr08_run_flags():
    ...


@program(
    argv=["d..k", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="main.py: d..k находит disk",
    level="full",
)
def task_gr08_run_dots():
    ...


@program(
    argv=["-c", "^$", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="1",
    match="exact",
    expected_exit=0,
    description="main.py: -c '^$' считает пустые строки",
    level="full",
)
def task_gr08_run_blank_count():
    ...


@program(
    argv=["-n", "^$", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="8:",
    match="exact",
    expected_exit=0,
    description="main.py: пустая строка печатается с номером",
    level="full",
)
def task_gr08_run_blank_number():
    ...


@program(
    argv=["-v", "^INFO", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout=(
        "ERROR disk full\nerror: timeout\nWARN slow response\n"
        "ERROR disk full again\n\nnote: ERROR is not at start"
    ),
    match="exact",
    expected_exit=0,
    description="main.py: -v ^INFO",
    level="full",
)
def task_gr08_run_invert():
    ...


@program(
    argv=["-c", ".", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="8",
    match="exact",
    expected_exit=0,
    description="main.py: точка подходит к любой непустой строке",
    level="full",
)
def task_gr08_run_any_char():
    ...


@program(
    argv=["5$ t", "prices.txt"],
    files={"prices.txt": "price: 5$ today\nprice 5 today\n"},
    expected_stdout="price: 5$ today",
    match="exact",
    expected_exit=0,
    description="main.py: $ внутри шаблона — обычный символ",
    level="full",
)
def task_gr08_run_dollar_inside():
    ...


@program(
    argv=["ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout=(
        "ERROR disk full\nERROR disk full again\nnote: ERROR is not at start"
    ),
    match="exact",
    expected_exit=0,
    description="main.py: простой шаблон без особых символов работает как раньше",
    level="full",
)
def task_gr08_run_plain():
    ...


@program(
    argv=["-A", "1", "^WARN", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="WARN slow response\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="main.py: шаблон с ^ работает вместе с контекстом",
    level="full",
)
def task_gr08_run_context():
    ...


@program(
    argv=["-c", "^ERROR", "a.log", "b.log"],
    files={"a.log": "ERROR one\nok\n", "b.log": "fine\nERROR two\nERROR three\n"},
    expected_stdout="a.log:1\nb.log:2",
    match="exact",
    expected_exit=0,
    description="main.py: шаблон с ^ и несколько файлов",
    level="full",
)
def task_gr08_run_two_files():
    ...
