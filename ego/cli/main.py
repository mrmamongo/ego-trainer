"""ego CLI — реализован в задаче ego-trainer-8bv.1+."""

import argparse
import sys

from ego import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ego", description="Ego practice platform")
    parser.add_argument("--version", action="version", version=f"ego {__version__}")
    parser.add_argument(
        "command", nargs="?", help="command to run (init/check/pull/push/list)"
    )
    # Реализация команд — в задаче ego-trainer-8bv.1+
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    print(f"Command '{args.command}' not implemented yet", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
