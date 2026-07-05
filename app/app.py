"""Dashboard Streamlit - Investigacao do Desperdicio de Alimentos em Buffets.

Ponto de entrada da aplicacao (Parte 2 da entrega final). Concentra a
navegacao entre paginas e delega calculo de indicadores, filtros e
graficos para os modulos em `app/services` e `app/components`.

Uso:
    streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from components.charts import (
    distribution_plot,
    group_mean_bar,
    interaction_heatmap,
    quantity_vs_wastage_scatter,
    risk_ranking_bar,
)
from components.filters import render_sidebar_filters
from components.indicators import render_indicator_cards
from services.data import apply_filters, load_data, risk_profiles

PAGES = [
    "Contexto e problema",
    "Indicadores gerais",
    "Analises por pergunta",
    "Perfis de risco",
    "Conclusoes e limitacoes",
]


def page_contexto(df) -> None:
    st.title("Desperdicio de alimentos em servicos de buffet")
    st.markdown(
        """
        Servicos de buffet precisam estimar, com antecedencia, quanto
        alimento preparar para cada evento. Errar essa estimativa gera
        desperdicio de comida, custo operacional e impacto ambiental.
        Este dashboard explora um conjunto de eventos de buffet para
        entender **em que condicoes o desperdicio tende a ser maior**,
        usando a camada gold do pipeline do projeto
        (`data/gold/food_wastage_gold.csv`).
        """
    )

    st.subheader("Perguntas analiticas do projeto")
    st.markdown(
        """
        - **Q1** - O metodo de preparo e as condicoes de armazenamento
          influenciam o volume de desperdicio?
        - **Q2** - Como o tipo e o porte do evento se relacionam com o
          volume de desperdicio?
        - **Q3** - Existe relacao entre a quantidade produzida, a faixa de
          preco (pricing) e a taxa de desperdicio?
        - **Q4** - Quais combinacoes de caracteristicas operacionais estao
          associadas aos maiores niveis de desperdicio?
        """
    )

    st.subheader("Base de dados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros (apos filtros globais de qualidade)", f"{len(df):,}".replace(",", "."))
    col2.metric("Colunas", len(df.columns))
    col3.metric("Perfis operacionais distintos", df["event_profile"].nunique())

    with st.expander("Ver amostra da base gold"):
        st.dataframe(df.head(20), use_container_width=True)

    st.info(
        "Os filtros na barra lateral valem para todas as demais paginas do "
        "dashboard (Indicadores gerais, Analises por pergunta e Perfis de risco)."
    )


def page_indicadores(df_filtered) -> None:
    st.title("Indicadores gerais")
    st.caption("Resumo do desperdicio para a selecao atual de filtros.")
    render_indicator_cards(df_filtered)

    if df_filtered.empty:
        return

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            group_mean_bar(
                df_filtered,
                "event_type",
                "wastage_rate",
                title="Taxa media de desperdicio por tipo de evento",
            ),
            use_container_width=True,
        )
        st.caption(
            "Compara a taxa media de desperdicio entre os tipos de evento "
            "presentes na selecao atual; barras mais altas indicam eventos "
            "proporcionalmente mais desperdicadores."
        )
    with col2:
        st.plotly_chart(
            distribution_plot(
                df_filtered,
                "preparation_method",
                "wastage_rate",
                kind="box",
                title="Distribuicao da taxa de desperdicio por metodo de preparo",
            ),
            use_container_width=True,
        )
        st.caption(
            "O boxplot mostra a dispersao da taxa de desperdicio dentro de "
            "cada metodo de preparo, alem da mediana e possiveis valores atipicos."
        )


def page_perguntas(df_filtered) -> None:
    st.title("Analises por pergunta")
    if df_filtered.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return

    tab_q1, tab_q2, tab_q3, tab_q4 = st.tabs(["Q1", "Q2", "Q3", "Q4"])

    with tab_q1:
        st.subheader("Q1 - Metodo de preparo, armazenamento e tipo de alimento")
        st.plotly_chart(
            distribution_plot(
                df_filtered,
                "type_of_food",
                "wastage_rate",
                kind="violin",
                title="Distribuicao da taxa de desperdicio por tipo de alimento",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            interaction_heatmap(
                df_filtered,
                "storage_conditions",
                "type_of_food",
                "wastage_rate",
                title="Taxa media de desperdicio: armazenamento x tipo de alimento",
            ),
            use_container_width=True,
        )
        st.markdown(
            "**Leitura:** o violin plot mostra como a taxa de desperdicio se "
            "distribui dentro de cada tipo de alimento (forma mais larga = "
            "mais eventos naquela faixa de valor). O heatmap evidencia se o "
            "efeito da condicao de armazenamento muda conforme o alimento, "
            "em vez de ser constante entre categorias."
        )
        st.caption(
            "Achado da AED (base completa): Sit-down Dinner tem taxa media de "
            "7,51% contra 6,06% de Finger Food. O armazenamento nao muda a "
            "media geral (Refrigerado 6,88% vs. Temp. ambiente 6,86%), mas "
            "muda por alimento: Baked Goods e Dairy Products desperdicam "
            "cerca de 1,3 a 1,6 p.p. a mais em temperatura ambiente, enquanto "
            "Carnes e Vegetais nao mostram esse padrao."
        )

    with tab_q2:
        st.subheader("Q2 - Tipo e porte do evento")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                group_mean_bar(
                    df_filtered,
                    "event_type",
                    "wastage_per_guest",
                    title="Desperdicio medio por convidado, por tipo de evento",
                ),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                distribution_plot(
                    df_filtered,
                    "event_size",
                    "wastage_per_guest",
                    kind="box",
                    title="Distribuicao do desperdicio por convidado, por porte do evento",
                ),
                use_container_width=True,
            )
        st.markdown(
            "**Leitura:** compara o desperdicio per capita entre tipos de "
            "evento e portes de evento. Se as caixas/barras forem parecidas "
            "entre portes, o porte isolado explica pouco do desperdicio por "
            "convidado; diferencas mais claras aparecem por tipo de evento."
        )
        st.caption(
            "Achado da AED (base completa): desperdicio por convidado e quase "
            "constante entre portes (Pequeno 0,088, Medio 0,089, Grande "
            "0,092). Entre tipos de evento a diferenca tambem e pequena "
            "(Wedding 6,96% vs. Birthday/Corporate ~6,82%), sugerindo que "
            "porte isolado nao e um bom preditor do desperdicio per capita."
        )

    with tab_q3:
        st.subheader("Q3 - Quantidade produzida, pricing e taxa de desperdicio")
        st.plotly_chart(
            quantity_vs_wastage_scatter(
                df_filtered,
                color_col="pricing",
                title="Quantidade produzida x taxa de desperdicio",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            interaction_heatmap(
                df_filtered,
                "pricing",
                "preparation_method",
                "wastage_rate",
                title="Taxa media de desperdicio: pricing x metodo de preparo",
            ),
            use_container_width=True,
        )
        corr = df_filtered["quantity_of_food"].corr(df_filtered["wastage_rate"])
        st.markdown(
            f"**Leitura:** a correlacao linear entre quantidade produzida e "
            f"taxa de desperdicio na selecao atual e **r = {corr:.3f}**. O "
            "heatmap mostra se pricing e metodo de preparo interagem, ou "
            "seja, se o efeito de um depende do nivel do outro, o que uma "
            "media isolada por variavel nao revelaria."
        )
        st.caption(
            "Achado da AED (base completa): pricing High tem taxa media de "
            "8,81% contra 5,46% (Low) e 5,84% (Moderate) - a maior diferenca "
            "isolada entre variaveis categoricas do estudo. A quantidade "
            "produzida tem correlacao fraca a moderada com a taxa de "
            "desperdicio (r = 0,25 na base completa); a celula mais critica "
            "do heatmap e pricing High + Sit-down Dinner (9,16%), e a mais "
            "baixa e pricing Low + Finger Food (5,00%)."
        )

    with tab_q4:
        st.subheader("Q4 - Perfis operacionais de maior risco")
        profiles = risk_profiles(df_filtered)
        st.plotly_chart(risk_ranking_bar(profiles, top_n=10), use_container_width=True)
        st.markdown(
            "**Leitura:** cada perfil combina porte do evento, metodo de "
            "preparo e pricing (`event_profile`). Perfis com poucos eventos "
            "(marcados como baixa confianca na tabela da pagina *Perfis de "
            "risco*) podem ter medias instaveis e devem ser interpretados "
            "com cautela."
        )
        st.caption(
            "Achado da AED (base completa, 27 perfis): o maior risco e "
            "'Pequeno | Sit-down Dinner | High' (~11,14% de taxa media, 18 "
            "eventos - amostra pequena). Entre os perfis com mais eventos, "
            "'Medio | Sit-down Dinner | High' e 'Grande | Sit-down Dinner | "
            "High' tambem aparecem no topo, por volta de 9%."
        )


def page_perfis(df_filtered) -> None:
    st.title("Perfis de risco")
    if df_filtered.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return

    profiles = risk_profiles(df_filtered)
    top = profiles.iloc[0]

    st.markdown(
        f"O perfil com maior taxa media de desperdicio na selecao atual e "
        f"**{top['event_profile']}**, com taxa media de **{top['taxa_media']:.2f}%** "
        f"em **{int(top['n_eventos'])}** evento(s)."
    )

    st.plotly_chart(risk_ranking_bar(profiles, top_n=15), use_container_width=True)

    st.subheader("Tabela completa de perfis")
    display_cols = {
        "rank_risco": "Rank",
        "event_profile": "Perfil (porte | preparo | pricing)",
        "n_eventos": "N eventos",
        "taxa_media": "Taxa media (%)",
        "taxa_mediana": "Taxa mediana (%)",
        "desperdicio_medio": "Desperdicio medio",
        "convidados_medios": "Convidados medios",
        "baixa_confianca": "Baixa confianca (n < 3)",
    }
    rounded = profiles.round(
        {"taxa_media": 2, "taxa_mediana": 2, "desperdicio_medio": 2, "convidados_medios": 1}
    )
    st.dataframe(
        rounded.rename(columns=display_cols)[list(display_cols.values())],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Perfis marcados como 'baixa confianca' tem menos de 3 eventos na "
        "selecao atual; suas medias podem variar muito com poucos casos a mais."
    )


def page_conclusoes() -> None:
    st.title("Conclusoes e limitacoes")

    st.subheader("Hipoteses avaliadas (base completa)")
    st.caption(
        "Situacao de cada hipotese avaliada na etapa de analise estatistica "
        "final (ver `analysis/analise_estatistica.py` para os testes formais: "
        "Welch, Kruskal-Wallis, bootstrap e correlacao)."
    )
    hipoteses = [
        {
            "Hipotese": "HE-01 (Q1)",
            "Descricao": "Sit-down Dinner tem maior taxa de desperdicio que os demais metodos de preparo.",
            "Achado": "7,51% vs. 6,06% (Finger Food) e 7,02% (Buffet).",
            "Situacao": "Confirmada",
        },
        {
            "Hipotese": "HE-02 (Q1)",
            "Descricao": "O efeito do armazenamento depende do tipo de alimento.",
            "Achado": "Sem diferenca na media geral (6,88% vs. 6,86%), mas Baked Goods/Dairy pioram ~1,3-1,6 p.p. em temp. ambiente.",
            "Situacao": "Confirmada (efeito condicional, nao geral)",
        },
        {
            "Hipotese": "HE-03 (Q3)",
            "Descricao": "Pricing High esta associado a maior taxa de desperdicio.",
            "Achado": "8,81% (High) vs. 5,46% (Low) e 5,84% (Moderate).",
            "Situacao": "Confirmada",
        },
        {
            "Hipotese": "HE-04 (Q3)",
            "Descricao": "Maior quantidade produzida se associa a maior taxa de desperdicio.",
            "Achado": "7,54% (Alta) vs. 6,28% (Baixa); correlacao r = 0,25 (fraca a moderada).",
            "Situacao": "Parcialmente confirmada",
        },
        {
            "Hipotese": "HE-05 (Q4)",
            "Descricao": "Existem perfis operacionais que concentram maior risco de desperdicio.",
            "Achado": "'Pequeno | Sit-down Dinner | High' lidera com ~11,1% (18 eventos); High + Sit-down Dinner e o pior par em todo porte.",
            "Situacao": "Confirmada (com ressalva de amostra pequena no perfil-lider)",
        },
        {
            "Hipotese": "HE-06 (Q2)",
            "Descricao": "O porte do evento, isolado, e bom preditor do desperdicio por convidado.",
            "Achado": "Desperdicio por convidado quase constante entre portes (0,088 a 0,092).",
            "Situacao": "Rejeitada",
        },
    ]
    st.table(pd.DataFrame(hipoteses).set_index("Hipotese"))

    st.subheader("Conclusoes tecnicas")
    st.markdown(
        """
        - O metodo de preparo (`preparation_method`) esta associado a
          diferencas consistentes na taxa media de desperdicio: Sit-down
          Dinner desperdica mais que Buffet e Finger Food, em todas as
          faixas de pricing.
        - O efeito da condicao de armazenamento (`storage_conditions`)
          nao e uniforme entre tipos de alimento: o heatmap da pagina *Q1*
          mostra que Baked Goods e Dairy Products sao mais sensiveis ao
          armazenamento em temperatura ambiente do que Carnes e Vegetais.
        - A faixa de preco (`pricing`) e a variavel isolada com maior poder
          de discriminacao encontrada na analise: eventos High tem taxa de
          desperdicio bem acima de Low e Moderate.
        - A quantidade produzida tem relacao positiva, porem fraca a
          moderada, com a taxa de desperdicio (r = 0,25); nao deve ser
          usada isoladamente para prever desperdicio.
        - Perfis operacionais que combinam pricing High com Sit-down Dinner
          concentram os maiores riscos de desperdicio, especialmente em
          eventos pequenos, e justificam atencao operacional direcionada
          (pagina *Perfis de risco*).
        - O porte do evento (`event_size`), isoladamente, nao explica bem o
          desperdicio por convidado; diferencas de tipo de evento e pricing
          parecem pesar mais.
        """
    )

    st.subheader("Limitacoes e cuidados de interpretacao")
    st.markdown(
        """
        - O dataset e **observacional**: as associacoes descritas aqui nao
          devem ser lidas como relacoes de causa e efeito.
        - Perfis operacionais com poucos eventos (ver coluna "baixa
          confianca" na pagina *Perfis de risco*) tem medias mais instaveis
          e sensiveis a valores extremos.
        - Os indicadores mudam conforme os filtros aplicados; comparacoes
          entre paginas so sao validas quando os mesmos filtros estao ativos.
        - Este dashboard resume os achados; os testes estatisticos formais
          (intervalos de confianca, p-valor, tamanho de efeito) estao
          documentados em `analysis/analise_estatistica.py` e nos relatorios
          gerados por ele.
        - Algumas categorias sao sub-representadas na base (ex.: metodo
          Buffet e historico de compra "Occasional"), o que reduz a
          estabilidade de rankings e medias que dependam delas.
        - O dataset tem origem sintetica/educacional (Kaggle); os padroes
          encontrados ilustram o metodo de analise, mas nao devem ser
          generalizados diretamente para operacoes reais sem validacao
          adicional.
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Desperdicio de Alimentos em Buffets",
        page_icon="🍽️",
        layout="wide",
    )

    try:
        df = load_data()
    except (FileNotFoundError, ValueError) as exc:
        st.title("Desperdicio de alimentos em servicos de buffet")
        st.error(str(exc))
        st.stop()
        return

    st.sidebar.title("Navegacao")
    page = st.sidebar.radio("Ir para", PAGES, label_visibility="collapsed")

    selections = render_sidebar_filters(df)
    df_filtered = apply_filters(df, selections)

    if page == "Contexto e problema":
        page_contexto(df)
    elif page == "Indicadores gerais":
        page_indicadores(df_filtered)
    elif page == "Analises por pergunta":
        page_perguntas(df_filtered)
    elif page == "Perfis de risco":
        page_perfis(df_filtered)
    elif page == "Conclusoes e limitacoes":
        page_conclusoes()


if __name__ == "__main__":
    main()
