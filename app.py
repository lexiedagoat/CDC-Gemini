"""
app.py
Complete single-file Streamlit dashboard for CDC Provisional Natality 2025 data.
Tailored for undergraduate business analytics students.
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & UTILITIES
# ==========================================
st.set_page_config(
    page_title="CDC 2025 Provisional Natality Dashboard",
    page_icon="📊",
    layout="wide",
)

# State Name to Postal Abbreviation Mapping
US_STATE_ABBREV = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


# ==========================================
# 2. DATA LOADING & VALIDATION
# ==========================================
@st.cache_data
def load_data(
    file_name: str = "Provisional_Natality_2025_CDC1.csv",
) -> pd.DataFrame:
    """Loads, validates, and processes the provisional natality dataset."""
    path = Path(__file__).parent / file_name if Path(__file__).exists() else Path(file_name)

    if not path.exists():
        st.error(f"Dataset file not found at: {path}")
        st.stop()

    df = pd.read_csv(path)

    # Data validation checks
    required_cols = [
        "state_of_residence",
        "month",
        "month_code",
        "year_code",
        "sex_of_infant",
        "births",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(
            f"Data Validation Error: Missing required columns: {missing_cols}"
        )
        st.stop()

    # Data formatting and sanitization
    df["births"] = pd.to_numeric(df["births"], errors="coerce").fillna(0)

    # Preserve chronological month ordering
    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    df["month"] = pd.Categorical(
        df["month"], categories=month_order, ordered=True
    )

    # Map state names to 2-letter postal codes for choropleth plotting
    df["state_code"] = df["state_of_residence"].map(US_STATE_ABBREV)

    return df


# ==========================================
# 3. CHART CREATION HELPERS
# ==========================================
def create_monthly_trend_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates chronological line chart of monthly birth counts."""
    monthly_summary = (
        filtered_df.groupby(["month_code", "month"], observed=False)["births"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly_summary,
        x="month",
        y="births",
        markers=True,
        title="Monthly Birth Trend (2025)",
        labels={"month": "Month", "births": "Total Birth Counts"},
        color_discrete_sequence=["#1f77b4"],
    )
    fig.update_layout(
        yaxis=dict(range=[0, monthly_summary["births"].max() * 1.1]),
        hovermode="x unified",
    )
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f} Births")
    return fig


def create_choropleth_map(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates US choropleth map of state birth counts."""
    state_summary = (
        filtered_df.groupby(["state_of_residence", "state_code"])["births"]
        .sum()
        .reset_index()
    )

    fig = px.choropleth(
        state_summary,
        locations="state_code",
        locationmode="USA-states",
        color="births",
        scope="usa",
        color_continuous_scale="Blues",
        labels={"births": "Total Births"},
        title="Geographic Birth Distribution across the United States",
        hover_name="state_of_residence",
    )
    fig.update_traces(hovertemplate="%{hovertext}<br>Births: %{z:,.0f}")
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


def create_state_ranking_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates horizontal bar chart ranking selected geographies."""
    state_summary = (
        filtered_df.groupby("state_of_residence")["births"]
        .sum()
        .reset_index()
        .sort_values(by="births", ascending=True)
    )

    fig = px.bar(
        state_summary,
        x="births",
        y="state_of_residence",
        orientation="h",
        title="State Birth Volume Ranking",
        labels={"births": "Total Births", "state_of_residence": "State"},
        color_discrete_sequence=["#2b5c8f"],
    )
    fig.update_layout(
        xaxis=dict(range=[0, state_summary["births"].max() * 1.1]),
        height=max(400, len(state_summary) * 22),
    )
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f} Births")
    return fig


