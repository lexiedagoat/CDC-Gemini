"""
components/sidebar.py
Renders sidebar filter selection controls, Select All toggles, reset capabilities, and active filter summaries.
"""

import pandas as pd
import streamlit as st


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Renders interactive filtering controls and returns filtered DataFrame."""
    st.sidebar.header("Filter Options")

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

    # Session state default initializations
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    # Select All / Reset Actions
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Select All Filters"):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = "All"
        st.rerun()

    if col2.button("Reset Filters"):
        st.session_state.selected_states = all_states
        st.session_state.selected_months = all_months
        st.session_state.selected_sex = "All"
        st.rerun()

    # Geography Selection
    selected_states = st.sidebar.multiselect(
        "State / Geography",
        options=all_states,
        default=st.session_state.selected_states,
        key="ms_states",
    )

    # Month Selection
    selected_months = st.sidebar.multiselect(
        "Month",
        options=all_months,
        default=st.session_state.selected_months,
        key="ms_months",
    )

    # Sex Selection
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

    # Apply filters to dataset
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

    return filtered_df
