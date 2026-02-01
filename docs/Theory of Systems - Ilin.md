TRANSPORT AND TELECOMMUNICATION INSTITUTE  
DOCTORAL FACULTY  
TELEMATICS AND LOGISTICS  
   
   
**SELF-STUDY ASSIGNMENT**  
   
# Nonlinear Dynamics and Chaos in Urban Logistics Inventory Systems: An Empirical Analysis of FreshRetailNet-50K

of the course "Systems Theory" for doctoral students  
   
   
   
   
   
   
STUDENT:     
Maksim ILIN (83835)  
GROUP:  
5402DTL

   
 

   
   
2026  
Riga

This research investigates the dynamic behavior of perishable inventory systems using high-frequency data from the FreshRetailNet-50K dataset. The study follows a three-stage systems theory approach. First, a Linear Control System (ACS) model defines the inventory loop as an integrator with proportional control; stability analysis demonstrates that while theoretically stable, the system loses stability under significant transport delays ($L=2$), mimicking real-world supply chain latency. Second, a Nonlinear Dynamic Model (2nd order ODE) incorporating temperature-dependent spoilage reveals a "Stable Focus" equilibrium, explaining the damped oscillations often observed as the Bullwhip Effect. Finally, empirical Chaos Analysis of the "Golden Sample" hourly time series identifies a Hurst Exponent ($H \\approx 0.59$) and a fractional Correlation Dimension ($D\_2 \\approx 1.15$). These findings confirm the presence of a Strange Attractor, suggesting that the inventory system operates in a regime of low-dimensional deterministic chaos driven by censored demand (stockouts) and replenishment constraints.

## **Task 1 Report: Linear Control System (ACS) Analysis**

### **1. Introduction**

This section documents the linear automatic control system (ACS) formulation for the inventory dynamics of the doctoral research object. The goal is to provide a clear control-theoretic representation, derive the necessary transfer functions, and establish stability criteria to support subsequent nonlinear and chaos analyses.

### **2. ACS Structural Diagram**

The inventory control system is modeled as a feedback loop where the controller adjusts replenishment based on the error between the target and actual inventory levels.

**[INSERT STRUCTURAL DIAGRAM HERE]**

**Interpretation of Elements:**

* **Controller ():** Represents the replenishment policy (e.g., order-up-to) that sets the replenishment rate  proportional to the inventory deficit ().
* **Process ():** Represents the conservation of mass in the warehouse; inventory  is the time-integral of the net flow ().
* **Disturbance ():** The hourly sales rate (demand) from the *FreshRetailNet-50K* dataset that depletes the inventory.
* **Feedback Loop:** The mechanism that attempts to restore inventory  to the target level  despite stochastic demand.

### **3. Element Transfer Functions**

The system components are described by the following linear approximations:

* **Process (Inventory Integrator):**


* **Controller (Proportional):**


* **Lead Time (Optional Delay):**
For scenarios with transport delay , the delay is approximated using a first-order Padé approximation:



### **4. Closed-Loop Transfer Function & Stability**

Combining the controller and process with unity feedback, the overall closed-loop transfer function from the target inventory  to the actual inventory  is derived as:

**Stability Analysis:**
The characteristic equation of the system is , which yields a single pole at .

* **Condition:** The system is stable if the real part of the pole is negative ().
* **Result:** For any positive proportional gain (), the baseline first-order system is theoretically stable.

### **5. Simulation Results and Discussion**

Using the implemented Python model with , the following behaviors were observed:

1. **Baseline Scenario (No Delay):**
* Transfer function: .
* Pole: .
* **Outcome:** The system is stable and effectively tracks the inventory target.


2. **Disturbance Rejection:**
* The transfer function from Demand () to Inventory () is . The system inherently resists demand fluctuations, though a steady-state error may persist without integral action.


3. **Effect of Supply Chain Lead Time ():**
* When a transport delay of  hours is introduced (using Padé approximation), the system dynamics change significantly.
* Resulting Poles:  and .
* **Outcome:** The appearance of a positive pole () indicates that the system **loses stability**. This mathematically confirms that while the simplified model is stable, real-world delays can cause oscillations (Bullwhip Effect) or instability if the controller gain  is too high.



