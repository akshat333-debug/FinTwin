# FinTwin — MSME Financial Stress Simulator

> **30-second financial stress testing** for Indian MSMEs using Monte Carlo simulation.

## Architecture

```
React Frontend (Vite) ← HTTP → FastAPI Backend ← Python Engine
       :5173                    :8000             (src/ modules)
```

## Quick Start

```bash
# 1 — Install Python deps
pip install -r requirements.txt

# 2 — Start backend
uvicorn api.main:app --reload --port 8000

# 3 — Start frontend
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173** in your browser.

## Features

- **CSV Upload** — Parse & validate MSME financial CSVs
- **Synthetic Data** — 4 business presets (stable, growing, struggling, seasonal)
- **Health Score** — 5-component 1–10 composite score with SVG gauge
- **Monte Carlo Simulation** — 1000+ iterations across 7 India-specific shocks
- **Risk Analysis** — Severity-graded risk cards with evidence
- **Financial Roadmap** — 5 prioritized actions with timelines

## Shocks Modeled

| Shock | Impact |
|-------|--------|
| Recession | −20% revenue |
| GST Hike | +5% expenses |
| Fuel/Logistics Spike | +10% expenses |
| Pandemic Lockdown | −35% revenue (3 months) |
| Credit Freeze | −40% cash, −15% revenue (3 months) |
| Demonetization | −50% revenue (2 months) |
| Inflation Shock | +15% expenses |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Upload CSV, get full analysis |
| POST | `/api/synthetic` | Generate synthetic data + analysis |
| GET | `/api/shocks` | List available shock scenarios |
| GET | `/api/health` | API health check |

## Testing

```bash
python -m pytest tests/ -v  # 79 tests
```

## Tech Stack

**Backend:** Python, FastAPI, NumPy, Pandas  
**Frontend:** React, Vite, Recharts, Framer Motion, Lucide Icons  
**Simulation:** Monte Carlo with deterministic seeding  
**LLM-ready:** Prompt templates for OpenAI integration (currently using mock generators)
