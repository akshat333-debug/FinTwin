"""Task 1 validation: Verify sample CSV loads correctly and meets schema requirements."""
import pandas as pd
import sys
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_msme_data.csv")

REQUIRED_COLUMNS = ["month", "revenue", "fixed_costs", "variable_costs", "loan_emi", "cash_reserve"]
MIN_ROWS = 6


def validate():
    errors = []

    # 1. File exists
    if not os.path.exists(CSV_PATH):
        print(f"FAIL: CSV not found at {CSV_PATH}")
        return False

    # 2. Load CSV
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"FAIL: Could not load CSV — {e}")
        return False

    # 3. Required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # 4. Minimum rows
    if len(df) < MIN_ROWS:
        errors.append(f"Need >= {MIN_ROWS} rows, got {len(df)}")

    # 5. No negative revenue or cash_reserve
    if (df["revenue"] < 0).any():
        errors.append("Negative revenue found")
    if (df["cash_reserve"] < 0).any():
        errors.append("Negative cash_reserve found")

    # 6. Month parseable
    try:
        pd.to_datetime(df["month"], format="%Y-%m")
    except Exception:
        errors.append("'month' column not parseable as YYYY-MM dates")

    # 7. No nulls in numeric columns
    numeric_cols = REQUIRED_COLUMNS[1:]  # everything except 'month'
    nulls = df[numeric_cols].isnull().sum()
    if nulls.any():
        errors.append(f"Null values found: {nulls[nulls > 0].to_dict()}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return False

    print(f"PASS: CSV loaded successfully — {len(df)} rows, {len(df.columns)} columns")
    print(f"PASS: All {len(REQUIRED_COLUMNS)} required columns present")
    print(f"PASS: {len(df)} months of data (>= {MIN_ROWS} required)")
    print(f"PASS: No negative revenue or cash_reserve")
    print(f"PASS: All months parseable as dates")
    print(f"PASS: No null values in numeric columns")
    print(f"\nSample:\n{df.head(3).to_string(index=False)}")
    return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
