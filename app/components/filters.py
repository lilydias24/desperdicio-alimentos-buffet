"""Componente de filtros da barra lateral."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from services.data import FILTER_COLUMNS, filter_options

FILTER_LABELS = {
    "preparation_method": "Método de preparo",
    "pricing": "Faixa de preço (pricing)",
    "event_type": "Tipo de evento",
    "type_of_food": "Tipo de alimento",
    "event_size": "Porte do evento",
    "storage_conditions": "Condição de armazenamento",
}


def render_sidebar_filters(df: pd.DataFrame) -> dict[str, list[str]]:
    """Renderiza os multiselects de filtro e retorna a seleção atual.

    Todos os filtros começam com todos os valores marcados, garantindo que
    a aplicação abra sem filtros vazios e sem gerar dataframe vazio.
    """
    options = filter_options(df)
    st.sidebar.header("Filtros")

    selections: dict[str, list[str]] = {}
    for col in FILTER_COLUMNS:
        col_options = options[col]
        selections[col] = st.sidebar.multiselect(
            FILTER_LABELS[col],
            options=col_options,
            default=col_options,
            key=f"filter_{col}",
        )

    if st.sidebar.button("Limpar filtros (selecionar tudo)", use_container_width=True):
        for col in FILTER_COLUMNS:
            st.session_state[f"filter_{col}"] = options[col]
        st.rerun()

    return selections
