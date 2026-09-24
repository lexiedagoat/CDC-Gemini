"""
components/kpi_cards.py
Renders top-level summary metrics with clear thousands separators.
"""

import pandas as pd
import streamlit as st


def render_kpi_cards(filtered_df: pd.DataFrame) -> None:
    """Calculates and renders 5 KPI cards across top of dashboard."""
    col1, col2, col3, col4, col5 = st.columns(5)

    if filtered_df.empty:
        col1.metric("Total Births", "0")
        col2.metric("Geographies", "0")
        col3.metric("Avg Births / Month", "0")
        col4.metric("Highest Geography", "N/A")
        col5.metric("Peak Month", "N/A")
        return

    total_births = int(filtered_df["births"].sum())
    num_geographies = filtered_df["state_of_residence"].nunique()
    num_months = filtered_df["month"].nunique()

    avg_births_per_month = (
        int(total_births / num_months) if num_months > 0 else 0
    )

    # Top state calculation
    state_grp = filtered_df.groupby("state_of_residence")["births"].sum()
    top_state = state_grp.idxmax() if not state_grp.empty else "N/A"

    # Peak month calculation
    month_grp = filtered_df.groupby("month", observed=False)["births"].sum()
    peak_month = month_grp.idxmax() if not month_grp.empty else "N/A"

    col1.metric("Total Births", f"{total_births:,}")
    col2.metric("Geographies", f"{num_geographies:,}")
    col3.metric("Avg Births / Month", f"{avg_births_per_month:,}")
    col4.metric("Highest Geography", top_state)
    col5.metric("Peak Month", str(peak_month))
