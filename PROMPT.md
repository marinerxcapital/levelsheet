# CODEX/CURSOR AGENT PROMPT — "LevelSheet" Futures Daily Levels Generator (MAXIMAL SPEC)

Copy everything below this line into Codex/Cursor as the initial task prompt. This is a complete, unambiguous build spec. Do not ask clarifying questions — every decision is defined. Where something is genuinely undefined, pick the professional-grade default and log it in `DECISIONS.md`.

---

## ROLE

You are a senior Python software architect and quantitative tooling engineer building a production application called **LevelSheet** from a completely empty directory — zero existing code, zero scaffolding, zero assumptions. You will create every file, every function body, every config value listed below. You will not stop, summarize, or ask for confirmation between phases; you will execute Phase 0 through Phase 7 sequentially, committing after each phase, and end with a working, tested, documented application that satisfies every acceptance criterion in §16.

## PROJECT GOAL

Given any CME/CBOT/NYMEX/COMEX futures root (ES, NQ, CL, GC, SI, ZB, 6E, RTY, or any user-typed root resolvable via the symbol table) and a trading date, generate a single-page, color-coded, print-ready **daily levels sheet** as a 300 DPI PNG and a US-Letter-landscape PDF, matching the layout, density, and formula set of institutional prop-trading levels sheets, computed and rendered in under 10 seconds from cached data (under 20 seconds on a cold/first-fetch run).

---

## 1. TECH STACK — LOCKED VERSIONS

Pin these in `requirements.txt` (exact `==` versions the agent selects as latest-stable-at-build-time; write the resolved versions into `DECISIONS.md`):

- Python 3.12+
- pandas, numpy, scipy
- yfinance (primary free fallback provider)
- polygon-api-client (primary paid provider)
- ib_insync (optional live provider — lazy import only, never a hard dependency; guarded by `try/except ImportError`)
- matplotlib (Agg backend, headless-safe: `matplotlib.use("Agg")` set at the top of `render/__init__.py` before any other matplotlib import)
- seaborn (styling context only — `sns.set_theme` for font scaling; **no** `sns.*plot` calls anywhere in the renderer, all drawing is raw matplotlib primitives for pixel control)
- Pillow (compositing logo image onto footer, PNG post-processing)
- reportlab (low-level PDF canvas primitives for the multi-page "book" export)
- weasyprint (HTML→PDF fallback render path, feature-flagged via `render.engine`)
- streamlit (GUI)
- pydantic v2 (all config/schema validation — no bare dicts passed between layers)
- pydantic-settings (for `.env` → config binding of secrets)
- loguru (structured logging)
- click **or** argparse — use **argparse** (stdlib, zero extra dependency) with subparsers
- pytest, pytest-cov, pytest-mock, hypothesis (testing)
- black, ruff, mypy (quality gates)
- pyarrow (Parquet cache backend)
- tenacity (retry/backoff wrapper around all provider network calls)

---

## 2. FULL DIRECTORY STRUCTURE

```
levelsheet/
├── .github/workflows/ci.yml
├── src/levelsheet/
│   ├── __init__.py
│   ├── errors.py
│   ├── logging_config.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── loader.py
│   │   └── default_config.yaml
│   ├── calc/
│   │   ├── __init__.py
│   │   ├── pivots.py
│   │   ├── fibonacci.py
│   │   ├── moving_averages.py
│   │   ├── atr.py
│   │   ├── bias.py
│   │   ├── elliott_wave.py
│   │   ├── extreme_moves.py
│   │   ├── nr7_wr7.py
│   │   ├── warnings_flags.py
│   │   └── autotrade.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── yfinance_provider.py
│   │   │   ├── polygon_provider.py
│   │   │   └── ib_provider.py
│   │   ├── cache.py
│   │   ├── continuous_contract.py
│   │   ├── roll_calendar.py
│   │   └── symbols.py
│   ├── render/
│   │   ├── __init__.py
│   │   ├── layout.py
│   │   ├── theme.py
│   │   ├── fonts.py
│   │   ├── panels/
│   │   │   ├── __init__.py
│   │   │   ├── header.py
│   │   │   ├── daily_pivots.py
│   │   │   ├── center_ohlc_ma.py
│   │   │   ├── mini_candlestick.py
│   │   │   ├── weekly_monthly.py
│   │   │   ├── atr_nr7.py
│   │   │   ├── long_term_fib.py
│   │   │   ├── daily_fib_extreme.py
│   │   │   ├── bias_panel.py
│   │   │   ├── autotrade_panel.py
│   │   │   ├── elliott_panel.py
│   │   │   ├── projected_ma_panel.py
│   │   │   ├── warnings_panel.py
│   │   │   └── footer.py
│   │   ├── export_pdf.py
│   │   └── export_png.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── __main__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   └── streamlit_app.py
│   └── plugins/
│       ├── __init__.py
│       ├── base.py
│       └── registry.py
├── tests/
│   ├── unit/ (one test file per calc/* module, named test_<module>.py)
│   ├── integration/
│   │   ├── test_cache_roundtrip.py
│   │   ├── test_provider_fallback.py
│   │   ├── test_continuous_contract_roll.py
│   │   └── test_full_sheet_generation.py
│   ├── fixtures/
│   │   ├── ES_sample.csv
│   │   ├── ES_weekly_sample.csv
│   │   ├── ES_monthly_sample.csv
│   │   └── expected_values.json
│   └── conftest.py
├── scripts/bootstrap_cache.py
├── assets/{fonts/,logo/}
├── output/{pdf/,png/}
├── cache/
├── logs/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
└── DECISIONS.md
```

---

## 3. DATA SCHEMA — CANONICAL OHLC DATAFRAME

Every provider adapter must return a `pandas.DataFrame` conforming exactly to this schema (validated at the provider boundary via `models/schemas.py::validate_ohlc_df`):

| column        | dtype            | notes                                              |
|---------------|------------------|-----------------------------------------------------|
| index (`date`)| `pandas.DatetimeIndex`, tz-naive, normalized to midnight | sorted ascending, no duplicate dates |
| `open`        | `float64`        | > 0                                                 |
| `high`        | `float64`        | >= open, close, low                                 |
| `low`         | `float64`        | <= open, close, high                                |
| `close`       | `float64`        | > 0                                                  |
| `volume`      | `Int64` (nullable)| may be NaN for some FX/index futures via yfinance   |
| `contract`    | `str`            | e.g. `"ESU6"` — the specific front-month contract that produced this row (required for continuous series audit trail) |

`models/schemas.py::validate_ohlc_df(df: pd.DataFrame) -> None` raises `levelsheet.errors.DataValidationError` on any violation (NaN in OHLC, high < low, unsorted index, duplicate index).

---

## 4. ERROR HIERARCHY — `errors.py`

