# DevLog

Date: 2026-02-01

Task: Initial project scaffolding and moving existing config.

Decisions made:
- Created `config/params.yaml` with initial parameter placeholders.
- Scaffolded `src/`, `tests/`, `data/`, `docs/` and minimal module stubs and tests.

Problems solved:
- Ensured not to overwrite root-level `AGENTS.md` and `README.md`.

Next steps:
- Implement data streaming from HF in `src/data_loader.py` and add corresponding failing tests (TDD).
- Extend preprocessing to handle `is_stockout` recovery and interpolation.
- Add CI (GitHub Actions) and make tests run in the conda `tsi` env.
- Performed a live integration test: successfully streamed one example from `Dingdong-Inc/FreshRetailNet-50K` and verified it is publicly accessible (no HF token required).
- Added `.gitignore` patterns for large/binary files and a `scripts/check_large_files.py` check with a corresponding GitHub Action to prevent committing files >100MB.
- Added CI workflow `.github/workflows/ci-conda-tsi.yml` which creates and activates the `tsi` conda environment from `environment.yml`, runs the large-file check and executes the test-suite using `pytest`.

Task: Planned execution of assignment.

Decisions made:
- Created a detailed execution plan aligned to docs/assignment.md in docs/plans/assignment-plan.md.

Updates:
- Expanded plan to include smart SKU selection (heuristic ranking), parameter estimation for models, and visualization artifacts.

Next steps:
- Execute the plan starting with data loading/preprocessing TDD.

Task: Implemented data-loader enhancements for golden sample selection.

Decisions made:
- Added streaming hourly expansion, dtype normalization, heuristic scan-and-select, and materialization to parquet in src/data_loader.py.
- Added tests covering hourly streaming, heuristic selection, and materialization in tests/test_data_loader.py.

Next steps:
- Run pytest tests/ and adjust based on failures.

Task: Addressed preprocessing warning.

Decisions made:
- Replaced deprecated fillna(method="ffill") with ffill() in src/preprocessing.py to preserve behavior without warnings.

Task: Updated data loader to blind bestseller strategy.

Decisions made:
- Replaced data loader API with category-agnostic scan_and_select and hourly expansion aligned to first_category_id fields.
- Updated tests in tests/test_data_loader.py to match new API and 24-hour expansion behavior.
