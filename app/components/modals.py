"""Modais (st.dialog) que complementam as páginas do dashboard.

Cada modal é uma função decorada com `@st.dialog`; chamar a função a
partir de um botão abre o modal na mesma execução (padrão do Streamlit).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.formatting import format_number, format_percent
from utils.styling import risk_badge_html


@st.dialog("Glossário rápido")
def glossario_modal() -> None:
    st.markdown(
        """
        | Termo | Significado |
        |---|---|
        | `wastage_rate` | Taxa de desperdício: `wastage_food_amount / quantity_of_food * 100`, em %. |
        | `wastage_per_guest` | Desperdício dividido pelo número de convidados. |
        | `event_size` | Porte do evento (Pequeno / Médio / Grande), por quartil de `number_of_guests`. |
        | `quantity_tier` | Faixa de quantidade produzida (Baixa / Média / Alta), por tercil. |
        | `event_profile` | Perfil operacional: `porte \\| método de preparo \\| pricing`. |
        | `waste_risk_rank` | Ranking dos perfis pela taxa média de desperdício (1 = maior risco). |
        """
    )
    st.caption(
        "Definições completas, com fórmulas e ressalvas, em "
        "`docs/dicionario_indicadores.md`."
    )
    if st.button("Fechar", key="fechar_glossario"):
        st.rerun()


@st.dialog("Como ler este dashboard")
def interpretacao_modal() -> None:
    st.markdown(
        """
        Para evitar conclusões apressadas, separe sempre três níveis de
        leitura ao explorar os gráficos:

        - **Observação** — o que o gráfico mostra diretamente (ex.: "eventos
          com pricing High têm taxa média de 8,81%").
        - **Interpretação** — o que essa observação sugere no contexto do
          problema (ex.: "eventos mais caros parecem desperdiçar mais").
        - **Conclusão** — o que se pode afirmar com razoável confiança,
          incluindo limitações (ex.: "há associação consistente entre
          pricing e desperdício, mas os dados são observacionais e não
          permitem afirmar causalidade").

        Cuidados adicionais:

        - Os indicadores mudam conforme os filtros da barra lateral;
          comparações entre páginas só valem com os mesmos filtros ativos.
        - Perfis com poucos eventos (marcados como baixa confiança) têm
          médias mais instáveis.
        - Nenhum resultado aqui deve ser lido como relação de causa e
          efeito.
        """
    )
    if st.button("Fechar", key="fechar_interpretacao"):
        st.rerun()


def _nivel_risco(rank: int, total: int) -> str:
    """Classifica o rank em tercis (1 = maior risco) para o badge visual."""
    posicao_relativa = rank / max(total, 1)
    if posicao_relativa <= 1 / 3:
        return "alto"
    if posicao_relativa <= 2 / 3:
        return "medio"
    return "baixo"


@st.dialog("Detalhes do perfil")
def perfil_detalhe_modal(row: pd.Series, media_geral: float, total_perfis: int) -> None:
    nivel = _nivel_risco(int(row["rank_risco"]), total_perfis)
    texto_nivel = {"alto": "Alto risco", "medio": "Risco médio", "baixo": "Baixo risco"}[nivel]

    st.markdown(f"### {row['event_profile']}")
    st.markdown(risk_badge_html(nivel, texto_nivel), unsafe_allow_html=True)
    if row["baixa_confianca"]:
        st.markdown(
            risk_badge_html("medio", "Amostra pequena (baixa confiança)"),
            unsafe_allow_html=True,
        )
    st.write("")

    col1, col2 = st.columns(2)
    col1.metric("Taxa média de desperdício", format_percent(row["taxa_media"]))
    col2.metric("Taxa mediana", format_percent(row["taxa_mediana"]))
    col1.metric("Convidados médios", format_number(row["convidados_medios"], decimals=0))
    col2.metric("Nº de eventos", int(row["n_eventos"]))

    diff = row["taxa_media"] - media_geral
    sinal = "acima" if diff >= 0 else "abaixo"
    st.markdown(
        f"Este perfil está **{abs(diff):.2f} pontos percentuais {sinal}** da "
        f"taxa média geral da seleção atual ({format_percent(media_geral)})."
    )

    if st.button("Fechar", key="fechar_perfil_detalhe"):
        st.rerun()
