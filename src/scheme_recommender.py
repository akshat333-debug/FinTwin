"""
Government Scheme Recommender for Indian MSMEs.
Rule-based matching of financial health indicators to eligible government schemes.
"""

from __future__ import annotations
from typing import Any


# ── Scheme Database ──────────────────────────────────────────────────────────

import json
import os

def load_schemes() -> list[dict[str, Any]]:
    """Load government schemes from JSON configuration."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

SCHEMES = load_schemes()


# ── Recommendation Engine ────────────────────────────────────────────────────

def recommend_schemes(
    metrics: dict[str, Any],
    health: dict[str, Any],
    sim_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Recommend government schemes based on financial health indicators.
    Returns a scored + sorted list of scheme recommendations.
    """
    score = health["health_score"]
    grade = health["grade"]
    avg_revenue = metrics.get("avg_revenue", 0)
    avg_profit = metrics.get("avg_monthly_profit", 0)
    cash = metrics.get("latest_cash_reserve", 0)
    burn = metrics.get("burn_rate", 0)
    margin = metrics.get("avg_profit_margin", 0)

    # Calculate cash runway months
    if burn > 0:
        runway_months = cash / burn
    else:
        runway_months = 12  # Profitable, no burn

    # Average survival across all shocks
    avg_survival = sum(s["survival_percentage"] for s in sim_results) / max(len(sim_results), 1)

    recommendations = []

    for scheme in SCHEMES:
        relevance = 0
        reason = ""
        sid = scheme["id"]

        # ── Emergency / Critical health ──
        if sid == "eclgs":
            if score <= 5 or avg_survival < 50:
                relevance = 95
                reason = f"Health score {score}/10 and {avg_survival:.0f}% avg survival — emergency credit line strongly recommended"
            elif score <= 7:
                relevance = 40
                reason = "Moderate stress — emergency credit as precautionary buffer"

        elif sid == "champions":
            if score <= 4:
                relevance = 90
                reason = f"Critical health score ({score}/10) qualifies for MSME revival support"
            elif score <= 6 and avg_survival < 40:
                relevance = 60
                reason = "Below-average health with low survival probability"

        # ── Cash flow / Working capital ──
        elif sid == "trade_receivables":
            if runway_months < 4:
                relevance = 85
                reason = f"Only {runway_months:.1f} months cash runway — TReDS can accelerate receivables"
            elif runway_months < 6:
                relevance = 55
                reason = "Limited cash runway, receivables financing can help"

        elif sid == "nsic_raw_material":
            if margin < 0.15 and avg_revenue > 100000:
                relevance = 70
                reason = f"Thin margins ({margin:.0%}) — raw material assistance can reduce COGS"
            elif margin < 0.25:
                relevance = 35
                reason = "Moderate margins, raw material support beneficial"

        # ── Credit access (Mudra) ──
        elif sid == "mudra_shishu":
            if avg_revenue < 200000:
                relevance = 80
                reason = f"Revenue ₹{avg_revenue/1000:.0f}K/month fits Shishu micro-loan profile"
            elif avg_revenue < 500000:
                relevance = 30
                reason = "Could use Shishu for supplementary working capital"

        elif sid == "mudra_kishore":
            if 200000 <= avg_revenue <= 1000000 and score >= 5:
                relevance = 75
                reason = f"Revenue ₹{avg_revenue/100000:.1f}L qualifies for Kishore growth financing"
            elif avg_revenue <= 500000:
                relevance = 25
                reason = "May qualify for Kishore with growth plan"

        elif sid == "mudra_tarun":
            if avg_revenue > 1000000 and score >= 6:
                relevance = 70
                reason = f"Strong revenue ₹{avg_revenue/100000:.1f}L — Tarun loan for scaling"
            elif avg_revenue > 500000:
                relevance = 30
                reason = "Approaching Tarun eligibility"

        # ── Credit guarantee ──
        elif sid == "cgtmse":
            if score >= 4 and avg_revenue > 100000:
                relevance = 65
                reason = "CGTMSE eliminates collateral requirement for bank loans"
                if score <= 6:
                    relevance = 80
                    reason += f" — especially important at health score {score}/10"

        # ── Growth & quality ──
        elif sid == "stand_up_india":
            if avg_revenue < 500000:
                relevance = 50
                reason = "Suitable for SC/ST/Women entrepreneurs starting greenfield units"

        elif sid == "clcss":
            if score >= 6 and avg_revenue > 300000:
                relevance = 55
                reason = "Healthy business can leverage 15% tech upgrade subsidy"

        elif sid == "pmegp":
            if avg_revenue < 300000:
                relevance = 60
                reason = f"Revenue ₹{avg_revenue/1000:.0f}K — margin money subsidy for growth"

        elif sid == "zed_certification":
            if score >= 7:
                relevance = 45
                reason = "Strong health — ZED certification adds credibility + quality improvement"

        # Only include schemes with relevance > 20
        if relevance > 20:
            recommendations.append({
                **scheme,
                "relevance_score": relevance,
                "reason": reason,
                "urgency": "Critical" if relevance >= 85 else "High" if relevance >= 65 else "Medium" if relevance >= 45 else "Low",
            })

    # Sort by relevance
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations
