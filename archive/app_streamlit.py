"""
FinTwin — MSME Financial Stress Simulator
Streamlit Application (Tasks 8 + 11).

Full pipeline: CSV → Metrics → Health Score → Simulation → LLM → UI
"""

import io
import time

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.csv_parser import parse_csv, CSVValidationError
from src.metrics_engine import compute_metrics
from src.health_score import calculate_health_score
from src.shock_models import ALL_SHOCKS
from src.simulation_engine import run_all_simulations
from src.llm_prompts import generate_mock_risks, generate_mock_roadmap
from src.synthetic_data import generate_synthetic_msme_data


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FinTwin — MSME Stress Simulator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.85;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #30475e;
    }
    .metric-card h3 {
        color: #e0e0e0;
        font-size: 0.85rem;
        margin-bottom: 0.3rem;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #00d4ff;
    }
    .grade-excellent { color: #00e676; }
    .grade-good { color: #69f0ae; }
    .grade-fair { color: #ffd740; }
    .grade-poor { color: #ff6e40; }
    .grade-critical { color: #ff1744; }
    .risk-card {
        background: #1a1a2e;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 4px solid;
    }
    .risk-critical { border-color: #ff1744; }
    .risk-high { border-color: #ff6e40; }
    .risk-medium { border-color: #ffd740; }
    .risk-low { border-color: #69f0ae; }
    .action-card {
        background: #16213e;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.6rem;
        border-left: 4px solid #00d4ff;
    }
    .stApp {
        background-color: #0a0a1a;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="main-header">
    <h1>🏦 FinTwin</h1>
    <p>MSME Financial Stress Simulator — 30-Second Survival Analysis</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 📁 Data Source")

    data_source = st.radio(
        "Choose input method:",
        ["Upload CSV", "Generate Synthetic Data"],
        index=0,
    )

    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload your MSME financial CSV",
            type=["csv"],
            help="CSV must contain: month, revenue, fixed_costs, variable_costs, loan_emi, cash_reserve",
        )
    else:
        st.markdown("#### Synthetic Data Settings")
        biz_type = st.selectbox(
            "Business Type",
            ["stable", "growing", "struggling", "seasonal"],
            index=0,
        )
        n_months = st.slider("Months of Data", 6, 24, 12)
        base_rev = st.number_input("Base Monthly Revenue (₹)", value=500000, step=50000)
        synth_seed = st.number_input("Random Seed", value=42, step=1)
        uploaded_file = None

    st.markdown("---")
    st.markdown("### ⚙️ Simulation Settings")
    n_sims = st.slider("Monte Carlo Iterations", 100, 5000, 1000, step=100)
    noise_level = st.slider("Market Noise (%)", 1, 20, 5) / 100.0

    st.markdown("---")
    st.markdown("### 📋 CSV Schema")
    st.code("month, revenue, fixed_costs,\nvariable_costs, loan_emi,\ncash_reserve", language="text")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(df: pd.DataFrame, n_sims: int, noise: float):
    """Execute the full pipeline and return results dict."""
    start_time = time.time()

    # Step 1: Compute metrics
    metrics = compute_metrics(df)

    # Step 2: Health score
    health = calculate_health_score(metrics)

    # Step 3: Run all simulations
    sim_results = run_all_simulations(
        metrics=metrics,
        n_simulations=n_sims,
        noise_std=noise,
        seed=42,
    )

    # Step 4: Generate risk analysis (mock — swap for real LLM later)
    risks = generate_mock_risks(metrics, sim_results)

    # Step 5: Generate roadmap (mock — swap for real LLM later)
    roadmap = generate_mock_roadmap(metrics, sim_results, risks)

    elapsed = time.time() - start_time

    return {
        "metrics": metrics,
        "health": health,
        "simulations": sim_results,
        "risks": risks,
        "roadmap": roadmap,
        "elapsed_seconds": round(elapsed, 2),
    }


def render_health_gauge(score: float, grade: str):
    """Render a gauge visualization for health score."""
    color_map = {
        "Excellent": "#00e676",
        "Good": "#69f0ae",
        "Fair": "#ffd740",
        "Poor": "#ff6e40",
        "Critical": "#ff1744",
    }
    color = color_map.get(grade, "#ffffff")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"Health Score — {grade}", "font": {"size": 20, "color": "white"}},
        number={"font": {"size": 48, "color": color}},
        gauge={
            "axis": {"range": [1, 10], "tickwidth": 2, "tickcolor": "white"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#1a1a2e",
            "borderwidth": 2,
            "bordercolor": "#30475e",
            "steps": [
                {"range": [1, 3], "color": "rgba(255,23,68,0.15)"},
                {"range": [3, 5], "color": "rgba(255,110,64,0.15)"},
                {"range": [5, 7], "color": "rgba(255,215,64,0.15)"},
                {"range": [7, 8.5], "color": "rgba(105,240,174,0.15)"},
                {"range": [8.5, 10], "color": "rgba(0,230,118,0.15)"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=280,
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig


def render_survival_chart(sim_results: list):
    """Render horizontal bar chart of survival probabilities."""
    names = [r["shock_name"] for r in sim_results]
    probs = [r["survival_percentage"] for r in sim_results]

    colors = []
    for p in probs:
        if p >= 80:
            colors.append("#00e676")
        elif p >= 60:
            colors.append("#69f0ae")
        elif p >= 40:
            colors.append("#ffd740")
        elif p >= 20:
            colors.append("#ff6e40")
        else:
            colors.append("#ff1744")

    fig = go.Figure(go.Bar(
        x=probs,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{p:.0f}%" for p in probs],
        textposition="outside",
        textfont={"color": "white", "size": 13},
    ))
    fig.update_layout(
        title={"text": "Survival Probability by Shock Scenario", "font": {"color": "white", "size": 18}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        xaxis={"title": "Survival %", "range": [0, 110], "gridcolor": "#30475e"},
        yaxis={"autorange": "reversed", "gridcolor": "#30475e"},
        height=380,
        margin=dict(l=10, r=10, t=50, b=40),
    )
    return fig


def render_profit_chart(metrics: dict):
    """Render monthly profit trend."""
    enriched = metrics["raw_df"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=enriched["month"],
        y=enriched["monthly_profit"],
        marker_color=["#00e676" if p >= 0 else "#ff1744" for p in enriched["monthly_profit"]],
        name="Monthly Profit",
    ))
    fig.add_trace(go.Scatter(
        x=enriched["month"],
        y=enriched["revenue"],
        mode="lines+markers",
        name="Revenue",
        line={"color": "#00d4ff", "width": 2},
    ))
    fig.update_layout(
        title={"text": "Revenue & Profit Trend", "font": {"color": "white", "size": 18}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        xaxis={"gridcolor": "#30475e"},
        yaxis={"title": "₹ (INR)", "gridcolor": "#30475e"},
        height=350,
        margin=dict(l=10, r=10, t=50, b=40),
        legend={"bgcolor": "rgba(0,0,0,0)"},
    )
    return fig


# ---------------------------------------------------------------------------
# Main Content
# ---------------------------------------------------------------------------

df = None

# Handle data input
if data_source == "Upload CSV" and uploaded_file is not None:
    try:
        df = parse_csv(uploaded_file)
        st.success(f"✅ CSV loaded: {len(df)} months of data")
    except CSVValidationError as e:
        st.error(f"❌ CSV Validation Error:\n{e}")
elif data_source == "Generate Synthetic Data":
    df = generate_synthetic_msme_data(
        n_months=n_months,
        base_revenue=base_rev,
        seed=synth_seed,
        business_type=biz_type,
    )
    st.info(f"🔧 Generated synthetic {biz_type} business data — {len(df)} months")

if df is not None:
    # Show data preview
    with st.expander("📊 Raw Data Preview", expanded=False):
        st.dataframe(df, width='stretch')

    # Run pipeline
    with st.spinner("🔄 Running stress simulation..."):
        results = run_pipeline(df, n_sims, noise_level)

    st.success(f"⚡ Analysis complete in {results['elapsed_seconds']}s")

    # ── Row 1: Key Metrics ──
    st.markdown("## 📈 Financial Overview")
    m = results["metrics"]
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Avg Revenue", f"₹{m['avg_revenue']:,.0f}")
    with c2:
        st.metric("Avg Profit", f"₹{m['avg_monthly_profit']:,.0f}")
    with c3:
        st.metric("Profit Margin", f"{m['avg_profit_margin']:.1%}")
    with c4:
        st.metric("Cash Reserve", f"₹{m['latest_cash_reserve']:,.0f}")
    with c5:
        st.metric("Revenue Volatility", f"{m['revenue_volatility']:.1%}")

    # ── Row 2: Health Gauge + Profit Chart ──
    col_gauge, col_chart = st.columns([1, 2])
    with col_gauge:
        fig_gauge = render_health_gauge(
            results["health"]["health_score"],
            results["health"]["grade"],
        )
        st.plotly_chart(fig_gauge, width='stretch')
        st.markdown(f"*{results['health']['interpretation']}*")

        # Component breakdown
        st.markdown("**Score Breakdown:**")
        for comp, score in results["health"]["component_scores"].items():
            label = comp.replace("_", " ").title()
            st.progress(score / 3.0 if "margin" in comp else score / 2.0, text=f"{label}: {score}")

    with col_chart:
        st.plotly_chart(render_profit_chart(m), width='stretch')

    # ── Row 3: Survival Chart ──
    st.markdown("## 🛡️ Stress Test Results")
    st.plotly_chart(render_survival_chart(results["simulations"]), width='stretch')

    # Detailed simulation table
    with st.expander("📋 Detailed Simulation Results"):
        sim_df = pd.DataFrame([
            {
                "Shock": r["shock_name"],
                "Survival %": f"{r['survival_percentage']:.1f}%",
                "Survived": r["survived_count"],
                "Failed": r["failed_count"],
                "Avg Months Survived": r["avg_months_survived"],
            }
            for r in results["simulations"]
        ])
        st.dataframe(sim_df, width='stretch')

    # ── Row 4: Risk Analysis ──
    st.markdown("## ⚠️ Top Risks")
    for risk in results["risks"]:
        severity = risk["severity"].lower()
        color_map = {"critical": "#ff1744", "high": "#ff6e40", "medium": "#ffd740", "low": "#69f0ae"}
        border_color = color_map.get(severity, "#ffffff")

        st.markdown(f"""
        <div style="background: #1a1a2e; padding: 1rem; border-radius: 8px;
                    margin-bottom: 0.8rem; border-left: 4px solid {border_color};">
            <strong style="color: {border_color};">[{risk['severity']}]</strong>
            <strong style="color: white;"> {risk['risk_name']}</strong><br>
            <span style="color: #b0bec5;">{risk['explanation']}</span><br>
            <small style="color: #78909c;">Evidence: {risk['evidence']}</small>
        </div>
        """, unsafe_allow_html=True)

    # ── Row 5: Action Roadmap ──
    st.markdown("## 🗺️ Financial Roadmap")
    for action in results["roadmap"]:
        st.markdown(f"""
        <div style="background: #16213e; padding: 1rem; border-radius: 8px;
                    margin-bottom: 0.6rem; border-left: 4px solid #00d4ff;">
            <strong style="color: #00d4ff;">Priority {action['priority']}</strong>
            <span style="color: #78909c; float: right;">{action['category']} · {action['timeline']}</span><br>
            <span style="color: white;">{action['action']}</span><br>
            <small style="color: #69f0ae;">Impact: {action['impact']}</small>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #78909c;'>"
        f"FinTwin v1.0 · {n_sims} simulations · {noise_level:.0%} noise · "
        f"Completed in {results['elapsed_seconds']}s</p>",
        unsafe_allow_html=True,
    )

else:
    # Landing state
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #78909c;">
        <h2>👈 Upload a CSV or generate synthetic data to begin</h2>
        <p>FinTwin will analyze your MSME's financial health across 7 India-specific shock scenarios
        using Monte Carlo simulation.</p>
    </div>
    """, unsafe_allow_html=True)
