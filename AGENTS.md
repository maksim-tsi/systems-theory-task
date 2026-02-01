# AI Developer Instructions & Context

**Role:** You are an expert Scientific Developer and PhD Research Assistant.
**Goal:** Collaboratively implement a "Systems Theory" doctoral assignment using Python. We are NOT competing; we are co-creating a rigorous analysis pipeline.

## 1. Development Environment (Strict Constraints)
- **Interpreter:** Python 3.11 (located at `/Users/max/miniconda3/envs/tsi/bin/python`).
- **Environment:** All commands must run within `conda activate tsi`.
- **Available Libraries:**
    - Use **`scipy`** (1.14.1) and **`statsmodels`** (0.14.5) for mathematical modeling and ODEs.
    - Use **`pandas`** (2.2.3) and **`numpy`** (2.1.3) for data manipulation.
    - Use **`plotly`** (6.3.1) for interactive visualizations.
    - *Note:* Libraries `datasets`, `nolds`, and `hurst` may need to be installed. Check/install if missing.

## 2. Architectural Standards (Script-Based)
- **No Notebooks for Core Logic:** Do not generate `.ipynb` files for processing or modeling.
- **Project Structure:**
    - `src/`: Reusable modules (keep < 200 lines/file).
    - `tests/`: Unit tests (pytest).
    - `config/`: YAML configurations.
    - `docs/`: Project documentation.
        - `reports/`: Generated analysis reports and the critical **`devlog.md`**.
        - `plans/`: Implementation plans and roadmaps.
        - `guidelines/`: Standards (e.g., `documentation.md`).
    - `main.py`: CLI entry point.
- **Code Style:**
    - **Type Hinting:** Mandatory (`typing.List`, `np.ndarray`, etc.).
    - **Docstrings:** Google-style required for all functions.
    - **Paths:** Use `pathlib.Path` relative to project root.

## 3. Test-Driven Development (TDD) Workflow
**You must strictly follow this cycle for every task:**
1.  **Understand:** Analyze the requirement.
2.  **Test First:** Create/Update a test file in `tests/` (e.g., `tests/test_data_loader.py`). Use **Mocking** for external calls.
3.  **Fail:** Verify the test fails.
4.  **Implement:** Write the minimum code in `src/` to pass the test.
5.  **Refactor:** Optimize ensuring tests still pass.

## 4. Documentation Strategy (Strict)
- **DevLog (`docs/reports/devlog.md`):** This is the Source of Truth for project state.
    - **MUST UPDATE** after every significant task completion.
    - Format: Date, Task, Decisions Made, Problems Solved, Next Steps.
- **Directory-Level READMEs:** Every significant directory (`src/`, `tests/`, `data/`) MUST contain a `README.md` explaining its contents and purpose.
- **Standards:** Follow guidelines in `docs/guidelines/documentation.md` (create if missing).

## 5. Domain Context: FreshRetailNet-50K Analysis
- **Data Source:** `Dingdong-Inc/FreshRetailNet-50K` (Parquet).
- **Key Transformation:** Explode nested lists (`hours_sale`) into flat hourly time-series.
- **Stockouts:** Explicitly handle `is_stockout` flags.
    - *Constraint:* Do not compute Fractal Dimension on zero-padded data caused by stockouts. Use interpolation or latent demand recovery.

## 6. Specific Assignments Implementation
- **Linear Model (ACS):** Use `scipy.signal.TransferFunction`. Inventory as integrator with delay.
- **Nonlinear Model (ODE):** Use `scipy.integrate.odeint`. Model includes **Decay Term** (spoilage) dependent on Temperature.
- **Chaos Analysis:** Implement R/S analysis (Hurst) and Correlation Dimension ($D_2$).