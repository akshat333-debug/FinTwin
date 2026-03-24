"""
Reference routes — shocks, schemes, events, health check.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from src.shock_models import ALL_SHOCKS
from src.llm_integration import is_llm_available

router = APIRouter(prefix="/api", tags=["reference"])


class ShockInfo(BaseModel):
    key: str
    name: str
    description: str
    severity: str


@router.get("/shocks", response_model=list[ShockInfo])
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


@router.get("/health")
def health_check():
    """API health check."""
    return {
        "status": "ok",
        "version": "3.2.0",
        "llm_available": is_llm_available(),
        "llm_provider": "openai" if os.environ.get("OPENAI_API_KEY") else "gemini" if os.environ.get("GOOGLE_API_KEY") else None,
    }


@router.get("/events")
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


@router.get("/schemes/all")
def list_all_schemes():
    """List all available government schemes."""
    from src.scheme_recommender import SCHEMES
    return SCHEMES
