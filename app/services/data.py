"""Camada de acesso a dados do dashboard.

Le a base gold e disponibiliza funcoes de filtragem e agregacao usadas
pelas paginas do app. Mantida separada da camada de apresentacao para que
os componentes visuais nao precisem conhecer o caminho ou o formato do
arquivo de origem.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_DIR.parent
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "gold" / "food_wastage_gold.csv"

REQUIRED_COLUMNS = [
    "type_of_food",
    "event_type",
    "number_of_guests",
    "quantity_of_food",
    "wastage_food_amount",
    "preparation_method",
    "storage_conditions",
    "pricing",
    "wastage_rate",
    "wastage_per_guest",
    "event_size",
    "quantity_tier",
    "event_profile",
]

FILTER_COLUMNS = [
    "preparation_method",
    "pricing",
    "event_type",
    "type_of_food",
    "event_size",
    "storage_conditions",
]

NUMERIC_COLUMNS = [
    "number_of_guests",
    "quantity_of_food",
    "wastage_food_amount",
    "wastage_rate",
    "wastage_per_guest",
]


@st.cache_data(show_spinner="Carregando base gold...")
def load_data(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Carrega a camada gold do projeto.

    Levanta um erro amigavel caso o arquivo nao exista ou esteja com
    colunas incompativeis, para que a pagina de contexto possa exibir
    uma mensagem clara em vez de um traceback.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Base gold não encontrada em '{path}'. "
            "Copie 'food_wastage_gold.csv' para 'data/gold/' antes de iniciar o dashboard."
        )

    df = pd.read_csv(path, encoding="utf-8")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "A base gold não contém as colunas obrigatórias: " + ", ".join(missing)
        )

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)
    return df


def filter_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """Retorna, para cada coluna filtravel, a lista ordenada de valores unicos."""
    return {col: sorted(df[col].dropna().unique().tolist()) for col in FILTER_COLUMNS}


def apply_filters(df: pd.DataFrame, selections: dict[str, list[str]]) -> pd.DataFrame:
    """Aplica os filtros de sidebar ao dataframe.

    Uma selecao vazia para uma coluna e tratada como 'sem filtro' (mantem
    todos os valores), o que evita que o usuario fique com um dataframe
    vazio por desmarcar tudo sem querer.
    """
    filtered = df
    for col, selected_values in selections.items():
        if selected_values:
            filtered = filtered[filtered[col].isin(selected_values)]
    return filtered


def risk_profiles(df: pd.DataFrame, min_events: int = 3) -> pd.DataFrame:
    """Ranking de perfis operacionais por taxa media de desperdicio.

    Perfis com menos de `min_events` ocorrencias sao marcados como baixa
    confianca (media instavel), mas nao sao removidos do ranking.
    """
    profiles = (
        df.groupby("event_profile", observed=True)
        .agg(
            n_eventos=("wastage_rate", "size"),
            taxa_media=("wastage_rate", "mean"),
            taxa_mediana=("wastage_rate", "median"),
            desperdicio_medio=("wastage_food_amount", "mean"),
            convidados_medios=("number_of_guests", "mean"),
        )
        .reset_index()
        .sort_values(["taxa_media", "n_eventos"], ascending=[False, False])
        .reset_index(drop=True)
    )
    profiles.insert(0, "rank_risco", profiles.index + 1)
    profiles["baixa_confianca"] = profiles["n_eventos"] < min_events
    return profiles
