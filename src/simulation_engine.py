"""
Monte Carlo Simulation Engine.

Runs N stochastic simulations for each shock scenario,
applying random noise to the shocked metrics and evaluating
survival based on the survival rule.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .shock_models import apply_shock, ALL_SHOCKS, get_all_shock_names
from .survival_rule import evaluate_survival


def run_simulation(
    metrics: dict[str, Any],
    shock_key: str,
    n_simulations: int = 1000,
    noise_std: float = 0.05,
    seed: int | None = None,
) -> dict[str, Any]:
    """Run Monte Carlo simulation for a single shock scenario.

    Parameters
    ----------
    metrics : dict
        Output of compute_metrics().
    shock_key : str
        Key from ALL_SHOCKS registry.
    n_simulations : int
        Number of Monte Carlo iterations (default 1000).
    noise_std : float
        Standard deviation of random noise applied to monthly profits
        (as a fraction of absolute profit). Default 0.05 (5%).
    seed : int | None
        Random seed for reproducibility. None = non-deterministic.

    Returns
    -------
    dict
        {
            "shock_key": str,
            "shock_name": str,
            "survival_probability": float (0–1),
            "survival_percentage": float (0–100),
            "n_simulations": int,
            "survived_count": int,
            "failed_count": int,
            "avg_months_survived": float,
            "worst_case_months": int,
        }
    """
    rng = np.random.default_rng(seed)
    shocked_metrics = apply_shock(metrics, shock_key)

    base_profits = np.array(shocked_metrics["monthly_profit"], dtype=float)
    cash_reserve = shocked_metrics["latest_cash_reserve"]
    n_months = len(base_profits)

    survived = 0
    total_months_survived = 0
    worst_months = n_months

    for _ in range(n_simulations):
        # Add random noise to each month's profit
        noise = rng.normal(0, noise_std, size=n_months)
        noisy_profits = base_profits * (1 + noise)

        result = evaluate_survival(
            monthly_profits=noisy_profits.tolist(),
            initial_cash=cash_reserve,
        )

        if result["survived"]:
            survived += 1
            total_months_survived += n_months
        else:
            total_months_survived += result["months_survived"]
            worst_months = min(worst_months, result["months_survived"])

    survival_prob = survived / n_simulations

    return {
        "shock_key": shock_key,
        "shock_name": ALL_SHOCKS[shock_key]["name"],
        "survival_probability": round(survival_prob, 4),
        "survival_percentage": round(survival_prob * 100, 2),
        "n_simulations": n_simulations,
        "survived_count": survived,
        "failed_count": n_simulations - survived,
        "avg_months_survived": round(total_months_survived / n_simulations, 1),
        "worst_case_months": worst_months,
    }


def run_all_simulations(
    metrics: dict[str, Any],
    n_simulations: int = 1000,
    noise_std: float = 0.05,
    seed: int | None = 42,
) -> list[dict[str, Any]]:
    """Run Monte Carlo simulation for all 7 shock scenarios.

    Parameters
    ----------
    metrics : dict
        Output of compute_metrics().
    n_simulations : int
        Iterations per shock scenario.
    noise_std : float
        Noise standard deviation.
    seed : int | None
        Base seed (each shock gets seed + i for reproducibility).

    Returns
    -------
    list[dict]
        List of simulation results, one per shock.
    """
    results = []
    for i, shock_key in enumerate(get_all_shock_names()):
        sim_seed = (seed + i) if seed is not None else None
        result = run_simulation(
            metrics=metrics,
            shock_key=shock_key,
            n_simulations=n_simulations,
            noise_std=noise_std,
            seed=sim_seed,
        )
        results.append(result)

    return results
