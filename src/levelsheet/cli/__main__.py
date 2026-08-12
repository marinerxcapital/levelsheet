"""LevelSheet argparse CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from loguru import logger

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


def _generate_command(args: argparse.Namespace) -> int:
    from levelsheet.config.loader import load_config
    from levelsheet.pipeline import apply_roll_rule_json, export_sheet_files, parse_date

    config = load_config(cli_overrides=vars(args))
    as_of = parse_date(args.date)
    formats = [f.strip().lower() for f in args.format.split(",") if f.strip()]
    for symbol in args.symbols:
        if args.roll_rule_json:
            apply_roll_rule_json(symbol, args.roll_rule_json)
        paths = export_sheet_files(
            symbol,
            as_of,
            config,
            Path(args.output_dir),
            formats,
            force_refresh=args.force_refresh,
        )
        for kind, path in paths.items():
            logger.info("Wrote {} -> {}", kind, path)
            print(path)
    return 0


def _book_command(args: argparse.Namespace) -> int:
    from levelsheet.config.loader import load_config
    from levelsheet.pipeline import generate_figure, parse_date
    from levelsheet.render.export_pdf import export_book

    config = load_config(cli_overrides=vars(args))
    as_of = parse_date(args.date)
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    sheets = []
    for symbol in symbols:
        _, fig = generate_figure(symbol, as_of, config)
        sheets.append((symbol, fig))
    export_book(sheets, Path(args.output))
    logger.info("Wrote book -> {}", args.output)
    print(args.output)
    return 0


def _cache_command(args: argparse.Namespace) -> int:
    from datetime import date, timedelta

    from levelsheet.config.loader import load_config
    from levelsheet.data.cache import CachedDataFetcher
    from levelsheet.data.providers import get_provider_chain

    config = load_config(cli_overrides=vars(args))
    fetcher = CachedDataFetcher(get_provider_chain(config), config)
    end = date.today()
    start = end - timedelta(days=365 * 3)
    df = fetcher.fetch(
        args.symbol,
        args.interval,
        start,
        end,
        as_of_date=end,
        force_refresh=True,
    )
    logger.info("Refreshed {} {} -> {} rows", args.symbol, args.interval, len(df))
    print(f"{args.symbol} {args.interval}: {len(df)} rows")
    return 0


def _config_command(args: argparse.Namespace) -> int:
    from levelsheet.config.loader import load_config

    config = load_config(cli_overrides=vars(args))
    if args.config_command == "show":
        print(config.model_dump_json(indent=2))
    return 0


def main() -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args()
    configure_logging(debug=args.debug)
    try:
        if args.command == "generate":
            return _generate_command(args)
        if args.command == "book":
            return _book_command(args)
        if args.command == "cache":
            return _cache_command(args)
        if args.command == "config":
            return _config_command(args)
        print(f"Unknown command {args.command}", file=sys.stderr)
        return 1
    except LevelSheetError as exc:
        logger.error(str(exc))
        if args.debug:
            raise
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
