"""Read and check the Hosting showback CSV.

The CSV comes from the Athena query in showback_scope.html section 10.
No Streamlit here, so the tests run with plain pytest.
"""

import pandas as pd

TEXT_COLUMNS = [
    "billing_period",
    "cost_category_service_area",
    "business_unit",
    "account_name",
    "tag_namespace",
    "tag_service_area",
    "product_name",
]

BOOL_COLUMNS = ["is_taggable_product"]

COST_COLUMNS = [
    "spend_usd",
    "usage_cost_usd",
    "tagged_service_area_usage_cost_usd",
    "tagged_business_unit_usage_cost_usd",
    "tagged_application_usage_cost_usd",
    "tagged_owner_usage_cost_usd",
    "tagged_is_production_usage_cost_usd",
    "tagged_environment_name_usage_cost_usd",
    "tagged_namespace_usage_cost_usd",
]

EXPECTED_COLUMNS = TEXT_COLUMNS + BOOL_COLUMNS + COST_COLUMNS

_BOOL_VALUES = {"true": True, "false": False}


class MissingColumnsError(ValueError):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"CSV is missing columns: {', '.join(missing)}")


def read_hosting_csv(source) -> pd.DataFrame:
    """Read the CSV from a path or file-like object, with fixed column types.

    Raises MissingColumnsError if expected columns are absent, and ValueError
    if a boolean or cost column holds a value that cannot be converted.
    """
    df = pd.read_csv(source, dtype=str, keep_default_na=False)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise MissingColumnsError(missing)

    df = df[EXPECTED_COLUMNS].copy()

    try:
        billing_months = pd.to_datetime(df["billing_period"], format="%Y-%m", errors="raise")
    except ValueError as exc:
        raise ValueError("Column billing_period must contain valid months in YYYY-MM format.") from exc
    if not billing_months.dt.strftime("%Y-%m").eq(df["billing_period"]).all():
        raise ValueError("Column billing_period must contain valid months in YYYY-MM format.")

    for col in BOOL_COLUMNS:
        lowered = df[col].str.strip().str.lower()
        bad = sorted(set(lowered) - set(_BOOL_VALUES))
        if bad:
            raise ValueError(f"Column {col} has values other than true/false: {bad[:5]}")
        df[col] = lowered.map(_BOOL_VALUES).astype(bool)

    for col in COST_COLUMNS:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise").astype(float)
        except ValueError as exc:
            raise ValueError(f"Column {col} has a non-numeric value: {exc}") from exc

    return df
