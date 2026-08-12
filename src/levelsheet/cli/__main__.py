"""LevelSheet argparse CLI. Fully wired in Phase 5."""

from __future__ import annotations

import argparse
import sys

from levelsheet.errors import LevelSheetError
from levelsheet.logging_config import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Build the levelsheet argparse parser with subcommands."""
    parser = argparse.ArgumentParser(prog="levelsheet")
    parser.add_argument("--debug", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate")
    gen.add_argument("symbols", nargs="+")
    gen.add_argument("--date", type=str, default=None)
    gen.add_argument("--format", type=str, default="pdf,png")
    gen.add_argument("--batch", action="store_true")
    gen.add_argument("--force-refresh", action="store_true")
    gen.add_argument("--fib-swing-high-date", type=str, default=None)
    gen.add_argument("--fib-swing-low-date", type=str, default=None)
    gen.add_argument("--roll-rule-json", type=str, default=None)
    gen.add_argument("--output-dir", type=str, default="output")

    book = sub.add_parser("book")
    book.add_argument("--date", type=str, default=None)
    book.add_argument("--symbols", type=str, required=True)
    book.add_argument("--output", type=str, required=True)

    cache = sub.add_parser("cache")
    cache_sub = cache.add_subparsers(dest="cache_command", required=True)
    refresh = cache_sub.add_parser("refresh")
    refresh.add_argument("--symbol", required=True)
    refresh.add_argument("--interval", default="1d")

    cfg = sub.add_parser("config")
    cfg_sub = cfg.add_subparsers(dest="config_command", required=True)
    cfg_sub.add_parser("show")

    return parser


def main() -> int:
    """CLI entrypoint. Dispatch fully implemented in Phase 5."""
    args = build_parser().parse_args()
    configure_logging(debug=args.debug)
    try:
        from levelsheet.config.loader import load_config

        _config = load_config(cli_overrides=vars(args))
        if args.command == "config" and getattr(args, "config_command", None) == "show":
            print(_config.model_dump_json(indent=2))
            return 0
        print(f"Command '{args.command}' not yet fully implemented (Phase 5).", file=sys.stderr)
        return 0
    except LevelSheetError as exc:
        from loguru import logger

        logger.error(str(exc))
        if args.debug:
            raise
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
