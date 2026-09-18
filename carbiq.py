import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pulp

st.set_page_config(
    page_title="CarbIQ | Industrial Carbon Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Dark Theme CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.2rem;
        background: #111827;
        border-radius: 10px;
        border: 1px solid #1f2937;
        margin-bottom: 1.5rem;
    }
    .top-bar h2 { margin: 0; font-size: 1.35rem; color: #f9fafb; font-weight: 600; }
    .badge {
        background: #064e3b;
        color: #34d399;
        font-size: 0.8rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
    }
    .section-label {
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        margin-bottom: 0.75rem;
    }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 12px 16px;
    }
    div[data-testid="stMetricLabel"] p { font-size: 0.8rem !important; color: #9ca3af !important; }
    div[data-testid="stMetricValue"] div { font-size: 1.35rem !important; font-weight: 700 !important; }
</style>
<div class="top-bar">
    <div>
        <h2>CarbIQ Industrial Carbon Intelligence</h2>
        <span style="color: #6b7280; font-size: 0.85rem;">Budget-Constrained Decarbonization Knapsack Solver</span>
    </div>
    <div class="badge">● SENSORS ONLINE</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.markdown("### Operational Controls")
budget = st.sidebar.slider("Sustainability Budget (INR)", min_value=50000, max_value=800000, value=350000, step=25000)
internal_carbon_tax = st.sidebar.number_input("Internal Carbon Fee (INR/tCO2e)", value=2500, step=250)

st.sidebar.markdown("---")
st.sidebar.markdown("### CEMS Sensor Simulation")
flue_stack_ppm = st.sidebar.slider("Chimney CO2 Telemetry (PPM)", min_value=400, max_value=2000, value=1450, step=25)
stack_ppm_limit = st.sidebar.number_input("Regulatory Safety Limit (PPM)", value=1250, step=50)

st.sidebar.caption("TEAM_80 | Prescriptive Decarbonization Engine")

# Continuous Stack Telemetry Alert
if flue_stack_ppm > stack_ppm_limit:
    st.error(f"🚨 **CEMS Regulatory Alert**: Chimney concentration at **{flue_stack_ppm} PPM** exceeds threshold of **{stack_ppm_limit} PPM**! Fuel/air adjustment needed.")
else:
    st.success(f"✅ **Continuous Sensor Normal**: Chimney concentration at **{flue_stack_ppm} PPM** is within regulatory limits.")

# Operational Streams
st.markdown('<div class="section-label">Real-Time Operational Emission Streams</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Chimney CO2", f"{flue_stack_ppm} PPM", delta=f"{flue_stack_ppm - stack_ppm_limit:+d} PPM", delta_color="inverse")
c2.metric("Electricity (Scope 2)", "1.03 tCO2e", delta="1,256 kWh", delta_color="off")
c3.metric("Boiler Fuel (Scope 1)", "1.10 tCO2e", delta="410 L", delta_color="off")
c4.metric("Logistics (Scope 3)", "0.20 tCO2e", delta="1,364 km", delta_color="off")
c5.metric("Solid Waste (Scope 3)", "0.10 tCO2e", delta="221 kg", delta_color="off")

st.write("")

# Optimization Core: 0/1 Knapsack MILP Formulation
candidate_projects = [
    {"Name": "Air-to-Fuel Ratio Controller", "Source": "Boilers (Scope 1)", "Cost": 80000, "Reduction": 18, "Savings": 45000},
    {"Name": "Boiler Burner Retrofit", "Source": "Boilers (Scope 1)", "Cost": 60000, "Reduction": 14, "Savings": 35000},
    {"Name": "Fleet Route Optimization", "Source": "Logistics (Scope 3)", "Cost": 45000, "Reduction": 12, "Savings": 28000},
    {"Name": "Onsite Composting Unit", "Source": "Waste (Scope 3)", "Cost": 30000, "Reduction": 6, "Savings": 12000},
    {"Name": "Variable Frequency Drives", "Source": "Electricity (Scope 2)", "Cost": 110000, "Reduction": 22, "Savings": 72000},
    {"Name": "Waste Heat Recovery (WHR)", "Source": "Boilers (Scope 1)", "Cost": 150000, "Reduction": 34, "Savings": 95000},
    {"Name": "LED Overhaul & Sensors", "Source": "Electricity (Scope 2)", "Cost": 25000, "Reduction": 5, "Savings": 18000},
]
df = pd.DataFrame(candidate_projects)

prob = pulp.LpProblem("CarbIQ_Solver", pulp.LpMaximize)
n = len(df)
x = [pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary) for i in range(n)]

# Objective: Maximize CO2 Abatement
prob += pulp.lpSum([df.loc[i, "Reduction"] * x[i] for i in range(n)])

# Constraint: CapEx <= Budget
prob += pulp.lpSum([df.loc[i, "Cost"] * x[i] for i in range(n)]) <= budget
prob.solve(pulp.PULP_CBC_CMD(msg=0))

df["Funded"] = [bool(x[i].varValue == 1.0) for i in range(n)]
df["CostPerTon"] = (df["Cost"] / df["Reduction"]).round(2)
df["Payback"] = (df["Cost"] / df["Savings"]).round(1)
df = df.sort_values(by="CostPerTon").reset_index(drop=True)

allocated_capex = df.loc[df["Funded"], "Cost"].sum()
total_abatement = df.loc[df["Funded"], "Reduction"].sum()
remaining_budget = budget - allocated_capex
fee_savings = total_abatement * internal_carbon_tax
budget_utilization = (allocated_capex / budget) * 100 if budget > 0 else 0

# Prescriptive Results
st.markdown('<div class="section-label">Prescriptive Decarbonization Strategy</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Available Budget", f"INR {budget:,.0f}")
k2.metric("Optimal CapEx Allocated", f"INR {allocated_capex:,.0f}", delta=f"INR {remaining_budget:,.0f} Unused", delta_color="normal")
k3.metric("Projected Total CO2 Cut", f"{total_abatement} Tons/yr")
k4.metric("Annual Fee Savings", f"INR {fee_savings:,.0f}", delta=f"@{internal_carbon_tax}/t")
k5.metric("Budget Utilization", f"{budget_utilization:.1f}%")

# Clean Formatted Strategy Table
table_df = pd.DataFrame({
    "Status": df["Funded"].apply(lambda f: "✅ FUNDED" if f else "❌ UNFUNDED"),
    "Intervention": df["Name"],
    "Operational Stream": df["Source"],
    "CapEx (INR)": df["Cost"].apply(lambda v: f"{v:,.0f}"),
    "Cut (Tons)": df["Reduction"],
    "Marginal Cost (INR/t)": df["CostPerTon"].apply(lambda v: f"{v:,.2f}"),
    "Payback": df["Payback"].apply(lambda v: f"{v:.1f} yrs")
})

st.dataframe(
    table_df.style.applymap(
        lambda val: "background-color: rgba(34, 197, 94, 0.15); color: #4ade80; font-weight: 600;" if "FUNDED" in str(val)
        else ("background-color: rgba(239, 68, 68, 0.15); color: #f87171;" if "UNFUNDED" in str(val) else ""),
        subset=["Status"]
    ),
    hide_index=True,
    use_container_width=True
)

st.write("")

# MACC & Donut Visualizations
st.markdown('<div class="section-label">MACC Optimization Curve & Scope Breakdown</div>', unsafe_allow_html=True)
v1, v2 = st.columns([2, 1])

with v1:
    df["Width"] = df["Reduction"]
    df["X_Center"] = df["Width"].cumsum() - (df["Width"] / 2)

    fig_macc = go.Figure()
    funded_mask = df["Funded"] == True
    if funded_mask.any():
        fig_macc.add_trace(go.Bar(
            name="Funded",
            x=df.loc[funded_mask, "X_Center"],
            y=df.loc[funded_mask, "CostPerTon"],
            width=df.loc[funded_mask, "Width"],
            customdata=df.loc[funded_mask, ["Name", "Cost", "Reduction"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Marginal Cost: INR %{y:,.2f}/t<br>Abatement: %{customdata[2]} t<extra></extra>",
            marker_color="#10b981"
        ))

    unfunded_mask = ~funded_mask
    if unfunded_mask.any():
        fig_macc.add_trace(go.Bar(
            name="Unfunded",
            x=df.loc[unfunded_mask, "X_Center"],
            y=df.loc[unfunded_mask, "CostPerTon"],
            width=df.loc[unfunded_mask, "Width"],
            customdata=df.loc[unfunded_mask, ["Name", "Cost", "Reduction"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Marginal Cost: INR %{y:,.2f}/t<br>Abatement: %{customdata[2]} t<extra></extra>",
            marker_color="#ef4444"
        ))

    fig_macc.add_hline(
        y=internal_carbon_tax,
        line_dash="dot",
        line_color="#38bdf8",
        annotation_text=f"Internal Tax: INR {internal_carbon_tax}/t",
        annotation_position="bottom right"
    )

    fig_macc.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=20, b=30),
        xaxis_title="Cumulative Abatement (Tons CO2e)",
        yaxis_title="Marginal Cost (INR / tCO2e)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_macc, use_container_width=True)

with v2:
    footprint_df = pd.DataFrame({
        "Scope": ["Scope 1 (Boilers)", "Scope 2 (Grid)", "Scope 3 (Logistics)", "Scope 3 (Waste)"],
        "Emissions": [1.10, 1.03, 0.20, 0.10]
    })
    fig_donut = px.pie(
        footprint_df,
        values="Emissions",
        names="Scope",
        hole=0.65,
        color_discrete_sequence=["#38bdf8", "#818cf8", "#f472b6", "#fbbf24"]
    )
    fig_donut.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=20, b=30),
        showlegend=False
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

# Export Section
exp1, exp2 = st.columns([3, 1])
with exp1:
    st.caption("Optimized deterministically via Mixed-Integer Linear Programming (PuLP Branch & Bound). Compliant with GHG Protocol Scopes 1–3.")
with exp2:
    st.download_button(
        label="📥 Export Plan (CSV)",
        data=table_df.to_csv(index=False).encode('utf-8'),
        file_name="CarbIQ_Allocations.csv",
        mime="text/csv",
        use_container_width=True
    )