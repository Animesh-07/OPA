# 🛒 Multi-Counter Queueing System Simulator

An interactive Discrete Event Simulation (DES) Decision Support System built with **Streamlit**, **Pandas**, and **NumPy**. This application simulates customer inter-arrival and service dynamics for single- or multi-counter retail environments using Monte Carlo Cumulative Distribution Function (CDF) mapping.

👉 **Live Application:** [https://opa-planning.streamlit.app/](https://opa-planning.streamlit.app/)

---

## 📌 Features

- **Multi-Counter Scheduling (`M/M/c` Queueing Model):** Dynamically routes incoming customers across 1 to 10 checkout servers, assigning arriving customers to the earliest available counter.
- **Dual Randomness Modes:**
  - **Slide Preset Mode:** Replicates exact historical random number sequences for deterministic testing and benchmark verification.
  - **Dynamic Monte Carlo Mode:** Generates uniform random distributions across scalable customer volumes (1 to 1,000 customers).
- **Fully Parameterized Distributions:**
  - **Inter-arrival Times:** Discrete uniform distribution across 1–8 minutes.
  - **Service Times:** Customizable probability mass functions across 1–6 minutes.
- **Operational Metrics & Dashboards:** Real-time tracking of:
  - Average & Maximum Customer Wait Times
  - Average Service Duration
  - Counter Utilization Rates
  - Individual Customer Event Logs & Visual Analytics

---

## 📁 Repository Structure

```text
├── app.py              # Main Streamlit application containing simulation logic
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
