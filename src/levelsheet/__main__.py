"""Allow `python -m levelsheet` to invoke the CLI."""

from levelsheet.cli.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
