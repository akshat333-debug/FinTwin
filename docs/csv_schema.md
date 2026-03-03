# MSME Financial Data — CSV Schema

## Required Columns

| Column             | Type    | Description                                      | Example     |
|--------------------|---------|--------------------------------------------------|-------------|
| `month`            | string  | Month-Year in `YYYY-MM` format                   | 2025-01     |
| `revenue`          | float   | Total monthly revenue (INR)                       | 520000.00   |
| `fixed_costs`      | float   | Rent, salaries, EMIs — costs that don't vary      | 180000.00   |
| `variable_costs`   | float   | Raw materials, logistics, utilities               | 145000.00   |
| `loan_emi`         | float   | Monthly loan EMI payment (INR), 0 if none         | 35000.00    |
| `cash_reserve`     | float   | Cash/bank balance at end of month (INR)           | 310000.00   |

## Derived (computed in-code, NOT required in CSV)

| Metric              | Formula                                                  |
|----------------------|----------------------------------------------------------|
| `total_expenses`     | `fixed_costs + variable_costs + loan_emi`                |
| `monthly_profit`     | `revenue - total_expenses`                               |
| `profit_margin`      | `monthly_profit / revenue`                               |
| `burn_rate`          | `total_expenses` (when profit < 0)                       |
| `revenue_volatility` | `std(revenue) / mean(revenue)` across all months         |
| `fixed_ratio`        | `fixed_costs / total_expenses`                           |

## Constraints

- Minimum **6 rows** (6 months of data)
- No negative `revenue` or `cash_reserve`
- `month` values must be parseable as dates
- All numeric columns must be non-null (after cleaning)

## File Naming Convention

- Sample: `sample_msme_data.csv`
- Synthetic: `synthetic_msme_data_<N>.csv`
