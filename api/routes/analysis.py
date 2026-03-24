"""
Analysis routes — CSV upload and synthetic data analysis.
"""

from __future__ import annotations

import io
import time
import os
from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

from src.csv_parser import parse_csv, CSVValidationError
from src.metrics_engine import compute_metrics
from src.health_score import calculate_health_score
from src.shock_models import ALL_SHOCKS
from src.simulation_engine import run_all_simulations, run_simulation
from src.synthetic_data import generate_synthetic_msme_data
from src.scheme_recommender import recommend_schemes
from src.cashflow_forecast import forecast_cashflow
from src.historical_backtest import run_historical_backtest
from src.llm_integration import (
    generate_llm_risks,
    generate_llm_roadmap,
    generate_executive_summary,
    is_llm_available,
)

router = APIRouter(prefix="/api", tags=["analysis"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class SyntheticRequest(BaseModel):
    business_type: str = Field(default="stable", description="stable | growing | struggling | seasonal")
    n_months: int = Field(default=12, ge=6, le=36)
    base_revenue: float = Field(default=500000)
    seed: int = Field(default=42)
    n_simulations: int = Field(default=1000, ge=100, le=5000)
    noise_std: float = Field(default=0.05, ge=0.01, le=0.30)


class CustomShockRequest(BaseModel):
    """Request body for running a custom shock scenario."""
    shock_name: str = Field(..., min_length=1, max_length=100, description="Name of the custom shock")
    revenue_impact: float = Field(default=0.0, ge=-1.0, le=1.0, description="Revenue change factor (-1 to 1). E.g. -0.4 = 40% drop")
    expense_impact: float = Field(default=0.0, ge=-0.5, le=1.0, description="Expense change factor. E.g. 0.15 = 15% increase")
    duration_months: int | None = Field(default=None, ge=1, le=36, description="Months affected (None = all months)")
    cash_reserve_impact: float = Field(default=0.0, ge=-1.0, le=0.0, description="Cash reserve change. E.g. -0.4 = 40% drop")
    n_simulations: int = Field(default=1000, ge=100, le=5000)
    noise_std: float = Field(default=0.05, ge=0.01, le=0.30)
    # The context: provide either synthetic params or uploaded CSV data
    business_type: str = Field(default="stable")
    n_months: int = Field(default=12, ge=6, le=36)
    base_revenue: float = Field(default=500000)
    seed: int = Field(default=42)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(df, n_simulations: int = 1000, noise_std: float = 0.05) -> dict:
    """Execute the full analysis pipeline with LLM-powered insights."""
    start = time.time()

    metrics = compute_metrics(df)
    health = calculate_health_score(metrics)
    sims = run_all_simulations(metrics, n_simulations=n_simulations, noise_std=noise_std, seed=42)

    # LLM-powered risk & roadmap (falls back to mock if no API key)
    risks = generate_llm_risks(metrics, health, sims)
    roadmap = generate_llm_roadmap(metrics, health, sims, risks)

    # Extra features
    schemes = recommend_schemes(metrics, health, sims)
    metrics_for_forecast = {k: v for k, v in metrics.items() if k != "raw_df"}
    enriched = metrics["raw_df"]
    metrics_for_forecast["months"] = enriched["month"].tolist()
    fc = forecast_cashflow(metrics_for_forecast, months_ahead=6, n_simulations=n_simulations)
    backtest = run_historical_backtest(metrics)

    # AI Executive Summary
    metrics_clean = {k: v for k, v in metrics.items() if k != "raw_df"}
    metrics_clean["months"] = enriched["month"].tolist()
    metrics_clean["revenues"] = enriched["revenue"].tolist()
    ai_summary = generate_executive_summary(metrics_clean, health, sims, fc, backtest)

    elapsed = time.time() - start

    # Data preview (first 6 rows)
    preview = df.head(6).to_dict(orient="records")

    llm_active = "openai" if os.environ.get("OPENAI_API_KEY") else "gemini" if os.environ.get("GOOGLE_API_KEY") else "mock"

    return {
        "metrics": metrics_clean,
        "health": health,
        "simulations": sims,
        "risks": risks,
        "roadmap": roadmap,
        "schemes": schemes,
        "forecast": fc,
        "backtest": backtest,
        "ai_summary": ai_summary,
        "llm_provider": llm_active,
        "elapsed_seconds": round(elapsed, 3),
        "data_preview": preview,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    n_simulations: int = 1000,
    noise_std: float = 0.05,
):
    """Upload a CSV and get full financial stress analysis."""
    try:
        contents = await file.read()
        buf = io.StringIO(contents.decode("utf-8"))
        df = parse_csv(buf)
    except CSVValidationError as e:
        raise HTTPException(status_code=422, detail={"errors": e.errors})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"errors": [str(e)]})

    result = _run_pipeline(df, n_simulations=n_simulations, noise_std=noise_std)
    return result


@router.post("/synthetic")
def analyze_synthetic(req: SyntheticRequest):
    """Generate synthetic data and run full analysis."""
    valid_types = ["stable", "growing", "struggling", "seasonal"]
    if req.business_type not in valid_types:
        raise HTTPException(status_code=422, detail={"errors": [f"Invalid business_type. Choose from: {valid_types}"]})

    df = generate_synthetic_msme_data(
        n_months=req.n_months,
        base_revenue=req.base_revenue,
        seed=req.seed,
        business_type=req.business_type,
    )
    result = _run_pipeline(df, n_simulations=req.n_simulations, noise_std=req.noise_std)
    return result


@router.post("/custom-shock")
def run_custom_shock(req: CustomShockRequest):
    """Run a custom user-defined shock scenario.

    Generates synthetic data, then applies the custom shock parameters
    and runs Monte Carlo simulations on the result.
    """
    from src.shock_models import _apply_revenue_shock, _apply_expense_shock
    import copy

    df = generate_synthetic_msme_data(
        n_months=req.n_months,
        base_revenue=req.base_revenue,
        seed=req.seed,
        business_type=req.business_type,
    )
    metrics = compute_metrics(df)

    # Build a custom shock function by composing the helpers
    def custom_shock_fn(m: dict) -> dict:
        result = copy.deepcopy(m)
        if req.revenue_impact != 0:
            result = _apply_revenue_shock(result, factor=req.revenue_impact, months=req.duration_months)
        if req.expense_impact != 0:
            result = _apply_expense_shock(result, factor=req.expense_impact)
        if req.cash_reserve_impact != 0:
            result["latest_cash_reserve"] = round(result["latest_cash_reserve"] * (1 + req.cash_reserve_impact), 2)
            result["avg_cash_reserve"] = round(result["avg_cash_reserve"] * (1 + req.cash_reserve_impact), 2)
        return result

    # Register temporarily for simulation
    from src.shock_models import ALL_SHOCKS
    custom_key = "_custom_user_shock"
    ALL_SHOCKS[custom_key] = {
        "name": req.shock_name,
        "description": f"Custom: rev {req.revenue_impact:+.0%}, exp {req.expense_impact:+.0%}, cash {req.cash_reserve_impact:+.0%}",
        "severity": "Custom",
        "function": custom_shock_fn,
    }

    try:
        sim_result = run_simulation(
            metrics=metrics,
            shock_key=custom_key,
            n_simulations=req.n_simulations,
            noise_std=req.noise_std,
            seed=req.seed,
        )
    finally:
        ALL_SHOCKS.pop(custom_key, None)

    return sim_result