### **6. Conclusion**

The linear ACS model successfully defines the foundational mechanics of the inventory system. While the ideal proportional-integrator model ensures stability, the analysis demonstrates that the system is sensitive to transport delays. This justifies the need for the more complex nonlinear and chaotic analyses performed in subsequent tasks to capture realistic supply chain behaviors.

Вот проект отчета по **Task 2 (Nonlinear Dynamic Model)**.

Он составлен на английском языке, чтобы соответствовать стилю первого отчета и академическим требованиям. Структура продолжает логику исследования: после линейного анализа (Task 1) мы вводим физические нелинейности (порчу товара).

---

## **Task 2 Report: Nonlinear Dynamic Model Analysis**

### **1. Introduction**

This section details the development and analysis of a second-order nonlinear dynamic model for the inventory system. While the linear model (Task 1) provided baseline stability criteria, it failed to account for temperature-dependent spoilage and the inertial dynamics of the replenishment process. This task introduces these nonlinearities to investigate more complex behaviors, such as oscillations (Bullwhip Effect) and equilibrium shifts.

### **2. Model Formulation**

To capture the realistic physics of perishable inventory, the system is modeled as a set of two coupled ordinary differential equations (ODEs).

**2.1. Variable Definitions**

* : Current inventory level (State Variable 1).
* : Rate of replenishment/supply (State Variable 2).
* : Constant demand rate (Disturbance).
* : Ambient temperature (Exogenous parameter).

**2.2. Nonlinear Spoilage Function**
Unlike the linear integrator, the inventory decays over time due to spoilage. The decay rate  is modeled as a function of temperature:



*Where  is the base decay rate at 20°C, and  is the temperature sensitivity coefficient.*

**2.3. System Equations**
The dynamics are governed by the following system:

1. **Inventory Dynamics (Mass Balance with Decay):**


2. **Replenishment Dynamics (Second-Order Control):**



*This equation models the supply chain inertia, where the replenishment rate  adjusts to the inventory error  with gain , but with a damping factor .*

### **3. Equilibrium Analysis**

The fixed points (equilibrium states)  are found by setting the time derivatives to zero:  and .

Solving the algebraic system yields:


**Physical Interpretation:**
The equilibrium inventory  is lower than  due to the "leakage" caused by spoilage () and demand (). The system requires a steady-state replenishment  that exceeds demand  exactly enough to cover the spoilage.

### **4. Stability Analysis (Jacobian Method)**

To classify the stability of the equilibrium, we analyze the Jacobian matrix  of the linearized system at :

The stability is determined by the eigenvalues  of characteristic equation :


### **5. Numerical Results and Classification**

Using the configuration parameters derived from the *FreshRetailNet-50K* context (, , , ):

1. **Computed Equilibrium:**
*  units.
*  units/hour.
* *Note: Even with a target of 100, the system settles at ~94.5 due to spoilage.*


2. **Eigenvalues:**
* 


3. **Classification:**
Since the eigenvalues are complex conjugates with a negative real part (), the equilibrium is classified as a **Stable Focus**.

### **6. Conclusion**

The nonlinear analysis reveals that the inventory system is locally stable but exhibits **damped oscillations** (Stable Focus).

* **Significance:** This mathematically explains the "Bullwhip Effect" observed in supply chains: a disturbance in demand causes the replenishment rate and inventory to oscillate before settling.
* **Comparison:** Unlike the Linear model (Task 1), which predicted simple exponential decay (Node), the 2nd-order nonlinear model correctly captures the oscillatory transient response inherent in systems with inertia and decay.

## **Task 3 Report: Empirical Chaos Theory Analysis**

### **1. Introduction**

Following the identification of oscillatory behavior (Stable Focus) in the nonlinear model (Task 2), this task investigates the nature of these oscillations using empirical time series analysis. The objective is to determine whether the variability in the *FreshRetailNet-50K* inventory data is purely stochastic (random noise) or evidence of **deterministic chaos**.

To prove the existence of a **Strange Attractor**, we analyze the "Golden Sample" time series using phase space reconstruction and fractal geometry metrics.

