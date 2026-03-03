"""
Financial Metrics Computation Module.

Provides `compute_metrics(df)` that takes a cleaned DataFrame (from csv_parser)
and returns a dictionary of financial health indicators.

All computation is deterministic — no LLM involvement.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute MSME financial health metrics from cleaned CSV data.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame with columns: month, revenue, fixed_costs,
        variable_costs, loan_emi, cash_reserve.

    Returns
    -------
    dict
        Dictionary containing:
        - monthly_profit: list of per-month profit values
        - total_expenses: list of per-month total expenses
        - avg_monthly_profit: float
        - avg_profit_margin: float (0–1 scale)
        - profit_margins: list of per-month margins
        - burn_rate: float (avg monthly expenses when losing money, 0 if always profitable)
        - revenue_volatility: float (coefficient of variation, 0–1+ scale)
        - fixed_cost_ratio: float (fixed_costs / total_expenses, 0–1 scale)
        - avg_revenue: float
        - avg_expenses: float
        - avg_cash_reserve: float
        - latest_cash_reserve: float
        - months_of_data: int
        - revenue_trend: float (slope of revenue over time, positive = growing)
        - raw_df: pd.DataFrame (input data with computed columns added)
    """

    # ---- Per-month computations ----
    total_expenses = df["fixed_costs"] + df["variable_costs"] + df["loan_emi"]
    monthly_profit = df["revenue"] - total_expenses
    profit_margin = monthly_profit / df["revenue"].replace(0, np.nan)

    # ---- Aggregates ----
    avg_revenue = float(df["revenue"].mean())
    avg_expenses = float(total_expenses.mean())
    avg_monthly_profit = float(monthly_profit.mean())

    # Profit margin: average of per-month margins (excluding months with 0 revenue)
    valid_margins = profit_margin.dropna()
    avg_profit_margin = float(valid_margins.mean()) if len(valid_margins) > 0 else 0.0

    # Burn rate: average expenses in months where the business is losing money
    loss_months = total_expenses[monthly_profit < 0]
    burn_rate = float(loss_months.mean()) if len(loss_months) > 0 else 0.0

    # Revenue volatility: coefficient of variation (std / mean)
    rev_mean = df["revenue"].mean()
    rev_std = df["revenue"].std(ddof=1)  # sample std
    revenue_volatility = float(rev_std / rev_mean) if rev_mean > 0 else 0.0

    # Fixed cost ratio: avg(fixed_costs) / avg(total_expenses)
    avg_fixed = float(df["fixed_costs"].mean())
    fixed_cost_ratio = float(avg_fixed / avg_expenses) if avg_expenses > 0 else 0.0

    # Revenue trend: simple linear regression slope
    if len(df) >= 2:
        x = np.arange(len(df), dtype=float)
        y = df["revenue"].values.astype(float)
        slope = float(np.polyfit(x, y, 1)[0])
    else:
        slope = 0.0

    # ---- Build enriched DataFrame ----
    enriched_df = df.copy()
    enriched_df["total_expenses"] = total_expenses
    enriched_df["monthly_profit"] = monthly_profit
    enriched_df["profit_margin"] = profit_margin

    return {
        # Per-month series
        "monthly_profit": monthly_profit.tolist(),
        "total_expenses": total_expenses.tolist(),
        "profit_margins": profit_margin.fillna(0.0).tolist(),
        # Aggregates
        "avg_monthly_profit": round(avg_monthly_profit, 2),
        "avg_profit_margin": round(avg_profit_margin, 4),
        "burn_rate": round(burn_rate, 2),
        "revenue_volatility": round(revenue_volatility, 4),
        "fixed_cost_ratio": round(fixed_cost_ratio, 4),
        "avg_revenue": round(avg_revenue, 2),
        "avg_expenses": round(avg_expenses, 2),
        "avg_cash_reserve": round(float(df["cash_reserve"].mean()), 2),
        "latest_cash_reserve": round(float(df["cash_reserve"].iloc[-1]), 2),
        "months_of_data": len(df),
        "revenue_trend": round(slope, 2),
        # Enriched data
        "raw_df": enriched_df,
    }
