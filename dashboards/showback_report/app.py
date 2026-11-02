import plotly.express as px
import streamlit as st


from auth import require_auth0_login
from config import APP_ENV, DASHBOARD_NAME
from hosting_data import MissingColumnsError, read_hosting_csv
from hosting_report import (
    ALL_BUSINESS_UNITS,
    filter_view,
    financial_year_spend,
    monthly_spend,
    spend_by_account,
    spend_by_business_unit,
    spend_by_namespace,
    spend_by_namespace_service_type,
    spend_by_service_type,
    tagging_coverage,
)
from local_data_input import manual_file_upload
from render_html import render_footer, render_header

st.set_page_config(
    page_title=DASHBOARD_NAME,
    page_icon="💰",
    layout="wide",
)

render_header()

if APP_ENV:
    require_auth0_login()

st.title(DASHBOARD_NAME)
st.caption(
    "Cost in the AWS cost category service_area = Hosting. "
    "Net cost, excluding tax, discount and fee lines."
)


@st.cache_data
def load_hosting_csv(uploaded_file):
    return read_hosting_csv(uploaded_file)


# -----------------------------
# Data load
# -----------------------------
csv_file = manual_file_upload()

try:
    with st.spinner("Loading and validating the Hosting CSV..."):
        df = load_hosting_csv(csv_file)
except MissingColumnsError as exc:
    st.error("The CSV is missing these columns:")
    st.write(exc.missing)
    st.stop()
except ValueError as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV contains no rows.")
    st.stop()

# -----------------------------
# Month and Business Unit filter
# -----------------------------
st.sidebar.header("Filters")
months = sorted(df["billing_period"].unique(), reverse=True)
if st.session_state.get("billing_month") not in months:
    st.session_state["billing_month"] = months[0]
month = st.sidebar.selectbox("Billing month", months, key="billing_month")
if len(months) == 1:
    st.sidebar.caption(f"Available reporting month: {month}")
business_units = [ALL_BUSINESS_UNITS] + sorted(df.loc[df["billing_period"] == month, "business_unit"].unique())
if st.session_state.get("business_unit") not in business_units:
    st.session_state["business_unit"] = ALL_BUSINESS_UNITS
business_unit = st.sidebar.selectbox("Business Unit", business_units, key="business_unit")

view = filter_view(df, month, business_unit)

account_options = sorted(view["account_name"].unique())
namespace_options = sorted(view["tag_namespace"].unique())
for filter_key, options in (
    ("account_filter", account_options),
    ("namespace_filter", namespace_options),
):
    st.session_state[filter_key] = [
        value for value in st.session_state.get(filter_key, []) if value in options
    ]
selected_accounts = st.sidebar.multiselect(
    "Accounts", account_options, key="account_filter", placeholder="All accounts"
)
selected_namespaces = st.sidebar.multiselect(
    "Namespaces", namespace_options, key="namespace_filter", placeholder="All namespaces"
)
history = df
if business_unit != ALL_BUSINESS_UNITS:
    history = history[history["business_unit"] == business_unit]
if selected_accounts:
    history = history[history["account_name"].isin(selected_accounts)]
if selected_namespaces:
    history = history[history["tag_namespace"].isin(selected_namespaces)]
view = history[history["billing_period"] == month]

account_scope = ", ".join(selected_accounts) or "All accounts"
namespace_scope = ", ".join(selected_namespaces) or "All namespaces"
st.caption(
    f"Month: {month}. Business Unit: {business_unit}. "
    f"Accounts: {account_scope}. Namespaces: {namespace_scope}. {len(view):,} rows."
)

if view.empty:
    st.info("No rows match the selected filters. Clear an account or namespace selection, or choose another month or business unit.")
    st.stop()

# -----------------------------
# Charts and table formats
# -----------------------------
BAR_COLOUR = "#12436D"
TABLE_COLUMNS = {
    "billing_period": "Billing month",
    "availability": "Data availability",
    "business_unit": "Business unit",
    "account_name": "Account",
    "tag_namespace": "Namespace",
    "service_type": "Service type",
    "tag": "Tag",
    "spend_usd": st.column_config.NumberColumn(
        "Spend (USD)", format="dollar"
    ),
    "pct_of_total": st.column_config.ProgressColumn(
        "Share of total (%)", format="%.1f%%", min_value=0, max_value=100
    ),
    "pct_of_account": st.column_config.ProgressColumn(
        "Share of account spend (%)", format="%.1f%%", min_value=0, max_value=100
    ),
    "pct_of_namespace": st.column_config.ProgressColumn(
        "Share of namespace spend (%)", format="%.1f%%", min_value=0, max_value=100
    ),
    "tagged_usage_cost_usd": st.column_config.NumberColumn(
        "Tagged usage cost (USD)", format="dollar"
    ),
    "taggable_usage_cost_usd": st.column_config.NumberColumn(
        "Taggable usage cost (USD)", format="dollar"
    ),
    "pct_tagged": st.column_config.ProgressColumn(
        "Tagging coverage (%)", format="%.1f%%", min_value=0, max_value=100
    ),
}


