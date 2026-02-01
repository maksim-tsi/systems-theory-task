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