### **2. Methodology and Data Preparation**

**2.1. Data Preprocessing**
The analysis utilizes the hourly sales time series from the "Golden Sample".

* **Daytime Filtering:** To avoid mathematical degeneracy caused by overnight stockouts (long sequences of zeros), the analysis is restricted to the active daytime window (**08:00 – 22:00**).
* **Sample Size:** The resulting dataset consists of  hourly observations, sufficient for low-dimensional chaos estimation.

**2.2. Metrics**
Two key invariants were computed to classify the system dynamics:

1. **Hurst Exponent ():** Calculated via Rescaled Range (R/S) analysis to detect long-term memory.
2. **Correlation Dimension ():** Estimated using the Grassberger-Procaccia algorithm to determine the fractal dimension of the attractor.

### **3. Visual Analysis**

**3.1. Time Series Dynamics**
The raw time series exhibits quasi-periodic behavior driven by the daily cycle, but with significant irregularity in peak amplitudes and stockout events.

**[INSERT FIGURE 1: Time Series Plot from HTML Report]**
*Fig 1. Hourly sales dynamics showing irregular peaks and stockout events (red dots).*

**3.2. Phase Space Reconstruction**
Using the time-delay embedding method ( vs. ), we reconstruct the phase portrait. The trajectory does not form a closed loop (Limit Cycle) nor a scattered cloud (White Noise). Instead, it forms a structured "tangle" characteristic of a strange attractor.

**[INSERT FIGURE 2: Phase Portrait Plot from HTML Report]**
*Fig 2. Phase space reconstruction () revealing a bounded but non-repeating trajectory.*

### **4. Quantitative Results**

**4.1. Hurst Exponent ()**
The R/S analysis yields a Hurst exponent of:


**Interpretation:**
Since , the process is **persistent**. The system has "memory": high values are likely to be followed by high values. This rules out the hypothesis of a purely Random Walk () or Mean Reversion (), confirming the influence of feedback loops identified in Task 1.

**[INSERT FIGURE 3: Hurst Log-Log Plot from HTML Report]**
*Fig 3. Rescaled Range (R/S) scaling showing persistence ().*

**4.2. Correlation Dimension ()**
The correlation sum  exhibits a clear scaling region with a slope of:


**Interpretation:**

* **:** The system is not a fixed point.
* ** is fractional:** This is the definitive signature of a **fractal geometry**.
* **:** The dynamics cannot be described by a simple 1D curve (Limit Cycle). The attractor has a "thickness" in phase space.

**[INSERT FIGURE 4: Correlation Dimension Plot from HTML Report]**
*Fig 4. Correlation Sum scaling indicating a fractional dimension .*

### **5. Discussion**

The combination of a fractional dimension () and system memory () confirms that the inventory system operates in a regime of **low-dimensional deterministic chaos**.

This empirical finding validates the theoretical predictions from Task 1 and Task 2:

1. **Instability:** The sensitivity to delays (Task 1) pushes the system away from a stable equilibrium.
2. **Nonlinearity:** The spoilage and constraints (Task 2) fold the trajectory back, preventing explosion.
3. **Chaos:** The interaction of these forces creates a **Strange Attractor**, where the state is bounded but never exactly repeats.

### **6. Conclusion**

The research successfully identifies the underlying physics of the *FreshRetailNet-50K* system. It is not driven by random external noise, but by internal chaotic dynamics resulting from the interplay of replenishment delays and inventory constraints. This implies that traditional linear forecasting methods will degrade over time (due to the Butterfly Effect), and control strategies must account for the system's fractal nature.

## References

Dingdong-Inc (2025). *FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail* [Dataset]. Available at: [https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/tree/main/data](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/tree/main/data) (Accessed: 1 February 2026).

Forrester, J.W. (1961). *Industrial Dynamics*. Waltham, MA: Pegasus Communications.

Grassberger, P. and Procaccia, I. (1983). 'Characterization of strange attractors', *Physical Review Letters*, 50(5), pp. 346–349.

Hurst, H.E. (1951). 'Long-term storage capacity of reservoirs', *Transactions of the American Society of Civil Engineers*, 116, pp. 770–799.

