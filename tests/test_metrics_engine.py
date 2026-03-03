"""Unit tests for Financial Metrics Computation (Task 3)."""

import io
import os
import sys
import math

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_parser import parse_csv
from src.metrics_engine import compute_metrics


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_msme_data.csv")

# A simple, predictable 6-month dataset for deterministic testing
DETERMINISTIC_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,100000,30000,20000,10000,50000
2025-02,100000,30000,20000,10000,90000
2025-03,100000,30000,20000,10000,130000
2025-04,100000,30000,20000,10000,170000
2025-05,100000,30000,20000,10000,210000
2025-06,100000,30000,20000,10000,250000
"""

# Dataset where some months are unprofitable
LOSS_MONTHS_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,100000,80000,40000,10000,50000
2025-02,100000,80000,40000,10000,20000
2025-03,200000,30000,20000,10000,160000
2025-04,200000,30000,20000,10000,300000
2025-05,200000,30000,20000,10000,440000
2025-06,200000,30000,20000,10000,580000
"""


def _df(csv_str: str) -> pd.DataFrame:
    return parse_csv(io.StringIO(csv_str))


class TestComputeMetricsDeterministic:
    """Tests with perfectly predictable data."""

    def test_monthly_profit(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        # Revenue 100k, expenses 30k+20k+10k = 60k, profit = 40k per month
        assert all(p == 40000.0 for p in metrics["monthly_profit"])

    def test_total_expenses(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert all(e == 60000.0 for e in metrics["total_expenses"])

    def test_avg_profit_margin(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        # margin = 40000 / 100000 = 0.4
        assert metrics["avg_profit_margin"] == 0.4

    def test_burn_rate_zero_when_always_profitable(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["burn_rate"] == 0.0

    def test_revenue_volatility_zero_when_constant(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["revenue_volatility"] == 0.0

    def test_fixed_cost_ratio(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        # fixed = 30k, total = 60k → ratio = 0.5
        assert metrics["fixed_cost_ratio"] == 0.5

    def test_revenue_trend_flat(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["revenue_trend"] == 0.0

    def test_months_of_data(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["months_of_data"] == 6

    def test_avg_revenue(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["avg_revenue"] == 100000.0

    def test_latest_cash_reserve(self):
        df = _df(DETERMINISTIC_CSV)
        metrics = compute_metrics(df)
        assert metrics["latest_cash_reserve"] == 250000.0


class TestComputeMetricsWithLosses:
    """Tests with months that have losses."""

    def test_burn_rate_computed_for_loss_months(self):
        df = _df(LOSS_MONTHS_CSV)
        metrics = compute_metrics(df)
        # Months 1-2: revenue 100k, expenses 130k → loss. Burn rate = 130k
        assert metrics["burn_rate"] == 130000.0

    def test_contains_negative_profit(self):
        df = _df(LOSS_MONTHS_CSV)
        metrics = compute_metrics(df)
        assert any(p < 0 for p in metrics["monthly_profit"])

    def test_avg_profit_positive_overall(self):
        df = _df(LOSS_MONTHS_CSV)
        metrics = compute_metrics(df)
        # 2 months loss (-30k each) + 4 months profit (+140k each) → avg positive
        assert metrics["avg_monthly_profit"] > 0


class TestComputeMetricsSampleData:
    """Tests with the actual sample dataset."""

    def test_loads_and_computes(self):
        df = parse_csv(SAMPLE_CSV_PATH)
        metrics = compute_metrics(df)
        assert "avg_monthly_profit" in metrics
        assert "revenue_volatility" in metrics
        assert metrics["months_of_data"] == 12

    def test_sample_data_is_profitable(self):
        df = parse_csv(SAMPLE_CSV_PATH)
        metrics = compute_metrics(df)
        assert metrics["avg_monthly_profit"] > 0
        assert metrics["avg_profit_margin"] > 0

    def test_enriched_df_has_computed_columns(self):
        df = parse_csv(SAMPLE_CSV_PATH)
        metrics = compute_metrics(df)
        enriched = metrics["raw_df"]
        assert "total_expenses" in enriched.columns
        assert "monthly_profit" in enriched.columns
        assert "profit_margin" in enriched.columns

    def test_revenue_volatility_reasonable(self):
        df = parse_csv(SAMPLE_CSV_PATH)
        metrics = compute_metrics(df)
        # For a stable small business, CV should be < 0.5
        assert 0 < metrics["revenue_volatility"] < 0.5
