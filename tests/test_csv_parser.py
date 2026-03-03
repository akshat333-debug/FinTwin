"""Unit tests for CSV ingestion + validation module (Task 2)."""

import io
import os
import tempfile

import pandas as pd
import pytest

# Add project root to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_parser import parse_csv, CSVValidationError, REQUIRED_COLUMNS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_msme_data.csv")

VALID_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,520000,180000,145000,35000,310000
2025-02,485000,180000,138000,35000,347000
2025-03,560000,180000,155000,35000,437000
2025-04,510000,182000,142000,35000,488000
2025-05,475000,182000,135000,35000,511000
2025-06,530000,182000,150000,35000,574000
"""

MISSING_COLUMN_CSV = """month,revenue,fixed_costs
2025-01,520000,180000
2025-02,485000,180000
2025-03,560000,180000
2025-04,510000,182000
2025-05,475000,182000
2025-06,530000,182000
"""

TOO_FEW_ROWS_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,520000,180000,145000,35000,310000
2025-02,485000,180000,138000,35000,347000
"""

NEGATIVE_REVENUE_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,-520000,180000,145000,35000,310000
2025-02,485000,180000,138000,35000,347000
2025-03,560000,180000,155000,35000,437000
2025-04,510000,182000,142000,35000,488000
2025-05,475000,182000,135000,35000,511000
2025-06,530000,182000,150000,35000,574000
"""

CSV_WITH_NULLS = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
2025-01,520000,,145000,35000,310000
2025-02,485000,180000,,35000,347000
2025-03,560000,180000,155000,35000,437000
2025-04,510000,182000,142000,35000,488000
2025-05,475000,182000,135000,35000,511000
2025-06,530000,182000,150000,35000,574000
"""

CSV_WITH_WHITESPACE_HEADERS = """  Month , Revenue , Fixed_Costs , Variable_Costs , Loan_EMI , Cash_Reserve
2025-01,520000,180000,145000,35000,310000
2025-02,485000,180000,138000,35000,347000
2025-03,560000,180000,155000,35000,437000
2025-04,510000,182000,142000,35000,488000
2025-05,475000,182000,135000,35000,511000
2025-06,530000,182000,150000,35000,574000
"""

BAD_DATE_CSV = """month,revenue,fixed_costs,variable_costs,loan_emi,cash_reserve
not-a-date,520000,180000,145000,35000,310000
also-bad,485000,180000,138000,35000,347000
nope,560000,180000,155000,35000,437000
wrong,510000,182000,142000,35000,488000
invalid,475000,182000,135000,35000,511000
broken,530000,182000,150000,35000,574000
"""

EMPTY_CSV = ""


def _buf(csv_str: str) -> io.StringIO:
    """Helper to create a file-like buffer from CSV string."""
    return io.StringIO(csv_str)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParseCSVHappyPath:
    """Tests for valid CSV inputs."""

    def test_loads_sample_csv_from_file_path(self):
        df = parse_csv(SAMPLE_CSV_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 6
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

    def test_loads_valid_csv_from_buffer(self):
        df = parse_csv(_buf(VALID_CSV))
        assert len(df) == 6
        assert list(df.columns) == REQUIRED_COLUMNS

    def test_sorted_by_month(self):
        df = parse_csv(_buf(VALID_CSV))
        months = df["month"].tolist()
        assert months == sorted(months)

    def test_returns_correct_dtypes(self):
        df = parse_csv(_buf(VALID_CSV))
        for col in REQUIRED_COLUMNS[1:]:  # numeric columns
            assert pd.api.types.is_numeric_dtype(df[col])

    def test_handles_whitespace_headers(self):
        """Column names with whitespace/mixed case should be normalized."""
        df = parse_csv(_buf(CSV_WITH_WHITESPACE_HEADERS))
        assert len(df) == 6
        for col in REQUIRED_COLUMNS:
            assert col in df.columns


class TestParseCSVNullHandling:
    """Tests for CSVs with missing values."""

    def test_fills_nulls_with_zero(self):
        """Null numeric values should be filled with 0, not rejected."""
        df = parse_csv(_buf(CSV_WITH_NULLS))
        assert df["fixed_costs"].iloc[0] == 0.0  # was empty
        assert df["variable_costs"].iloc[1] == 0.0  # was empty
        assert not df[REQUIRED_COLUMNS[1:]].isnull().any().any()


class TestParseCSVRejections:
    """Tests for CSVs that should be rejected."""

    def test_rejects_missing_columns(self):
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(MISSING_COLUMN_CSV))
        assert "Missing required columns" in str(exc_info.value)

    def test_rejects_too_few_rows(self):
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(TOO_FEW_ROWS_CSV))
        assert "at least" in str(exc_info.value).lower()

    def test_rejects_negative_revenue(self):
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(NEGATIVE_REVENUE_CSV))
        assert "negative" in str(exc_info.value).lower()

    def test_rejects_empty_csv(self):
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(EMPTY_CSV))
        assert len(exc_info.value.errors) > 0

    def test_rejects_bad_dates(self):
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(BAD_DATE_CSV))
        assert "month" in str(exc_info.value).lower() or "date" in str(exc_info.value).lower()

    def test_error_contains_list_of_issues(self):
        """CSVValidationError.errors should be a list of strings."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(_buf(MISSING_COLUMN_CSV))
        assert isinstance(exc_info.value.errors, list)
        assert all(isinstance(e, str) for e in exc_info.value.errors)


class TestParseCSVEdgeCases:
    """Edge case handling."""

    def test_file_path_not_found(self):
        with pytest.raises(CSVValidationError):
            parse_csv("/nonexistent/path/data.csv")

    def test_exactly_six_rows(self):
        """Minimum row count should be accepted."""
        df = parse_csv(_buf(VALID_CSV))
        assert len(df) == 6  # VALID_CSV has exactly 6 rows
