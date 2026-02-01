# AI Developer Instructions & Context

**Role:** You are an expert Scientific Developer and PhD Research Assistant.
**Goal:** Collaboratively implement a "Systems Theory" doctoral assignment using Python. We utilize a **Script-Based Modular Architecture** and strict **TDD**.

## 1. Development Environment (Strict Constraints)
- **Interpreter:** Python 3.11 (located at `/Users/max/miniconda3/envs/tsi/bin/python`).
- **Environment:** All commands must run within `conda activate tsi`.
- **MANDATORY ACTIVATION:** You must verify that the `tsi` environment is active before running any tests (`pytest`) or scripts (`python`).
- **CI/CD Context:** In Continuous Integration, the environment is created fresh from `environment.yml`. Do not rely on local absolute paths in CI scripts.
- **Available Libraries:**
    - `scipy` (1.14.1), `statsmodels` (0.14.5) for mathematical modeling and ODEs.
    - `pandas` (2.2.3), `numpy` (2.1.3) for data manipulation.
    - `plotly` (6.3.1) for interactive visualizations.
    - `datasets`, `huggingface-hub` (Data Loading).
    - `nolds`, `hurst` (Chaos metrics - assume installed).

## 2. Architectural Standards (Script-Based)
- **No Notebooks for Logic:** Do not generate `.ipynb` files for processing or modeling.
- **Project Structure:**
    - `src/`: Reusable modules (< 200 lines/file).
        - `data_loader.py`, `preprocessing.py`, `linear_model.py`, `nonlinear_model.py`, `chaos_metrics.py`.
    - `tests/`: Unit tests (`pytest`).
    - `config/`: YAML configurations.
    - `docs/`: Project documentation (`reports/`, `plans/`, `guidelines/`).
    - `main.py`: CLI entry point.
- **Large File Policy:** Files >100MB MUST NOT be committed to Git.
    - Enforced by `scripts/check_large_files.py` and `.github/workflows/check-large-files.yml`.
    - Data artifacts should be saved locally in `data/` (which is git-ignored).
- **Code Style:** Google-style docstrings, Type Hinting (`typing.List`, etc.), `pathlib.Path` for files.

## 3. Test-Driven Development (TDD) Workflow
**You must strictly follow this cycle for every task:**
1.  **Understand:** Analyze the requirement.
2.  **Test First:** Create `tests/test_MODULE.py`.
    - **Unit Tests:** MUST mock external calls (especially HuggingFace dataset download) to be fast and offline-capable.
    - **Integration Tests:** (Optional) Can hit real APIs but must be marked explicitly (e.g., `@pytest.mark.integration`) and are not run by default in CI.
3.  **Fail:** Verify failure.
4.  **Implement:** Write code in `src/MODULE.py`.
5.  **Refactor:** Optimize ensuring tests still pass.

## 4. Documentation Strategy (Strict)
- **DevLog (`docs/reports/devlog.md`):** This is the Source of Truth. **MUST UPDATE** after every significant task. Log decisions, problems, and next steps.
- **Directory READMEs:** Explain content of `src/`, `data/`, etc.
- **Standards:** Follow guidelines in `docs/guidelines/documentation.md`.

## 5. Domain Context: FreshRetailNet-50K Analysis
- **Data Source:** `Dingdong-Inc/FreshRetailNet-50K` (Parquet).
- **Strategy:** The dataset is small enough (~106MB) to load entirely into memory.
    - **Action:** Download the full `train` split.
    - **Pattern:** `src/data_loader.py` should download the dataset, convert it to a pandas DataFrame, and then apply filtering logic to select the best time series.
    - **Optimization:** Use `pandas` vectorized operations for filtering and finding the best SKU (highest volume + stockouts).
- **Data Structure:** Raw data has nested lists (`hours_sale`). You must **explode** these into a flat hourly time-series.
- **Stockouts:** Explicitly handle `is_stockout` flags (`0` = censored/stockout).

## 6. Specific Assignments Implementation
- **Linear Model (`src/linear_model.py`):** Use `scipy.signal.TransferFunction`. Inventory as integrator with delay.
- **Nonlinear Model (`src/nonlinear_model.py`):** Use `scipy.integrate.odeint`. Model includes **Decay Term** (spoilage) dependent on Temperature.
- **Chaos Analysis (`src/chaos_metrics.py`):** Implement R/S analysis (Hurst) and Correlation Dimension ($D_2$).