# DECISIONS.md — LevelSheet Agent Judgment Log

This file records every non-obvious choice made while implementing LevelSheet
from the maximal build spec. Updated each phase; finalized in Phase 7.

## Phase 0

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package layout | `src/levelsheet/` | Matches pyproject `where = ["src"]`; avoids import shadowing. |
| Dependency pins | Latest stable on 2026-08-12 via `pip index versions` | Spec requires `==` pins written here. See versions below. |
| argparse vs click | argparse | Spec mandates stdlib argparse. |
| Config merge strategy | Deferred to Phase 6 (deep-merge dicts + pydantic validate) | Stub returns defaults in Phase 0. |
| ib_insync | Optional extra `[ib]`, lazy import only | Never a hard dependency. |
| Weasyprint system deps | Documented in Dockerfile (pango/cairo) | Required for HTML→PDF path. |

### Resolved dependency versions (build-time)

```
pandas==3.0.5
numpy==2.5.2
scipy==1.18.0
yfinance==1.5.2
polygon-api-client==1.16.3
matplotlib==3.11.1
seaborn==0.13.2
Pillow==12.3.0
reportlab==5.0.0
weasyprint==69.0
streamlit==1.61.1
pydantic==2.13.4
pydantic-settings==2.15.0
loguru==0.7.3
pyarrow==19.0.1
tenacity==9.1.4
PyYAML==6.0.3
pytest==9.1.1
pytest-cov==7.1.0
pytest-mock==3.15.1
hypothesis==6.165.3
black==26.5.1
ruff==0.16.2
mypy==2.3.0
ib_insync==0.9.86
```

**Note:** `pyarrow` pinned to `19.0.1` (not latest 25.x) because `streamlit==1.61.1` requires `pyarrow<25`.

## Phase 1

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ATR fixture series | 15 synthetic OHLC bars in expected_values.json | Hand-computed Wilder ATR[14]=4.346938775510204 |
| ElliottProjection.waves | list[dict] not raw DataFrame | Pydantic-serializable; conversion at boundary |
| Zigzag consecutive same-kind | Keep more extreme | Ensures strictly alternating output |
| Fib 261.8% fixture | Assert 4414.60 (formula) not spec's 4415.40 | Spec typo: 4900−300×1.618=4414.60 |
| classic_pivots property | Assert R2+S2==2P (not R1+S1) | Spec typo; R1+S1==2P only when C=(H+L)/2 |

## Phase 2

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Polygon ticker format | `I:{ROOT}` | Continuous futures index-style; overridable via resolve_symbol |
| Ratio back-adjustment | `new_close/old_close` (not old/new) | Spec inverted; correct stitch zeroes roll gap |
| IB fetch | Availability probe only; fetch raises | Avoid hard-failing without live Gateway |
| Cache historical freshness | Skip staleness when as_of < max_cached | History immutable |
| ES fixtures | 300-row RNG seed 42 from 2025-01-02 | Deterministic integration baseline |

## Phase 3

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sheet composer module | `render/compose.py` + `render/sheet_data.py` | Keeps panel modules pure draw functions |
| Seaborn usage | `sns.set_theme` only | Spec forbids `sns.*plot` |
| Sample layout fixture | `tests/fixtures/expected_layout.png` (5100×3300) | Pixel-diff / visual regression baseline |

## Phase 4

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default PDF engine | matplotlib `savefig` | Matches 17×11 canvas; weasyprint feature-flagged |
| Book export | `PdfPages` | Spec §13 multi-page concatenation |

## Phase 5

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestration | `pipeline.py` | Shared by CLI + GUI; fixture fallback for ES offline |
| CLI `symbols` vs config | Only merge dict-typed CLI overrides into config | Avoids argparse list colliding with `SymbolsConfig` |

## Phase 6

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Config merge | Manual deep-merge then `model_validate` | Clear precedence; pydantic-settings for `LEVELSHEET__*` |
| Sample plugin | `annotate_root` | Demonstrates registry without changing sheet numbers |

## Phase 7

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Coverage omit | `gui/streamlit_app.py`, `__main__.py` | Streamlit side-effectful; package `__main__` thin re-export |
| Sample assets | `assets/sample_ES_sheet.png` + live render | README embed + visual acceptance |
| Docker verification | `docker compose config` + image build when Docker available | Compose file validated; runtime needs daemon |
| Date for acceptance demo | Prefer live trading day; fixtures cover 2026-02-25 | yfinance warm-cache path verified under 10s |
