# Refinement Plan (Professor Feedback)

Date: 2026-02-03
Owner: GitHub Copilot

## Objectives
- Task 1: Update report to use $p$ notation and include explicit $W(p)=P(p)/Q(p)$ derivation and characteristic equation.
- Task 2: Add phase portrait with nullclines and vector field; update Task 2 report and main report.
- Task 3: Add correlation-dimension saturation scan and plot; integrate into HTML report.

## Execution Checklist
1. [x] Add/adjust tests (TDD)
   - [x] `tests/test_models.py`: tests for `compute_nullclines()`
   - [x] `tests/test_chaos.py`: tests for `correlation_dimension_scan()` output shape
2. [x] Implement Task 1 report edits
   - [x] Replace $s$ with $p$ in transfer function section
   - [x] Add explicit $W_{open}(p)$ and $W(p)=P(p)/Q(p)$ derivation
   - [x] Add characteristic equation and root statement
3. [x] Implement Task 2 phase portrait
   - [x] `src/nonlinear_model.py`: add `compute_nullclines()`
   - [x] `src/visualization.py`: add `plot_phase_portrait_with_nullclines()` (quiver + nullclines + trajectory)
   - [x] Update `docs/reports/task2-nonlinear-model-report.md` with nullclines + figure reference
4. [x] Implement Task 3 saturation analysis
   - [x] `src/chaos_metrics.py`: add `correlation_dimension_scan()` returning `{'m': [...], 'd2': [...]}`
   - [x] `src/visualization.py`: add `plot_dimension_saturation()` with y=x reference
   - [x] `src/generate_task3_report.py`: include new plot in HTML
5. [x] Update main report
   - [x] `docs/Theory of Systems - Ilin.md`: update Task 1 notation, Task 2 figure, Task 3 saturation text
6. [ ] Regenerate HTML report and validate
7. [x] Update devlog

## Notes
- Use quiver field (15x15 grid) and analytical nullclines.
- Correlation dimension scan should be simple dict output only.
- HTML first, PDF after validation.
