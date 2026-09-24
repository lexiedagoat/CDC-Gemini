"""
utils/charts.py
Modular functions to create accessible Plotly charts without misleading axis truncations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_monthly_trend_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Generates a chronological line chart of monthly birth counts."""
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
    """Generates a US choropleth map of state birth counts."""
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
    """Generates a horizontal bar chart ranking selected geographies."""
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
    fig.update_layout(
        yaxis=dict(range=[0, sex_monthly["births"].max() * 1.1])
    )
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
        labels=dict(
            x="Month", y="State of Residence", color="Birth Count"
        ),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Viridis",
        title="State-by-Month Birth Concentration Heatmap",
        aspect="auto",
    )
    fig.update_layout(
        height=max(450, len(pivot_df.index) * 20),
    )
    return fig
