"""ego CLI — subcommands: init, list, check, pull, push."""

import argparse
import sys

from ego import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ego", description="Ego practice platform")
    parser.add_argument("--version", action="version", version=f"ego {__version__}")
    sub = parser.add_subparsers(dest="command")

    # init — реализован в ego.cli.init_cmd (эта задача, ego-trainer-8bv.1)
    p_init = sub.add_parser("init", help="Initialize .ego/ in current directory")
    p_init.add_argument("--local", action="store_true", help="Offline mode, no server")
    p_init.add_argument(
        "--server-url", default="http://localhost:8000", help="Server URL (online mode)"
    )
    p_init.add_argument("--force", action="store_true", help="Overwrite existing .ego/")

    # list — реализуется в ego.cli.list_cmd (задача 8bv.6, параллельно)
    p_list = sub.add_parser("list", help="List tasks and progress")
    p_list.add_argument(
        "--local",
        action="store_true",
        help="Scan docs/tasks/ offline (no .ego/ needed)",
    )

    # check — реализован в ego.cli.check_cmd (задача 8bv.2)
    p_check = sub.add_parser("check", help="Check a task solution against reference")
    p_check.add_argument("task_id", help="Task id, e.g. F1 or 1.5")
    p_check.add_argument(
        "--local",
        action="store_true",
        help="Offline: parse docs/tasks/ directly, no .ego/ needed",
    )

    # Заглушки для будущих команд (реализуются в других задачах)
    for cmd in ("pull", "push"):
        sub.add_parser(cmd, help=f"{cmd} (not implemented yet)")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "init":
        from ego.cli.init_cmd import run as run_init
        return run_init(args)
    if args.command == "list":
        try:
            from ego.cli.list_cmd import run as run_list
        except ImportError:
            print(
                "ego list is not implemented yet (see beads ego-trainer-8bv.6)",
                file=sys.stderr,
            )
            return 1
        return run_list(args)
    if args.command == "check":
        from ego.cli.check_cmd import run as run_check
        return run_check(args)
    if args.command in ("pull", "push"):
        print(f"ego {args.command} is not implemented yet (see beads roadmap)", file=sys.stderr)
        return 1
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
