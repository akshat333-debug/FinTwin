"""
Auth routes — user registration, login, and analysis history.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from src.database import (
    register_user,
    login_user,
    get_user_by_token,
    save_analysis,
    get_analysis_history,
    get_analysis_detail,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class SaveAnalysisRequest(BaseModel):
    result: dict[str, Any]
    business_type: str = "unknown"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_current_user(authorization: str | None = Header(None)) -> dict:
    """Extract and verify user from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register")
def register(req: RegisterRequest):
    """Register a new user."""
    try:
        result = register_user(req.username, req.password)
        return {"status": "ok", **result}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
def login(req: LoginRequest):
    """Log in and receive an auth token."""
    try:
        result = login_user(req.username, req.password)
        return {"status": "ok", **result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
def get_me(authorization: str | None = Header(None)):
    """Get current user info from token."""
    user = _get_current_user(authorization)
    return {"username": user["username"], "user_id": user["id"]}


@router.post("/history/save")
def save_history(req: SaveAnalysisRequest, authorization: str | None = Header(None)):
    """Save an analysis result to the user's history."""
    user = _get_current_user(authorization)
    entry_id = save_analysis(user["id"], req.result, req.business_type)
    return {"status": "saved", "id": entry_id}


@router.get("/history")
def list_history(limit: int = 20, authorization: str | None = Header(None)):
    """List recent analysis history for the logged-in user."""
    user = _get_current_user(authorization)
    history = get_analysis_history(user["id"], limit=limit)
    return {"history": history}


@router.get("/history/{analysis_id}")
def get_history_detail(analysis_id: int, authorization: str | None = Header(None)):
    """Get full analysis detail by ID."""
    user = _get_current_user(authorization)
    detail = get_analysis_detail(user["id"], analysis_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return detail