```python
class LevelSheetError(Exception):
    """Base class for all application errors."""

class ConfigError(LevelSheetError):
    """Raised on invalid or missing configuration."""

class ProviderUnavailableError(LevelSheetError):
    """Raised when a data provider cannot be used (missing key, missing package, network down)."""

class DataValidationError(LevelSheetError):
    """Raised when fetched/cached OHLC data fails schema validation."""

class InsufficientHistoryError(LevelSheetError):
    """Raised when a calculation needs more bars than are available (e.g., MA(200) with 90 bars)."""

class RollCalendarError(LevelSheetError):
    """Raised when a root has no roll calendar entry and none was provided via config override."""

class RenderError(LevelSheetError):
    """Raised on any matplotlib/reportlab/weasyprint failure during sheet composition."""

class ExportError(LevelSheetError):
    """Raised when PDF/PNG write fails (disk, permissions, invalid path)."""

class CacheError(LevelSheetError):
    """Raised on cache read/write corruption; handler should log + fall through to network fetch."""
```

Every public function in `calc/`, `data/`, and `render/` must raise one of the above (never a bare `Exception` or unguarded stdlib exception) so the CLI's top-level handler in `cli/__main__.py` can catch `LevelSheetError` uniformly, log via loguru at `ERROR` level, print a one-line human message to stderr, and exit code `1` — while `--debug` re-raises with full traceback.

---

## 5. LOGGING SPEC — `logging_config.py`

```python
from loguru import logger
import sys

def configure_logging(debug: bool = False) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else "INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        "logs/levelsheet.log",
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        serialize=True,   # JSON lines for machine parsing / audit trail
        enqueue=True,
    )
```

Every calculation function logs at `DEBUG` on entry with its inputs and on exit with its result (e.g. `logger.debug("classic_pivots(high={}, low={}, close={}) -> {}", high, low, close, result)`) so any generated sheet's numbers are fully reproducible/auditable from `logs/levelsheet.log`.

---

## 6. FUTURES SYMBOL RESOLUTION & MONTH CODES — `data/symbols.py`

Standard CME month codes (implement as a fixed dict, never hardcode elsewhere):

```python
MONTH_CODES = {
    "F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
    "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12,
}
CODE_FOR_MONTH = {v: k for k, v in MONTH_CODES.items()}
```

