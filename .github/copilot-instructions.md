# Copilot Instructions (systems-theory-task)

## Big picture / architecture
- Script-based modular pipeline (no notebooks for logic). Core modules live in src/ and are kept <200 LOC with type hints + Google-style docstrings.
- Data flow: HuggingFace streaming dataset → ETL filter in src/data_loader.py → materialized pandas DataFrame (saved under data/) → preprocessing → modeling (linear/nonlinear/chaos).
- Downstream modules (src/nonlinear_model.py, src/chaos_metrics.py) must accept pandas DataFrames, not streaming iterators.

## Project-specific data conventions
- Dataset: Dingdong-Inc/FreshRetailNet-50K (Parquet). Use load_dataset(..., streaming=True) due to size.
- Raw rows include nested lists (hours_sale). Explode to flat hourly time series in preprocessing.
- Stockouts: handle is_stockout flags explicitly (0 = censored/stockout).

## Modeling requirements (domain-specific)
- Linear model in src/linear_model.py uses scipy.signal.TransferFunction (inventory as integrator with delay).
- Nonlinear model in src/nonlinear_model.py uses scipy.integrate.odeint with a temperature-dependent decay term.
- Chaos metrics in src/chaos_metrics.py implement Hurst (R/S) and correlation dimension D2.

## Developer workflows (non-obvious)
- Environment is conda env “tsi” (Python 3.11). Activate before running anything.
- Run tests with: pytest tests/
- Run pipeline with: python main.py
- CI uses environment.yml; do not depend on absolute local paths.

## Repo conventions / policies
- Large file policy: do not commit artifacts >100MB; data outputs go under data/ (git-ignored). Enforced by scripts/check_large_files.py.
- Config values live in config/params.yaml (ODE/control parameters).
- Documentation: update docs/reports/devlog.md after significant tasks; follow docs/guidelines/documentation.md.

## TDD expectations
- Tests live in tests/ (e.g., test_data_loader.py, test_preprocessing.py, test_models.py, test_chaos.py).
- Unit tests must mock external calls (especially HuggingFace streaming). Integration tests should be marked with @pytest.mark.integration.
