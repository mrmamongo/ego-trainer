# Demo-задачи для штатного checker

В `block_demo/` находятся две задачи в поддерживаемом legacy-формате:
условие `.md`, эталон `.solution.py` и тесты `.tests.py`. Это локальные примеры
для разработки; каталог сервера и прогресс студентов они не изменяют.

Из корня репозитория проверь эталоны обычным `ego.checker.run_check`:

```powershell
uv run python -B -c "from pathlib import Path; from ego.parser import parse_task_file; from ego.checker import run_check, format_check_result; t=parse_task_file(Path('examples/tasks/block_demo/task_demo1.md')); r=run_check(t,t.solution_py,level='all'); print(format_check_result(r)); raise SystemExit(0 if r.all_passed else 1)"
uv run python -B -c "from pathlib import Path; from ego.parser import parse_task_file; from ego.checker import run_check, format_check_result; t=parse_task_file(Path('examples/tasks/block_demo/task_demo2.md')); r=run_check(t,t.solution_py,level='all'); print(format_check_result(r)); raise SystemExit(0 if r.all_passed else 1)"
```

Ожидается `passed`, по три теста на каждую задачу. Для проверки своего решения
передай его исходный код вместо `t.solution_py`. Эти вызовы проверяют поведение,
но не записывают `.ego/progress.json` или логи запусков ученика.
