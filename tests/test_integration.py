"""Integration tests for LLM prompts, synthetic data, and full pipeline (Tasks 9-12)."""

import io
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_parser import parse_csv
from src.metrics_engine import compute_metrics
from src.health_score import calculate_health_score
from src.simulation_engine import run_all_simulations
from src.llm_prompts import (
    build_risk_prompt,
    build_roadmap_prompt,
    generate_mock_risks,
    generate_mock_roadmap,
)
from src.synthetic_data import (
    generate_synthetic_msme_data,
    generate_multiple_datasets,
)


SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_msme_data.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_pipeline(df):
    """Run full pipeline and return all results."""
    metrics = compute_metrics(df)
    health = calculate_health_score(metrics)
    sims = run_all_simulations(metrics, n_simulations=100, seed=42)
    risks = generate_mock_risks(metrics, sims)
    roadmap = generate_mock_roadmap(metrics, sims, risks)
    return metrics, health, sims, risks, roadmap


# ===========================================================================
# Task 9: LLM Risk Prompt Tests
# ===========================================================================

class TestLLMRiskPrompts:
    def test_risk_prompt_contains_metrics(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, _, _ = _full_pipeline(df)
        prompt = build_risk_prompt(metrics, health, sims)
        assert "Revenue" in prompt
        assert "Profit" in prompt
        assert "Health Score" in prompt

    def test_risk_prompt_contains_simulation_results(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, _, _ = _full_pipeline(df)
        prompt = build_risk_prompt(metrics, health, sims)
        assert "Recession" in prompt
        assert "survival" in prompt.lower()

    def test_risk_prompt_requests_json(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, _, _ = _full_pipeline(df)
        prompt = build_risk_prompt(metrics, health, sims)
        assert "JSON" in prompt

    def test_mock_risks_returns_three(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, _, sims, risks, _ = _full_pipeline(df)
        assert len(risks) == 3

    def test_mock_risks_have_required_fields(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, _, sims, risks, _ = _full_pipeline(df)
        for risk in risks:
            assert "risk_name" in risk
            assert "severity" in risk
            assert "explanation" in risk
            assert "evidence" in risk

    def test_mock_risks_severity_valid(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, _, sims, risks, _ = _full_pipeline(df)
        valid_severities = {"Critical", "High", "Medium", "Low"}
        for risk in risks:
            assert risk["severity"] in valid_severities


# ===========================================================================
# Task 10: LLM Roadmap Tests
# ===========================================================================

class TestLLMRoadmapPrompts:
    def test_roadmap_prompt_contains_metrics(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, risks, _ = _full_pipeline(df)
        prompt = build_roadmap_prompt(metrics, health, sims, risks)
        assert "Revenue" in prompt
        assert "Health Score" in prompt

    def test_roadmap_prompt_contains_weakest_scenarios(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, risks, _ = _full_pipeline(df)
        prompt = build_roadmap_prompt(metrics, health, sims, risks)
        assert "survival" in prompt.lower()

    def test_mock_roadmap_returns_five_actions(self):
        df = parse_csv(SAMPLE_CSV)
        _, _, _, _, roadmap = _full_pipeline(df)
        assert len(roadmap) == 5

    def test_mock_roadmap_has_required_fields(self):
        df = parse_csv(SAMPLE_CSV)
        _, _, _, _, roadmap = _full_pipeline(df)
        for action in roadmap:
            assert "action" in action
            assert "impact" in action
            assert "timeline" in action
            assert "priority" in action
            assert "category" in action

    def test_mock_roadmap_priorities_ordered(self):
        df = parse_csv(SAMPLE_CSV)
        _, _, _, _, roadmap = _full_pipeline(df)
        priorities = [a["priority"] for a in roadmap]
        assert priorities == [1, 2, 3, 4, 5]

    def test_mock_roadmap_categories_valid(self):
        df = parse_csv(SAMPLE_CSV)
        _, _, _, _, roadmap = _full_pipeline(df)
        valid_categories = {
            "Cost Reduction", "Revenue Growth", "Cash Management",
            "Risk Mitigation", "Operational Efficiency",
        }
        for action in roadmap:
            assert action["category"] in valid_categories


# ===========================================================================
# Task 12: Synthetic Data Tests
# ===========================================================================

class TestSyntheticData:
    def test_generates_correct_row_count(self):
        df = generate_synthetic_msme_data(n_months=12, seed=42)
        assert len(df) == 12

    def test_generates_correct_columns(self):
        df = generate_synthetic_msme_data(seed=42)
        expected = {"month", "revenue", "fixed_costs", "variable_costs", "loan_emi", "cash_reserve"}
        assert set(df.columns) == expected

    def test_no_negative_values(self):
        df = generate_synthetic_msme_data(seed=42)
        assert (df["revenue"] >= 0).all()
        assert (df["cash_reserve"] >= 0).all()

    def test_deterministic_with_seed(self):
        df1 = generate_synthetic_msme_data(seed=42)
        df2 = generate_synthetic_msme_data(seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self):
        df1 = generate_synthetic_msme_data(seed=42)
        df2 = generate_synthetic_msme_data(seed=99)
        assert not df1["revenue"].equals(df2["revenue"])

    def test_struggling_business_lower_profit(self):
        df_stable = generate_synthetic_msme_data(seed=42, business_type="stable")
        df_struggle = generate_synthetic_msme_data(seed=42, business_type="struggling")
        m_stable = compute_metrics(df_stable)
        m_struggle = compute_metrics(df_struggle)
        assert m_struggle["avg_profit_margin"] < m_stable["avg_profit_margin"]

    def test_growing_business_trend(self):
        df = generate_synthetic_msme_data(seed=42, business_type="growing")
        m = compute_metrics(df)
        assert m["revenue_trend"] > 0  # growing business should have positive trend

    def test_multiple_datasets_returns_four(self):
        datasets = generate_multiple_datasets(n_datasets=4, seed=42)
        assert len(datasets) == 4
        assert set(datasets.keys()) == {"stable", "growing", "struggling", "seasonal"}

    def test_synthetic_data_passes_csv_validation(self):
        """Synthetic data should be parseable by our CSV parser."""
        df = generate_synthetic_msme_data(n_months=12, seed=42)
        # Save to buffer and re-parse
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        parsed = parse_csv(buf)
        assert len(parsed) == 12

    def test_all_business_types_work_end_to_end(self):
        """Full pipeline should work for all business types."""
        for btype in ["stable", "growing", "struggling", "seasonal"]:
            df = generate_synthetic_msme_data(n_months=12, seed=42, business_type=btype)
            metrics, health, sims, risks, roadmap = _full_pipeline(df)
            assert 1.0 <= health["health_score"] <= 10.0
            assert len(sims) == 7
            assert len(risks) == 3
            assert len(roadmap) == 5


# ===========================================================================
# Task 11: Full Pipeline Integration Tests
# ===========================================================================

class TestFullPipeline:
    def test_under_30_seconds(self):
        """Full pipeline must complete under 30 seconds."""
        import time
        start = time.time()
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, risks, roadmap = _full_pipeline(df)
        elapsed = time.time() - start
        assert elapsed < 30.0, f"Pipeline took {elapsed:.1f}s (limit: 30s)"

    def test_sample_csv_full_pipeline(self):
        df = parse_csv(SAMPLE_CSV)
        metrics, health, sims, risks, roadmap = _full_pipeline(df)

        # Health score
        assert 1.0 <= health["health_score"] <= 10.0
        assert health["grade"] in ("Critical", "Poor", "Fair", "Good", "Excellent")

        # Simulations
        assert len(sims) == 7
        for s in sims:
            assert 0.0 <= s["survival_probability"] <= 1.0

        # Risks
        assert len(risks) == 3

        # Roadmap
        assert len(roadmap) == 5

    def test_synthetic_struggling_has_lower_survival(self):
        """A struggling business should have lower survival than stable."""
        df_stable = generate_synthetic_msme_data(seed=42, business_type="stable")
        df_struggle = generate_synthetic_msme_data(seed=42, business_type="struggling")

        _, _, sims_stable, _, _ = _full_pipeline(df_stable)
        _, _, sims_struggle, _, _ = _full_pipeline(df_struggle)

        avg_stable = sum(s["survival_percentage"] for s in sims_stable) / len(sims_stable)
        avg_struggle = sum(s["survival_percentage"] for s in sims_struggle) / len(sims_struggle)

        assert avg_struggle < avg_stable, (
            f"Struggling ({avg_struggle:.1f}%) should survive less than stable ({avg_stable:.1f}%)"
        )
