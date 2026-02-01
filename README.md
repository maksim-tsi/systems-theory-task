# Systems Theory: Nonlinear Dynamics in SCM
## Doctoral Coursework Project (D-01-007)

## Project Overview
This repository hosts the computational implementation of the "Systems Theory" doctoral assignment. 

**Methodology:** We utilize a **Script-Based Modular Architecture** rather than Jupyter Notebooks to ensure code robustness, reproducibility, and effective collaboration with AI coding assistants (GitHub Copilot). All development follows a strict **Test-Driven Development (TDD)** cycle. Intermediate analysis artifacts are stored under `docs/reports/artifacts/YYYY-MM-DD/` and linked from reports.

**Objective:** Apply rigorous mathematical modeling to real-world Supply Chain Management data (Control Theory, Differential Equations, Chaos Theory).

## Dataset
**Source:** [FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K)
**Domain:** Hourly perishable goods demand.
**Key Features:** Hourly granularity, Stockout annotations, Exogenous variables.

## Research Assignments (Implemented as Modules)
1. **Linear Control System (`src/linear_model.py`):** Modeling inventory replenishment as a feedback loop.
2. **Nonlinear Dynamics (`src/nonlinear_model.py`):** Modeling decay (spoilage) using ODEs.
3. **Chaos Analysis (`src/chaos_metrics.py`):** Estimation of Hurst Exponent and Fractal Dimension.

## Development Environment
- **Environment:** `conda activate tsi`
- **Testing:** `pytest tests/`
- **Execution:** `python main.py`

## Project Repo Structure
```
systems-theory-task/
├── data/                   # Raw and processed data (git-ignored)
├── config/                 # Configuration files
│   └── params.yaml         # Parameters for ODEs, Control Theory, etc.
├── src/                    # Core Logic (Max ~200 loc per file)
│   ├── __init__.py
│   ├── data_loader.py      # Full dataset download & filtering
│   ├── preprocessing.py    # Explode lists, imputation, smoothing
│   ├── linear_model.py     # ACS Transfer Functions logic
│   ├── nonlinear_model.py  # ODE solvers (scipy.integrate)
│   ├── chaos_metrics.py    # Hurst, Lyapunov, Fractal Dim
│   └── visualization.py    # Plotting functions (save to files)
├── tests/                  # TDD Suite
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_preprocessing.py
│   ├── test_models.py
│   └── test_chaos.py
├── main.py                 # CLI Entry point to run pipeline
├── docs/
│   └── reports/
│       └── artifacts/      # Dated analysis artifacts (txt/csv/json)
├── environment.yml         # Conda env export
├── agents.md               # Instructions for Copilot
└── README.md               # Project documentation
```
