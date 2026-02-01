# AI Developer Instructions & Context

**Role:** You are an expert Scientific Developer and PhD Research Assistant.
**Goal:** Collaboratively implement a "Systems Theory" doctoral assignment using Python. We utilize a **Script-Based Modular Architecture** and strict **TDD**.

## 1. Development Environment (Strict Constraints)
- **Interpreter:** Python 3.11 (located at `/Users/max/miniconda3/envs/tsi/bin/python`).
- **Environment:** All commands must run within `conda activate tsi`.
- **MANDATORY ACTIVATION:** You must verify that the `tsi` environment is active before running any tests (`pytest`) or scripts (`python`). Do not use the base environment.
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
    - `tests/`: Unit tests (`pytest`).
    - `config/`: YAML configurations.
    - `docs/`: Project documentation.
        - `reports/`: Generated analysis reports and the critical **`devlog.md`**.
        - `plans/`: Implementation plans and roadmaps.
        - `guidelines/`: Standards (e.g., `documentation.md`).
    - `main.py`: CLI entry point.
- **Code Style:** Google-style docstrings, Type Hinting (`typing.List`, etc.), `pathlib.Path` for files.

## 3. Test-Driven Development (TDD) Workflow
**You must strictly follow this cycle for every task:**
1.  **Understand:** Analyze the requirement.
2.  **Test First:** Create `tests/test_MODULE.py`. **Mock external calls** (especially HuggingFace streaming) to avoid network dependency in tests.
3.  **Fail:** Verify failure.
4.  **Implement:** Write code in `src/MODULE.py`.
5.  **Refactor:** Optimize.

## 4. Documentation Strategy (Strict)
- **DevLog (`docs/reports/devlog.md`):** This is the Source of Truth. **MUST UPDATE** after every significant task. Log decisions, problems, and next steps.
- **Directory READMEs:** Explain content of `src/`, `data/`, etc.
- **Standards:** Follow guidelines in `docs/guidelines/documentation.md`.

## 5. Domain Context: FreshRetailNet-50K Analysis
- **Data Source:** `Dingdong-Inc/FreshRetailNet-50K` (Parquet).
- **Streaming Strategy (Critical Architectural Decision):**
    - The dataset is large. Use `load_dataset(..., streaming=True)`.
    - **Constraint:** Analytical modules (ODE, Chaos) require dense in-memory arrays (NumPy), not iterators.
    - **Pattern:** `src/data_loader.py` acts as an **ETL Filter**.
        1.  Stream raw data.
        2.  Iterate and filter for a specific Target SKU/Store.
        3.  **Materialize** this subset into a Pandas DataFrame and save locally (e.g., `data/processed_sample.parquet`).
    - **Downstream:** Modules `dynamics.py` and `chaos.py` must accept **Pandas DataFrames** as input, NOT HuggingFace datasets.
- **Data Structure:** Raw data has nested lists (`hours_sale`). You must **explode** these into a flat hourly time-series.
- **Stockouts:** Explicitly handle `is_stockout` flags (`0` = censored/stockout).

## 6. Specific Assignments Implementation
- **Linear Model (ACS):** Use `scipy.signal.TransferFunction`. Inventory as integrator with delay.
- **Nonlinear Model (ODE):** Use `scipy.integrate.odeint`. Model includes **Decay Term** (spoilage) dependent on Temperature.
- **Chaos Analysis:** Implement R/S analysis (Hurst) and Correlation Dimension ($D_2$).