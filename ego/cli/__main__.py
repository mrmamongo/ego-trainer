"""Allow `python -m ego.cli …` (used by vscode-ego offline check)."""

from ego.cli.main import main

raise SystemExit(main())
