"""
Survival Rule Engine.

Defines the bankruptcy/survival logic:
- The business survives if cumulative cash stays > 0 for all months.
- Goes bankrupt the first month cumulative cash drops to 0 or below.
"""

from __future__ import annotations

from typing import Any


def evaluate_survival(
    monthly_profits: list[float],
    initial_cash: float,
    bankruptcy_threshold: float = 0.0,
) -> dict[str, Any]:
    """Evaluate whether a business survives a given profit trajectory.

    The simulation walks month-by-month:
        cash[t] = cash[t-1] + profit[t]
    Bankruptcy occurs the first month cash <= bankruptcy_threshold.

    Parameters
    ----------
    monthly_profits : list[float]
        Profit (or loss) for each month in the simulation period.
    initial_cash : float
        Starting cash reserve.
    bankruptcy_threshold : float
        Cash level at or below which the business is bankrupt. Default 0.

    Returns
    -------
    dict
        {
            "survived": bool,
            "months_survived": int (0-indexed count of months before failure),
            "final_cash": float,
            "min_cash": float (lowest cash point during simulation),
            "cash_trajectory": list[float],
        }
    """
    cash = initial_cash
    min_cash = cash
    trajectory = [cash]

    for month_idx, profit in enumerate(monthly_profits):
        cash += profit
        trajectory.append(cash)
        min_cash = min(min_cash, cash)

        if cash <= bankruptcy_threshold:
            return {
                "survived": False,
                "months_survived": month_idx + 1,
                "final_cash": round(cash, 2),
                "min_cash": round(min_cash, 2),
                "cash_trajectory": [round(c, 2) for c in trajectory],
            }

    return {
        "survived": True,
        "months_survived": len(monthly_profits),
        "final_cash": round(cash, 2),
        "min_cash": round(min_cash, 2),
        "cash_trajectory": [round(c, 2) for c in trajectory],
    }
