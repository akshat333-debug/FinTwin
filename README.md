# FinTwin — MSME Financial Stress Simulator 🏦

30-second financial stress simulator for Indian MSMEs. Upload your revenue/expense CSV, run India-specific shock simulations, and get a survival probability with an actionable financial roadmap.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features

- **CSV Financial Parser** — Validates and cleans MSME financial data
- **Health Score Engine** — 1-10 composite score with 5 weighted components
- **7 India-Specific Shocks** — Recession, GST hike, fuel spike, pandemic, credit freeze, demonetization, inflation
- **Monte Carlo Simulator** — 1000+ stochastic simulations per shock scenario
- **Survival Probability Gauge** — Visual probability of surviving each shock
- **Risk Analysis** — Top 3 risks ranked by severity
- **Financial Roadmap** — 5 prioritized actions tied to simulation output

## Architecture

```
CSV Upload → parse_csv() → compute_metrics() → calculate_health_score()
                                    ↓
                          run_all_simulations()
                                    ↓
                     generate_risks() + generate_roadmap()
                                    ↓
                            Streamlit UI
```

**Key design decision:** Python handles all deterministic financial calculations. LLM is reserved *only* for narrative risk explanation and roadmap generation.

## Project Structure

```
FinTwin/
├── app.py                    # Streamlit UI + pipeline integration
├── requirements.txt
├── PROJECT.md
├── TASKS.md
├── data/
│   └── sample_msme_data.csv  # 12-month sample dataset
├── docs/
│   └── csv_schema.md         # CSV field documentation
├── src/
│   ├── csv_parser.py         # CSV ingestion + validation
│   ├── metrics_engine.py     # Financial metrics computation
│   ├── health_score.py       # 1-10 health score engine
│   ├── shock_models.py       # 7 India-specific shocks
│   ├── survival_rule.py      # Bankruptcy/survival logic
│   ├── simulation_engine.py  # Monte Carlo engine
│   ├── llm_prompts.py        # LLM prompt templates + mock generators
│   └── synthetic_data.py     # Synthetic MSME data generator
└── tests/
    ├── test_csv_parser.py
    ├── test_metrics_engine.py
    └── test_simulation_core.py
```

## Testing

```bash
python -m pytest tests/ -v
```
