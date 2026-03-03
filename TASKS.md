# Task List

## Task 1
Description:
Design CSV schema standard and sample test CSV.

Expected Output:
- sample_msme_data.csv
- Documented required fields

Validation:
- CSV loads without error
- Contains 6 months revenue + expenses

---

## Task 2
Description:
Build CSV ingestion + validation module.

Expected Output:
- Function: parse_csv(file) -> cleaned DataFrame

Validation:
- Reject missing columns
- Handle empty values
- Unit test for malformed CSV

---

## Task 3
Description:
Compute financial metrics.

Metrics:
- Monthly profit
- Profit margin
- Burn rate
- Revenue volatility
- Fixed vs variable cost ratio

Expected Output:
- Function: compute_metrics(df) -> metrics dict

Validation:
- Values correct for sample dataset

---

## Task 4
Description:
Implement Health Score Engine (1–10 scale).

Expected Output:
- Function: calculate_health_score(metrics)

Validation:
- High profit → higher score
- Negative margin → score < 4

---

## Task 5
Description:
Define 7 India-specific shock models.

Shocks:
- Recession (-20% revenue)
- GST hike (+5% expenses)
- Fuel spike (+10% logistics)
- Pandemic (-35% revenue 3 months)
- Credit freeze (cashflow delay)
- Demonetization (short-term drop)
- Inflation shock

Expected Output:
- shock_functions.py

Validation:
- Each shock modifies baseline correctly

---

## Task 6
Description:
Build Monte Carlo engine (1000 simulations).

Expected Output:
- Function: run_simulation(metrics, shock)

Validation:
- Returns survival probability
- Deterministic seed test

---

## Task 7
Description:
Define survival logic.

Example:
- Survive if cash > 0 for 6 months
- Bankruptcy if cumulative loss exceeds threshold

Expected Output:
- survival_rule.py

Validation:
- Known input produces known survival %

---

## Task 8
Description:
Build survival probability visualization.

Expected Output:
- Streamlit gauge / bar chart

Validation:
- Displays correct value

---

## Task 9
Description:
LLM prompt template for risk summary.

Expected Output:
- Prompt template file
- Top 3 risks generated

Validation:
- Output references computed metrics

---

## Task 10
Description:
LLM roadmap generator (5 prioritized actions).

Expected Output:
- Structured JSON:
  {
    action,
    impact,
    timeline
  }

Validation:
- At least 5 actions
- Actions tied to simulation output

---

## Task 11
Description:
Integrate pipeline: CSV → Metrics → Simulation → LLM → UI

Expected Output:
- End-to-end working MVP

Validation:
- Full flow under 30 seconds

---

## Task 12
Description:
Add synthetic dataset generator (Faker).

Expected Output:
- generate_synthetic_msme_data(n)

Validation:
- Generates realistic financial data
