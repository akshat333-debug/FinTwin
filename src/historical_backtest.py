"""
Historical Stress Backtesting.
Simulates how the business would have performed during real Indian economic events.
"""

from __future__ import annotations
from typing import Any
import copy


# ── Historical Events Database ───────────────────────────────────────────────

HISTORICAL_EVENTS = [
    {
        "id": "covid_2020",
        "name": "COVID-19 Lockdown",
        "year": "2020",
        "period": "Mar 2020 – Jun 2020",
        "description": "Nationwide lockdown halted business operations. MSMEs faced severe demand collapse, supply chain disruptions, and labor exodus.",
        "icon": "🦠",
        "shocks": [
            {"month_start": 0, "month_end": 1, "revenue_impact": -0.70, "expense_impact": -0.10, "cash_drain": 0.20},
            {"month_start": 2, "month_end": 3, "revenue_impact": -0.40, "expense_impact": 0.0, "cash_drain": 0.10},
        ],
        "duration_months": 4,
        "severity": "Critical",
        "gdp_impact": "-23.9% (Q1 FY21)",
    },
    {
        "id": "demonetization_2016",
        "name": "Demonetization",
        "year": "2016",
        "period": "Nov 2016 – Feb 2017",
        "description": "₹500/₹1000 notes were invalidated overnight. Cash-dependent MSMEs faced severe liquidity crunch and demand destruction.",
        "icon": "💵",
        "shocks": [
            {"month_start": 0, "month_end": 1, "revenue_impact": -0.55, "expense_impact": -0.05, "cash_drain": 0.35},
            {"month_start": 2, "month_end": 3, "revenue_impact": -0.20, "expense_impact": 0.0, "cash_drain": 0.0},
        ],
        "duration_months": 4,
        "severity": "High",
        "gdp_impact": "-1.5% (estimated MSME sector)",
    },
    {
        "id": "gst_rollout_2017",
        "name": "GST Implementation",
        "year": "2017",
        "period": "Jul 2017 – Dec 2017",
        "description": "Complex GST compliance requirements disrupted MSME operations. Initial confusion led to working capital lockups and demand slowdown.",
        "icon": "📋",
        "shocks": [
            {"month_start": 0, "month_end": 2, "revenue_impact": -0.15, "expense_impact": 0.08, "cash_drain": 0.10},
            {"month_start": 3, "month_end": 5, "revenue_impact": -0.05, "expense_impact": 0.05, "cash_drain": 0.0},
        ],
        "duration_months": 6,
        "severity": "Medium",
        "gdp_impact": "Short-term disruption, long-term formalization",
    },
    {
        "id": "il_fs_2018",
        "name": "IL&FS / NBFC Crisis",
        "year": "2018",
        "period": "Sep 2018 – Mar 2019",
        "description": "IL&FS default triggered NBFC liquidity crisis. Credit flow to MSMEs dried up as NBFCs (major MSME lenders) faced severe stress.",
        "icon": "🏛️",
        "shocks": [
            {"month_start": 0, "month_end": 2, "revenue_impact": -0.10, "expense_impact": 0.03, "cash_drain": 0.25},
            {"month_start": 3, "month_end": 5, "revenue_impact": -0.08, "expense_impact": 0.02, "cash_drain": 0.10},
        ],
        "duration_months": 6,
        "severity": "High",
        "gdp_impact": "Credit growth fell from 15% to 8%",
    },
    {
        "id": "russia_ukraine_2022",
        "name": "Russia-Ukraine War (Commodity Shock)",
        "year": "2022",
        "period": "Feb 2022 – Aug 2022",
        "description": "War disrupted global supply chains, spiking fuel, raw material, and edible oil prices. Indian MSMEs faced severe input cost inflation.",
        "icon": "⛽",
        "shocks": [
            {"month_start": 0, "month_end": 3, "revenue_impact": -0.05, "expense_impact": 0.20, "cash_drain": 0.05},
            {"month_start": 4, "month_end": 5, "revenue_impact": -0.03, "expense_impact": 0.12, "cash_drain": 0.0},
        ],
        "duration_months": 6,
        "severity": "Medium",
        "gdp_impact": "WPI inflation hit 15.88% (May 2022)",
    },
    {
        "id": "second_wave_2021",
        "name": "COVID-19 Second Wave",
        "year": "2021",
        "period": "Apr 2021 – Jun 2021",
        "description": "Devastating second wave with localized lockdowns. MSMEs faced renewed demand destruction, worker absenteeism, and oxygen/medical supply diversion.",
        "icon": "🏥",
        "shocks": [
            {"month_start": 0, "month_end": 1, "revenue_impact": -0.35, "expense_impact": -0.05, "cash_drain": 0.10},
            {"month_start": 2, "month_end": 2, "revenue_impact": -0.15, "expense_impact": 0.0, "cash_drain": 0.0},
        ],
        "duration_months": 3,
        "severity": "High",
        "gdp_impact": "GDP recovered but MSMEs lagged",
    },
]


def run_historical_backtest(
    metrics: dict[str, Any],
    event_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Simulate business performance during historical events.
    Returns month-by-month cash trajectory for each event.
    """
    events = HISTORICAL_EVENTS
    if event_id:
        events = [e for e in events if e["id"] == event_id]

    avg_revenue = metrics["avg_revenue"]
    avg_expenses = metrics["avg_expenses"]
    initial_cash = metrics["latest_cash_reserve"]
    avg_profit = metrics["avg_monthly_profit"]

    results = []

    for event in events:
        trajectory = []
        cash = initial_cash
        survived = True
        bankruptcy_month = None

        for month in range(event["duration_months"]):
            # Find applicable shock for this month
            revenue_impact = 0
            expense_impact = 0
            cash_drain = 0
            for shock in event["shocks"]:
                if shock["month_start"] <= month <= shock["month_end"]:
                    revenue_impact = shock["revenue_impact"]
                    expense_impact = shock["expense_impact"]
                    cash_drain = shock.get("cash_drain", 0)
                    break

            # Apply shocks
            monthly_revenue = avg_revenue * (1 + revenue_impact)
            monthly_expenses = avg_expenses * (1 + expense_impact)
            monthly_profit = monthly_revenue - monthly_expenses

            # Cash drain (supply chain disruption, forced payments, etc.)
            if cash_drain > 0:
                cash -= cash * cash_drain

            cash += monthly_profit

            month_data = {
                "month": month + 1,
                "label": f"M{month + 1}",
                "revenue": round(monthly_revenue, 2),
                "expenses": round(monthly_expenses, 2),
                "profit": round(monthly_profit, 2),
                "cash": round(cash, 2),
                "revenue_change": round(revenue_impact * 100, 1),
                "expense_change": round(expense_impact * 100, 1),
            }
            trajectory.append(month_data)

            if cash <= 0 and survived:
                survived = False
                bankruptcy_month = month + 1

        results.append({
            "event_id": event["id"],
            "event_name": event["name"],
            "year": event["year"],
            "period": event["period"],
            "description": event["description"],
            "severity": event["severity"],
            "icon": event["icon"],
            "gdp_impact": event["gdp_impact"],
            "survived": survived,
            "bankruptcy_month": bankruptcy_month,
            "final_cash": round(cash, 2),
            "cash_change_pct": round((cash - initial_cash) / max(initial_cash, 1) * 100, 1),
            "min_cash": round(min(m["cash"] for m in trajectory), 2),
            "trajectory": trajectory,
        })

    return results
