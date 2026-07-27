import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Multi-Counter Queue Simulator",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛒 Multi-Counter Queueing System Simulation")
st.markdown("Simulate customer inter-arrival and service dynamics for single or multi-counter configurations.")

# -----------------------------
# Sidebar: Parameters & Settings
# -----------------------------
st.sidebar.header("⚙️ Simulation Settings")

num_counters = st.sidebar.number_input(
    "Number of Counters (Servers)", min_value=1, max_value=10, value=1, step=1
)

num_customers = st.sidebar.number_input(
    "Number of Customers", min_value=1, max_value=1000, value=10, step=1
)

use_preset_randoms = st.sidebar.checkbox(
    "Use Slide's Preset Random Numbers (10 Customers)", value=True
)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Inter-Arrival Distribution (1-8 mins)")
st.sidebar.caption("Uniform probability across integers 1 to 8 minutes (12.5% each).")

# Service Time Distribution Parameters
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Service Time Distribution")
st.sidebar.caption("Probabilities for 1 to 6 minutes of service time:")

s_probs = []
s_defaults = [0.10, 0.20, 0.30, 0.25, 0.10, 0.05]
for i in range(1, 7):
    p = st.sidebar.number_input(f"P(Service = {i} min)", value=s_defaults[i-1], step=0.05, min_value=0.0, max_value=1.0)
    s_probs.append(p)

# Normalize probabilities if they don't sum to 1
total_p = sum(s_probs)
if not np.isclose(total_p, 1.0):
    st.sidebar.warning(f"⚠️ Service probabilities sum to {total_p:.2f}. Auto-normalizing...")
    s_probs = [p / total_p for p in s_probs]

# Cumulative distribution for Service Times
service_cum_probs = np.cumsum(s_probs)

# -----------------------------
# Mapping Helper Functions
# -----------------------------
def get_interarrival_time(r_val):
    """Uniform mapping across 1 to 8 minutes: [0, 0.125) -> 1, [0.125, 0.250) -> 2, etc."""
    return int(np.ceil(r_val * 8)) if r_val < 1.0 else 8

def get_service_time(r_val):
    """Monte Carlo CDF mapping for service times 1-6 minutes."""
    for idx, cum_p in enumerate(service_cum_probs):
        if r_val <= cum_p:
            return idx + 1
    return 6

# -----------------------------
# Preset Random Numbers from Slide
# -----------------------------
slide_arr_rands = [0.018, 0.268, 0.051, 0.729, 0.822, 0.050, 0.710, 0.171, 0.844, 0.160]
slide_ser_rands = [0.217, 0.826, 0.311, 0.688, 0.401, 0.276, 0.817, 0.671, 0.283, 0.036]

# Prepare Random Numbers
if use_preset_randoms and num_customers <= 10:
    arr_rands = slide_arr_rands[:num_customers]
    ser_rands = slide_ser_rands[:num_customers]
else:
    np.random.seed(42)  # Seed for reproducibility when generating random runs
    arr_rands = np.random.uniform(0, 1, num_customers).tolist()
    ser_rands = np.random.uniform(0, 1, num_customers).tolist()

# -----------------------------
# Discrete Event Simulation Logic
# -----------------------------
def run_simulation():
    records = []
    counter_available_time = [0] * num_counters  # Track free time for each counter
    
    clock_arrival = 0

    for idx in range(num_customers):
        r_arr = arr_rands[idx]
        r_ser = ser_rands[idx]

        # Customer 1 arrives at t = 0
        if idx == 0:
            inter_time = 0
        else:
            inter_time = get_interarrival_time(r_arr)
        
        clock_arrival += inter_time
        service_time = get_service_time(r_ser)

        # Multi-counter allocation: Assign customer to the earliest available counter
        assigned_counter = int(np.argmin(counter_available_time))
        earliest_start = counter_available_time[assigned_counter]

        service_start = max(clock_arrival, earliest_start)
        wait_time = service_start - clock_arrival
        service_end = service_start + service_time
        time_in_system = wait_time + service_time

        # Update availability of assigned counter
        counter_available_time[assigned_counter] = service_end

        records.append({
            "Customer": idx + 1,
            "Arrival Rand": round(r_arr, 3),
            "Inter-Arrival": inter_time,
            "Arrival Time": clock_arrival,
            "Service Rand": round(r_ser, 3),
            "Service Time": service_time,
            "Assigned Counter": f"Counter {assigned_counter + 1}",
            "Service Start": service_start,
            "Wait Time": wait_time,
            "Service End": service_end,
            "System Time": time_in_system
        })

    return pd.DataFrame(records)

# -----------------------------
# Execution & UI Display
# -----------------------------
if st.button("🚀 Run Simulation", type="primary"):
    df_results = run_simulation()

    # KPI Metrics Highlights
    avg_wait = df_results["Wait Time"].mean()
    avg_service = df_results["Service Time"].mean()
    max_wait = df_results["Wait Time"].max()
    utilization = (df_results["Service Time"].sum() / (df_results["Service End"].max() * num_counters)) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Wait Time", f"{avg_wait:.2f} mins")
    col2.metric("Average Service Time", f"{avg_service:.2f} mins")
    col3.metric("Max Wait Time", f"{max_wait} mins")
    col4.metric("Counter Utilization", f"{utilization:.1f}%")

    st.markdown("---")
    st.markdown("### 📋 Complete Customer Event Log")
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    st.markdown("### 📊 Queue Visualizations")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Customer Wait Time Breakdown**")
        st.bar_chart(df_results.set_index("Customer")["Wait Time"], color="#ff4b4b")
    with c2:
        st.markdown("**Service Time per Customer**")
        st.bar_chart(df_results.set_index("Customer")["Service Time"], color="#1f77b4")

else:
    st.info("👈 Set your parameters on the left sidebar and click **'Run Simulation'**.")