def create_top_bottom_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates side-by-side bar chart of Top 5 and Bottom 5 selected states."""
    state_summary = (
        filtered_df.groupby("state_of_residence")["births"].sum().reset_index()
    )

    if len(state_summary) < 2:
        return None

    top5 = state_summary.nlargest(5, "births").assign(Group="Top 5")
    bottom5 = state_summary.nsmallest(5, "births").assign(Group="Bottom 5")
    combined = pd.concat([top5, bottom5]).drop_duplicates()

    fig = px.bar(
        combined,
        x="state_of_residence",
        y="births",
        color="Group",
        barmode="group",
        title="Top vs. Bottom Geographies Comparison",
        labels={
            "births": "Total Births",
            "state_of_residence": "State",
            "Group": "Category",
        },
        color_discrete_map={"Top 5": "#1f77b4", "Bottom 5": "#aec7e8"},
    )
    fig.update_layout(yaxis=dict(range=[0, combined["births"].max() * 1.1]))
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f} Births")
    return fig


def create_sex_comparison_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates grouped bar chart comparing Female and Male births by month."""
    sex_monthly = (
        filtered_df.groupby(["month", "sex_of_infant"], observed=False)["births"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        sex_monthly,
        x="month",
        y="births",
        color="sex_of_infant",
        barmode="group",
        title="Monthly Birth Counts by Infant Sex",
        labels={
            "month": "Month",
            "births": "Total Births",
            "sex_of_infant": "Infant Sex",
        },
        color_discrete_map={"Female": "#e377c2", "Male": "#1f77b4"},
    )
    fig.update_layout(yaxis=dict(range=[0, sex_monthly["births"].max() * 1.1]))
    fig.update_traces(hovertemplate="%{x} (%{fullData.name}): %{y:,.0f} Births")
    return fig


def create_state_month_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates state-by-month birth count heatmap matrix."""
    pivot_df = filtered_df.pivot_table(
        index="state_of_residence",
        columns="month",
        values="births",
        aggfunc="sum",
        fill_value=0,
        observed=False,
    )

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State of Residence", color="Birth Count"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Viridis",
        title="State-by-Month Birth Concentration Heatmap",
        aspect="auto",
    )
    fig.update_layout(height=max(450, len(pivot_df.index) * 20))
    return fig


# ==========================================
# 4. MAIN APP LOGIC
# ==========================================
def main():
    # Load dataset
    df = load_data()

    all_states = sorted(df["state_of_residence"].unique().tolist())
    all_months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    all_sexes = sorted(df["sex_of_infant"].unique().tolist())

    # Session State Filter Defaults
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    # Header Components
    st.title("CDC Provisional Natality Explorer (2025)")
    st.markdown(
        """
    *An interactive analytics portal for examining geographic, temporal, and sex-based birth counts across the United States.*
    """
    )
    st.warning(
        "**NOTICE**: The figures displayed in this dashboard represent **provisional raw birth counts**, not finalized figures or population-adjusted birth rates. Data source: **CDC WONDER**."
    )

    # Sidebar Filter Controls
    st.sidebar.header("Filter Options")

    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("Select All Filters"):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = "All"
        st.rerun()

    if col_btn2.button("Reset Filters"):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = "All"
        st.rerun()

    selected_states = st.sidebar.multiselect(
        "State / Geography",
        options=all_states,
        default=st.session_state.selected_states,
        key="ms_states",
    )

    selected_months = st.sidebar.multiselect(
        "Month",
        options=all_months,
        default=st.session_state.selected_months,
        key="ms_months",
    )

    selected_sex = st.sidebar.radio(
        "Infant Sex",
        options=["All"] + all_sexes,
        index=(
            0
            if st.session_state.selected_sex == "All"
            else all_sexes.index(st.session_state.selected_sex) + 1
        ),
        key="radio_sex",
    )

    # Apply Sidebar Filters
    filtered_df = df[
        (df["state_of_residence"].isin(selected_states))
        & (df["month"].isin(selected_months))
    ]
    if selected_sex != "All":
        filtered_df = filtered_df[filtered_df["sex_of_infant"] == selected_sex]

    # Active Filter Summary Panel
    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filters Summary")
    st.sidebar.info(
        f"**Geographies:** {len(selected_states)} of {len(all_states)} selected\n\n"
        f"**Months:** {len(selected_months)} of {len(all_months)} selected\n\n"
        f"**Infant Sex:** {selected_sex}"
    )

    # Render KPI Cards Banner
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    if filtered_df.empty:
        kpi_col1.metric("Total Births", "0")
        kpi_col2.metric("Geographies", "0")
        kpi_col3.metric("Avg Births / Month", "0")
        kpi_col4.metric("Highest Geography", "N/A")
        kpi_col5.metric("Peak Month", "N/A")
    else:
        total_births = int(filtered_df["births"].sum())
        num_geographies = filtered_df["state_of_residence"].nunique()
        num_months = filtered_df["month"].nunique()

        avg_births_per_month = (
            int(total_births / num_months) if num_months > 0 else 0
        )

        state_grp = filtered_df.groupby("state_of_residence")["births"].sum()
        top_state = state_grp.idxmax() if not state_grp.empty else "N/A"

        month_grp = filtered_df.groupby("month", observed=False)["births"].sum()
        peak_month = month_grp.idxmax() if not month_grp.empty else "N/A"

        kpi_col1.metric("Total Births", f"{total_births:,}")
        kpi_col2.metric("Geographies", f"{num_geographies:,}")
        kpi_col3.metric("Avg Births / Month", f"{avg_births_per_month:,}")
        kpi_col4.metric("Highest Geography", top_state)
        kpi_col5.metric("Peak Month", str(peak_month))

    st.markdown("---")

    # Render Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Overview",
            "Geographic Analysis",
            "Monthly & Sex Analysis",
            "Data Table & Download",
            "About the Data",
        ]
    )

    with tab1:
        st.subheader("National Birth Overview")
        if filtered_df.empty:
            st.warning("No observations match the selected filter combination.")
        else:
            st.plotly_chart(
                create_choropleth_map(filtered_df), use_container_width=True
            )
            st.plotly_chart(
                create_monthly_trend_chart(filtered_df),
                use_container_width=True,
            )

    with tab2:
        st.subheader("Geographic & State Comparisons")
        if filtered_df.empty:
            st.warning("No observations match the selected filter combination.")
        else:
            st.plotly_chart(
                create_state_ranking_chart(filtered_df),
                use_container_width=True,
            )
            top_bottom_fig = create_top_bottom_chart(filtered_df)
            if top_bottom_fig:
                st.plotly_chart(top_bottom_fig, use_container_width=True)
            else:
                st.info(
                    "Select at least 2 geographies to view Top vs Bottom comparison."
                )

    with tab3:
        st.subheader("Monthly Distributions & Sex Demographic Breakdown")
        if filtered_df.empty:
            st.warning("No observations match the selected filter combination.")
        else:
            st.plotly_chart(
                create_sex_comparison_chart(filtered_df),
                use_container_width=True,
            )
            st.plotly_chart(
                create_state_month_heatmap(filtered_df),
                use_container_width=True,
            )

    with tab4:
        st.subheader("Filtered Data Inspection & Data Export")
        if filtered_df.empty:
            st.warning("No observations match the selected filter combination.")
        else:
            st.dataframe(
                filtered_df.style.format({"births": "{:,.0f}"}),
                use_container_width=True,
            )
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv_data,
                file_name="provisional_natality_filtered_2025.csv",
                mime="text/csv",
            )

    with tab5:
        st.subheader("About the CDC Provisional Natality Dataset")
        st.markdown(
            """
        ### Pedagogical Notes for Analytics Students

        * **Data Source Attribution**: This dataset originates from the **CDC WONDER** (Centers for Disease Control and Prevention) Provisional Natality Statistics for calendar year 2025.
        * **Provisional Data Nature**: Provisional figures are non-final operational records. They are continuously updated as state vital statistics offices report final demographic certificates.
        * **Critical Analytical Distinction (Birth Counts vs. Birth Rates)**:
            * **Birth Counts (Absolute Metrics)**: Represent total raw numbers of live births occurring within a given geographic region or timeframe. Highly populated states (e.g., California, Texas) naturally yield far higher birth counts due to baseline population size.
            * **Birth Rates (Standardized Metrics)**: Standardize birth counts against underlying population size (e.g., *Births per 1,000 residents* or *Crude Birth Rate*). 
            * **Analytical Caution**: Do not confuse a high absolute birth count with a higher fertility rate. When conducting comparative regional business or healthcare demand analytics, standardizing by demographic denominators is necessary.
        """
        )


if __name__ == "__main__":
    main()
