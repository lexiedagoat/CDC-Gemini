"""
components/tabs.py
Renders the individual content for all 5 dashboard tabs.
"""

import pandas as pd
import streamlit as st
from utils.charts import (
    create_choropleth_map,
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_state_month_heatmap,
    create_state_ranking_chart,
    create_top_bottom_chart,
)


def render_overview_tab(filtered_df: pd.DataFrame) -> None:
    """Tab 1: Overview visualizations."""
    st.subheader("National Birth Overview")
    if filtered_df.empty:
        st.warning(
            "No observations match the selected filter combination. Please adjust your filters."
        )
        return

    st.plotly_chart(
        create_choropleth_map(filtered_df), use_container_width=True
    )
    st.plotly_chart(
        create_monthly_trend_chart(filtered_df), use_container_width=True
    )


def render_geographic_tab(filtered_df: pd.DataFrame) -> None:
    """Tab 2: Geographic Analysis visualizations."""
    st.subheader("Geographic & State Comparisons")
    if filtered_df.empty:
        st.warning(
            "No observations match the selected filter combination. Please adjust your filters."
        )
        return

    st.plotly_chart(
        create_state_ranking_chart(filtered_df), use_container_width=True
    )

    top_bottom_fig = create_top_bottom_chart(filtered_df)
    if top_bottom_fig:
        st.plotly_chart(top_bottom_fig, use_container_width=True)
    else:
        st.info("Select at least 2 geographies to view Top vs Bottom comparison.")


def render_monthly_sex_tab(filtered_df: pd.DataFrame) -> None:
    """Tab 3: Monthly and Sex Distribution Visualizations."""
    st.subheader("Monthly Distributions & Sex Demographic Breakdown")
    if filtered_df.empty:
        st.warning(
            "No observations match the selected filter combination. Please adjust your filters."
        )
        return

    st.plotly_chart(
        create_sex_comparison_chart(filtered_df), use_container_width=True
    )
    st.plotly_chart(
        create_state_month_heatmap(filtered_df), use_container_width=True
    )


def render_data_table_tab(filtered_df: pd.DataFrame) -> None:
    """Tab 4: Filtered Data Table & Download Options."""
    st.subheader("Filtered Data Inspection & Data Export")
    if filtered_df.empty:
        st.warning(
            "No observations match the selected filter combination. Please adjust your filters."
        )
        return

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


def render_about_tab() -> None:
    """Tab 5: Pedagogical context and data source documentation."""
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
