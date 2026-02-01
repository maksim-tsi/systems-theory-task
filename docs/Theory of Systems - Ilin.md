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