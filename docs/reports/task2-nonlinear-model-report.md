# Task 2 — Nonlinear Dynamic Model Report

## 1. Scope and Inputs
This report documents the nonlinear model selection, equilibrium analysis, and stability classification for the inventory system.

**Inputs used in code (from config):**
- inventory_decay_rate = 0.01
- temperature_sensitivity = 0.001
- temperature = 20.0
- demand = 10.0
- replenishment_gain = 1.0
- replenishment_decay = 0.5
- i_target = 100.0

**Computed artifact:**
- Nonlinear model analysis: [docs/reports/artifacts/2026-02-01/nonlinear_model_analysis.txt](docs/reports/artifacts/2026-02-01/nonlinear_model_analysis.txt)

## 2. Model Selection
We use a second-order nonlinear ODE system that captures inventory dynamics with temperature-dependent spoilage and a replenishment policy. This structure is standard in supply-chain control analogs and is minimal while still enabling stability classification.

## 3. Model Equations
Decay term:
$$\delta(T) = k\,(1 + \alpha_T (T - 20))$$

State variables: inventory $I(t)$ and replenishment rate $R(t)$.

$$\frac{dI}{dt} = R - D - \delta(T) I$$
$$\frac{dR}{dt} = a (I_{target} - I) - bR$$

## 4. Equilibrium Points
Setting $\frac{dI}{dt}=0$ and $\frac{dR}{dt}=0$ yields the fixed point:

$$I^* = \frac{\frac{a}{b} I_{target} - D}{\frac{a}{b} + \delta(T)}$$
$$R^* = D + \delta(T) I^*$$

## 5. Local Stability Classification
The Jacobian is

$$J = \begin{bmatrix}-\delta(T) & 1 \\ -a & -b \end{bmatrix}$$

Equilibrium type is determined by the eigenvalues of $J$:
- **Saddle** if $\det(J) < 0$.
- **Node** if eigenvalues are real.
- **Focus** if eigenvalues are complex with non-zero real part.
- **Center** if eigenvalues are purely imaginary.

## 6. Computed Results (from code)
Using the parameters above:
- Equilibrium: $I^* \approx 94.53$, $R^* \approx 10.95$.
- Eigenvalues: $-0.255 \pm 0.970i$.
- Classification: **stable focus**.

See the recorded outputs in [docs/reports/artifacts/2026-02-01/nonlinear_model_analysis.txt](docs/reports/artifacts/2026-02-01/nonlinear_model_analysis.txt).

## 7. Phase Portrait with Nullclines
Nullclines are derived from the model equations:

$$\frac{dI}{dt}=0 \Rightarrow R = D + \delta(T) I$$
$$\frac{dR}{dt}=0 \Rightarrow R = \frac{a}{b}(I_{target} - I)$$

The phase portrait overlays the vector field, nullclines, and trajectories converging to the stable focus at $(I^*, R^*)$.
See the interactive figure in [docs/reports/task3_chaos_report.html](docs/reports/task3_chaos_report.html), section “Nonlinear Model Phase Portrait”.

## 8. Recommendations and Next Steps
1. Validate parameters against observed demand statistics from the dataset.
2. Connect nonlinear dynamics to chaos metrics in Task 3 by extracting long trajectories.
