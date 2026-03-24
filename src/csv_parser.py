"""
CSV Ingestion & Validation Module.

Provides `parse_csv(file_path_or_buffer)` that:
  1. Reads a CSV from a file path or file-like object (Streamlit UploadedFile).
  2. Validates required columns, data types, and value constraints.
  3. Returns a cleaned pandas DataFrame ready for downstream processing.

Raises `CSVValidationError` with a human-readable message on failure.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Union

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: list[str] = [
    "month",
    "revenue",
    "fixed_costs",
    "variable_costs",
    "loan_emi",
    "cash_reserve",
]

# Optional granular expense categories (backward compatible)
OPTIONAL_EXPENSE_COLUMNS: list[str] = [
    "payroll",
    "marketing",
    "software",
    "logistics",
]

NUMERIC_COLUMNS: list[str] = [
    "revenue",
    "fixed_costs",
    "variable_costs",
    "loan_emi",
    "cash_reserve",
]

MIN_ROWS: int = 6

# ---------------------------------------------------------------------------
# Custom Exception
# ---------------------------------------------------------------------------


class CSVValidationError(Exception):
    """Raised when the uploaded CSV fails schema/data validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("CSV validation failed:\n" + "\n".join(f"  • {e}" for e in errors))


# ---------------------------------------------------------------------------
# Validation Result
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Container for validation outcome."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def parse_csv(source: Union[str, io.IOBase, "streamlit.runtime.uploaded_file_manager.UploadedFile"]) -> pd.DataFrame:
    """Parse and validate an MSME financial CSV.

    Parameters
    ----------
    source : str | file-like
        File path (str) or file-like object (e.g. Streamlit UploadedFile).

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with validated columns and sorted by month.

    Raises
    ------
    CSVValidationError
        If the CSV fails any validation check.
    """
    result = ValidationResult()

    # ------------------------------------------------------------------
    # 1. Read CSV
    # ------------------------------------------------------------------
    try:
        if isinstance(source, str):
            df = pd.read_csv(source)
        else:
            df = pd.read_csv(source)
    except pd.errors.EmptyDataError:
        result.add_error("CSV file is empty.")
        raise CSVValidationError(result.errors)
    except Exception as exc:
        result.add_error(f"Could not read CSV: {exc}")
        raise CSVValidationError(result.errors)

    # ------------------------------------------------------------------
    # 2. Normalize column names (lowercase, strip whitespace)
    # ------------------------------------------------------------------
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # ------------------------------------------------------------------
    # 3. Check required columns
    # ------------------------------------------------------------------
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        result.add_error(f"Missing required columns: {missing}")

    # Bail early if columns are missing — further checks won't work.
    if not result.is_valid:
        raise CSVValidationError(result.errors)

    # ------------------------------------------------------------------
    # 4. Minimum row count
    # ------------------------------------------------------------------
    if len(df) < MIN_ROWS:
        result.add_error(f"Need at least {MIN_ROWS} rows of data, got {len(df)}.")

    # ------------------------------------------------------------------
    # 5. Coerce numeric columns (required + optional)
    # ------------------------------------------------------------------
    present_optional = [col for col in OPTIONAL_EXPENSE_COLUMNS if col in df.columns]
    all_numeric = NUMERIC_COLUMNS + present_optional

    for col in all_numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------------------------------------------------------
    # 6. Handle missing values — fill with 0 and warn
    # ------------------------------------------------------------------
    null_counts = df[all_numeric].isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        result.add_warning(
            f"Null/unparseable values found and filled with 0: "
            f"{cols_with_nulls.to_dict()}"
        )
        df[all_numeric] = df[all_numeric].fillna(0.0)

    # Tag which granular expense columns are present
    df.attrs["granular_expenses"] = present_optional

    # ------------------------------------------------------------------
    # 7. Validate month column is parseable
    # ------------------------------------------------------------------
    try:
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m").dt.strftime("%Y-%m")
    except Exception:
        try:
            # Fallback: try flexible date parsing
            df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")
            result.add_warning("Month column parsed with flexible format (not strict YYYY-MM).")
        except Exception:
            result.add_error("'month' column contains unparseable date values.")

    # ------------------------------------------------------------------
    # 8. No negative revenue or cash_reserve
    # ------------------------------------------------------------------
    if (df["revenue"] < 0).any():
        result.add_error("Revenue contains negative values.")
    if (df["cash_reserve"] < 0).any():
        result.add_error("Cash reserve contains negative values.")

    # ------------------------------------------------------------------
    # Raise if any errors accumulated
    # ------------------------------------------------------------------
    if not result.is_valid:
        raise CSVValidationError(result.errors)

    # ------------------------------------------------------------------
    # 9. Sort by month and reset index
    # ------------------------------------------------------------------
    df = df.sort_values("month").reset_index(drop=True)

    return df


def get_validation_warnings(source: Union[str, io.IOBase]) -> list[str]:
    """Return any non-fatal warnings from parsing (for UI display).

    This is a helper that wraps parse_csv and captures warnings.
    """
    result = ValidationResult()
    try:
        parse_csv(source)
    except CSVValidationError:
        pass  # errors handled elsewhere

    # Re-run lightweight checks for warnings only
    warnings: list[str] = []
    try:
        if isinstance(source, str):
            df = pd.read_csv(source)
        else:
            source.seek(0)
            df = pd.read_csv(source)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        null_counts = df[NUMERIC_COLUMNS].isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]
        if not cols_with_nulls.empty:
            warnings.append(
                f"Null values filled with 0: {cols_with_nulls.to_dict()}"
            )
    except Exception:
        pass

    return warnings
