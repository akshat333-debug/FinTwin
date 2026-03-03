"""
Synthetic MSME Dataset Generator (Task 12).

Generates realistic Indian MSME financial data using configurable parameters.
No external dependencies beyond NumPy/Pandas (Faker not needed for numeric data).
"""

from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd


def generate_synthetic_msme_data(
    n_months: int = 12,
    base_revenue: float = 500000.0,
    revenue_growth: float = 0.02,
    revenue_noise: float = 0.08,
    fixed_cost_ratio: float = 0.35,
    variable_cost_ratio: float = 0.30,
    loan_emi: float = 35000.0,
    initial_cash: float = 300000.0,
    seed: int | None = None,
    business_type: str = "stable",
) -> pd.DataFrame:
    """Generate synthetic MSME financial data.

    Parameters
    ----------
    n_months : int
        Number of months to generate (default 12).
    base_revenue : float
        Starting monthly revenue in INR.
    revenue_growth : float
        Monthly revenue growth rate (0.02 = 2%/month).
    revenue_noise : float
        Standard deviation of revenue noise (as fraction).
    fixed_cost_ratio : float
        Fixed costs as fraction of revenue.
    variable_cost_ratio : float
        Variable costs as fraction of revenue.
    loan_emi : float
        Monthly loan EMI.
    initial_cash : float
        Starting cash reserve.
    seed : int | None
        Random seed for reproducibility.
    business_type : str
        One of: "stable", "growing", "struggling", "seasonal".

    Returns
    -------
    pd.DataFrame
        DataFrame matching the MSME CSV schema.
    """
    rng = np.random.default_rng(seed)

    # ── Business type presets ──
    if business_type == "growing":
        revenue_growth = 0.05
        revenue_noise = 0.06
    elif business_type == "struggling":
        revenue_growth = -0.03
        revenue_noise = 0.15
        fixed_cost_ratio = 0.50
        variable_cost_ratio = 0.35
    elif business_type == "seasonal":
        revenue_growth = 0.01
        revenue_noise = 0.20

    months = []
    revenues = []
    fixed_costs_list = []
    variable_costs_list = []
    loan_emis = []
    cash_reserves = []

    cash = initial_cash

    for i in range(n_months):
        # Month label
        month_offset = i
        year = 2025 + month_offset // 12
        month_num = (month_offset % 12) + 1
        months.append(f"{year}-{month_num:02d}")

        # Revenue with growth + noise + optional seasonality
        growth_factor = (1 + revenue_growth) ** i
        noise = rng.normal(0, revenue_noise)

        if business_type == "seasonal":
            # Simulate festive season boost (Oct-Dec) and slow months (Jun-Aug)
            seasonal = {10: 0.25, 11: 0.30, 12: 0.20, 6: -0.15, 7: -0.20, 8: -0.10}
            seasonal_factor = seasonal.get(month_num, 0.0)
            noise += seasonal_factor

        revenue = max(0, base_revenue * growth_factor * (1 + noise))
        revenues.append(round(revenue, 2))

        # Costs
        fixed = base_revenue * fixed_cost_ratio * (1 + rng.normal(0, 0.02))  # small fixed cost drift
        fixed = round(max(0, fixed), 2)
        fixed_costs_list.append(fixed)

        variable = revenue * variable_cost_ratio * (1 + rng.normal(0, 0.05))
        variable = round(max(0, variable), 2)
        variable_costs_list.append(variable)

        loan_emis.append(loan_emi)

        # Cash reserve
        profit = revenue - fixed - variable - loan_emi
        cash = max(0, cash + profit)
        cash_reserves.append(round(cash, 2))

    df = pd.DataFrame({
        "month": months,
        "revenue": revenues,
        "fixed_costs": fixed_costs_list,
        "variable_costs": variable_costs_list,
        "loan_emi": loan_emis,
        "cash_reserve": cash_reserves,
    })

    return df


def save_synthetic_data(
    df: pd.DataFrame,
    filepath: str,
) -> str:
    """Save synthetic data to CSV file.

    Returns
    -------
    str
        Path where file was saved.
    """
    df.to_csv(filepath, index=False)
    return filepath


def generate_multiple_datasets(
    n_datasets: int = 4,
    seed: int = 42,
) -> dict[str, pd.DataFrame]:
    """Generate datasets for all business types.

    Returns
    -------
    dict
        Mapping of business_type -> DataFrame.
    """
    types = ["stable", "growing", "struggling", "seasonal"]
    datasets = {}
    for i, btype in enumerate(types[:n_datasets]):
        datasets[btype] = generate_synthetic_msme_data(
            n_months=12,
            seed=seed + i,
            business_type=btype,
        )
    return datasets
