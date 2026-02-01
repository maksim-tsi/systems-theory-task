# Source Code (`src/`)

This directory contains the core logic modules for the `systems-theory-task` project. 
The architecture follows a modular, script-based approach (no notebooks for logic) with strict type hinting and Google-style docstrings.
Intermediate analysis artifacts should be saved under docs/reports/artifacts/YYYY-MM-DD/ and linked from the relevant report.

## Module Overview

### 1. Data Engineering
- **`data_loader.py`**: Handles dataset acquisition and initial filtering.
  - **Strategy:** "Full Download". Since `FreshRetailNet-50K` is small (~106MB Parquet), we download the entire train split into memory.
  - **Selection Logic:** Implements a vectorized search (`pandas`) to find the "Golden Sample" — a single Store/Product time-series with high sales velocity and sufficient stockout events for nonlinear modeling.
  - **Transformation:** Explodes nested daily lists (`hours_sale`) into a flat hourly time-series saved as `data/golden_sample.parquet`.

- **`preprocessing.py`**: Data cleaning and feature engineering.
  - **Imputation:** Handles `is_stockout` flags (censored demand) using interpolation or latent demand recovery.
  - **Smoothing:** Optional noise reduction for derivative estimation.

### 2. Modeling & Analysis
- **`linear_model.py`**: (Planned) Implements Linear Control System analysis (Transfer Functions, Stability) using `scipy.signal`.
- **`nonlinear_model.py`**: (Planned) Solves Differential Equations (ODEs) representing inventory dynamics with decay and saturation using `scipy.integrate`.
- **`chaos_metrics.py`**: (Planned) Computes complexity metrics (Hurst Exponent, Fractal Dimension) to classify the system's behavior.

### 3. Utilities
- **`visualization.py`**: (Planned) Generates publication-ready plots (Phase portraits, Time series) saved to `docs/reports/figures/`.