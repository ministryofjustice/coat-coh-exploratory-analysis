"""Tests for hosting_data.py. Run from showback_report/: python -m pytest"""

import io
from pathlib import Path

import pandas as pd
import pytest

from hosting_data import (
    COST_COLUMNS,
    EXPECTED_COLUMNS,
    MissingColumnsError,
    read_hosting_csv,
)

SAMPLE = Path(__file__).parent / "sample_hosting.csv"


def test_sample_loads_with_expected_columns():
    df = read_hosting_csv(SAMPLE)
    assert list(df.columns) == EXPECTED_COLUMNS
    assert len(df) == 10


def test_types():
    df = read_hosting_csv(SAMPLE)
    assert df["is_taggable_product"].dtype == bool
    for col in COST_COLUMNS:
        assert pd.api.types.is_float_dtype(df[col]), col
    assert df["billing_period"].tolist()[0] == "2026-07"


def test_sample_totals():
    df = read_hosting_csv(SAMPLE)
    # Hand-summed from sample_hosting.csv
    assert df["spend_usd"].sum() == pytest.approx(4515.0)
    by_month = df.groupby("billing_period")["spend_usd"].sum().to_dict()
    assert by_month == pytest.approx({"2026-07": 1550.0, "2026-08": 1415.0, "2026-09": 1550.0})
    assert df["usage_cost_usd"].sum() == pytest.approx(5876.0)
    assert (~df["is_taggable_product"]).sum() == 1


def test_missing_columns_are_named():
    text = SAMPLE.read_text().replace('"spend_usd",', "").replace('"tag_namespace",', "")
    with pytest.raises(MissingColumnsError) as err:
        read_hosting_csv(io.StringIO(text))
    assert err.value.missing == ["tag_namespace", "spend_usd"]


def test_bad_boolean_is_rejected():
    text = SAMPLE.read_text().replace('"false"', '"maybe"')
    with pytest.raises(ValueError, match="is_taggable_product"):
        read_hosting_csv(io.StringIO(text))


def test_non_numeric_cost_is_rejected():
    text = SAMPLE.read_text().replace('"-5.0"', '"n/a"')
    with pytest.raises(ValueError, match="spend_usd"):
        read_hosting_csv(io.StringIO(text))


@pytest.mark.parametrize("month", ["2026-13", "2026-9", "September", ""])
def test_invalid_billing_month_is_rejected(month):
    text = SAMPLE.read_text().replace('"2026-07"', f'"{month}"')
    with pytest.raises(ValueError, match="billing_period.*YYYY-MM"):
        read_hosting_csv(io.StringIO(text))
