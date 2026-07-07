"""Construtores de gráficos Plotly usados nas páginas do dashboard.

Cada função retorna uma figura pronta para `st.plotly_chart`, mantendo a
lógica de plot separada das páginas para facilitar reuso e testes visuais.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.palette import (
    CATEGORICAL_PALETTE,
    GREEN_SCALE,
    NEUTRAL_DARK,
    PRICING_COLOR_MAP,
    PRIMARY_GREEN,
)

TEMPLATE = "plotly_white"


def distribution_plot(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "wastage_rate",
    kind: str = "box",
    title: str | None = None,
) -> go.Figure:
    """Boxplot ou violin plot da distribuição de `value_col` por `group_col`."""
    plot_fn = px.violin if kind == "violin" else px.box
    extra = {"box": True, "points": "outliers"} if kind == "violin" else {"points": "outliers"}
    fig = plot_fn(
        df,
        x=group_col,
        y=value_col,
        color=group_col,
        color_discrete_sequence=CATEGORICAL_PALETTE,
        template=TEMPLATE,
        title=title,
        **extra,
    )
    fig.update_layout(showlegend=False, xaxis_title=group_col, yaxis_title=value_col)
    return fig


def group_mean_bar(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "wastage_rate",
    title: str | None = None,
) -> go.Figure:
    """Barras com a média de `value_col` por categoria de `group_col`."""
    summary = (
        df.groupby(group_col, observed=True)[value_col]
        .agg(media="mean", n="size")
        .reset_index()
        .sort_values("media", ascending=False)
    )
    fig = px.bar(
        summary,
        x=group_col,
        y="media",
        text=summary["media"].round(2),
        hover_data={"n": True},
        template=TEMPLATE,
        title=title,
        color_discrete_sequence=[PRIMARY_GREEN],
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(xaxis_title=group_col, yaxis_title=f"Média de {value_col}")
    return fig


def interaction_heatmap(
    df: pd.DataFrame,
    row_col: str,
    col_col: str,
    value_col: str = "wastage_rate",
    title: str | None = None,
) -> go.Figure:
    """Heatmap da média de `value_col` cruzando `row_col` x `col_col`."""
    pivot = df.pivot_table(index=row_col, columns=col_col, values=value_col, aggfunc="mean")
    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale=GREEN_SCALE,
        template=TEMPLATE,
        title=title,
        aspect="auto",
    )
    fig.update_layout(
        xaxis_title=col_col,
        yaxis_title=row_col,
        coloraxis_colorbar_title=value_col,
    )
    return fig


def risk_ranking_bar(profiles: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Ranking horizontal dos perfis operacionais com maior taxa média de desperdício."""
    top = profiles.head(top_n).sort_values("taxa_media")
    fig = px.bar(
        top,
        x="taxa_media",
        y="event_profile",
        orientation="h",
        text=top["taxa_media"].round(2),
        hover_data={"n_eventos": True, "baixa_confianca": True},
        template=TEMPLATE,
        title=f"Top {top_n} perfis por taxa média de desperdício",
        color="taxa_media",
        color_continuous_scale=GREEN_SCALE,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Taxa média de wastage_rate (%)",
        yaxis_title="Perfil (porte | preparo | pricing)",
        coloraxis_showscale=False,
    )
    return fig


def quantity_vs_wastage_scatter(
    df: pd.DataFrame,
    color_col: str = "pricing",
    title: str | None = None,
) -> go.Figure:
    """Scatter de quantity_of_food x wastage_rate."""
    color_kwargs = (
        {"color_discrete_map": PRICING_COLOR_MAP}
        if color_col == "pricing"
        else {"color_discrete_sequence": CATEGORICAL_PALETTE}
    )
    fig = px.scatter(
        df,
        x="quantity_of_food",
        y="wastage_rate",
        color=color_col,
        opacity=0.65,
        template=TEMPLATE,
        title=title,
        hover_data=["event_type", "type_of_food", "preparation_method"],
        **color_kwargs,
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color=NEUTRAL_DARK)))
    fig.update_layout(xaxis_title="Quantidade de alimento produzida", yaxis_title="Taxa de desperdício (%)")
    return fig
