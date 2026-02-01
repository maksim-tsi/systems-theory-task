# Task 1 — Linear Control System (ACS) Report

## 1. Scope and Inputs
This report covers the completed portion of Task 1 (Linear ACS). It documents the linear control model, transfer functions, and stability assessment computed from the current implementation of the inventory control system.

**Inputs used in code (for reproducibility):**
- Proportional gain $K_p = 1.0$
- Target inventory $I_{target} = 1.0$

**Computed artifact:**
- Linear ACS computation output: [docs/reports/artifacts/2026-02-01/linear_control_analysis.txt](docs/reports/artifacts/2026-02-01/linear_control_analysis.txt)

## 2. ACS Structural Diagram (Conceptual)
**for review** — Conceptual structure for the inventory ACS (feedback loop):

```mermaid
flowchart LR
	R[I_target] --> E[Σ: error = I_target - I]
	E --> C[Proportional Controller Kp]
	C --> U[Replenishment U]
	U --> P[Process: Inventory Integrator 1/s]
	D[Demand D] -->|minus| P
	P --> I[Inventory I]
	I -->|feedback| E
```

Interpretation:
- **Controller ($G_c$):** replenishment policy (e.g., order-up-to) that sets $U(t)$ proportional to the inventory deficit.
- **Process ($G_p$):** conservation of mass in the warehouse; inventory is the time-integral of net inflow $U(t)-D(t)$.
- **Disturbance ($D$):** hourly sales rate from the dataset that depletes inventory.
- **Feedback loop:** attempts to restore $I(t)$ to $I_{target}$ under stochastic demand.

## 3. Element Transfer Functions (Linear Approximation)
**for review** — Linearized elements used in the model:

- **Process (inventory integrator):**
	$$I(s) = \frac{1}{s}\bigl(U(s) - D(s)\bigr)$$
	Transfer from $U$ to $I$: $$G_p(s) = \frac{1}{s}$$

- **Controller (proportional):**
	$$U(t) = K_p\bigl(I_{target} - I(t)\bigr)$$
	Transfer from error $E(s)$ to $U(s)$: $$G_c(s) = K_p$$

- **Lead time (delay) approximation (optional):**
	$$G_d(s) = e^{-Ls} \approx \frac{1 - \frac{Ls}{2}}{1 + \frac{Ls}{2}}$$

Assumption: demand $D(s)$ is treated as a disturbance input; the closed-loop transfer below is from $I_{target}$ to $I$.

## 4. Overall Closed-Loop Transfer Function
Combining $G_c(s)$ and $G_p(s)$ with unity feedback, the closed-loop transfer from $I_{target}$ to $I$ is:

$$G_{cl}(s) = \frac{G_c(s)G_p(s)}{1 + G_c(s)G_p(s)} = \frac{K_p \cdot (1/s)}{1 + K_p \cdot (1/s)} = \frac{K_p}{s + K_p}$$

**Characteristic equation:**
$$s + K_p = 0$$

## 4b. Disturbance Transfer Function (Demand Rejection)
For SCM, the key response is to demand $D(s)$. With negative feedback and disturbance at the plant input:

$$G_{DI}(s) = \frac{I(s)}{D(s)} = -\frac{G_p(s)}{1 + G_c(s)G_d(s)G_p(s)}$$

For $L=0$ (no delay):

$$G_{DI}(s) = -\frac{1}{s+K_p}$$

## 5. Stability Analysis
The system is stable if all closed-loop poles have negative real parts. For $G_{cl}(s) = \frac{K_p}{s + K_p}$, the pole is at $s = -K_p$.

**Stability condition:**
$$K_p > 0 \Rightarrow \Re(s) < 0$$

Therefore, any positive proportional gain yields a stable first-order closed-loop response.

## 6. Computed Results (from code)
Using the current configuration ($K_p = 1.0$):

- Closed-loop transfer function: $G_{cl}(s) = \frac{1}{s + 1}$
- Characteristic equation: $s + 1 = 0$
- Closed-loop pole: $s = -1$
- Stability: stable (all poles have negative real parts)

See the recorded outputs in [docs/reports/artifacts/2026-02-01/linear_control_analysis.txt](docs/reports/artifacts/2026-02-01/linear_control_analysis.txt).

## 7. Recommendations and Next Steps
1. **Finalize structural diagram** with domain-specific labels (inventory units, time scale) and confirm sign conventions for the disturbance path (**for review**).
2. **Add interpretive notes** for each element (controller, integrator, disturbance) and relate to the supply-chain context (**for review**).
3. **Consider parameter selection**: test multiple $K_p$ values to show stability margin and response speed (rise time, settling time).
4. **Document disturbance response** (transfer from $D$ to $I$) to describe stockout sensitivity.
5. **Add lead time scenario** using Padé delay approximation and show how stability margin decreases with larger $L$.
6. **Integrate results into final PDF report** with a short narrative for Task 1.

## 8. Conclusion
The linear ACS model for inventory control is fully specified with a proportional controller and integrator process. The resulting closed-loop transfer function $G_{cl}(s) = \frac{K_p}{s + K_p}$ yields a single pole at $s = -K_p$, ensuring stability for any $K_p > 0$. The computed artifact confirms stability for the current configuration and provides concrete values to reference in the final report.

## 9. Introduction
This section documents the linear automatic control system (ACS) formulation for the inventory dynamics of the doctoral research object. The goal is to provide a clear control-theoretic representation, derive the necessary transfer functions, and establish stability criteria to support subsequent nonlinear and chaos analyses in the broader assignment.
