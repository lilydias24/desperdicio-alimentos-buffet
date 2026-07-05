"""Indicadores principais (KPIs) do dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from services.data import risk_profiles
from utils.formatting import format_delta_percent, format_number, format_percent


def compute_group_gap(df: pd.DataFrame, group_col: str, value_col: str, min_count: int = 5) -> dict | None:
    """Maior diferenca de media entre categorias de `group_col`.

    Grupos com menos de `min_count` observacoes sao ignorados para evitar
    que uma categoria rara distorca a comparacao.
    """
    means = (
        df.groupby(group_col, observed=True)[value_col]
        .agg(["mean", "count"])
        .query("count >= @min_count")
    )
    if len(means) < 2:
        return None

    top = means["mean"].idxmax()
    bottom = means["mean"].idxmin()
    return {
        "group_col": group_col,
        "top": top,
        "bottom": bottom,
        "diff": float(means.loc[top, "mean"] - means.loc[bottom, "mean"]),
    }


def render_indicator_cards(df: pd.DataFrame) -> None:
    """Renderiza os cartoes de indicadores principais para o dataframe filtrado."""
    if df.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return

    taxa_media = df["wastage_rate"].mean()
    desperdicio_evento = df["wastage_food_amount"].mean()
    desperdicio_convidado = df["wastage_per_guest"].mean()
    quantidade_media = df["quantity_of_food"].mean()

    profiles = risk_profiles(df)
    top_profile = profiles.iloc[0]

    gap = compute_group_gap(df, "preparation_method", "wastage_rate")

    col1, col2, col3 = st.columns(3)
    col1.metric("Taxa media de desperdicio", format_percent(taxa_media))
    col2.metric("Desperdicio medio por evento", f"{format_number(desperdicio_evento)} kg/un")
    col3.metric("Desperdicio por convidado", format_number(desperdicio_convidado, decimals=3))

    col4, col5, col6 = st.columns(3)
    col4.metric("Quantidade media produzida", format_number(quantidade_media))

    with col5:
        st.caption("Perfil de maior risco")
        st.markdown(f"#### {top_profile['event_profile']}")
        st.caption(
            f"Taxa media {format_percent(top_profile['taxa_media'])} "
            f"em {int(top_profile['n_eventos'])} evento(s)."
        )

    with col6:
        st.caption("Maior diferenca entre grupos")
        if gap is not None:
            st.markdown(f"#### {format_delta_percent(gap['diff'])}")
            st.caption(
                f"{gap['group_col']}: {gap['top']} (maior) vs {gap['bottom']} "
                "(menor), em pontos percentuais de wastage_rate."
            )
        else:
            st.markdown("#### -")
            st.caption("Grupos insuficientes para comparacao com os filtros atuais.")

    st.caption(
        f"Indicadores calculados sobre {len(df):,} registro(s) apos aplicacao dos filtros."
        .replace(",", ".")
    )
