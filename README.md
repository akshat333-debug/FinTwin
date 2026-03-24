# FinTwin — MSME Financial Stress Simulator

> **30-second financial stress testing** for Indian MSMEs using Monte Carlo simulation.

## Architecture

```
React Frontend (Vite) ← HTTP → FastAPI Backend ← Python Engine
       :5173                    :8000             (src/ modules)
```

### Backend Modules (api/routes/)
| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `analysis.py` | `/api/analyze`, `/api/synthetic`, `/api/custom-shock` | CSV, synthetic, and custom shock analysis |
| `chat.py` | `/api/chat` | Context-aware AI chat |
| `reference.py` | `/api/shocks`, `/api/health`, `/api/events`, `/api/schemes/all` | Reference data |
| `auth.py` | `/api/auth/register`, `/api/auth/login`, `/api/auth/history` | Authentication & history |

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

- **CSV Upload** — Parse & validate MSME financial CSVs (with optional granular expense columns)
- **Synthetic Data** — 4 business presets (stable, growing, struggling, seasonal)
- **Health Score** — 5-component 1–10 composite score with SVG gauge
- **Monte Carlo Simulation** — 1000+ iterations across 7 India-specific shocks
- **Custom Shock Builder** — Design your own what-if scenarios with sliders
- **Risk Analysis** — Severity-graded risk cards with evidence
- **Financial Roadmap** — 5 prioritized actions with timelines
- **Government Schemes** — Matched recommendations based on your profile
- **Cash Flow Forecast** — 6-month Monte Carlo projection with confidence bands
- **Historical Backtesting** — Test against 6 real Indian economic crises
- **AI Chat** — Context-aware conversational advisor (OpenAI/Gemini/mock)
- **Auth & History** — Token-based auth with analysis tracking over time
- **React Router** — URL-based navigation with bookmarkable pages
- **Error Boundaries** — Graceful error handling per dashboard section

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
| **Custom** | User-defined revenue/expense/cash impacts |

## CSV Schema

### Required Columns
`month`, `revenue`, `fixed_costs`, `variable_costs`, `loan_emi`, `cash_reserve`

### Optional Granular Expense Columns
`payroll`, `marketing`, `software`, `logistics` — enables specific LLM cost-cutting advice.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Upload CSV, get full analysis |
| POST | `/api/synthetic` | Generate synthetic data + analysis |
| POST | `/api/custom-shock` | Run custom shock scenario |
| POST | `/api/chat` | Context-aware AI chat |
| GET | `/api/shocks` | List available shock scenarios |
| GET | `/api/health` | API health check |
| GET | `/api/events` | List historical events |
| GET | `/api/schemes/all` | List government schemes |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, get token |
| GET | `/api/auth/me` | Current user info |
| POST | `/api/auth/history/save` | Save analysis to history |
| GET | `/api/auth/history` | List user's analysis history |

## Testing

```bash
python -m pytest tests/ -v
```

## Tech Stack

**Backend:** Python, FastAPI, NumPy, Pandas, SQLite
**Frontend:** React, Vite, React Router, Recharts, Framer Motion, Lucide Icons
**Simulation:** Monte Carlo with deterministic seeding
**LLM:** OpenAI / Google Gemini / Smart Fallback
**Auth:** Token-based with SQLite storage