`data/symbols.py::resolve_symbol(root: str, provider: str) -> str` maps a bare root (e.g. `"ES"`) to the provider-specific continuous-front-month ticker string (e.g. yfinance `"ES=F"`, Polygon `"C:ES"` style prefix or the appropriate futures ticker format for that provider's API — implement provider-specific formatting functions `to_yfinance_ticker(root)`, `to_polygon_ticker(root)`). Also implement `parse_contract_code(code: str) -> ContractSpec` which splits e.g. `"ESU26"` into `root="ES"`, `month="U"`, `year=2026`, and `format_contract_code(root, month, year) -> str` as the inverse.

`data/symbols.py::SUPPORTED_ROOTS: dict[str, RootSpec]` — a table (not exhaustive-restrictive; unknown roots fall back to a `default RootSpec` with a logged warning) covering at minimum: `ES, NQ, RTY, YM, CL, NG, GC, SI, HG, ZB, ZN, ZF, ZT, 6E, 6J, 6B, 6A, 6C, ZC, ZS, ZW`. Each `RootSpec` includes: `exchange`, `point_value`, `tick_size`, `default_pivot_decimals` (2 for index/energy/metals, 4 for FX), `contract_months: list[str]` (subset of the 12 month codes that this product actually lists, e.g. equity index = `[H, M, U, Z]` quarterly only; CL = all 12 months).

---

## 7. ROLL CALENDAR — `data/roll_calendar.py`

```python
@dataclass(frozen=True)
class RollRule:
    contract_months: list[str]          # e.g. ["H", "M", "U", "Z"] for quarterly
    days_before_first_notice: int       # trading days before First Notice Day / expiry to roll
    roll_reference: Literal["volume_crossover", "fixed_calendar"]

ROLL_CALENDAR: dict[str, RollRule] = {
    "ES":  RollRule(["H","M","U","Z"], days_before_first_notice=8, roll_reference="volume_crossover"),
    "NQ":  RollRule(["H","M","U","Z"], days_before_first_notice=8, roll_reference="volume_crossover"),
    "RTY": RollRule(["H","M","U","Z"], days_before_first_notice=8, roll_reference="volume_crossover"),
    "YM":  RollRule(["H","M","U","Z"], days_before_first_notice=8, roll_reference="volume_crossover"),
    "CL":  RollRule(["F","G","H","J","K","M","N","Q","U","V","X","Z"], days_before_first_notice=5, roll_reference="fixed_calendar"),
    "NG":  RollRule(["F","G","H","J","K","M","N","Q","U","V","X","Z"], days_before_first_notice=3, roll_reference="fixed_calendar"),
    "GC":  RollRule(["G","J","M","Q","V","Z"], days_before_first_notice=5, roll_reference="volume_crossover"),
    "SI":  RollRule(["H","K","N","U","Z"], days_before_first_notice=5, roll_reference="volume_crossover"),
    "HG":  RollRule(["H","K","N","U","Z"], days_before_first_notice=5, roll_reference="volume_crossover"),
    "ZB":  RollRule(["H","M","U","Z"], days_before_first_notice=10, roll_reference="fixed_calendar"),
    "ZN":  RollRule(["H","M","U","Z"], days_before_first_notice=10, roll_reference="fixed_calendar"),
    "6E":  RollRule(["H","M","U","Z"], days_before_first_notice=6, roll_reference="volume_crossover"),
    "6J":  RollRule(["H","M","U","Z"], days_before_first_notice=6, roll_reference="volume_crossover"),
    "ZC":  RollRule(["H","K","N","U","Z"], days_before_first_notice=7, roll_reference="fixed_calendar"),
    "ZS":  RollRule(["F","H","K","N","Q","U","X"], days_before_first_notice=7, roll_reference="fixed_calendar"),
    "ZW":  RollRule(["H","K","N","U","Z"], days_before_first_notice=7, roll_reference="fixed_calendar"),
}
```
Any root not in this table raises `RollCalendarError` unless the user supplies `--roll-rule-json` (CLI) with an inline `RollRule` override.

`roll_calendar.py::next_roll_date(root: str, as_of: date) -> date` and `::front_month_contract(root: str, as_of: date) -> str` implement the logic: for `volume_crossover` products, approximate via the standard "N business days before third-Friday-of-contract-month" heuristic documented inline (since true volume crossover requires live volume data not always available); for `fixed_calendar` products, use `days_before_first_notice` counted back from the contract month's first business day.

---

## 8. CONTINUOUS CONTRACT CONSTRUCTION — `data/continuous_contract.py`

Implement **ratio-adjusted back-adjustment** (not simple point-difference) so long-term Fibonacci swing detection over years of data isn't distorted by additive roll gaps compounding into negative prices for low-priced-early-history contracts:

```python
def build_continuous_series(root: str, provider: DataProvider, start: date, end: date) -> pd.DataFrame:
    """
    1. Determine the sequence of front-month contracts covering [start, end]
       using roll_calendar.front_month_contract() stepped forward month by month.
    2. Fetch each individual contract's OHLC from `provider`.
    3. Walking backwards from the most recent contract, at each roll boundary
       compute adjustment_ratio = old_contract_close_on_roll_date / new_contract_close_on_roll_date.
    4. Multiply all OHLC values of every earlier-in-time segment by the
       cumulative product of adjustment_ratios computed so far.
    5. Concatenate all adjusted segments into a single continuous DataFrame,
       preserving the original unadjusted `contract` column per row for audit.
    6. Validate the result with models.schemas.validate_ohlc_df before returning.
    """
```
Unit test `tests/integration/test_continuous_contract_roll.py` must construct a synthetic 3-contract sequence with known prices and assert the stitched series has zero discontinuity (>0.01%) at roll boundaries after adjustment.

---

## 9. CACHE LAYER — `data/cache.py`

- Storage: `cache/{root}/{interval}.parquet` (interval ∈ `{1d, 1wk, 1mo}`), written via `pyarrow` with `pandas.DataFrame.to_parquet(engine="pyarrow")`.
- Sidecar metadata: `cache/{root}/{interval}.meta.json` = `{"fetched_at": ISO8601, "source": "polygon|yfinance|ib", "row_count": int, "min_date": ISO8601, "max_date": ISO8601}`.
- Freshness policy (`config.data.cache.max_staleness_hours`, default `18`): if `now - fetched_at > max_staleness_hours` **and** the request's `as_of_date` includes "today", refetch; otherwise serve from cache. Historical `as_of_date` requests (any date strictly before the most recent cached trading day) always serve from cache without a freshness check, since history doesn't change.
- `CachedDataFetcher.fetch(root, interval, start, end, as_of_date, force_refresh=False) -> pd.DataFrame` implements: cache-hit-and-fresh → return slice; cache-hit-but-stale-or-force → fetch delta from provider chain, merge (drop-duplicate on index, keep newest), rewrite parquet + meta, return slice; cache-miss → full fetch, write, return slice. On any read corruption (`pyarrow.ArrowInvalid` etc.) raise `CacheError`, log, delete the corrupt file, and transparently fall through to a full network fetch (self-healing cache).
- `scripts/bootstrap_cache.py` — standalone script that pre-warms the cache for every root in `config.symbols.default_list` across `1d/1wk/1mo`, intended for a nightly cron/GitHub Action.

---

## 10. PROVIDER CHAIN — `data/providers/*`

`data/providers/base.py`:
```python
class DataProvider(Protocol):
    name: str
    def is_available(self) -> bool: ...
    def fetch_ohlc(self, symbol: str, start: date, end: date, interval: Literal["1d","1wk","1mo"]) -> pd.DataFrame: ...
```

All three provider implementations wrap their network call in `tenacity.retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), retry=retry_if_exception_type((requests.RequestException, TimeoutError)))`. On final failure, raise `ProviderUnavailableError` with the original exception chained (`raise ProviderUnavailableError(...) from exc`).

- `yfinance_provider.py::YFinanceProvider` — always `is_available() -> True`; wraps `yfinance.download(ticker, start=start, end=end, interval=interval_map[interval], progress=False, auto_adjust=False)`; renames columns to canonical schema; sets `contract` column to the resolved continuous ticker string since yfinance doesn't expose discrete contract identity.
- `polygon_provider.py::PolygonProvider` — `is_available()` checks `os.environ.get("POLYGON_API_KEY")` is set and non-empty; uses `polygon.RESTClient(api_key)`; calls `client.get_aggs(ticker, 1, timespan_map[interval], from_=start, to=end)`; maps response `Agg` objects into canonical schema rows with real per-row `contract` identity when available.
- `ib_provider.py::IBProvider` — `is_available()` returns `False` unless `ib_insync` import succeeds **and** `os.environ.get("IB_ENABLED") == "true"` **and** a live TWS/Gateway socket connects within a 2-second timeout (caught and treated as unavailable, never crashes the chain).

`data/providers/__init__.py::get_provider_chain(config: LevelSheetConfig) -> list[DataProvider]` returns `[PolygonProvider(...), YFinanceProvider(), IBProvider(...)]` filtered/ordered per config, and `CachedDataFetcher` iterates this list, logging each attempt at `INFO` (`"Trying provider={name} for symbol={symbol}"`) and the first success wins.

---

## 11. CALCULATION ENGINE — FULL FORMULAS, SIGNATURES, AND WORKED FIXTURES

All functions: full type hints, Google-style docstrings citing the formula, `DEBUG`-level logging per §5. Below each formula is a **worked numeric fixture** that must appear verbatim as a `pytest.approx` assertion in the corresponding unit test.

### 11.1 Classic Floor Pivots — `calc/pivots.py::classic_pivots`
```python
def classic_pivots(high: float, low: float, close: float) -> PivotSet:
    p = (high + low + close) / 3
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2 * (p - low)
    s3 = low - 2 * (high - p)
    return PivotSet(p=p, r1=r1, r2=r2, r3=r3, s1=s1, s2=s2, s3=s3)
```
**Fixture:** `high=5100.00, low=5060.00, close=5080.00` → `p=5080.00, r1=5100.00, s1=5060.00, r2=5120.00, s2=5040.00, r3=5140.00, s3=5020.00`.

### 11.2 Camarilla Pivots — `calc/pivots.py::camarilla_pivots`
```python
def camarilla_pivots(high: float, low: float, close: float) -> PivotSet:
    rng = high - low
    r4 = close + rng * 1.1 / 2
    r3 = close + rng * 1.1 / 4
    r2 = close + rng * 1.1 / 6
    r1 = close + rng * 1.1 / 12
    s1 = close - rng * 1.1 / 12
    s2 = close - rng * 1.1 / 6
    s3 = close - rng * 1.1 / 4
    s4 = close - rng * 1.1 / 2
    return PivotSet(p=close, r1=r1, r2=r2, r3=r3, r4=r4, s1=s1, s2=s2, s3=s3, s4=s4)
```
**Fixture:** `high=5100.00, low=5060.00, close=5080.00` (rng=40) → `r1=5083.67, r2=5087.33, r3=5091.00, r4=5102.00, s1=5076.33, s2=5072.67, s3=5069.00, s4=5058.00` (rounded to 2dp).

### 11.3 Woodie Pivots — `calc/pivots.py::woodie_pivots`
```python
def woodie_pivots(high: float, low: float, close: float) -> PivotSet:
    p = (high + low + 2 * close) / 4
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    return PivotSet(p=p, r1=r1, r2=r2, s1=s1, s2=s2)
```
**Fixture:** same OHLC → `p=5080.00, r1=5100.00, s1=5060.00, r2=5120.00, s2=5040.00`.

### 11.4 Fibonacci — `calc/fibonacci.py::fibonacci_levels`
```python
RETRACEMENT_RATIOS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.764, 1.0]
EXTENSION_RATIOS = [1.272, 1.618, 2.0, 2.618]

def fibonacci_levels(swing_high: float, swing_low: float, direction: Literal["up", "down"]) -> dict[str, float]:
    rng = swing_high - swing_low
    levels: dict[str, float] = {}
    for r in RETRACEMENT_RATIOS:
        price = swing_high - rng * r if direction == "down" else swing_low + rng * r
        levels[f"{r*100:.1f}%"] = round(price, 2)
    for r in EXTENSION_RATIOS:
        price = swing_low - rng * (r - 1) if direction == "down" else swing_high + rng * (r - 1)
        levels[f"{r*100:.1f}%"] = round(price, 2)
    return levels
```
**Fixture:** `swing_high=5200.00, swing_low=4900.00, direction="down"` (rng=300) → `0.0%=5200.00, 23.6%=5129.20, 38.2%=5085.40, 50.0%=5050.00, 61.8%=5014.60, 76.4%=4970.80, 100.0%=4900.00, 127.2%=4818.40, 161.8%=4714.60, 200.0%=4600.00, 261.8%=4415.40`.

### 11.5 Moving Averages + Bias — `calc/moving_averages.py`, `calc/bias.py`
```python
def sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=length, min_periods=length).mean()

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False, min_periods=length).mean()

def bias(close: float, ma_value: float) -> Literal["LONG", "SHORT", "NONE"]:
    if pd.isna(ma_value):
        return "NONE"
    if close > ma_value:
        return "LONG"
    if close < ma_value:
        return "SHORT"
    return "NONE"
```
If `len(series) < length`, `sma`/`ema` correctly return `NaN` for all positions (via `min_periods`) rather than raising; the *panel renderer* (not the calc function) is responsible for raising `InsufficientHistoryError` with a clear message ("MA(200) requires 200 bars, only 90 available for root=CL") when the **most recent** value needed for the sheet is `NaN`.

### 11.6 True Range / Wilder ATR — `calc/atr.py`
```python
def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    a = df["high"] - df["low"]
    b = (df["high"] - prev_close).abs()
    c = (df["low"] - prev_close).abs()
    return pd.concat([a, b, c], axis=1).max(axis=1)

def atr_wilder(df: pd.DataFrame, length: int = 14) -> pd.Series:
    tr = true_range(df)
    atr = pd.Series(index=df.index, dtype="float64")
    atr.iloc[:length] = np.nan
    atr.iloc[length - 1] = tr.iloc[:length].mean()
    for i in range(length, len(tr)):
        atr.iloc[i] = (atr.iloc[i - 1] * (length - 1) + tr.iloc[i]) / length
    return atr
```
**Fixture:** 15-row synthetic OHLC series in `tests/fixtures/expected_values.json::atr_wilder_14` with exact expected ATR at index 14 (agent must hand-compute and commit the value — do not leave a placeholder).

### 11.7 Projected MA — `calc/moving_averages.py::projected_ma`
```python
def projected_ma(ma_series: pd.Series) -> float:
    """Projected MA = current MA + slope(last two points) * 1"""
    if len(ma_series.dropna()) < 2:
        raise InsufficientHistoryError("projected_ma requires at least 2 non-NaN MA values")
    slope = ma_series.iloc[-1] - ma_series.iloc[-2]
    return round(ma_series.iloc[-1] + slope, 2)
```

### 11.8 Simplified Elliott Wave — `calc/elliott_wave.py`
Full zigzag algorithm (implement exactly, do not approximate):
```python
def detect_swings_zigzag(df: pd.DataFrame, threshold_pct: float = 3.0) -> pd.DataFrame:
    """
    Standard percentage zigzag:
      - Start at the first bar; initialize `last_extreme_price = close[0]`,
        `last_extreme_idx = 0`, `direction = None`.
      - Walk forward bar by bar. Track the running max (if direction is up
        or undetermined) and running min (if direction is down or undetermined)
        since `last_extreme_idx`.
      - A new swing is CONFIRMED the first time price reverses from the
        running extreme by >= threshold_pct:
          if direction in (None, "up") and low[i] <= running_max * (1 - threshold_pct/100):
              confirm running_max as a High swing point; direction = "down";
              reset running_min tracking from i.
          if direction in (None, "down") and high[i] >= running_min * (1 + threshold_pct/100):
              confirm running_min as a Low swing point; direction = "up";
              reset running_max tracking from i.
      - At the end of the series, the current running extreme (unconfirmed)
        is NOT added as a swing point (avoids lookahead bias / false final wave).
      - Return columns: [date, price, kind] where kind in {"High","Low"},
        strictly alternating.
    """

def elliott_wave_projection(swings: pd.DataFrame) -> ElliottProjection:
    """
    Take the last 5 confirmed alternating swing points as Wave 1-5 (impulse,
    oldest=Wave0/start, then Wave1..Wave5 endpoints). Requires >= 6 points
    (0 through 5); raise InsufficientHistoryError otherwise.
      wave1_len = abs(price[1] - price[0])
      wave3_len = abs(price[3] - price[2])
      wave4_end = price[4]
      extended_third = wave3_len > wave1_len * 1.618
      ext_ratio = 2.618 if extended_third else 1.618
      direction_sign = 1 if price[1] > price[0] else -1
      wave5_target = wave4_end + direction_sign * wave1_len * ext_ratio
    Return ElliottProjection(waves=swings.tail(6), ext_ratio=ext_ratio,
                              wave5_target=round(wave5_target, 2))
    """
```

### 11.9 Extreme Moves — `calc/extreme_moves.py`
```python
EXTREME_MOVE_PCTS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]

def extreme_move_targets(current_price: float) -> dict[str, float]:
    up = {f"+{p}%": round(current_price * (1 + p / 100), 2) for p in EXTREME_MOVE_PCTS}
    down = {f"-{p}%": round(current_price * (1 - p / 100), 2) for p in EXTREME_MOVE_PCTS}
    return up | down
```

### 11.10 NR7 / WR7 — `calc/nr7_wr7.py`
```python
def is_nr7(df: pd.DataFrame) -> bool:
    ranges = (df["high"] - df["low"]).tail(7)
    if len(ranges) < 7:
        raise InsufficientHistoryError("NR7 requires 7 bars")
    return bool(ranges.iloc[-1] == ranges.min())

def is_wr7(df: pd.DataFrame) -> bool:
    ranges = (df["high"] - df["low"]).tail(7)
    if len(ranges) < 7:
        raise InsufficientHistoryError("WR7 requires 7 bars")
    return bool(ranges.iloc[-1] == ranges.max())
```

### 11.11 Warning Flags — `calc/warnings_flags.py`
```python
def is_false_day(today: OHLCBar, yesterday: OHLCBar) -> bool:
    """True if today's open is outside yesterday's range but today's close
    is back inside yesterday's range (failed breakout)."""
    opened_outside = today.open > yesterday.high or today.open < yesterday.low
    closed_inside = yesterday.low <= today.close <= yesterday.high
    return opened_outside and closed_inside

def is_rth_gap(today_open: float, prev_close: float, threshold_pct: float = 0.15) -> bool:
    return abs(today_open - prev_close) / prev_close * 100 >= threshold_pct

def is_blud(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Big Low Up Day: today's low undercuts yesterday's low, but today
    closes green and in the top `close_proximity_pct` of today's own range."""
    undercut_low = today.low < yesterday.low
    closed_green = today.close > today.open
    day_range = today.high - today.low
    near_high = day_range > 0 and (today.high - today.close) / day_range * 100 <= close_proximity_pct
    return undercut_low and closed_green and near_high

def is_ahdd(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Above High Down Day: mirror of BLUD on the upside."""
    exceeded_high = today.high > yesterday.high
    closed_red = today.close < today.open
    day_range = today.high - today.low
    near_low = day_range > 0 and (today.close - today.low) / day_range * 100 <= close_proximity_pct
    return exceeded_high and closed_red and near_low
```

### 11.12 Auto-Trade Settings — `calc/autotrade.py`
```python
def compute_autotrade_settings(atr_value: float, root: str, config: AutoTradeConfig, point_value: float) -> AutoTradeSettings:
    max_stop = round(atr_value * config.stop_atr_mult, 2)
    return AutoTradeSettings(
        max_stop=max_stop,
        trail=round(atr_value * config.trail_atr_mult, 2),
        frequency=config.frequency,
        max_target=round(atr_value * config.target_atr_mult, 2),
        side=config.side,
        size=config.contracts,
        scale_out=config.scale_out_pct,
        max_risk_dollars=round(max_stop * point_value * config.contracts, 2),
    )
```

---

## 12. PIXEL-PERFECT RENDER SPEC

### 12.1 Canvas & Grid — `render/layout.py`
- Figure size: `figsize=(17, 11)`, `dpi=300` (→ 5100×3300 px), `matplotlib.figure.Figure(facecolor="#FFFFFF")`.
- Grid: `matplotlib.gridspec.GridSpec(nrows=80, ncols=120, figure=fig, left=0.02, right=0.98, top=0.97, bottom=0.03, wspace=0.0, hspace=0.0)` (fine-grained 80×120 unit grid, NOT 8×12, so panels can be positioned with sub-inch precision). Define `SHEET_LAYOUT: dict[str, GridSpecRegion]` mapping every panel name to `(row_start, row_end, col_start, col_end)` in this 80×120 unit space:

```python
SHEET_LAYOUT = {
    "header":              (0, 8,   0, 120),
    "daily_pivots":        (9, 33,  0, 24),
    "center_ohlc_ma":      (9, 33,  25, 60),
    "mini_candlestick":    (9, 33,  61, 70),
    "weekly_panel":        (9, 20,  71, 95),
    "monthly_panel":       (9, 20,  96, 120),
    "atr_nr7_panel":       (21, 33, 71, 95),
    "hilo_7_20_panel":     (21, 33, 96, 120),
    "long_term_fib":       (34, 58, 0, 36),
    "daily_fib_extreme":   (34, 58, 37, 72),
    "bias_panel":          (34, 50, 73, 120),
    "autotrade_panel":     (51, 58, 73, 120),
    "elliott_panel":       (59, 74, 0, 55),
    "projected_ma_panel":  (59, 74, 56, 82),
    "warnings_panel":      (59, 74, 83, 120),
    "footer":              (75, 80, 0, 120),
}
```
Each panel module receives `fig.add_subplot(gs[row_start:row_end, col_start:col_end])`, sets `ax.axis("off")`, and draws purely with `ax.text`, `ax.add_patch(Rectangle(...))`, `ax.add_line(Line2D(...))` for full pixel control — no default matplotlib table styling.

### 12.2 Typography — `render/fonts.py`
- Primary family: `"DejaVu Sans"` (bundled with matplotlib, guaranteed available headless) with a config override `theme.font_family` for environments that install a custom font into `assets/fonts/` (loaded via `matplotlib.font_manager.fontManager.addfont`).
- Size scale (in points, at the 300 DPI/17x11 canvas): Header title `28pt bold`, header subtitle `14pt regular`, header roll-warning `11pt italic`, panel section headers `12pt bold uppercase letter-spaced`, table labels `10pt regular`, table values `10pt monospace-style (DejaVu Sans Mono)`, bias panel word `14pt bold`, footer `9pt regular`.
- All numeric values rendered with `f"{value:,.2f}"` (thousands separator, 2 decimals) for index/energy/metals products; FX roots (6E, 6J, 6B, 6A, 6C) use 4 decimals (`f"{value:,.4f}"`) per `RootSpec.default_pivot_decimals`.

### 12.3 Color Theme — `render/theme.py`
```python
@dataclass(frozen=True)
class Theme:
    bullish: str = "#1B7A3D"
    bullish_fill_light: str = "#E9F6EC"
    bearish: str = "#B32020"
    bearish_fill_light: str = "#FBE9E9"
    key_level: str = "#F2C230"
    key_level_text: str = "#5A4300"
    open_settlement: str = "#ADD8E6"
    neutral: str = "#8C8C8C"
    header_bg: str = "#0B1F33"
    header_text: str = "#FFFFFF"
    border: str = "#333333"
    border_width_pt: float = 0.75
    body_text: str = "#1A1A1A"
    footer_text: str = "#777777"
```
Loaded from `config.theme.*` via pydantic so every hex code is user-overridable without touching code.

### 12.4 Panel-by-panel drawing spec (all in `render/panels/*.py`, each exposing `def draw(ax: Axes, data: SheetData, theme: Theme) -> None`)

- **header.py**: 3 `ax.text` calls at `y=0.85/0.5/0.15` (axes fraction), left-aligned `x=0.01`. Roll-warning line color conditional: `theme.bearish` if `days_to_roll <= 5` else `theme.neutral`.
- **daily_pivots.py**: draws 7 stacked `Rectangle` rows (`height=1/7` each in axes fraction, `width=1.0`), label text left-aligned at `x=0.08`, value text right-aligned at `x=0.92`, `edgecolor=theme.border`, `linewidth=theme.border_width_pt`. Row fill logic: `R*` rows → `bullish_fill_light`/text `bullish`; `S*` rows → `bearish_fill_light`/text `bearish`; `PIVOT` row → `key_level` fill / `key_level_text` text.
- **center_ohlc_ma.py**: top half (axes y 0.55–1.0) = 6-row OHLC/GSO labeled grid; bottom half (y 0.0–0.55) = MA table with a colored bias pill (`FancyBboxPatch`, `boxstyle="round,pad=0.02"`) per row using theme bias colors from §11.5's `bias()` output.
- **mini_candlestick.py**: `draw_single_candle(ax, ohlc: OHLCBar, theme: Theme) -> None` — wick = `Line2D([0.5,0.5],[low_norm,high_norm], color=body_color, linewidth=1.5)`; body = `Rectangle((0.3, min(open_norm,close_norm)), width=0.4, height=abs(close_norm-open_norm), facecolor=body_color, edgecolor=theme.border)`; normalize open/high/low/close into `[0,1]` against `(low - 10%*range, high + 10%*range)`; `body_color = theme.bullish if close>=open else theme.bearish`.
- **weekly_monthly.py**: reuses `daily_pivots.py`'s row-drawing helper (extract shared function `draw_pivot_table(ax, pivot_set, theme, header_label)` into `render/panels/_shared.py` to avoid duplication) but sourced from weekly/monthly OHLC pivot calcs.
- **atr_nr7_panel.py**: single large stat box (`open_settlement` fill) for 5-D ATR value at 18pt; two pill badges below for NR7/WR7 booleans (`bullish` fill if true, `neutral` outline-only if false); 7-D/20-D hi-lo as a compact 2×2 grid beneath.
- **long_term_fib.py / daily_fib_extreme.py**: shared `draw_fib_table(ax, levels: dict[str,float], theme, key_levels={"61.8%","50.0%","38.2%"})` — highlights key rows at `key_level` fill 25% alpha (`alpha=0.25` on the `Rectangle`).
- **bias_panel.py**: 2×3 grid of `FancyBboxPatch` cells, lookback label 9pt top, bias word 14pt bold bottom, fill/text per `bias()` → theme mapping.
- **autotrade_panel.py**: 8-row label/value table, header row `header_bg` fill / `header_text` color.
- **elliott_panel.py**: 6-row table (Wave 0–5) + one-line projection text beneath in `key_level_text` on `key_level` background pill.
- **projected_ma_panel.py**: 6-row table, MA length / today value / projected tomorrow value, projected column highlighted `open_settlement` fill.
- **warnings_panel.py**: 3 stacked pill badges, `bearish` fill if flagged else outline-only `neutral`.
- **footer.py**: centered `ax.text` at 9pt `footer_text` color; if `assets/logo/logo.png` exists, composite via `OffsetImage`/`AnnotationBbox` right-aligned.

---

## 13. EXPORT LAYER

- `render/export_png.py::export_png(fig: Figure, path: Path) -> None` — `fig.savefig(path, dpi=300, format="png", facecolor=fig.get_facecolor())`; asserts resulting file size > 50KB post-write or raises `ExportError` (sanity check against a blank/corrupt render).
- `render/export_pdf.py::export_pdf(fig: Figure, path: Path) -> None` (matplotlib engine) — `fig.savefig(path, format="pdf")` with `Letter` landscape enforced via the 17×11 figsize already matching US Letter landscape at 1:1 scale in points... explicitly set `fig.set_size_inches(17, 11)` before saving to guarantee it regardless of DPI.
- `render/export_pdf.py::export_book(sheets: list[tuple[str, Figure]], path: Path) -> None` — uses `matplotlib.backends.backend_pdf.PdfPages` to concatenate one page per symbol into a single multi-page PDF, in the order provided.
- Weasyprint fallback path (`render.engine: weasyprint`): each panel additionally exposes `def to_html(data: SheetData, theme: Theme) -> str` returning a `<div>` fragment with inline CSS matching the same hex codes and grid percentages; `export_pdf.py::export_pdf_weasyprint(html: str, path: Path)` wraps fragments in a full HTML page with `@page { size: letter landscape; margin: 0.4in }` and calls `weasyprint.HTML(string=full_html).write_pdf(path)`.

---

## 14. CONFIG SCHEMA — `config/schema.py` (full pydantic v2 models)

```python
from pydantic import BaseModel, Field, field_validator

class SymbolsConfig(BaseModel):
    default_list: list[str] = ["ES","NQ","CL","GC","SI","ZB","6E","RTY"]
    point_values: dict[str, float] = {}

class PivotsConfig(BaseModel):
    method: Literal["classic","camarilla","woodie"] = "classic"
    show_camarilla: bool = False
    show_woodie: bool = False

class MovingAveragesConfig(BaseModel):
    lengths: list[int] = [5,13,50,100,150,200]
    type: Literal["sma","ema"] = "sma"

class FibonacciConfig(BaseModel):
    retracement_ratios: list[float] = [0.0,0.236,0.382,0.5,0.618,0.764,1.0]
    extension_ratios: list[float] = [1.272,1.618,2.0,2.618]
    long_term_swing_threshold_pct: float = 5.0

class ElliottWaveConfig(BaseModel):
    zigzag_threshold_pct: float = 3.0

class ATRConfig(BaseModel):
    length: int = Field(14, gt=0)
    method: Literal["wilder"] = "wilder"

class AutoTradeConfig(BaseModel):
    stop_atr_mult: float = 1.0
    trail_atr_mult: float = 0.5
    target_atr_mult: float = 2.0
    frequency: str = "1/day"
    side: Literal["BOTH","LONG","SHORT"] = "BOTH"
    contracts: int = 1
    scale_out_pct: float = 50.0

class ExtremeMovesConfig(BaseModel):
    percentages: list[float] = [0.5,1.0,1.5,2.0,3.0,5.0]

class WarningsConfig(BaseModel):
    rth_gap_threshold_pct: float = 0.15
    close_proximity_pct: float = 25.0

class ThemeConfig(BaseModel):
    bullish: str = "#1B7A3D"
    bullish_fill_light: str = "#E9F6EC"
    bearish: str = "#B32020"
    bearish_fill_light: str = "#FBE9E9"
    key_level: str = "#F2C230"
    key_level_text: str = "#5A4300"
    open_settlement: str = "#ADD8E6"
    neutral: str = "#8C8C8C"
    header_bg: str = "#0B1F33"
    header_text: str = "#FFFFFF"
    border: str = "#333333"
    font_family: str = "DejaVu Sans"

    @field_validator("*")
    @classmethod
    def _validate_hex(cls, v: str, info) -> str:
        if info.field_name in ("font_family",):
            return v
        if not (isinstance(v, str) and v.startswith("#") and len(v) in (4,7)):
            raise ValueError(f"{info.field_name} must be a hex color, got {v!r}")
        return v

class BrandingConfig(BaseModel):
    company_name: str = "BPTC 26 LLC"
    footer_text: str = "For educational purposes only. Not financial advice."
    logo_path: str = "assets/logo/logo.png"

class CacheConfig(BaseModel):
    backend: Literal["parquet","sqlite"] = "parquet"
    dir: str = "cache"
    max_staleness_hours: int = 18

class ProvidersConfig(BaseModel):
    polygon_api_key_env: str = "POLYGON_API_KEY"
    ib_enabled_env: str = "IB_ENABLED"

class DataConfig(BaseModel):
    cache: CacheConfig = CacheConfig()
    providers: ProvidersConfig = ProvidersConfig()

class RenderConfig(BaseModel):
    engine: Literal["matplotlib","weasyprint"] = "matplotlib"
    dpi: int = 300
    page_size: Literal["letter_landscape"] = "letter_landscape"

class PluginsConfig(BaseModel):
    enabled: list[str] = []

class LevelSheetConfig(BaseModel):
    symbols: SymbolsConfig = SymbolsConfig()
    pivots: PivotsConfig = PivotsConfig()
    moving_averages: MovingAveragesConfig = MovingAveragesConfig()
    fibonacci: FibonacciConfig = FibonacciConfig()
    elliott_wave: ElliottWaveConfig = ElliottWaveConfig()
    atr: ATRConfig = ATRConfig()
    autotrade: AutoTradeConfig = AutoTradeConfig()
    extreme_moves: ExtremeMovesConfig = ExtremeMovesConfig()
    warnings: WarningsConfig = WarningsConfig()
    theme: ThemeConfig = ThemeConfig()
    branding: BrandingConfig = BrandingConfig()
    data: DataConfig = DataConfig()
    render: RenderConfig = RenderConfig()
    plugins: PluginsConfig = PluginsConfig()
```

`config/loader.py::load_config(cli_overrides: dict | None = None) -> LevelSheetConfig` merge order (lowest → highest precedence): `LevelSheetConfig()` defaults → `default_config.yaml` (shipped in package) → `~/.levelsheet/config.yaml` (if exists) → `./levelsheet.yaml` (project-local, if exists) → `cli_overrides` dict (from argparse namespace, only non-`None` values applied) → environment variables prefixed `LEVELSHEET__` (via `pydantic-settings`, double-underscore nested delimiter, e.g. `LEVELSHEET__THEME__BULLISH=#00FF00`). Implement with `pydantic_settings.BaseSettings` composition or manual deep-merge of dicts before final `LevelSheetConfig.model_validate(merged)` — agent's choice, document in `DECISIONS.md`.

`default_config.yaml` mirrors the above defaults verbatim in YAML form.

---

## 15. CLI & GUI — FULL SKELETONS

### 15.1 `cli/__main__.py` (argparse subparsers)
```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="levelsheet")
    parser.add_argument("--debug", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate")
    gen.add_argument("symbols", nargs="+")
    gen.add_argument("--date", type=str, default=None)          # defaults to today
    gen.add_argument("--format", type=str, default="pdf,png")
    gen.add_argument("--batch", action="store_true")
    gen.add_argument("--force-refresh", action="store_true")
    gen.add_argument("--fib-swing-high-date", type=str, default=None)
    gen.add_argument("--fib-swing-low-date", type=str, default=None)
    gen.add_argument("--roll-rule-json", type=str, default=None)
    gen.add_argument("--output-dir", type=str, default="output")

    book = sub.add_parser("book")
    book.add_argument("--date", type=str, default=None)
    book.add_argument("--symbols", type=str, required=True)      # comma-separated
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
    args = build_parser().parse_args()
    configure_logging(debug=args.debug)
    try:
        config = load_config(cli_overrides=vars(args))
        # dispatch to generate_command / book_command / cache_command / config_command
        ...
        return 0
    except LevelSheetError as exc:
        logger.error(str(exc))
        if args.debug:
            raise
        return 1
```
Usage examples that must work exactly as shown:
```
python -m levelsheet generate ES --date 2026-08-12 --format pdf,png
python -m levelsheet generate ES NQ CL GC --date 2026-08-12 --format pdf --batch
python -m levelsheet book --date 2026-08-12 --symbols ES,NQ,CL,GC --output output/pdf/full_book_2026-08-12.pdf
python -m levelsheet cache refresh --symbol ES --interval 1d
python -m levelsheet config show
```

### 15.2 `gui/streamlit_app.py` layout
```python
st.set_page_config(page_title="LevelSheet", layout="wide")
with st.sidebar:
    default_symbols = config.symbols.default_list
    chosen = st.selectbox("Symbol (or type any root below)", default_symbols)
    custom = st.text_input("Custom root (overrides dropdown)", "")
    symbol = custom.strip().upper() or chosen
    the_date = st.date_input("Date", value=date.today())
    pivot_method = st.radio("Pivot method", ["classic","camarilla","woodie"], index=0)
    generate = st.button("Generate Sheet", type="primary")

tab_single, tab_batch = st.tabs(["Single Sheet", "Full Book"])
with tab_single:
    if generate:
        with st.spinner(f"Generating {symbol} sheet for {the_date}..."):
            fig, pdf_bytes, png_bytes = build_sheet(symbol, the_date, pivot_method, config)
        st.pyplot(fig)
        col1, col2 = st.columns(2)
        col1.download_button("Download PDF", pdf_bytes, file_name=f"{symbol}_{the_date}.pdf", mime="application/pdf")
        col2.download_button("Download PNG", png_bytes, file_name=f"{symbol}_{the_date}.png", mime="image/png")
with tab_batch:
    picked = st.multiselect("Symbols for book", default_symbols, default=default_symbols[:4])
    if st.button("Export Full Book"):
        with st.spinner("Building multi-page book..."):
            book_pdf_bytes = build_book(picked, the_date, config)
        st.download_button("Download Book PDF", book_pdf_bytes, file_name=f"book_{the_date}.pdf", mime="application/pdf")
```

---

## 16. TESTING, QUALITY GATES & ACCEPTANCE CRITERIA

- `pytest --cov=src/levelsheet --cov-report=term-missing --cov-fail-under=90` passes in CI.
- Every `calc/` function has (a) a hand-computed fixture test using the exact worked examples in §11, asserted with `pytest.approx(expected, abs=1e-6)` for float outputs or exact equality for bools/strings; (b) at least one `hypothesis`-driven property test, minimum set:
  - `classic_pivots`: `R1 + S1 == pytest.approx(2 * P)`, and `R3 > R2 > R1 > P > S1 > S2 > S3` for any `high > low` and `low <= close <= high`.
  - `atr_wilder`: output series is always `>= 0` wherever non-NaN, for any randomly generated valid OHLC frame (`hypothesis.strategies` composite generating monotonic-valid H>=L, H>=O,C, L<=O,C).
  - `fibonacci_levels`: for `direction="down"`, all retracement outputs fall within `[swing_low, swing_high]` inclusive, for any `swing_high > swing_low`.
  - `sma`/`ema`: output length always equals input length; first `length-1` values are NaN for SMA.
- `mypy --strict src/` — zero errors.
- `ruff check src/ tests/` — zero errors. `black --check src/ tests/` — zero diffs.
- `tests/integration/test_full_sheet_generation.py`: runs the complete pipeline against `tests/fixtures/ES_sample.csv` (a committed, realistic ~300-row daily OHLC fixture the agent generates/derives), asserts: output PDF exists and is > 50KB; output PNG exists, is > 50KB, and has pixel dimensions exactly `5100×3300`; the computed classic pivot `P` for the fixture's last row matches a hand-verified value in `tests/fixtures/expected_values.json`; the MA(200) bias for the fixture's last row matches an independently hand-verified `LONG`/`SHORT`/`NONE` value.
- `tests/integration/test_provider_fallback.py`: mocks Polygon raising `ProviderUnavailableError`, asserts yfinance is then called and succeeds, asserts the correct `source` string lands in the cache sidecar JSON.
- `tests/integration/test_cache_roundtrip.py`: write→read→assert byte-identical DataFrame (modulo dtype-preserving round-trip through parquet); corrupt the parquet file manually mid-test and assert `CacheError` is caught internally and a fresh network fetch is transparently triggered (no crash).
- **Acceptance criteria (must all be true at the end of Phase 7):**
  1. `make test` passes with ≥90% coverage, zero lint/type errors.
  2. `python -m levelsheet generate ES --date <any recent trading day> --format pdf,png` completes in <10s on a warm cache and produces both files with correct dimensions.
  3. `make run-gui` launches Streamlit on port 8501 and a manual click-through of Generate → PDF/PNG download works.
  4. Every hex color in a generated sheet exactly matches `default_config.yaml`'s `theme.*` values (spot-checked via a pixel-sampling test in `tests/integration/test_full_sheet_generation.py` using Pillow's `Image.getpixel`).
  5. Changing `theme.bullish` in `levelsheet.yaml` and regenerating changes the rendered color with zero code edits.
  6. `docker-compose up` serves the GUI at `localhost:8501` with no manual steps beyond providing `POLYGON_API_KEY` in `.env`.

