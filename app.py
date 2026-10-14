from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_TITLE = "VizCraft"
st.set_page_config(page_title="VizCraft | Data Visualization Dashboard", page_icon="📊", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2.2rem; max-width: 1500px;}
    .hero {padding: 1.4rem 1.6rem; border-radius: 18px; color: white;
           background: linear-gradient(120deg, #172554 0%, #1d4ed8 55%, #0891b2 100%);
           margin-bottom: 1rem;}
    .hero h1 {font-size: 2.25rem; margin: 0 0 .35rem 0;}
    .hero p {font-size: 1rem; opacity: .92; margin: 0;}
    div[data-testid="stMetric"] {background: var(--secondary-background-color); padding: 1rem;
        border: 1px solid rgba(128,128,128,.18); border-radius: 14px;}
    .section-note {color: #64748b; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Reproducible demo data ----------
@st.cache_data
def make_demo_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 240
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    regions = rng.choice(["North", "South", "East", "West"], size=n, p=[.30, .25, .20, .25])
    categories = rng.choice(["Technology", "Furniture", "Office Supplies", "Accessories"], size=n)
    units = rng.integers(1, 16, size=n)
    price_map = {"Technology": 175.0, "Furniture": 120.0, "Office Supplies": 24.0, "Accessories": 42.0}
    unit_price = np.array([price_map[c] for c in categories]) * rng.uniform(.65, 1.4, size=n)
    sales = np.round(units * unit_price, 2)
    profit = np.round(sales * rng.uniform(.04, .28, size=n) - rng.uniform(0, 18, size=n), 2)
    df = pd.DataFrame({
        "Order Date": dates, "Region": regions, "Category": categories,
        "Units Sold": units, "Sales": sales, "Profit": profit,
        "Customer Rating": np.round(rng.uniform(2.5, 5.0, size=n), 1),
    })
    # Add a few realistic quality issues for demonstrating diagnostics.
    df.loc[[8, 71], "Customer Rating"] = np.nan
    df.loc[33, "Region"] = " North "
    df.loc[111, "Sales"] = df.loc[110, "Sales"] * 8  # potential outlier
    df.loc[200] = df.loc[199]  # duplicate row
    return df

def safe_read_csv(uploaded_file) -> pd.DataFrame:
    """Read CSV bytes with helpful encoding fallbacks and clear errors."""
    raw = uploaded_file.getvalue()
    if not raw or not raw.strip():
        raise ValueError("The uploaded file is empty.")
    errors = []
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            frame = pd.read_csv(io.BytesIO(raw), encoding=encoding)
            if frame.empty and len(frame.columns) == 0:
                raise ValueError("The CSV contains no columns.")
            return frame
        except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
            errors.append(str(exc))
    raise ValueError("Could not parse this CSV. Check that it is a valid, comma-separated file.")

def classify_columns(df: pd.DataFrame):
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    dates = []
    for col in df.columns:
        if col in numeric:
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            dates.append(col)
    return numeric, dates

def convert_date_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert likely date columns only when most non-null values parse successfully."""
    result = df.copy()
    for col in result.select_dtypes(include=["object", "string"]).columns:
        name_hint = any(word in str(col).lower() for word in ("date", "time", "day"))
        if name_hint:
            parsed = pd.to_datetime(result[col], errors="coerce")
            non_null = result[col].notna().sum()
            if non_null and parsed.notna().sum() / non_null >= .8:
                result[col] = parsed
    return result

def csv_bytes(df: pd.DataFrame) -> bytes:
    export = df.copy()
    for col in export.select_dtypes(include=["datetimetz"]).columns:
        export[col] = export[col].astype(str)
    return export.to_csv(index=False).encode("utf-8-sig")

def make_summary(df: pd.DataFrame) -> str:
    lines = [
        "VizCraft Data Analysis Summary",
        "=" * 32,
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns):,}",
        f"Duplicate rows: {int(df.duplicated().sum()):,}",
        f"Missing cells: {int(df.isna().sum().sum()):,}",
        "",
        "Column summary:",
        df.describe(include="all", datetime_is_numeric=True).transpose().to_string(),
        "",
        "Missing values by column:",
        df.isna().sum().to_string(),
    ]
    return "\n".join(lines)

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>📊 VizCraft</h1>
  <p>Interactive Data Visualization Dashboard · CodSoft Data Analytics Internship · Task 3</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Data workspace")
    source = st.radio("Choose data source", ["Built-in demo dataset", "Upload a CSV"], index=0)
    uploaded = None
    if source == "Upload a CSV":
        uploaded = st.file_uploader("Choose a CSV file", type=["csv"], help="UTF-8 CSV is recommended.")
    st.divider()
    st.caption("Tip: Start with the demo dataset to explore every dashboard section.")

if source == "Built-in demo dataset":
    raw_df = make_demo_data()
else:
    if uploaded is None:
        st.info("Upload a CSV in the sidebar, or switch to the built-in demo dataset to explore VizCraft.")
        st.stop()
    try:
        raw_df = safe_read_csv(uploaded)
    except Exception as exc:
        st.error(f"Unable to load this file: {exc}")
        st.stop()

if raw_df.empty:
    st.warning("This dataset has column headers but no data rows. Upload a non-empty CSV to continue.")
    st.dataframe(raw_df, use_container_width=True)
    st.stop()
if len(raw_df.columns) == 0:
    st.error("No columns were found. Please check the CSV file.")
    st.stop()

df = convert_date_candidates(raw_df)
numeric_cols, date_cols = classify_columns(df)
all_cols = df.columns.tolist()
categorical_cols = [c for c in all_cols if c not in numeric_cols and c not in date_cols]

st.subheader("Explore your data")
st.caption("Filter the dataset first. KPIs, charts, diagnostics, and exports below update to match your selection.")

# ---------- Filters ----------
with st.expander("🔎 Filters", expanded=True):
    filter_cols = st.columns(3)
    filtered = df.copy()
    category_filter_cols = [c for c in categorical_cols if df[c].nunique(dropna=True) <= 100]
    if category_filter_cols:
        with filter_cols[0]:
            category_col = st.selectbox("Category filter", ["None"] + category_filter_cols)
            if category_col != "None":
                options = sorted(df[category_col].dropna().astype(str).unique().tolist())
                chosen = st.multiselect(f"Values in {category_col}", options, default=options)
                filtered = filtered[filtered[category_col].astype(str).isin(chosen)]
    if numeric_cols:
        with filter_cols[1]:
            numeric_filter = st.selectbox("Numeric range filter", ["None"] + numeric_cols)
            if numeric_filter != "None":
                vals = pd.to_numeric(df[numeric_filter], errors="coerce").dropna()
                if not vals.empty:
                    low, high = float(vals.min()), float(vals.max())
                    if low == high:
                        st.caption(f"{numeric_filter} is constant at {low:g}.")
                    else:
                        selected_range = st.slider(
                            f"Range for {numeric_filter}", min_value=low, max_value=high,
                            value=(low, high), key=f"range_{numeric_filter}"
                        )
                        filtered = filtered[
                            pd.to_numeric(filtered[numeric_filter], errors="coerce").between(*selected_range)
                        ]
    if date_cols:
        with filter_cols[2]:
            date_filter = st.selectbox("Date filter", ["None"] + date_cols)
            if date_filter != "None":
                valid_dates = pd.to_datetime(df[date_filter], errors="coerce").dropna()
                if not valid_dates.empty:
                    min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                    date_range = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        start_d, end_d = date_range
                        dt = pd.to_datetime(filtered[date_filter], errors="coerce")
                        filtered = filtered[dt.dt.date.between(start_d, end_d)]

if filtered.empty:
    st.warning("No rows match the current filters. Adjust or clear a filter to continue.")
    st.stop()

# ---------- KPIs ----------
st.subheader("Dataset at a glance")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Rows in view", f"{len(filtered):,}", delta=f"{len(filtered) - len(df):+,} vs. full data")
k2.metric("Columns", f"{len(filtered.columns):,}")
k3.metric("Missing cells", f"{int(filtered.isna().sum().sum()):,}")
k4.metric("Duplicate rows", f"{int(filtered.duplicated().sum()):,}")

if numeric_cols:
    metric_cols = st.columns(min(4, len(numeric_cols)))
    for idx, col in enumerate(numeric_cols[:4]):
        metric_cols[idx].metric(f"Average · {col}", f"{filtered[col].mean():,.2f}" if filtered[col].notna().any() else "N/A")

# ---------- Data preview and summaries ----------
tab_data, tab_charts, tab_quality, tab_export = st.tabs(
    ["🧾 Data & columns", "📈 Visualizations", "🧪 Data quality", "📦 Downloads"]
)
with tab_data:
    st.markdown("#### Filtered data preview")
    st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)
    st.caption(f"Showing up to 100 of {len(filtered):,} filtered rows.")
    st.markdown("#### Column summary")
    summary = pd.DataFrame({
        "Column": filtered.columns,
        "Data type": [str(filtered[c].dtype) for c in filtered.columns],
        "Non-null": [int(filtered[c].notna().sum()) for c in filtered.columns],
        "Missing": [int(filtered[c].isna().sum()) for c in filtered.columns],
        "Unique values": [int(filtered[c].nunique(dropna=True)) for c in filtered.columns],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)
    with st.expander("Statistical summary"):
        st.dataframe(filtered.describe(include="all").transpose(), use_container_width=True)

with tab_charts:
    st.markdown("#### Build a chart")
    chart_type = st.selectbox("Chart type", [
        "Bar chart", "Line chart", "Scatter plot", "Histogram", "Box plot", "Pie chart"
    ])
    chart_cols = st.columns(3)
    if chart_type == "Bar chart":
        x = chart_cols[0].selectbox("Category / X axis", all_cols, key="bar_x")
        y_choices = numeric_cols or all_cols
        y = chart_cols[1].selectbox("Value / Y axis", y_choices, key="bar_y")
        agg_options = ["Sum", "Mean", "Count"] if numeric_cols else ["Count"]
        agg = chart_cols[2].selectbox("Aggregation", agg_options, key="bar_agg")
        if agg == "Count":
            plot_df = filtered.groupby(x, dropna=False).size().reset_index(name="Count")
            fig = px.bar(plot_df, x=x, y="Count", title=f"Count by {x}")
        else:
            vals = filtered.groupby(x, dropna=False)[y].agg("sum" if agg == "Sum" else "mean").reset_index()
            fig = px.bar(vals, x=x, y=y, title=f"{agg} of {y} by {x}")
    elif chart_type == "Line chart":
        x = chart_cols[0].selectbox("X axis", date_cols + numeric_cols + categorical_cols, key="line_x")
        y = chart_cols[1].selectbox("Y axis", numeric_cols or all_cols, key="line_y")
        color_col = chart_cols[2].selectbox("Color grouping (optional)", ["None"] + categorical_cols, key="line_color")
        plot_df = filtered.sort_values(x)
        fig = px.line(plot_df, x=x, y=y, color=None if color_col == "None" else color_col,
                      markers=True, title=f"{y} over {x}")
    elif chart_type == "Scatter plot":
        if len(numeric_cols) < 2:
            st.info("A scatter plot needs at least two numerical columns. Choose another chart or upload suitable data.")
            fig = None
        else:
            x = chart_cols[0].selectbox("X axis", numeric_cols, key="scatter_x")
            y = chart_cols[1].selectbox("Y axis", [c for c in numeric_cols if c != x] or numeric_cols, key="scatter_y")
            color_col = chart_cols[2].selectbox("Color grouping (optional)", ["None"] + categorical_cols, key="scatter_color")
            fig = px.scatter(filtered, x=x, y=y, color=None if color_col == "None" else color_col,
                             hover_data=all_cols[:8], title=f"{y} vs. {x}")
    elif chart_type == "Histogram":
        x = chart_cols[0].selectbox("Numerical column", numeric_cols or all_cols, key="hist_x")
        bins = chart_cols[1].slider("Bins", 5, 80, 30, key="hist_bins")
        fig = px.histogram(filtered, x=x, nbins=bins, title=f"Distribution of {x}")
    elif chart_type == "Box plot":
        if not numeric_cols:
            st.info("A box plot needs a numerical column. Choose another chart or upload data with numeric values.")
            fig = None
        else:
            y = chart_cols[0].selectbox("Numerical column", numeric_cols, key="box_y")
            x = chart_cols[1].selectbox("Group by (optional)", ["None"] + categorical_cols, key="box_x")
            fig = px.box(filtered, x=None if x == "None" else x, y=y, points="outliers", title=f"Box plot of {y}")
    else:
        pie_col = chart_cols[0].selectbox("Category", categorical_cols or all_cols, key="pie_col")
        count_mode = chart_cols[1].checkbox("Show row counts", value=True, key="pie_count")
        if count_mode:
            pie_df = filtered[pie_col].fillna("(Missing)").astype(str).value_counts().reset_index()
            pie_df.columns = [pie_col, "Count"]
            fig = px.pie(pie_df, names=pie_col, values="Count", title=f"Share by {pie_col}", hole=.28)
        elif numeric_cols:
            value_col = chart_cols[1].selectbox("Value column", numeric_cols, key="pie_value")
            pie_df = filtered.groupby(pie_col, dropna=False)[value_col].sum().reset_index()
            fig = px.pie(pie_df, names=pie_col, values=value_col, title=f"{value_col} by {pie_col}", hole=.28)
        else:
            pie_df = filtered[pie_col].fillna("(Missing)").astype(str).value_counts().reset_index()
            pie_df.columns = [pie_col, "Count"]
            fig = px.pie(pie_df, names=pie_col, values="Count", title=f"Share by {pie_col}", hole=.28)
    if "fig" in locals() and fig is not None:
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=60, b=20), height=480)
        st.plotly_chart(fig, use_container_width=True)
        try:
            st.download_button("Download chart as interactive HTML", fig.to_html(include_plotlyjs="cdn").encode("utf-8"),
                               file_name="vizcraft_chart.html", mime="text/html")
        except Exception:
            pass

    st.markdown("#### Numerical relationships")
    if len(numeric_cols) >= 2:
        corr = filtered[numeric_cols].corr(numeric_only=True)
        heat = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                         zmin=-1, zmax=1, title="Correlation heatmap (Pearson)")
        heat.update_layout(template="plotly_white", height=max(420, 55 * len(numeric_cols)))
        st.plotly_chart(heat, use_container_width=True)
        pairs = []
        for i, c1 in enumerate(numeric_cols):
            for c2 in numeric_cols[i + 1:]:
                value = corr.loc[c1, c2]
                if pd.notna(value):
                    pairs.append((c1, c2, float(value)))
        pairs.sort(key=lambda item: abs(item[2]), reverse=True)
        if pairs:
            st.markdown("**Strongest numerical relationships**")
            for c1, c2, value in pairs[:5]:
                strength = "strong" if abs(value) >= .7 else "moderate" if abs(value) >= .4 else "weak"
                direction = "positive" if value > 0 else "negative" if value < 0 else "neutral"
                st.write(f"- **{c1}** and **{c2}**: {direction}, {strength} correlation (r = {value:.2f}). Correlation does not prove causation.")
    else:
        st.info("The correlation heatmap needs at least two numerical columns.")

with tab_quality:
    st.markdown("#### Data quality checks")
    missing = filtered.isna().sum().rename("Missing values").to_frame()
    missing["Missing %"] = (missing["Missing values"] / max(len(filtered), 1) * 100).round(2)
    st.markdown("**Missing values by column**")
    st.dataframe(missing.sort_values("Missing values", ascending=False), use_container_width=True)
    duplicates = int(filtered.duplicated().sum())
    st.metric("Duplicate rows", duplicates)
    if duplicates:
        st.warning(f"{duplicates} duplicate row(s) detected. Review before removing them.")
        if st.checkbox("Preview duplicate rows"):
            st.dataframe(filtered[filtered.duplicated(keep=False)], use_container_width=True)
    else:
        st.success("No duplicate rows detected in the filtered data.")
    st.markdown("**Potential numerical outliers (IQR method)**")
    outlier_rows = []
    for col in numeric_cols:
        values = pd.to_numeric(filtered[col], errors="coerce").dropna()
        if len(values) < 4:
            continue
        q1, q3 = values.quantile(.25), values.quantile(.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        count = int(((values < lower) | (values > upper)).sum())
        outlier_rows.append({"Column": col, "Lower bound": round(float(lower), 3),
                             "Upper bound": round(float(upper), 3), "Potential outliers": count})
    if outlier_rows:
        st.dataframe(pd.DataFrame(outlier_rows).sort_values("Potential outliers", ascending=False),
                     use_container_width=True, hide_index=True)
        st.caption("IQR flags are review prompts, not proof that a value is erroneous.")
    else:
        st.info("Not enough numerical data to estimate outliers with the IQR method.")

with tab_export:
    st.markdown("#### Export your analysis")
    st.write("Downloads use the currently filtered rows.")
    st.download_button("⬇️ Download filtered data (CSV)", data=csv_bytes(filtered),
                       file_name="vizcraft_filtered_data.csv", mime="text/csv")
    summary_text = make_summary(filtered)
    st.download_button("⬇️ Download analysis summary (TXT)", data=summary_text.encode("utf-8"),
                       file_name="vizcraft_analysis_summary.txt", mime="text/plain")
    report_df = pd.DataFrame({
        "Metric": ["Rows", "Columns", "Missing cells", "Duplicate rows"],
        "Value": [len(filtered), len(filtered.columns), int(filtered.isna().sum().sum()), int(filtered.duplicated().sum())]
    })
    st.download_button("⬇️ Download KPI report (CSV)", data=report_df.to_csv(index=False).encode("utf-8"),
                       file_name="vizcraft_kpi_report.csv", mime="text/csv")
    st.info("For a portable report, save the summary and KPI CSV alongside your exported dataset.")

st.divider()
st.caption("VizCraft · Built with Python, Streamlit, Pandas, NumPy and Plotly · Demo data is reproducible (seed 42).")
