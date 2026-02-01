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

Task: Fixed data loader to enforce full dataset loading.

Decisions made:
- Enforced non-streaming load (streaming=False) and guarded against IterableDataset in src/data_loader.py.
- Clarified MultiIndex handling for best SKU selection and added scalar extraction for metrics.

Task: Updated data loader tests for non-streaming API.

Decisions made:
- Replaced streaming-based tests with checks for load_full_dataset, find_golden_sample_vectorized, and explode_and_save in tests/test_data_loader.py.

Task: Golden sample analysis report.

Decisions made:
- Computed descriptive statistics and hourly profiles from data/golden_sample.parquet and saved findings in docs/reports/golden-sample-analysis.md.

Task: Fixed stockout interpretation and price normalization.

Decisions made:
- Updated src/data_loader.py to treat stock_status 0 as available and >0 as stockout.
- Normalized price from discount using price = 1.0 - discount (fallback to 0.0 if discount >= 1.0).

Task: Updated golden sample analysis report (post-fix).

Decisions made:
- Recomputed summary stats for data/golden_sample.parquet and saved intermediate results in docs/reports/tmp/golden_sample_stats.txt.
- Overwrote docs/reports/golden-sample-analysis.md with corrected stockout and price findings.

Task: Standardized analysis artifact storage.

Decisions made:
- Moved golden sample stats to docs/reports/artifacts/2026-02-01/ and updated report links.
- Added artifact storage guidance to AGENTS.md, .github/copilot-instructions.md, and README files.

Task: Removed conda from CI.

Decisions made:
- Replaced conda-based CI workflow with actions/setup-python and pip installs.
- Updated AGENTS.md and copilot instructions to reflect non-conda CI.

Task: Implemented linear inventory control system.

Decisions made:
- Added `InventoryControlSystem` with proportional control, step response simulation, and closed-loop stability analysis in src/linear_model.py.

Task: Generated linear ACS analysis artifact.

Decisions made:
- Saved computed transfer function and stability results to docs/reports/artifacts/2026-02-01/linear_control_analysis.txt.

Task: Drafted Task 1 linear ACS report.

Decisions made:
- Added report with derived transfer functions, stability analysis, and recommendations in docs/reports/task1-linear-acs-report.md.

Task: Extended linear ACS model with delay and disturbance response.

Decisions made:
- Added lead-time (Padé) delay support and explicit disturbance transfer function in src/linear_model.py.
- Added tests for delay order increase and disturbance transfer behavior in tests/test_models.py.
- Updated Task 1 report with SCM interpretation, delay element, and demand-rejection transfer function.

Task: Revalidated linear ACS results after delay updates.

Decisions made:
- Ran pytest tests/ (all passing).
- Regenerated linear ACS analysis artifact with disturbance and delay scenarios.
- Updated Task 1 report computed results to reflect new artifact values.

Task: Implemented nonlinear model (Task 2) with equilibrium analysis.

Decisions made:
- Added 2D inventory–replenishment ODE with temperature-dependent decay, equilibrium solver, Jacobian, and stability classification in src/nonlinear_model.py.
- Added TDD coverage for equilibrium and classification in tests/test_models.py.
- Extended config parameters for nonlinear model in config/params.yaml.
- Generated nonlinear model analysis artifact and created Task 2 report.

Task: Implemented chaos metrics (Task 3) core estimators.

Decisions made:
- Replaced stub chaos tests with Hurst R/S expectations for white noise, persistent trend, and anti-persistent AR(1) series in tests/test_chaos.py.
- Implemented Hurst R/S estimator and correlation dimension (nolds if available, GP fallback) in src/chaos_metrics.py.

Task: Added daytime filtering and daily aggregation helpers.

Decisions made:
- Added filter_daytime_hours and aggregate_daily utilities to src/preprocessing.py with tests in tests/test_preprocessing.py.

Task: Added chaos analysis script for golden sample.

Decisions made:
- Added src/chaos_analysis.py to compute Hurst and correlation dimension on daytime hourly and daily aggregated series and save artifacts.
- Added a small IO test for saving artifacts in tests/test_chaos.py.

Task: Generated Task 3 chaos metrics artifact.

Decisions made:
- Ran chaos analysis on data/golden_sample.parquet with daytime window 08:00–22:00.
- Saved results to docs/reports/artifacts/2026-02-01/chaos_metrics_analysis.txt.

Task: Implemented robust chaos metrics and HTML reporting.

Decisions made:
- Added diagnostic versions of Hurst and correlation dimension (with log-log fit and R²) in src/chaos_metrics.py.
- Extended src/visualization.py with phase portrait and log-log diagnostic plots.
- Added src/report_generator.py and src/generate_task3_report.py to build an HTML report with Plotly figures.
- Added tests for chaos diagnostics and report generation in tests/test_chaos.py.

Task: Generated Task 3 HTML report.

Decisions made:
- Generated docs/reports/task3_chaos_report.html from data/golden_sample.parquet.

Task: Added scikit-learn chaos analysis run.

Decisions made:
- Added sklearn-enabled regression fitting in src/chaos_metrics.py.
- Added sklearn analysis runner in src/chaos_analysis_sklearn.py and comparison artifact generator.
- Added sklearn-conditional test in tests/test_chaos.py.

Task: Documented Task 3 chaos report.

Decisions made:
- Added extended Task 3 markdown report with methods, results, interpretation, and artifact links in docs/reports/task3-chaos-report.md.

Task: Reformatted final assignment report and generated PDF (Ilin).

Decisions made:
- Reformatted the main report to align with the assignment structure (Tasks 1–3) and moved key LaTeX equations into the main body: [docs/Theory of Systems - Ilin.md](docs/Theory%20of%20Systems%20-%20Ilin.md).
- Exported static figures for PDF inclusion:
	- Structural diagram: [docs/reports/figures/ilin_structural_diagram.pdf](docs/reports/figures/ilin_structural_diagram.pdf), [docs/reports/figures/ilin_structural_diagram.png](docs/reports/figures/ilin_structural_diagram.png).
	- Task 3 figures: [docs/reports/figures/task3_time_series.png](docs/reports/figures/task3_time_series.png), [docs/reports/figures/task3_phase_portrait.png](docs/reports/figures/task3_phase_portrait.png), [docs/reports/figures/task3_hurst_rs.png](docs/reports/figures/task3_hurst_rs.png), [docs/reports/figures/task3_correlation_dimension.png](docs/reports/figures/task3_correlation_dimension.png).
- Added a reproducible pandoc+XeLaTeX build script and generated the final PDF:
	- Script: [scripts/build_ilin_report_pdf.sh](scripts/build_ilin_report_pdf.sh)
	- Output: [docs/reports/Systems_Theory_Ilin.pdf](docs/reports/Systems_Theory_Ilin.pdf)

Commands:
- `conda run -n tsi python scripts/export_ilin_report_figures.py`
- `scripts/build_ilin_report_pdf.sh`