---

## 17. SUPPORTING FILES — FULL CONTENTS

### 17.1 `.env.example`
```
POLYGON_API_KEY=
IB_ENABLED=false
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
LEVELSHEET__THEME__BULLISH=#1B7A3D
LOG_LEVEL=INFO
```

### 17.2 `Makefile`
```makefile
.PHONY: install dev-install lint format typecheck test test-cov run-gui run-cli docker-build docker-run clean

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy --strict src/

test:
	pytest tests/unit tests/integration -v

test-cov:
	pytest --cov=src/levelsheet --cov-report=term-missing --cov-fail-under=90

run-gui:
	streamlit run src/levelsheet/gui/streamlit_app.py --server.port 8501

run-cli:
	python -m levelsheet generate $(SYMBOL) --date $(DATE) --format pdf,png

docker-build:
	docker build -t levelsheet:latest .

docker-run:
	docker-compose up

clean:
	rm -rf output/pdf/* output/png/* logs/*.log __pycache__ .pytest_cache .mypy_cache .ruff_cache
```

### 17.3 `Dockerfile`
```dockerfile
FROM python:3.12-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e .
EXPOSE 8501
ENTRYPOINT ["python", "-m", "levelsheet"]
CMD ["--help"]
```

### 17.4 `docker-compose.yml`
```yaml
services:
  levelsheet:
    build: .
    command: ["streamlit", "run", "src/levelsheet/gui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    ports:
      - "8501:8501"
    volumes:
      - ./cache:/app/cache
      - ./output:/app/output
      - ./logs:/app/logs
    env_file:
      - .env
```

