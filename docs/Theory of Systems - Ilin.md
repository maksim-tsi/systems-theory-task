---
title: "Nonlinear Dynamics and Chaos in Urban Logistics Inventory Systems: An Empirical Analysis of FreshRetailNet-50K"
subtitle: "Self-Study Assignment — Systems Theory (Doctoral Program, 2025–2026)"
author: "Maksim Ilin (83835), Group 5402DTL"
date: "2026-02-01"
lang: en
...

\newpage

	hispagestyle{empty}

Transport and Telecommunication Institute  
Doctoral Faculty  
Telematics and Logistics  

\vspace{18mm}

\begin{center}
	extbf{SELF-STUDY ASSIGNMENT}\\
\vspace{6mm}
	extbf{Systems Theory}\\
\vspace{10mm}
{\Large \textbf{Nonlinear Dynamics and Chaos in Urban Logistics Inventory Systems}}\\
\vspace{2mm}
{\large An Empirical Analysis of FreshRetailNet-50K}\\
\end{center}

\vspace{18mm}

Student: Maksim Ilin (83835)  
Group: 5402DTL  

\vfill

\begin{center}
Riga — 2026
\end{center}

\newpage

## Abstract

This report investigates the dynamic behavior of a perishable inventory system using high-frequency demand data from the FreshRetailNet-50K dataset. The work follows the assignment requirements in three parts: (1) a linear automatic control system (ACS) model of an inventory feedback loop (integrator + proportional controller) with a stability discussion and the effect of transport delay, (2) a nonlinear 2D ODE model with temperature-dependent spoilage and local equilibrium classification, and (3) empirical chaos diagnostics on a time series with more than 1000 samples.

For the chaos task, we analyze the "golden sample" hourly sales series (daytime window 08:00–22:00) and obtain $H \approx 0.59$ (persistent behavior) and $D_2 \approx 1.15$ (non-integer correlation dimension), consistent with low-dimensional complex dynamics under feedback, delays, and censoring due to stockouts.

\newpage

## 1. Assignment Alignment and Research Object

The research object is an urban logistics inventory replenishment system for perishable goods. We use FreshRetailNet-50K, a stockout-annotated censored demand dataset. The empirical indicator for Task 3 is the hourly sales series of the "golden sample" SKU/time window derived in the project pipeline.

This report corresponds to the assignment specification in [docs/assignment.md](docs/assignment.md):

- Task 1: Linear ACS model, transfer functions, closed-loop transfer function, stability.
- Task 2: Nonlinear ODE model (order \le 2), fixed point(s), Jacobian stability classification.
- Task 3: Chaos/time-series metrics for $N\ge 1000$ (Hurst exponent and correlation dimension) and interpretation.

\newpage

## 2. Task 1 — Linear Control System (ACS) Analysis

### 2.1 Structural diagram

The inventory system is modeled as a unity-feedback loop where the controller generates a replenishment signal based on the inventory error, and the plant integrates the net flow (replenishment minus demand). A transport lead time (delay) is optionally included.

![ACS structural diagram (inventory feedback loop)](docs/reports/figures/ilin_structural_diagram.png)

**Elements and interpretation**

- **Reference** $I_{target}$: desired inventory level (setpoint).
- **Error** $e(t)=I_{target}-I(t)$: deviation from target.
- **Controller** $K_p$: proportional replenishment policy.
- **Lead time / delay** $L$: transport delay in the supply chain.
- **Plant / process**: inventory mass balance (integrator in linear approximation).
- **Disturbance** $D(t)$: demand (hourly sales), subtracts inventory.

### 2.2 Element transfer functions

We use the standard linear approximation for inventory dynamics:

$$
I(s) = \frac{1}{s}\left(U(s) - D(s)\right).
$$

Controller (proportional control):

$$
U(t)=K_p\left(I_{target}-I(t)\right).
$$

Optional transport delay $e^{-Ls}$ is approximated by first-order Padé:

$$
G_d(s) \approx \frac{1 - \frac{Ls}{2}}{1 + \frac{Ls}{2}}.
$$

### 2.3 Closed-loop transfer function and stability

With unity feedback and an integrator plant, the reference-to-output closed-loop transfer function is:

$$
G_{cl}(s)=\frac{K_p}{s+K_p}.
$$

The characteristic equation is $s+K_p=0$ with pole $s=-K_p$. Therefore, the baseline system is stable for $K_p>0$.

**Effect of lead time.** Introducing delay increases phase lag and can destabilize the loop for sufficiently large $K_p$ and $L$. In the project implementation, a Padé approximation is used and the resulting poles indicate loss of stability in a scenario with significant delay (e.g., $L=2$ in model time units), consistent with the bullwhip effect under transportation/ordering latency.

\newpage

## 3. Task 2 — Nonlinear Dynamic Model (2D ODE) and Local Analysis

### 3.1 Model formulation

We extend the linear model by adding (i) inventory spoilage that depends on temperature and (ii) inertial dynamics for the replenishment rate.

Temperature-dependent decay (spoilage) is modeled as:

$$
\delta(T)=k\cdot\left(1+\alpha_T\,(T-20)\right).
$$

The 2D nonlinear system is:

$$
\frac{dI}{dt}=R-D-\delta(T)\,I,
\qquad
\frac{dR}{dt}=a\,(I_{target}-I)-b\,R.
$$

