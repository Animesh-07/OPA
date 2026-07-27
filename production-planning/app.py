import streamlit as st
import pulp
import pandas as pd

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Production Capacity Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Theme-Agnostic styling for dark and light modes
st.markdown("""
<style>
    .stMetric { 
        background-color: rgba(255, 255, 255, 0.05); 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Production Planning & Capacity Optimizer")
st.markdown("Adjust parameters on the sidebar, then click the **Run Optimization** button to evaluate optimal shift distributions, production numbers, and inventory levels.")

# -----------------------------
# Sidebar Parameters
# -----------------------------
st.sidebar.header("💰 Cost Configurations (£)")
normal_cost = st.sidebar.number_input("Normal Shift Cost", value=100000, step=5000)
extended_cost = st.sidebar.number_input("Extended Shift Cost", value=180000, step=5000)
holding_cost = st.sidebar.number_input("Holding Cost (per unit/month)", value=2.0, step=0.5)
switch_cost = st.sidebar.number_input("Shift Switch Cost", value=15000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("📦 Capacities & Baseline")
normal_capacity = st.sidebar.number_input("Normal Capacity Limit", value=5000, step=500)
extended_capacity = st.sidebar.number_input("Extended Capacity Limit", value=7500, step=500)
minimum_production = st.sidebar.number_input("Minimum Production Target", value=2000, step=100)
initial_inventory = st.sidebar.number_input("Initial Inventory Level", value=3000, step=500)
final_inventory = st.sidebar.number_input("Required Final Inventory", value=2000, step=500)

st.sidebar.markdown("---")
st.sidebar.header("📊 Monthly Market Demand")
months = range(6)
demand = []
cols = st.sidebar.columns(2)
default_demands = [6000, 6500, 7500, 7000, 6000, 6000]
for t in months:
    with cols[t % 2]:
        d = st.number_input(f"Month {t+1} Demand", value=default_demands[t], min_value=0)
        demand.append(d)

# -----------------------------
# Optimization Model Function
# -----------------------------
def run_optimization():
    model = pulp.LpProblem("Production_Planning", pulp.LpMinimize)
    
    P = pulp.LpVariable.dicts("Production", months, lowBound=0)
    I = pulp.LpVariable.dicts("Inventory", months, lowBound=1)
    N = pulp.LpVariable.dicts("Normal", months, cat=pulp.LpBinary)
    E = pulp.LpVariable.dicts("Extended", months, cat=pulp.LpBinary)
    S = pulp.LpVariable.dicts("Switch", months, cat=pulp.LpBinary)
    
    # Objective: Updated to include all months in the switch cost sum
    model += (
        pulp.lpSum(normal_cost * N[t] + extended_cost * E[t] + holding_cost * I[t] for t in months)
        + switch_cost * pulp.lpSum(S[t] for t in months)
    )
    
    # Inventory Balance
    model += I[0] == initial_inventory + P[0] - demand[0]
    for t in range(1, 6):
        model += I[t] == I[t-1] + P[t] - demand[t]
        
    # Boundary Conditions
    model += I[5] >= final_inventory
    
    for t in months:
        model += N[t] + E[t] <= 1
        model += P[t] <= normal_capacity * N[t] + extended_capacity * E[t]
        model += P[t] >= minimum_production * (N[t] + E[t])
        
    for t in range(1, 6):
        model += S[t] >= N[t-1] + E[t] - 1
    model += S[0] >= E[0]
    
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return model, P, I, N, E, S

# -----------------------------
# Execution & Display Results
# -----------------------------
if st.button("🚀 Run Optimization", type="primary"):
    model, P, I, N, E, S = run_optimization()
    status_str = pulp.LpStatus[model.status]

    if status_str == "Optimal":
        st.success("Optimal Solution Found!")
        
        # 1. KPI Metric Highlight Display
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Total Minimum Cost", f"£{pulp.value(model.objective):,.2f}")
        with m_col2:
            total_prod = sum(pulp.value(P[t]) for t in months)
            st.metric("Total Production Units", f"{int(total_prod):,}")
        with m_col3:
            total_holding_cost = sum(pulp.value(I[t]) * holding_cost for t in months)
            st.metric("Total Holding Costs", f"£{total_holding_cost:,.2f}")
        with m_col4:
            total_switches = sum(pulp.value(S[t]) for t in months)
            st.metric("Shift Switch Triggers", f"{int(total_switches)}")

        # 2. Extract Data for Visualization
        months_labels = [f"Month {t+1}" for t in months]
        prod_vals = [pulp.value(P[t]) for t in months]
        inv_vals = [pulp.value(I[t]) for t in months]
        
        shift_types = []
        for t in months:
            if pulp.value(N[t]) == 1: shift_types.append("Normal")
            elif pulp.value(E[t]) == 1: shift_types.append("Extended")
            else: shift_types.append("No Shift")
            
        df_chart = pd.DataFrame({
            "Month": months_labels,
            "Demand": demand,
            "Production": prod_vals,
            "Inventory": inv_vals,
            "Shift Active": shift_types
        })

        # 3. Charts Section
        st.markdown("### 📊 Operational Dashboards")
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            st.markdown("**Production Volume vs. Customer Demand**")
            st.bar_chart(df_chart.set_index("Month")[["Production", "Demand"]], color=["#1f77b4", "#ff7f0e"])
            
        with c_col2:
            st.markdown("**Ending Inventory Track**")
            st.line_chart(df_chart.set_index("Month")["Inventory"], color="#2ca02c")

        # 4. Data Frame and Shifts Allocation
        st.markdown("### 📋 Schedule & Shifts Summary")
        
        df_display = df_chart.copy()
        df_display["Switch Triggered"] = ["Yes" if pulp.value(S[t]) == 1 else "No" for t in months]
        
        # Formatting values for user presentation
        df_display["Demand"] = df_display["Demand"].map('{:,}'.format)
        df_display["Production"] = df_display["Production"].astype(int).map('{:,}'.format)
        df_display["Inventory"] = df_display["Inventory"].astype(int).map('{:,}'.format)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    else:
        st.error(f"⚠️ Solver failed to reach an optimal layout. Status Code: {status_str}")
        
else:
    st.info("👈 Adjust your variables inside the sidebar and click **'Run Optimization'** to solve.")
