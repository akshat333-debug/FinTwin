"""Unit tests for Tasks 4–7: Health Score, Shocks, Survival, Monte Carlo."""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_parser import parse_csv
from src.metrics_engine import compute_metrics
from src.health_score import calculate_health_score
from src.shock_models import apply_shock, get_all_shock_names, ALL_SHOCKS
from src.survival_rule import evaluate_survival
from src.simulation_engine import run_simulation, run_all_simulations


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_msme_data.csv")

# Profitable business
HEALTHY_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,500000,100000,100000,20000,800000
2025-02,520000,100000,105000,20000,895000
2025-03,540000,100000,110000,20000,1005000
2025-04,530000,102000,108000,20000,1105000
2025-05,550000,102000,112000,20000,1221000
2025-06,560000,102000,115000,20000,1344000
"""

# Struggling business
STRUGGLING_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,100000,80000,60000,20000,50000
2025-02,90000,80000,58000,20000,2000
2025-03,85000,82000,55000,20000,0
2025-04,95000,82000,57000,20000,0
2025-05,80000,82000,54000,20000,0
2025-06,88000,82000,56000,20000,0
"""


def _metrics(csv_str: str) -> dict:
    df = parse_csv(io.StringIO(csv_str))
    return compute_metrics(df)


# ===========================================================================
# Task 4: Health Score Tests
# ===========================================================================

class TestHealthScore:
    def test_healthy_business_scores_high(self):
        m = _metrics(HEALTHY_CSV)
        result = calculate_health_score(m)
        assert result["health_score"] >= 7.0
        assert result["grade"] in ("Good", "Excellent")

    def test_struggling_business_scores_low(self):
        m = _metrics(STRUGGLING_CSV)
        result = calculate_health_score(m)
        assert result["health_score"] <= 4.0
        assert result["grade"] in ("Critical", "Poor")

    def test_score_in_range(self):
        m = _metrics(HEALTHY_CSV)
        result = calculate_health_score(m)
        assert 1.0 <= result["health_score"] <= 10.0

    def test_component_scores_present(self):
        m = _metrics(HEALTHY_CSV)
        result = calculate_health_score(m)
        expected_components = {"profit_margin", "revenue_stability", "cash_runway", "burn_rate_safety", "cost_structure"}
        assert set(result["component_scores"].keys()) == expected_components

    def test_sample_data_score(self):
        df = parse_csv(SAMPLE_CSV)
        m = compute_metrics(df)
        result = calculate_health_score(m)
        assert result["health_score"] >= 5.0  # sample data is a stable business


# ===========================================================================
# Task 5: Shock Models Tests
# ===========================================================================

class TestShockModels:
    def test_all_seven_shocks_exist(self):
        assert len(ALL_SHOCKS) == 7

    def test_shock_names(self):
        expected = {"recession", "gst_hike", "fuel_spike", "pandemic", "credit_freeze", "demonetization", "inflation"}
        assert set(get_all_shock_names()) == expected

    def test_recession_reduces_profit(self):
        m = _metrics(HEALTHY_CSV)
        shocked = apply_shock(m, "recession")
        assert shocked["avg_monthly_profit"] < m["avg_monthly_profit"]

    def test_gst_hike_reduces_profit(self):
        m = _metrics(HEALTHY_CSV)
        shocked = apply_shock(m, "gst_hike")
        assert shocked["avg_monthly_profit"] < m["avg_monthly_profit"]

    def test_pandemic_reduces_early_months(self):
        m = _metrics(HEALTHY_CSV)
        shocked = apply_shock(m, "pandemic")
        # First 3 months should be hit harder
        for i in range(3):
            assert shocked["monthly_profit"][i] < m["monthly_profit"][i]

    def test_credit_freeze_reduces_cash(self):
        m = _metrics(HEALTHY_CSV)
        shocked = apply_shock(m, "credit_freeze")
        assert shocked["latest_cash_reserve"] < m["latest_cash_reserve"]

    def test_shocks_dont_modify_original(self):
        m = _metrics(HEALTHY_CSV)
        original_profit = m["avg_monthly_profit"]
        _ = apply_shock(m, "inflation")
        assert m["avg_monthly_profit"] == original_profit  # original unchanged

    def test_unknown_shock_raises(self):
        m = _metrics(HEALTHY_CSV)
        with pytest.raises(ValueError):
            apply_shock(m, "alien_invasion")


# ===========================================================================
# Task 7: Survival Rule Tests
# ===========================================================================

class TestSurvivalRule:
    def test_survives_with_profit(self):
        result = evaluate_survival(
            monthly_profits=[10000, 10000, 10000, 10000, 10000, 10000],
            initial_cash=50000,
        )
        assert result["survived"] is True
        assert result["months_survived"] == 6

    def test_fails_when_cash_runs_out(self):
        result = evaluate_survival(
            monthly_profits=[-20000, -20000, -20000, -20000, -20000, -20000],
            initial_cash=50000,
        )
        assert result["survived"] is False
        assert result["months_survived"] <= 3  # 50k / 20k = 2.5 months

    def test_trajectory_length(self):
        result = evaluate_survival(
            monthly_profits=[10000, 10000, 10000],
            initial_cash=50000,
        )
        # trajectory includes initial cash + 1 per month
        assert len(result["cash_trajectory"]) == 4

    def test_known_survival_percentage(self):
        # With 0 initial cash and positive profits, should survive
        result = evaluate_survival(
            monthly_profits=[1000, 1000, 1000],
            initial_cash=10000,
        )
        assert result["survived"] is True
        assert result["final_cash"] == 13000.0

    def test_bankruptcy_at_zero(self):
        result = evaluate_survival(
            monthly_profits=[-50000],
            initial_cash=50000,
        )
        assert result["survived"] is False


# ===========================================================================
# Task 6: Monte Carlo Tests
# ===========================================================================

class TestMonteCarlo:
    def test_deterministic_with_seed(self):
        m = _metrics(HEALTHY_CSV)
        r1 = run_simulation(m, "recession", n_simulations=100, seed=42)
        r2 = run_simulation(m, "recession", n_simulations=100, seed=42)
        assert r1["survival_probability"] == r2["survival_probability"]

    def test_returns_probability_range(self):
        m = _metrics(HEALTHY_CSV)
        result = run_simulation(m, "recession", n_simulations=100, seed=42)
        assert 0.0 <= result["survival_probability"] <= 1.0

    def test_healthy_business_survives_most_shocks(self):
        m = _metrics(HEALTHY_CSV)
        result = run_simulation(m, "gst_hike", n_simulations=100, seed=42)
        assert result["survival_probability"] >= 0.5  # GST hike is mild

    def test_all_simulations_returns_seven(self):
        m = _metrics(HEALTHY_CSV)
        results = run_all_simulations(m, n_simulations=50, seed=42)
        assert len(results) == 7

    def test_all_simulations_have_keys(self):
        m = _metrics(HEALTHY_CSV)
        results = run_all_simulations(m, n_simulations=50, seed=42)
        expected_keys = {"shock_key", "shock_name", "survival_probability", "survival_percentage",
                         "n_simulations", "survived_count", "failed_count", "avg_months_survived",
                         "worst_case_months"}
        for r in results:
            assert set(r.keys()) == expected_keys
