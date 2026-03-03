"""
FinTwin FastAPI Backend.

Exposes the Python simulation engine as REST endpoints.
"""

from __future__ import annotations

import io
import time
from typing import Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_parser import parse_csv, CSVValidationError
from src.metrics_engine import compute_metrics
from src.health_score import calculate_health_score
from src.shock_models import ALL_SHOCKS
from src.simulation_engine import run_all_simulations
from src.llm_prompts import generate_mock_risks, generate_mock_roadmap
from src.synthetic_data import generate_synthetic_msme_data
from src.scheme_recommender import recommend_schemes
from src.cashflow_forecast import forecast_cashflow
from src.historical_backtest import run_historical_backtest

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FinTwin API",
    description="MSME Financial Stress Simulator",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class AnalyzeRequest(BaseModel):
    n_simulations: int = Field(default=1000, ge=100, le=5000)
    noise_std: float = Field(default=0.05, ge=0.01, le=0.30)


class ShockInfo(BaseModel):
    key: str
    name: str
    description: str
    severity: str


class SimulationResult(BaseModel):
    shock_key: str
    shock_name: str
    survival_probability: float
    survival_percentage: float
    n_simulations: int
    survived_count: int
    failed_count: int
    avg_months_survived: float
    worst_case_months: int


class RiskItem(BaseModel):
    risk_name: str
    severity: str
    explanation: str
    evidence: str


class RoadmapAction(BaseModel):
    action: str
    impact: str
    timeline: str
    priority: int
    category: str


class HealthResult(BaseModel):
    health_score: float
    component_scores: dict[str, float]
    grade: str
    interpretation: str


class MetricsResult(BaseModel):
    monthly_profit: list[float]
    total_expenses: list[float]
    profit_margins: list[float]
    avg_monthly_profit: float
    avg_profit_margin: float
    burn_rate: float
    revenue_volatility: float
    fixed_cost_ratio: float
    avg_revenue: float
    avg_expenses: float
    avg_cash_reserve: float
    latest_cash_reserve: float
    months_of_data: int
    revenue_trend: float
    months: list[str]
    revenues: list[float]


class FullAnalysisResponse(BaseModel):
    metrics: MetricsResult
    health: HealthResult
    simulations: list[SimulationResult]
    risks: list[RiskItem]
    roadmap: list[RoadmapAction]
    schemes: list[dict[str, Any]]
    forecast: dict[str, Any]
    backtest: list[dict[str, Any]]
    elapsed_seconds: float
    data_preview: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(df, n_simulations: int = 1000, noise_std: float = 0.05) -> dict:
    """Execute the full analysis pipeline."""
    start = time.time()

    metrics = compute_metrics(df)
    health = calculate_health_score(metrics)
    sims = run_all_simulations(metrics, n_simulations=n_simulations, noise_std=noise_std, seed=42)
    risks = generate_mock_risks(metrics, sims)
    roadmap = generate_mock_roadmap(metrics, sims, risks)

    # New features
    schemes = recommend_schemes(metrics, health, sims)
    metrics_for_forecast = {k: v for k, v in metrics.items() if k != "raw_df"}
    enriched = metrics["raw_df"]
    metrics_for_forecast["months"] = enriched["month"].tolist()
    fc = forecast_cashflow(metrics_for_forecast, months_ahead=6, n_simulations=n_simulations)
    backtest = run_historical_backtest(metrics)

    elapsed = time.time() - start

    # Build serializable metrics (exclude raw_df)
    metrics_clean = {k: v for k, v in metrics.items() if k != "raw_df"}
    metrics_clean["months"] = enriched["month"].tolist()
    metrics_clean["revenues"] = enriched["revenue"].tolist()

    # Data preview (first 6 rows)
    preview = df.head(6).to_dict(orient="records")

    return {
        "metrics": metrics_clean,
        "health": health,
        "simulations": sims,
        "risks": risks,
        "roadmap": roadmap,
        "schemes": schemes,
        "forecast": fc,
        "backtest": backtest,
        "elapsed_seconds": round(elapsed, 3),
        "data_preview": preview,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/shocks", response_model=list[ShockInfo])
def list_shocks():
    """List all available shock scenarios."""
    return [
        ShockInfo(
            key=key,
            name=info["name"],
            description=info["description"],
            severity=info["severity"],
        )
        for key, info in ALL_SHOCKS.items()
    ]


@app.post("/api/analyze", response_model=FullAnalysisResponse)
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


@app.post("/api/synthetic", response_model=FullAnalysisResponse)
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


@app.get("/api/health")
def health_check():
    """API health check."""
    return {"status": "ok", "version": "3.0.0"}


@app.get("/api/events")
def list_events():
    """List available historical events for backtesting."""
    from src.historical_backtest import HISTORICAL_EVENTS
    return [
        {
            "id": e["id"],
            "name": e["name"],
            "year": e["year"],
            "period": e["period"],
            "severity": e["severity"],
            "icon": e["icon"],
        }
        for e in HISTORICAL_EVENTS
    ]


@app.get("/api/schemes/all")
def list_all_schemes():
    """List all available government schemes."""
    from src.scheme_recommender import SCHEMES
    return SCHEMES
