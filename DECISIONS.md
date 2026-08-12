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
pyarrow==25.0.1
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