### 17.5 `pyproject.toml` (key sections)
```toml
[project]
name = "levelsheet"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pandas", "numpy", "scipy", "yfinance", "polygon-api-client",
    "matplotlib", "seaborn", "Pillow", "reportlab", "weasyprint",
    "streamlit", "pydantic>=2", "pydantic-settings", "loguru",
    "pyarrow", "tenacity",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "pytest-mock", "hypothesis", "black", "ruff", "mypy"]
ib = ["ib_insync"]

[project.scripts]
levelsheet = "levelsheet.cli.__main__:main"

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
```

### 17.6 `.github/workflows/ci.yml`
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check src/ tests/
      - run: black --check src/ tests/
      - run: mypy --strict src/
      - run: pytest --cov=src/levelsheet --cov-report=term-missing --cov-fail-under=90
```

---

## 18. IMPLEMENTATION PHASES — EXECUTE IN ORDER, COMMIT AFTER EACH

- **Phase 0** — Repo skeleton (§2), `pyproject.toml`, `requirements*.txt`, `.gitignore`, `.env.example`, empty module stubs with full docstrings describing intended contents, CI workflow file (§17.6), README skeleton with TOC. Commit: `chore: phase 0 repo skeleton + CI`.
- **Phase 1** — Full `calc/` package per §11, 100% of unit tests + hypothesis properties from §16 green. Commit: `feat: phase 1 calculation engine`.
- **Phase 2** — `errors.py`, `logging_config.py`, `data/` package per §6–§10, `models/schemas.py` validation, integration tests for cache/provider-fallback/continuous-contract green. Commit: `feat: phase 2 data layer + caching + roll logic`.
- **Phase 3** — `render/layout.py`, `render/theme.py`, `render/fonts.py`, every panel in `render/panels/` per §12. Manually render one sample sheet, visually confirm against §12.1's grid, save as `tests/fixtures/expected_layout.png` for future pixel-diff regression. Commit: `feat: phase 3 pixel-perfect renderer`.
- **Phase 4** — `render/export_pdf.py`, `render/export_png.py`, book export, weasyprint fallback path. Commit: `feat: phase 4 exporters`.
- **Phase 5** — `cli/__main__.py` (§15.1) and `gui/streamlit_app.py` (§15.2), fully wired to the calc/data/render layers. Commit: `feat: phase 5 cli + gui`.
- **Phase 6** — `config/schema.py` (§14), `config/loader.py` merge chain, `plugins/` registry, branding end-to-end override test (change a hex code, confirm pixel change). Commit: `feat: phase 6 config system + plugins`.
- **Phase 7** — README with an embedded generated sample sheet screenshot, full install/setup/usage docs, `DECISIONS.md` finalized with every agent-made judgment call listed, Docker/compose verified end-to-end, final `make lint format typecheck test-cov` all green. Commit: `docs: phase 7 documentation + final polish`.

---

## 19. FINAL DELIVERABLE — END YOUR WORK WITH EXACTLY THIS

```bash
git clone <repo-url> levelsheet && cd levelsheet
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env   # then add POLYGON_API_KEY=...
make test-cov          # confirm >=90% coverage, all green, zero lint/type errors
python -m levelsheet generate ES --date 2026-08-12 --format pdf,png
# → output/pdf/ES_2026-08-12.pdf and output/png/ES_2026-08-12.png, generated in under 10 seconds
make run-gui
# → http://localhost:8501
```

Do not stop until every phase in §18 is complete, every acceptance criterion in §16 is met, and the commands above work exactly as shown against live or cached data.
