# Documentation guidelines

- Use Google-style docstrings for all public functions.
- Include type hints for all function signatures.
- Keep modules <200 LOC when possible.
- Maintain a `docs/reports/devlog.md` with each significant task update.

## Data & Large files

- Do not commit raw or large data files into the repository. Keep raw data under `data/` and ensure `data/` is git-ignored.
- Avoid committing files > 100 MB. Use Git LFS or external object storage for large artifacts.
- A check script is provided at `scripts/check_large_files.py` and a GitHub Action (`.github/workflows/check-large-files.yml`) will run on PRs to block large files.
