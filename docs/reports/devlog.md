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
