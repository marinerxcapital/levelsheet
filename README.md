# LevelSheet

Futures daily levels sheet generator for CME/CBOT/NYMEX/COMEX roots.

## Table of Contents

1. [Overview](#overview)
2. [Install](#install)
3. [Quick Start](#quick-start)
4. [CLI](#cli)
5. [GUI](#gui)
6. [Configuration](#configuration)
7. [Docker](#docker)
8. [Development](#development)
9. [License](#license)

## Overview

**LevelSheet** produces a single-page, color-coded, print-ready daily levels sheet
(300 DPI PNG + US-Letter-landscape PDF) for any futures root (ES, NQ, CL, GC, …).

> Documentation is completed in Phase 7. This skeleton tracks the planned TOC.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Quick Start

```bash
python -m levelsheet generate ES --date 2026-08-12 --format pdf,png
make run-gui
```

## CLI

See `python -m levelsheet --help` (wired in Phase 5).

## GUI

```bash
make run-gui
# → http://localhost:8501
```

## Configuration

Defaults live in `src/levelsheet/config/default_config.yaml`. Overrides via
`~/.levelsheet/config.yaml`, `./levelsheet.yaml`, CLI flags, and `LEVELSHEET__*` env vars.

## Docker

```bash
cp .env.example .env
docker-compose up
```

## Development

```bash
make lint
make typecheck
make test-cov
```

## License

Proprietary — BPTC 26 LLC. For educational purposes only. Not financial advice.
