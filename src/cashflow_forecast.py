"""
Cash Flow Forecast with Monte Carlo confidence intervals.
Projects cash position over N months with P10/P50/P90 bands.
"""

from __future__ import annotations
from typing import Any

import numpy as np


def forecast_cashflow(
    metrics: dict[str, Any],
    months_ahead: int = 6,
    n_simulations: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Monte Carlo cash flow forecast.

    Returns month-by-month projections with confidence bands.
    """
    rng = np.random.default_rng(seed)

    avg_profit = metrics["avg_monthly_profit"]
    cash = metrics["latest_cash_reserve"]
    volatility = metrics.get("revenue_volatility", 0.1)
    trend = metrics.get("revenue_trend", 0)
    avg_revenue = metrics["avg_revenue"]
    avg_expenses = metrics["avg_expenses"]

    # Run simulations
    all_trajectories = np.zeros((n_simulations, months_ahead))

    for sim in range(n_simulations):
        current_cash = cash
        for m in range(months_ahead):
            # Revenue with trend + noise
            revenue_noise = rng.normal(0, volatility * avg_revenue)
            trend_factor = 1 + trend * (m + 1) / 12
            projected_revenue = avg_revenue * trend_factor + revenue_noise

            # Expenses with small noise (less volatile than revenue)
            expense_noise = rng.normal(0, 0.03 * avg_expenses)
            projected_expenses = avg_expenses + expense_noise

            monthly_profit = projected_revenue - projected_expenses
            current_cash = current_cash + monthly_profit
            all_trajectories[sim, m] = current_cash

    # Calculate percentiles
    p10 = np.percentile(all_trajectories, 10, axis=0).tolist()
    p25 = np.percentile(all_trajectories, 25, axis=0).tolist()
    p50 = np.percentile(all_trajectories, 50, axis=0).tolist()
    p75 = np.percentile(all_trajectories, 75, axis=0).tolist()
    p90 = np.percentile(all_trajectories, 90, axis=0).tolist()

    # Calculate probability of running out of cash at each month
    prob_negative = (all_trajectories < 0).mean(axis=0).tolist()

    # Summary stats at end of forecast
    final_cash = all_trajectories[:, -1]
    prob_bankrupt = float((final_cash < 0).mean())
    expected_cash = float(np.median(final_cash))

    # Months until potential bankruptcy (median case)
    months_to_zero = None
    for m in range(months_ahead):
        if p50[m] <= 0:
            months_to_zero = m + 1
            break

    # Generate month labels
    last_month = metrics.get("months", [])
    if last_month:
        # Parse last month and extend
        import datetime
        try:
            last_date = datetime.datetime.strptime(last_month[-1], "%Y-%m")
        except (ValueError, IndexError):
            last_date = datetime.datetime.now()
        month_labels = []
        for i in range(1, months_ahead + 1):
            next_month = last_date + datetime.timedelta(days=32 * i)
            month_labels.append(next_month.strftime("%Y-%m"))
    else:
        month_labels = [f"M+{i+1}" for i in range(months_ahead)]

    return {
        "months": month_labels,
        "p10": [round(v, 2) for v in p10],
        "p25": [round(v, 2) for v in p25],
        "p50": [round(v, 2) for v in p50],
        "p75": [round(v, 2) for v in p75],
        "p90": [round(v, 2) for v in p90],
        "prob_negative": [round(v, 4) for v in prob_negative],
        "prob_bankrupt_by_end": round(prob_bankrupt, 4),
        "expected_cash_end": round(expected_cash, 2),
        "months_to_zero": months_to_zero,
        "months_ahead": months_ahead,
        "n_simulations": n_simulations,
        "starting_cash": round(cash, 2),
    }