def report_table(data, description, report_name):
    table_data = data.replace([float("inf"), float("-inf")], float("nan"))
    columns = TABLE_COLUMNS.copy()
    for column in ("pct_of_total", "pct_of_account", "pct_of_namespace", "pct_tagged"):
        if column not in table_data:
            continue
        within_tolerance = table_data[column].between(-1e-9, 100 + 1e-9)
        table_data.loc[within_tolerance, column] = table_data.loc[within_tolerance, column].clip(0, 100)
        values = table_data[column].dropna()
        if not values.between(0, 100).all():
            columns[column] = st.column_config.NumberColumn(
                TABLE_COLUMNS[column]["label"], format="%.1f%%"
            )
            st.info("Percentages outside 0-100% are displayed as numbers rather than bars.")
        if table_data[column].isna().any():
            st.info("Some percentages are unavailable and are shown as blank, not zero.")
    st.dataframe(
        table_data,
        hide_index=True,
        column_config=columns,
        alt=f"{description} Accounts: {account_scope}. Namespaces: {namespace_scope}.",
    )


def bar_chart(data, category, value, value_label, text_format, description):
    fig = px.bar(
        data.iloc[::-1],
        x=value,
        y=category,
        orientation="h",
        text=data.iloc[::-1][value].map(text_format),
        labels={value: value_label, category: ""},
        color_discrete_sequence=[BAR_COLOUR],
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color="#0b0c0c"))
    fig.update_layout(
        margin=dict(l=10, r=40, t=10, b=10),
        height=max(220, 32 * len(data) + 80),
        font=dict(color="#0b0c0c"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )
    fig.update_xaxes(tickfont=dict(color="#0b0c0c"), title_font=dict(color="#0b0c0c"))
    fig.update_yaxes(tickfont=dict(color="#0b0c0c"))
    st.plotly_chart(
        fig, width="stretch",
        alt=f"{description} Accounts: {account_scope}. Namespaces: {namespace_scope}.",
    )


def money(value):
    return f"${value:,.0f}"


def pct(value):
    return f"{value:.1f}%"


total_spend = view["spend_usd"].sum()
account_count = view["account_name"].nunique()
ytd = financial_year_spend(history, month)
ytd_missing = ytd.loc[ytd["spend_usd"].isna(), "billing_period"].tolist()
ytd_value = "Not available" if ytd_missing else f"${ytd['spend_usd'].sum():,.2f}"

spend_column, accounts_column, ytd_column = st.columns(3)

with spend_column:
    st.metric("Total spend (USD)", f"${total_spend:,.2f}")

with accounts_column:
    st.metric("Accounts", f"{account_count:,}")

with ytd_column:
    st.metric("YTD spend (USD)", ytd_value)
    if ytd_missing:
        st.caption(f"Incomplete history: {len(ytd) - len(ytd_missing)} of {len(ytd)} financial-year months available.")


tab_spend, tab_ytd, tab_trend, tab_forecast, tab_tags, tab_account, tab_type = st.tabs(
    ["Monthly spend", "Year-to-date", "Spend trend", "Forecast", "Tagging coverage", "By account / namespace", "By service type"]
)

# -----------------------------
# 1. Monthly spend
# -----------------------------
with tab_spend:
    by_bu = spend_by_business_unit(view)
    bar_chart(
        by_bu, "business_unit", "spend_usd", "Spend (USD)", money,
        f"Hosting spend by business unit for {month}, filtered to {business_unit}. "
        "Amounts are in US dollars. The table below contains the values.",
    )
    report_table(
        by_bu,
        f"Business unit spending for {month}, {business_unit}: USD and share of total spend.",
        "monthly-spend",
    )

with tab_ytd:
    st.subheader("Financial year-to-date spend")
    st.caption(f"April-to-March financial year: {ytd.iloc[0]['billing_period']} to {month}. Current business unit, account and namespace filters apply.")
    if ytd_missing:
        st.info(
            f"Full YTD spend is not available. Missing months for this selection: {', '.join(ytd_missing)}. "
            "It will populate when data for these months is included in the uploaded CSV. Missing months are not treated as zero."
        )
        st.metric("Available-month subtotal (USD, partial)", f"${ytd['spend_usd'].sum():,.2f}")
    else:
        st.metric("Financial YTD spend (USD)", ytd_value)
    report_table(
        ytd,
        f"Financial-year monthly spend through {month}, {business_unit}; unavailable months are blank.",
        "year-to-date",
    )
    st.caption("Based on rows in the uploaded CSV; month availability does not confirm that an export contains all charges. Budget comparison is not available: no budget data has been supplied.")

with tab_trend:
    st.subheader("12-month spend trend")
    trend = monthly_spend(history, month)
    trend_missing = trend.loc[trend["spend_usd"].isna(), "billing_period"].tolist()
    if trend_missing:
        st.info(
            f"Partial history: {12 - len(trend_missing)} of 12 months available. "
            f"Missing months for this selection: {', '.join(trend_missing)}. "
            "The trend will populate as more months are included in the uploaded CSV; gaps are not zero spend."
        )
    if trend["spend_usd"].notna().sum() < 2:
        st.info("A spend trend is not yet available: at least two months of spend data are needed. The available month is shown below.")
    else:
        trend_chart = px.line(
            trend, x="billing_period", y="spend_usd", markers=True,
            labels={"billing_period": "Billing month", "spend_usd": "Spend (USD)"},
            color_discrete_sequence=[BAR_COLOUR],
        )
        trend_chart.update_traces(connectgaps=False)
        trend_chart.update_xaxes(type="category", categoryorder="array", categoryarray=trend["billing_period"].tolist())
        st.plotly_chart(
            trend_chart, width="stretch",
            alt=f"Monthly Hosting spend over 12 months ending {month}, {business_unit}. Missing months are gaps. Accounts: {account_scope}. Namespaces: {namespace_scope}.",
        )
    report_table(
        trend,
        f"12-month spend history ending {month}, {business_unit}; unavailable months are blank.",
        "spend-trend",
    )

with tab_forecast:
    st.subheader("Forecasted spend")
    st.metric("Next 3 months forecast (USD)", "Not available")
    st.info(
        "Forecast data is not available in the current CSV. This section will populate once a forecast data source "
        "and an agreed forecasting method are connected. Additional actual-spend history alone does not provide a forecast."
    )

# -----------------------------
# 5. Tagging coverage
# -----------------------------
with tab_tags:
    st.info(
        "Service Area via the AWS rule (cost category) is 100% by definition: every row here is in "
        "the Hosting cost category. The bars show the share of cost that also carries each team tag."
    )
    coverage = tagging_coverage(view)
    if coverage["pct_tagged"].notna().any():
        bar_chart(
            coverage, "tag", "pct_tagged", "% of taggable Usage cost carrying the tag", pct,
            f"Tagging coverage for {month}, filtered to {business_unit}. "
            "Bars show the percentage of taggable usage cost carrying each tag. "
            "The table below contains the percentages and cost amounts.",
        )
    else:
        st.info("Tagging coverage is unavailable: the selected rows have no non-zero taggable usage cost. It will populate when taggable usage-cost data is available in the uploaded CSV.")
    report_table(
        coverage,
        f"Tagging coverage for {month}, {business_unit}: tagged and taggable usage cost in USD, and coverage percentage.",
        "tagging-coverage",
    )
    st.caption("Usage lines, unblended cost. Products that never carry tags are left out, as in the model.")
    st.info(
        "Resource-count tagging compliance is not available: resource counts and tag-validation results have not been supplied. "
        "The current measure is cost-weighted tag coverage, not the percentage of resources correctly tagged. "
        "Resource compliance can populate once those inputs are connected."
    )

# -----------------------------
# 6. By account / namespace
# -----------------------------
with tab_account:
    by_account = spend_by_account(view)
    top_accounts = (
    by_account.groupby("account_name", as_index=False)["spend_usd"]
    .sum()
    .sort_values("spend_usd", ascending=False)
    .head(15)
)
    st.subheader("Accounts: 15 largest by spend")
    bar_chart(
        top_accounts, "account_name", "spend_usd", "Spend (USD)", money,
        f"Up to 15 highest-spending accounts for {month}, filtered to {business_unit}. "
        "Spend is combined across the selected business units, in US dollars. "
        "The table below contains the same account totals.",
    )
    report_table(
        top_accounts,
        f"Top 15 account totals in USD for {month}, {business_unit}, ordered highest first.",
        "top-accounts",
    )
    st.subheader("All accounts")
    report_table(
        by_account,
        f"All accounts by business unit for {month}, {business_unit}: USD and share of total spend.",
        "accounts",
    )
    st.subheader("Namespaces (user_namespace tag)")
    report_table(
        spend_by_namespace(view),
        f"Namespace spending for {month}, {business_unit}: USD and share of total spend.",
        "namespaces",
    )

# -----------------------------
# 7. By service type
# -----------------------------
with tab_type:
    by_type = spend_by_service_type(view)
    bar_chart(
        by_type, "service_type", "spend_usd", "Spend (USD)", money,
        f"Hosting spend by service category for {month}, filtered to {business_unit}. "
        "Amounts are in US dollars. The table below contains the values.",
    )
    report_table(
        by_type,
        f"Service category spending for {month}, {business_unit}: USD and share of total spend.",
        "service-types",
    )
    st.subheader("Per namespace")
    if view["tag_namespace"].str.strip().str.lower().isin(["", "untagged"]).any():
        st.info("Some rows have no namespace attribution. Their costs remain in the untagged group and will be attributed when namespace tags are supplied in the CSV.")
    report_table(
        spend_by_namespace_service_type(view),
        f"Service breakdown for all namespaces in the current selection, {month}, {business_unit}: USD and share of each namespace's spend across the selected accounts.",
        "namespace-services",
    )
    st.caption("Mapping from AWS product name, as in showback_scope.html section 7. EC2 includes its storage volumes, NAT gateways and data transfer.")

render_footer()