Ilin, M. (2026). *Systems Theory Task: Analysis of Nonlinear Dynamics and Chaos in Inventory Systems*. GitHub Repository. Available at: [https://github.com/maksim-tsi/systems-theory-task](https://github.com/maksim-tsi/systems-theory-task) (Accessed: 1 February 2026).

Sterman, J.D. (2000). *Business Dynamics: Systems Thinking and Modeling for a Complex World*. Boston: Irwin/McGraw-Hill.

Strogatz, S.H. (2015). *Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry, and Engineering*. 2nd edn. Boulder, CO: Westview Press.

## ANNEX for Assistant

### LaTeX instructions

**Наши формулы для вставки (LaTeX) в отчет по заданию 1:**

* **Интегратор:**
`I(s) = \frac{1}{s}\left(U(s) - D(s)\right)`
* **Контроллер:**
`U(t) = K_p\left(I_{target} - I(t)\right)`
* **Задержка (Паде):**
`G_d(s) \approx \frac{1 - \frac{Ls}{2}}{1 + \frac{Ls}{2}}`
* **Замкнутый контур:**
`G_{cl}(s) = \frac{K_p}{s + K_p}`


**Для части 2 этого отчета используйте следующие LaTeX-коды:**

* **Функция распада:**
`\delta(T) = k \cdot (1 + \alpha_T (T - 20))`
* **Система уравнений:**
`\frac{dI}{dt} = R - D - \delta(T) \cdot I`
`\frac{dR}{dt} = a(I_{target} - I) - b \cdot R`
* **Точка равновесия:**
`I^* = \frac{a \cdot I_{target} - b \cdot D}{a + b \cdot \delta(T)}`
* **Матрица Якоби:**
`J = \begin{bmatrix} -\delta(T) & 1 \\ -a & -b \end{bmatrix}`
* **Собственные числа:**
`\lambda_{1,2} \approx -0.255 \pm 0.970i`

1. Реконструкция фазового пространства (Methodology)

Для описания того, как мы строили фазовый портрет (Embedding):

* **Вектор состояния (для 2D, как в нашем случае):**
`\mathbf{x}(t) = [x(t), x(t + \tau)]`
* **В общем виде (если нужно):**
`\mathbf{x}_i = [x_i, x_{i+\tau}, \dots, x_{i+(m-1)\tau}]`

2. Показатель Херста (Hurst Exponent)

Для раздела **4.1**, описывающего R/S анализ:

* **Основное соотношение (Power Law):**
`E\left[\frac{R(n)}{S(n)}\right] = C \cdot n^H`
* **Логарифмическая форма (линейная регрессия):**
`\log(R/S) \approx H \cdot \log(n) + \text{const}`

3. Корреляционная размерность ()

Для раздела **4.2**, описывающего алгоритм Грассбергера-Прокаччиа:

* **Корреляционная сумма (Correlation Sum):**
`C(r) = \frac{2}{N(N-1)} \sum_{i<j} \Theta(r - \|\mathbf{x}_i - \mathbf{x}_j\|)`
*(где  — функция Хевисайда, считающая пары точек ближе, чем )*
* **Закон скейлинга (Scaling Law):**
`C(r) \sim r^{D_2}`
* **Определение размерности:**
`D_2 = \lim_{r \to 0} \frac{\log C(r)}{\log r}`

---

**Совет:**
В разделе **Results** для конкретных значений лучше использовать простой текст с математическими символами (как в моем черновике отчета), так как там важны числа:
`H \approx 0.586`
`D_2 \approx 1.145`

А вот в разделе **Methodology**, где вы объясняете *суть метода*, эти формулы будут смотреться очень солидно и повысят академический вес работы.

### Как вставить графики:

1. Откройте ваш HTML-файл `docs/reports/task3_chaos_report.html` в браузере.
2. В каждом графике (Plotly) в правом верхнем углу есть иконка фотоаппарата **"Download plot as a png"**.
3. Нажмите на нее для каждого из 4 графиков.
4. Вставьте скачанные PNG файлы в Google Doc на места `[INSERT FIGURE X]`.