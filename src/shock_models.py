"""
India-Specific Shock Models.

7 macroeconomic shocks that modify baseline financial metrics
to simulate stress scenarios for Indian MSMEs.

Each shock function takes a metrics dict and returns a *modified copy*.
"""

from __future__ import annotations

import copy
from typing import Any, Callable


ShockFunction = Callable[[dict[str, Any]], dict[str, Any]]


def _apply_revenue_shock(metrics: dict, factor: float, months: int | None = None) -> dict:
    """Helper: reduce revenue by a factor across all or specified months."""
    m = copy.deepcopy(metrics)
    profits = list(m["monthly_profit"])
    revenues_original = [
        p + e for p, e in zip(m["monthly_profit"], m["total_expenses"])
    ]

    n = months if months and months < len(profits) else len(profits)
    for i in range(n):
        revenue_drop = revenues_original[i] * abs(factor)
        profits[i] -= revenue_drop

    m["monthly_profit"] = profits
    m["avg_monthly_profit"] = round(sum(profits) / len(profits), 2)
    m["avg_revenue"] = round(m["avg_revenue"] * (1 + factor), 2) if months is None else m["avg_revenue"]
    return m


def _apply_expense_shock(metrics: dict, factor: float, expense_type: str = "all") -> dict:
    """Helper: increase expenses by a factor."""
    m = copy.deepcopy(metrics)
    profits = list(m["monthly_profit"])
    expenses = list(m["total_expenses"])

    for i in range(len(profits)):
        expense_increase = expenses[i] * abs(factor)
        profits[i] -= expense_increase
        expenses[i] += expense_increase

    m["monthly_profit"] = profits
    m["total_expenses"] = expenses
    m["avg_monthly_profit"] = round(sum(profits) / len(profits), 2)
    m["avg_expenses"] = round(sum(expenses) / len(expenses), 2)
    return m


# ── SHOCK 1: Recession ────────────────────────────────────────────────
def shock_recession(metrics: dict[str, Any]) -> dict[str, Any]:
    """Recession: -20% revenue across all months."""
    return _apply_revenue_shock(metrics, factor=-0.20)


# ── SHOCK 2: GST Hike ─────────────────────────────────────────────────
def shock_gst_hike(metrics: dict[str, Any]) -> dict[str, Any]:
    """GST hike: +5% increase in all expenses."""
    return _apply_expense_shock(metrics, factor=0.05)


# ── SHOCK 3: Fuel Spike ───────────────────────────────────────────────
def shock_fuel_spike(metrics: dict[str, Any]) -> dict[str, Any]:
    """Fuel/logistics spike: +10% increase in variable costs (proxy: total expenses)."""
    return _apply_expense_shock(metrics, factor=0.10)


# ── SHOCK 4: Pandemic ─────────────────────────────────────────────────
def shock_pandemic(metrics: dict[str, Any]) -> dict[str, Any]:
    """Pandemic: -35% revenue for first 3 months."""
    return _apply_revenue_shock(metrics, factor=-0.35, months=3)


# ── SHOCK 5: Credit Freeze ────────────────────────────────────────────
def shock_credit_freeze(metrics: dict[str, Any]) -> dict[str, Any]:
    """Credit freeze: cash reserve drops 40% + 15% revenue loss for 3 months (delayed receivables)."""
    m = copy.deepcopy(metrics)
    m["latest_cash_reserve"] = round(m["latest_cash_reserve"] * 0.60, 2)
    m["avg_cash_reserve"] = round(m["avg_cash_reserve"] * 0.60, 2)
    # Delayed receivables also reduce effective revenue for 3 months
    profits = list(m["monthly_profit"])
    expenses = list(m["total_expenses"])
    n = min(3, len(profits))
    for i in range(n):
        revenue_i = profits[i] + expenses[i]
        revenue_drop = revenue_i * 0.15
        profits[i] -= revenue_drop
    m["monthly_profit"] = profits
    m["avg_monthly_profit"] = round(sum(profits) / len(profits), 2)
    return m


# ── SHOCK 6: Demonetization ───────────────────────────────────────────
def shock_demonetization(metrics: dict[str, Any]) -> dict[str, Any]:
    """Demonetization: -50% revenue for 2 months, then recovery."""
    return _apply_revenue_shock(metrics, factor=-0.50, months=2)


# ── SHOCK 7: Inflation Shock ──────────────────────────────────────────
def shock_inflation(metrics: dict[str, Any]) -> dict[str, Any]:
    """Sustained inflation: +15% increase in all expenses."""
    return _apply_expense_shock(metrics, factor=0.15)


# ── Registry ──────────────────────────────────────────────────────────

ALL_SHOCKS: dict[str, dict[str, Any]] = {
    "recession": {
        "name": "Recession",
        "description": "Revenue drops 20% across all months",
        "severity": "High",
        "function": shock_recession,
    },
    "gst_hike": {
        "name": "GST Hike",
        "description": "5% increase in all expenses due to tax policy change",
        "severity": "Medium",
        "function": shock_gst_hike,
    },
    "fuel_spike": {
        "name": "Fuel/Logistics Spike",
        "description": "10% increase in operating costs due to fuel price surge",
        "severity": "Medium",
        "function": shock_fuel_spike,
    },
    "pandemic": {
        "name": "Pandemic Lockdown",
        "description": "35% revenue drop for 3 months due to lockdown",
        "severity": "Very High",
        "function": shock_pandemic,
    },
    "credit_freeze": {
        "name": "Credit Freeze",
        "description": "Cash reserves drop 40% due to delayed receivables",
        "severity": "High",
        "function": shock_credit_freeze,
    },
    "demonetization": {
        "name": "Demonetization",
        "description": "50% revenue drop for 2 months, cash-dependent disruption",
        "severity": "Very High",
        "function": shock_demonetization,
    },
    "inflation": {
        "name": "Inflation Shock",
        "description": "15% sustained increase in all operating expenses",
        "severity": "High",
        "function": shock_inflation,
    },
}


def get_all_shock_names() -> list[str]:
    """Return list of all shock keys."""
    return list(ALL_SHOCKS.keys())


def apply_shock(metrics: dict[str, Any], shock_key: str) -> dict[str, Any]:
    """Apply a named shock to metrics.

    Parameters
    ----------
    metrics : dict
        Output of compute_metrics().
    shock_key : str
        Key from ALL_SHOCKS registry.

    Returns
    -------
    dict
        Modified metrics after shock application.
    """
    if shock_key not in ALL_SHOCKS:
        raise ValueError(f"Unknown shock: {shock_key}. Available: {list(ALL_SHOCKS.keys())}")
    return ALL_SHOCKS[shock_key]["function"](metrics)
