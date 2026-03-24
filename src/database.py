"""
Authentication & Analysis History Database.

Uses SQLite for lightweight local storage:
  - Users table with token-based authentication
  - Analysis history for tracking stress test results over time
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fintwin.db")


@contextmanager
def get_db():
    """Get a database connection with automatic commit/rollback."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                token TEXT UNIQUE,
                created_at REAL NOT NULL,
                last_login REAL
            );

            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at REAL NOT NULL,
                business_type TEXT,
                health_score REAL,
                health_grade TEXT,
                avg_revenue REAL,
                avg_profit REAL,
                profit_margin REAL,
                cash_reserve REAL,
                worst_shock TEXT,
                worst_survival_pct REAL,
                best_shock TEXT,
                best_survival_pct REAL,
                bankruptcy_prob REAL,
                ai_summary TEXT,
                full_result TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_history_user ON analysis_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_history_date ON analysis_history(created_at);
        """)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str) -> dict:
    """Register a new user. Returns user dict with token."""
    init_db()
    token = secrets.token_hex(32)
    now = time.time()
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, token, created_at) VALUES (?, ?, ?, ?)",
                (username, _hash_password(password), token, now),
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username}' already exists")

    return {"username": username, "token": token}


def login_user(username: str, password: str) -> dict:
    """Authenticate user and return a new token."""
    init_db()
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not row or row["password_hash"] != _hash_password(password):
            raise ValueError("Invalid username or password")

        token = secrets.token_hex(32)
        conn.execute(
            "UPDATE users SET token = ?, last_login = ? WHERE id = ?",
            (token, time.time(), row["id"]),
        )

    return {"username": username, "token": token}


def get_user_by_token(token: str) -> dict | None:
    """Verify a token and return user info, or None."""
    init_db()
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE token = ?",
            (token,),
        ).fetchone()
        if row:
            return {"id": row["id"], "username": row["username"], "created_at": row["created_at"]}
    return None


# ---------------------------------------------------------------------------
# Analysis history
# ---------------------------------------------------------------------------

def save_analysis(user_id: int, result: dict, business_type: str = "unknown") -> int:
    """Save an analysis result to history. Returns the history entry ID."""
    init_db()
    metrics = result.get("metrics", {})
    health = result.get("health", {})
    sims = result.get("simulations", [])
    forecast = result.get("forecast", {})

    worst = min(sims, key=lambda s: s["survival_probability"]) if sims else {}
    best = max(sims, key=lambda s: s["survival_probability"]) if sims else {}

    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO analysis_history
               (user_id, created_at, business_type, health_score, health_grade,
                avg_revenue, avg_profit, profit_margin, cash_reserve,
                worst_shock, worst_survival_pct, best_shock, best_survival_pct,
                bankruptcy_prob, ai_summary, full_result)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                time.time(),
                business_type,
                health.get("health_score"),
                health.get("grade"),
                metrics.get("avg_revenue"),
                metrics.get("avg_monthly_profit"),
                metrics.get("avg_profit_margin"),
                metrics.get("latest_cash_reserve"),
                worst.get("shock_name"),
                worst.get("survival_percentage"),
                best.get("shock_name"),
                best.get("survival_percentage"),
                forecast.get("prob_bankrupt_by_end"),
                result.get("ai_summary", ""),
                json.dumps(result, default=str),
            ),
        )
        return cursor.lastrowid


def get_analysis_history(user_id: int, limit: int = 20) -> list[dict]:
    """Retrieve analysis history for a user (newest first)."""
    init_db()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, created_at, business_type, health_score, health_grade,
                      avg_revenue, avg_profit, profit_margin, cash_reserve,
                      worst_shock, worst_survival_pct, best_shock, best_survival_pct,
                      bankruptcy_prob, ai_summary
               FROM analysis_history
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_analysis_detail(user_id: int, analysis_id: int) -> dict | None:
    """Retrieve full analysis result by ID."""
    init_db()
    with get_db() as conn:
        row = conn.execute(
            "SELECT full_result FROM analysis_history WHERE id = ? AND user_id = ?",
            (analysis_id, user_id),
        ).fetchone()
        if row:
            return json.loads(row["full_result"])
    return None


# Initialize DB on import
init_db()
