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


# ── Registry ──────────────────────────────────────────────────────────

import json
import os

def load_shocks() -> dict[str, dict[str, Any]]:
    """Load shock models from JSON configuration."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "shocks.json")
    with open(filepath, "r", encoding="utf-8") as f:
        shocks_list = json.load(f)

    registry = {}
    for shock in shocks_list:
        # Create a closure to capture the specific shock parameters
        def make_shock_func(config=shock):
            def custom_shock_fn(m: dict) -> dict:
                result = copy.deepcopy(m)
                if config.get("revenue_impact", 0.0) != 0.0:
                    result = _apply_revenue_shock(result, factor=config["revenue_impact"], months=config.get("duration_months"))
                if config.get("expense_impact", 0.0) != 0.0:
                    result = _apply_expense_shock(result, factor=config["expense_impact"])
                if config.get("cash_reserve_impact", 0.0) != 0.0:
                    result["latest_cash_reserve"] = round(result["latest_cash_reserve"] * (1 + config["cash_reserve_impact"]), 2)
                    result["avg_cash_reserve"] = round(result["avg_cash_reserve"] * (1 + config["cash_reserve_impact"]), 2)
                return result
            return custom_shock_fn

        registry[shock["key"]] = {
            "name": shock["name"],
            "description": shock["description"],
            "severity": shock["severity"],
            "function": make_shock_func(),
        }
    return registry


ALL_SHOCKS: dict[str, dict[str, Any]] = load_shocks()


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
