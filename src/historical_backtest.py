"""
Historical Stress Backtesting.
Simulates how the business would have performed during real Indian economic events.
"""

from __future__ import annotations
from typing import Any
import copy


import json
import os

def load_events() -> list[dict[str, Any]]:
    """Load historical events from JSON configuration."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

HISTORICAL_EVENTS = load_events()


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
