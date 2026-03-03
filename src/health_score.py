"""
Health Score Engine (1–10 scale).

Converts raw financial metrics into a single composite health score.
Deterministic — no LLM involvement.
"""

from __future__ import annotations

from typing import Any


def calculate_health_score(metrics: dict[str, Any]) -> dict[str, Any]:
    """Calculate an MSME financial health score on a 1–10 scale.

    Scoring breakdown (weights sum to 10):
    - Profit margin:       0–3 points
    - Revenue volatility:  0–2 points (lower = better)
    - Cash runway:         0–2 points
    - Burn rate safety:    0–1.5 points
    - Fixed cost ratio:    0–1.5 points (moderate = best)

    Parameters
    ----------
    metrics : dict
        Output of `compute_metrics()`.

    Returns
    -------
    dict
        {
            "health_score": float (1–10),
            "component_scores": dict of individual component scores,
            "grade": str ("Critical" | "Poor" | "Fair" | "Good" | "Excellent"),
            "interpretation": str
        }
    """

    components: dict[str, float] = {}

    # ── 1. Profit Margin Score (0–3) ──────────────────────────────────
    margin = metrics["avg_profit_margin"]
    if margin >= 0.25:
        components["profit_margin"] = 3.0
    elif margin >= 0.15:
        components["profit_margin"] = 2.5
    elif margin >= 0.08:
        components["profit_margin"] = 2.0
    elif margin >= 0.0:
        components["profit_margin"] = 1.0
    else:
        components["profit_margin"] = 0.0

    # ── 2. Revenue Volatility Score (0–2, lower volatility = higher score)
    volatility = metrics["revenue_volatility"]
    if volatility <= 0.05:
        components["revenue_stability"] = 2.0
    elif volatility <= 0.10:
        components["revenue_stability"] = 1.5
    elif volatility <= 0.20:
        components["revenue_stability"] = 1.0
    elif volatility <= 0.35:
        components["revenue_stability"] = 0.5
    else:
        components["revenue_stability"] = 0.0

    # ── 3. Cash Runway Score (0–2) ────────────────────────────────────
    # How many months can the business survive on cash alone?
    avg_expenses = metrics["avg_expenses"]
    cash = metrics["latest_cash_reserve"]
    if avg_expenses > 0:
        runway_months = cash / avg_expenses
    else:
        runway_months = 12.0  # No expenses = infinite runway

    if runway_months >= 6:
        components["cash_runway"] = 2.0
    elif runway_months >= 3:
        components["cash_runway"] = 1.5
    elif runway_months >= 1.5:
        components["cash_runway"] = 1.0
    elif runway_months >= 0.5:
        components["cash_runway"] = 0.5
    else:
        components["cash_runway"] = 0.0

    # ── 4. Burn Rate Safety (0–1.5) ───────────────────────────────────
    burn = metrics["burn_rate"]
    if burn == 0:
        components["burn_rate_safety"] = 1.5  # Never losing money
    else:
        burn_ratio = burn / avg_expenses if avg_expenses > 0 else 2.0
        if burn_ratio <= 1.0:
            components["burn_rate_safety"] = 1.0
        elif burn_ratio <= 1.3:
            components["burn_rate_safety"] = 0.5
        else:
            components["burn_rate_safety"] = 0.0

    # ── 5. Fixed Cost Ratio (0–1.5, moderate ~40-60% is optimal) ──────
    fixed_ratio = metrics["fixed_cost_ratio"]
    if 0.35 <= fixed_ratio <= 0.55:
        components["cost_structure"] = 1.5
    elif 0.25 <= fixed_ratio <= 0.65:
        components["cost_structure"] = 1.0
    elif 0.15 <= fixed_ratio <= 0.75:
        components["cost_structure"] = 0.5
    else:
        components["cost_structure"] = 0.0

    # ── Composite Score (clamp to 1–10) ───────────────────────────────
    raw_score = sum(components.values())
    health_score = max(1.0, min(10.0, round(raw_score, 1)))

    # ── Grade ─────────────────────────────────────────────────────────
    if health_score >= 8.5:
        grade = "Excellent"
        interpretation = "Strong financials. Business is well-positioned to weather shocks."
    elif health_score >= 7.0:
        grade = "Good"
        interpretation = "Healthy business with minor areas for improvement."
    elif health_score >= 5.0:
        grade = "Fair"
        interpretation = "Moderate risk. Some financial metrics need attention."
    elif health_score >= 3.0:
        grade = "Poor"
        interpretation = "Significant financial stress. Immediate action recommended."
    else:
        grade = "Critical"
        interpretation = "Severe financial distress. Business survival is at risk."

    return {
        "health_score": health_score,
        "component_scores": components,
        "grade": grade,
        "interpretation": interpretation,
    }
