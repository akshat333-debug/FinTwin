# Project Overview

## Goal
Build a 30-second MSME financial stress simulator that:
- Accepts monthly revenue/expense CSV
- Runs India-specific stress simulations
- Outputs survival probability
- Generates actionable financial roadmap

## Tech Stack
Frontend: Streamlit
Backend: Python (FastAPI optional later)
Simulation: NumPy
LLM: OpenAI / local LLM wrapper
Database (later): PostgreSQL
Auth (later): Simple token-based

## Core Features
- CSV financial parser
- Health score engine (1-10)
- Monte Carlo stress simulator
- Survival probability gauge
- LLM-generated financial roadmap

## Constraints
- Must run locally
- Must generate results under 30 seconds
- Must handle imperfect CSVs
- Must work with synthetic dataset initially

## Definition of Done
- User uploads CSV
- System outputs survival % under 7 shocks
- Displays gauge visualization
- Generates 5 prioritized actions
- Code modular + testable