Here $I$ is inventory, $R$ is replenishment rate, $D$ is (approximately) constant demand, $a$ is the replenishment gain, and $b$ is the replenishment damping/decay.

### 3.2 Fixed point (equilibrium)

Setting derivatives to zero yields an equilibrium $(I^*,R^*)$. For $I^*$ we use:

$$
I^* = \frac{a\,I_{target}-b\,D}{a+b\,\delta(T)}.
$$

The steady replenishment is then $R^*=D+\delta(T)I^*$.

### 3.3 Local stability (Jacobian and eigenvalues)

The Jacobian matrix is:

$$
J=\begin{bmatrix}
-\delta(T) & 1 \\
-a & -b
\end{bmatrix}.
$$

The equilibrium type is determined from the eigenvalues of $J$. In the project parameter regime, the eigenvalues are complex with negative real part, e.g.:

$$
\lambda_{1,2}\approx -0.255\pm 0.970i,
$$

which corresponds to a **stable focus** (damped oscillations). This matches the qualitative behavior typically associated with bullwhip-like oscillations: inventory and replenishment oscillate transiently and then settle.

\newpage

## 4. Task 3 — Chaos Theory and Time Series Analysis

### 4.1 Data and indicator

We analyze the "golden sample" hourly sales time series derived from FreshRetailNet-50K. The full hourly series exceeds 1000 samples (90 days × 24 hours = 2160). To reduce estimator degeneracy due to long overnight zero runs (stockouts/low demand), we restrict the analysis to daytime hours **08:00–22:00**.

### 4.2 Methods

**Phase space reconstruction (2D embedding):**

$$
\mathbf{x}(t)=[x(t),\,x(t+\tau)].
$$

**Hurst exponent (R/S):**

$$
\mathbb{E}\left[\frac{R(n)}{S(n)}\right]=C\,n^H,
\qquad
\log(R/S)\approx H\,\log(n)+\text{const}.
$$

**Correlation dimension ($D_2$):**

$$
C(r)=\frac{2}{N(N-1)}\sum_{i<j}\Theta\bigl(r-\|\mathbf{x}_i-\mathbf{x}_j\|\bigr),
\qquad
C(r)\sim r^{D_2},
\qquad
D_2=\lim_{r\to 0}\frac{\log C(r)}{\log r}.
$$

### 4.3 Visual diagnostics

![Hourly sales time series with stockout markers](docs/reports/figures/task3_time_series.png)

![Phase portrait (2D embedding, delay $\tau=1$)](docs/reports/figures/task3_phase_portrait.png)

![Hurst exponent estimation (R/S log-log fit)](docs/reports/figures/task3_hurst_rs.png)

![Correlation dimension estimation ($D_2$ log-log fit)](docs/reports/figures/task3_correlation_dimension.png)

### 4.4 Results and interpretation

The computed invariants for the daytime hourly series are:

- Hurst exponent: $H\approx 0.59$.
- Correlation dimension: $D_2\approx 1.15$.

**Interpretation.** Since $H>0.5$, the process is persistent (long-memory behavior), which is compatible with feedback-driven dynamics rather than a pure random walk. The non-integer value $D_2\approx 1.15$ indicates a low-dimensional geometric structure in reconstructed phase space, which is consistent with complex deterministic dynamics (potentially chaotic) rather than a purely stochastic cloud. Given the strong seasonality and the censoring introduced by stockouts, these results should be interpreted cautiously; however, together they support the hypothesis of bounded, non-trivial dynamics under supply-chain feedback.

For interactive versions of these plots, see [docs/reports/task3_chaos_report.html](docs/reports/task3_chaos_report.html).

\newpage

## 5. Conclusion

This work demonstrates a coherent systems-theory analysis of an inventory replenishment system using both theory-driven models and empirical diagnostics. The linear ACS formulation provides a baseline stability condition and shows how delays can destabilize the loop. The nonlinear 2D model introduces spoilage and inertia and yields a stable-focus equilibrium consistent with damped oscillations. Finally, the empirical time-series analysis on a long hourly sequence yields a persistent Hurst exponent and a non-integer correlation dimension, suggesting low-dimensional complex behavior influenced by feedback, delays, and stockout censoring.

\newpage

## References

Dingdong-Inc (2025). *FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail* [Dataset]. Available at: [https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/tree/main/data](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/tree/main/data) (Accessed: 1 February 2026).

Forrester, J.W. (1961). *Industrial Dynamics*. Waltham, MA: Pegasus Communications.

Grassberger, P. and Procaccia, I. (1983). 'Characterization of strange attractors', *Physical Review Letters*, 50(5), pp. 346–349.

Hurst, H.E. (1951). 'Long-term storage capacity of reservoirs', *Transactions of the American Society of Civil Engineers*, 116, pp. 770–799.

Ilin, M. (2026). *Systems Theory Task: Analysis of Nonlinear Dynamics and Chaos in Inventory Systems*. GitHub Repository. Available at: [https://github.com/maksim-tsi/systems-theory-task](https://github.com/maksim-tsi/systems-theory-task) (Accessed: 1 February 2026).

Sterman, J.D. (2000). *Business Dynamics: Systems Thinking and Modeling for a Complex World*. Boston: Irwin/McGraw-Hill.

Strogatz, S.H. (2015). *Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry, and Engineering*. 2nd edn. Boulder, CO: Westview Press.