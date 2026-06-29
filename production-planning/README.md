# 🏭 Multi-Period Production Planning & Capacity Optimizer

An interactive, enterprise-grade Decision Support System (DSS) developed using **Python**, **PuLP**, and **Streamlit**. This application models, solves, and visualizes multi-period production scheduling constraints using Mixed-Integer Linear Programming (MILP) via the COIN-OR CBC solver. 

The primary objective is to minimize total manufacturing, inventory holding, and operational switching costs over a 6-month planning horizon while matching volatile market demand.

---

## 🚀 Live Production Link
You can interact with the fully deployed cloud application here:
👉 **[INSERT YOUR DEPLOYED STREAMLIT URL HERE]**

---

## 📊 Core Architectural Features

* **Dynamic Scenario Management:** Tweak economic parameters (shift premiums, holding rates, transition costs) and operational boundaries (capacities, demand vectors) live via an intuitive sidebar.
* **Reactive Execution:** Utilizes Streamlit's structural execution model to re-solve the underlying mathematical matrices instantly when parameters change.
* **Advanced High-Level Metrics:** Highlights crucial Key Performance Indicators (KPIs) such as Total Optimized Cost, Cumulative Production Units, Total Holding Costs, and Shift Change Overheads.
* **Interactive Data Dashboards:** Features rich, theme-adaptive visualization components:
  * *Production vs. Demand:* A dual-variable comparison bar chart highlighting resource utilization against market requirements.
  * *Inventory Track:* A continuous trend-line showcasing safety stock tracking over time.

---

## 🛠️ Mathematical Model Formulation

The deterministic operational model handles decision-making under finite capacity over a planning horizon $T = \{1, 2, \dots, 6\}$.

### 1. Decision Variables
* $P_t \ge 0$: Continuous variable representing total units manufactured during month $t$.
* $I_t \ge 1$: Continuous variable tracking ending inventory at month $t$ (bounded by a safety stock floor of 1 unit).
* $N_t \in \{0, 1\}$: Binary variable indicating if a **Normal Shift** is active during month $t$.
* $E_t \in \{0, 1\}$: Binary variable indicating if an **Extended Shift** is active during month $t$.
* $S_t \in \{0, 1\}$: Binary variable tracking if a **Switch** to a higher operational cost tier occurs at month $t$.

### 2. Objective Function
Minimize the cumulative sum of variable operational allocations, storage penalties, and structural setup overheads:

$$\min \sum_{t \in T} \left( \text{NormalCost} \cdot N_t + \text{ExtendedCost} \cdot E_t + \text{HoldingCost} \cdot I_t \right) + \text{SwitchCost} \cdot \sum_{t=2}^{6} S_t$$

### 3. Constraints
* **Inventory Balance:** Consistently links sequential periods given deterministic customer demand ($D_t$):
  $$I_1 = \text{InitialInventory} + P_1 - D_1$$
  $$I_t = I_{t-1} + P_t - D_t \quad \forall t \in \{2, \dots, 6\}$$
* **Terminal Condition:** Ensures target strategic buffer stock is preserved at the end of the horizon:
  $$I_6 \ge \text{FinalInventory}$$
* **Mutual Exclusivity:** Prevents concurrent run configurations (only one shift type can run per month):
  $$N_t + E_t \le 1 \quad \forall t \in T$$
* **Capacity Bounds & Minimum Lot Sizes:** Restricts production volumes based on active binary states:
  $$P_t \le \text{NormalCapacity} \cdot N_t + \text{ExtendedCapacity} \cdot E_t \quad \forall t \in T$$
  $$P_t \ge \text{MinimumProduction} \cdot (N_t + E_t) \quad \forall t \in T$$
* **Tier Transition State Logic:** Captures structural switches when stepping up capacity or converting states:
  $$S_t \ge N_{t-1} + E_t - 1 \quad \forall t \in \{2, \dots, 6\}$$
  $$S_1 \ge E_1 \quad (\text{Assumes Initial State = Normal})$$

---

## 🔧 Local Setup & Installation

If your faculty wishes to inspect the raw engine locally, they can execute the workspace setup below:

1. **Clone and Navigate to the Workspace:**
   ```bash
   git clone <your-repository-url>
   cd production-optimizer
