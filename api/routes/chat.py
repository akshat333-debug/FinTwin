"""
Chat routes — AI-powered financial data chatbot.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.llm_integration import answer_chat_question

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    context: dict[str, Any] = Field(default_factory=dict)
    active_page: str = Field(default="dashboard", description="The frontend page the user is currently viewing")


# ── In-memory store for last analysis (for chat context) ──
_last_analysis: dict | None = None


@router.post("/chat")
def chat(req: ChatRequest):
    """Chat with your financial data using AI — now context-aware."""
    global _last_analysis

    # Use provided context or fallback to last analysis
    ctx = req.context if req.context else _last_analysis
    if not ctx:
        return {
            "answer": "Please run a financial analysis first before chatting. I need your data to provide insights.",
            "llm_provider": "none",
        }

    answer = answer_chat_question(
        question=req.question,
        metrics=ctx.get("metrics", {}),
        health=ctx.get("health", {}),
        simulation_results=ctx.get("simulations", []),
        forecast=ctx.get("forecast", {}),
        backtest=ctx.get("backtest", []),
        schemes=ctx.get("schemes", []),
        active_page=req.active_page,
    )

    return {
        "answer": answer,
        "llm_provider": "openai" if os.environ.get("OPENAI_API_KEY") else "gemini" if os.environ.get("GOOGLE_API_KEY") else "mock",
    }
