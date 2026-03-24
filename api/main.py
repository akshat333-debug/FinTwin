"""
FinTwin FastAPI Backend.

Exposes the Python simulation engine as REST endpoints.
Uses modular APIRouter architecture for clean separation of concerns.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.routes.analysis import router as analysis_router
from api.routes.chat import router as chat_router
from api.routes.reference import router as reference_router
from api.routes.auth import router as auth_router

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FinTwin API",
    description="MSME Financial Stress Simulator",
    version="3.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------

app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(reference_router)
app.include_router(auth_router)
