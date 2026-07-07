"""Dashboard Streamlit - Investigação do Desperdício de Alimentos em Buffets.

Ponto de entrada da aplicação (Parte 2 da entrega final). Concentra a
navegação entre páginas e delega cálculo de indicadores, filtros e
gráficos para os módulos em `app/services` e `app/components`.

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
from components.modals import glossario_modal, interpretacao_modal, perfil_detalhe_modal
from services.data import apply_filters, load_data, risk_profiles
from utils.styling import inject_custom_css, render_hero_banner

PAGES = [
    "Contexto e problema",
    "Indicadores gerais",
    "Análises por pergunta",
    "Perfis de risco",
    "Conclusões e limitações",
]


def page_contexto(df) -> None:
    st.title("Desperdício de alimentos em serviços de buffet")
    st.markdown(
        """
        Serviços de buffet precisam estimar, com antecedência, quanto
        alimento preparar para cada evento. Errar essa estimativa gera
        desperdício de comida, custo operacional e impacto ambiental.
        Este dashboard explora um conjunto de eventos de buffet para
        entender **em que condições o desperdício tende a ser maior**,
        usando a camada gold do pipeline do projeto
        (`data/gold/food_wastage_gold.csv`).
        """
    )

    st.subheader("Público-alvo")
    st.markdown(
        """
        Equipes de planejamento e operação de serviços de buffet
        (gestores de produção, compras e eventos) que precisam decidir
        quanto alimento preparar e identificar combinações operacionais
        (método de preparo, armazenamento, pricing, porte do evento) com
        maior risco de desperdício.
        """
    )

    st.subheader("Fonte, escopo e unidade de análise")
    st.markdown(
        """
        - **Fonte:** dataset *Food Wastage Data in Restaurant*, publicado
          no [Kaggle](https://www.kaggle.com/datasets/trevinhannibal/food-wastage-data-in-restaurant).
        - **Unidade de análise:** cada linha representa **um
          registro/evento de desperdício de alimentos** (um preparo/serviço
          associado a um evento) — a base gold não é agregada por categoria.
        - **Escopo e recorte:** dataset sintético/educacional, sem data de
          coleta, identificador único de evento ou recorte geográfico real
          documentados pela fonte; os valores de `quantity_of_food` e
          `wastage_food_amount` são tratados em uma unidade assumida (ver
          `docs/dicionario_indicadores.md`). Os resultados ilustram o
          método de análise e não devem ser generalizados para operações
          reais sem validação adicional.
        """
    )

    st.subheader("Perguntas analíticas do projeto")
    st.markdown(
        """
        - **Q1** — O método de preparo e as condições de armazenamento
          influenciam o volume de desperdício?
        - **Q2** — Como o tipo e o porte do evento se relacionam com o
          volume de desperdício?
        - **Q3** — Existe relação entre a quantidade produzida, a faixa de
          preço (pricing) e a taxa de desperdício?
        - **Q4** — Quais combinações de características operacionais estão
          associadas aos maiores níveis de desperdício?
        """
    )

    st.subheader("Base de dados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros (após filtros globais de qualidade)", f"{len(df):,}".replace(",", "."))
    col2.metric("Colunas", len(df.columns))
    col3.metric("Perfis operacionais distintos", df["event_profile"].nunique())

    with st.expander("Ver amostra da base gold"):
        st.dataframe(df.head(20), use_container_width=True)

    st.info(
        "Os filtros na barra lateral valem para todas as demais páginas do "
        "dashboard (Indicadores gerais, Análises por pergunta e Perfis de risco)."
    )


def page_indicadores(df_filtered) -> None:
    st.title("Indicadores gerais")
    st.caption("Resumo do desperdício para a seleção atual de filtros.")
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
                title="Taxa média de desperdício por tipo de evento",
            ),
            use_container_width=True,
        )
        st.caption(
            "Compara a taxa média de desperdício entre os tipos de evento "
            "presentes na seleção atual; barras mais altas indicam eventos "
            "proporcionalmente mais desperdiçadores."
        )
    with col2:
        kind_label = st.radio(
            "Tipo de gráfico",
            options=["Boxplot", "Violin"],
            horizontal=True,
            label_visibility="collapsed",
            key="indicadores_kind_toggle",
        )
        kind = "violin" if kind_label == "Violin" else "box"
        st.plotly_chart(
            distribution_plot(
                df_filtered,
                "preparation_method",
                "wastage_rate",
                kind=kind,
                title="Distribuição da taxa de desperdício por método de preparo",
            ),
            use_container_width=True,
        )
        st.caption(
            "O boxplot/violin mostra a dispersão da taxa de desperdício "
            "dentro de cada método de preparo, além da mediana e possíveis "
            "valores atípicos."
        )


def page_perguntas(df_filtered) -> None:
    st.title("Análises por pergunta")
    if df_filtered.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return

    tab_q1, tab_q2, tab_q3, tab_q4 = st.tabs(["Q1", "Q2", "Q3", "Q4"])

    with tab_q1:
        st.subheader("Q1 — Método de preparo, armazenamento e tipo de alimento")
        st.plotly_chart(
            distribution_plot(
                df_filtered,
                "type_of_food",
                "wastage_rate",
                kind="violin",
                title="Distribuição da taxa de desperdício por tipo de alimento",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            interaction_heatmap(
                df_filtered,
                "storage_conditions",
                "type_of_food",
                "wastage_rate",
                title="Taxa média de desperdício: armazenamento x tipo de alimento",
            ),
            use_container_width=True,
        )
        st.markdown(
            "**Leitura:** o violin plot mostra como a taxa de desperdício se "
            "distribui dentro de cada tipo de alimento (forma mais larga = "
            "mais eventos naquela faixa de valor). O heatmap evidencia se a "
            "diferença associada à condição de armazenamento muda conforme "
            "o alimento, em vez de ser constante entre categorias — sem "
            "testes formais de significância nesta página, essas são "
            "comparações descritivas."
        )
        st.caption(
            "Achado da AED (base completa): Sit-down Dinner tem taxa média de "
            "7,51% contra 6,06% de Finger Food. O armazenamento não muda a "
            "média geral (Refrigerado 6,88% vs. Temp. ambiente 6,86%). Na "
            "AED descritiva, Baked Goods e Dairy Products desperdiçam cerca "
            "de 1,3 a 1,6 p.p. a mais em temperatura ambiente — mas o teste "
            "de Welch formal por alimento (Parte 1) não confirma essa "
            "diferença como estatisticamente significativa (p = 0,076 e "
            "p = 0,058, respectivamente); tratar como padrão sugestivo, "
            "não como achado confirmado."
        )

    with tab_q2:
        st.subheader("Q2 — Tipo e porte do evento")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                group_mean_bar(
                    df_filtered,
                    "event_type",
                    "wastage_per_guest",
                    title="Desperdício médio por convidado, por tipo de evento",
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
                    title="Distribuição do desperdício por convidado, por porte do evento",
                ),
                use_container_width=True,
            )
        st.markdown(
            "**Leitura:** compara o desperdício per capita entre tipos de "
            "evento e portes de evento. Se as caixas/barras forem parecidas "
            "entre portes, o porte isolado explica pouco do desperdício por "
            "convidado; diferenças mais claras aparecem por tipo de evento."
        )
        st.caption(
            "Achado da AED (base completa): desperdício por convidado é quase "
            "constante entre portes (Pequeno 0,088, Médio 0,089, Grande "
            "0,092). Entre tipos de evento a diferença também é pequena "
            "(Wedding 6,96% vs. Birthday/Corporate ~6,82%), sugerindo que "
            "porte isolado não é um bom preditor do desperdício per capita."
        )

    with tab_q3:
        st.subheader("Q3 — Quantidade produzida, pricing e taxa de desperdício")
        st.plotly_chart(
            quantity_vs_wastage_scatter(
                df_filtered,
                color_col="pricing",
                title="Quantidade produzida x taxa de desperdício",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            interaction_heatmap(
                df_filtered,
                "pricing",
                "preparation_method",
                "wastage_rate",
                title="Taxa média de desperdício: pricing x método de preparo",
            ),
            use_container_width=True,
        )
        corr = df_filtered["quantity_of_food"].corr(df_filtered["wastage_rate"])
        st.markdown(
            f"**Leitura:** a correlação linear entre quantidade produzida e "
            f"taxa de desperdício na seleção atual é **r = {corr:.3f}**. O "
            "heatmap mostra a taxa média observada em cada combinação de "
            "pricing e método de preparo; combinações com taxa bem acima "
            "ou abaixo do esperado pelas médias isoladas de cada variável "
            "indicam um perfil de risco específico, sem que isso demonstre "
            "uma forma de interação estatística formal entre os fatores."
        )
        st.caption(
            "Achado da AED (base completa): pricing High tem taxa média de "
            "8,81% contra 5,46% (Low) e 5,84% (Moderate) — a maior diferença "
            "isolada entre variáveis categóricas do estudo. A quantidade "
            "produzida tem correlação fraca a moderada com a taxa de "
            "desperdício (r = 0,25 na base completa); a célula mais crítica "
            "do heatmap é pricing High + Sit-down Dinner (9,16%), e a mais "
            "baixa é pricing Low + Finger Food (5,00%)."
        )

    with tab_q4:
        st.subheader("Q4 — Perfis operacionais de maior risco")
        profiles = risk_profiles(df_filtered)
        st.plotly_chart(risk_ranking_bar(profiles, top_n=10), use_container_width=True)
        st.markdown(
            "**Leitura:** cada perfil combina porte do evento, método de "
            "preparo e pricing (`event_profile`). Perfis com poucos eventos "
            "(marcados como baixa confiança na tabela da página *Perfis de "
            "risco*) podem ter médias instáveis e devem ser interpretados "
            "com cautela."
        )
        st.caption(
            "Achado da AED (base completa, 27 perfis): o maior risco é "
            "'Pequeno | Sit-down Dinner | High' (~11,14% de taxa média, 18 "
            "eventos — amostra pequena). Entre os perfis com mais eventos, "
            "'Médio | Sit-down Dinner | High' e 'Grande | Sit-down Dinner | "
            "High' também aparecem no topo, por volta de 9%."
        )


def page_perfis(df_filtered) -> None:
    st.title("Perfis de risco")
    if df_filtered.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return

    profiles = risk_profiles(df_filtered)
    top = profiles.iloc[0]
    media_geral = df_filtered["wastage_rate"].mean()

    st.markdown(
        f"O perfil com maior taxa média de desperdício na seleção atual é "
        f"**{top['event_profile']}**, com taxa média de **{top['taxa_media']:.2f}%** "
        f"em **{int(top['n_eventos'])}** evento(s)."
    )

    col_ranking, col_detalhe = st.columns([3, 1])
    with col_ranking:
        top_n = st.slider(
            "Quantos perfis mostrar no ranking",
            min_value=5,
            max_value=len(profiles),
            value=min(15, len(profiles)),
            key="perfis_top_n",
        )
        st.plotly_chart(risk_ranking_bar(profiles, top_n=top_n), use_container_width=True)
    with col_detalhe:
        with st.container(border=True):
            st.markdown("**Consultar um perfil**")
            perfil_escolhido = st.selectbox(
                "Perfil",
                options=profiles["event_profile"],
                label_visibility="collapsed",
                key="perfis_selectbox",
            )
            if st.button("Ver detalhes", use_container_width=True):
                linha = profiles.loc[profiles["event_profile"] == perfil_escolhido].iloc[0]
                perfil_detalhe_modal(linha, media_geral, len(profiles))

    st.subheader("Tabela completa de perfis")
    display_cols = {
        "rank_risco": "Rank",
        "event_profile": "Perfil (porte | preparo | pricing)",
        "n_eventos": "Nº de eventos",
        "taxa_media": "Taxa média (%)",
        "taxa_mediana": "Taxa mediana (%)",
        "desperdicio_medio": "Desperdício médio",
        "convidados_medios": "Convidados médios",
        "baixa_confianca": "Baixa confiança (n < 3)",
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
        "Perfis marcados como 'baixa confiança' têm menos de 3 eventos na "
        "seleção atual; suas médias podem variar muito com poucos casos a mais."
    )


def page_conclusoes() -> None:
    st.title("Conclusões e limitações")

    st.subheader("Hipóteses avaliadas (base completa)")
    st.caption(
        "Cada hipótese é classificada como **Confirmada**, **Rejeitada** ou "
        "**Não avaliável** (dados insuficientes), conforme a etapa de "
        "análise estatística final (ver `analysis/analise_estatistica.py` "
        "para os testes formais: Welch, Kruskal-Wallis, bootstrap e "
        "correlação). Nenhuma das seis ficou como não avaliável: a base "
        "gold permitiu avaliar todas."
    )
    hipoteses = [
        {
            "Hipótese": "HE-01 (Q1)",
            "Descrição": "Sit-down Dinner tem maior taxa de desperdício que os demais métodos de preparo.",
            "Achado": "7,51% vs. 6,06% (Finger Food) e 7,02% (Buffet).",
            "Situação": "Confirmada",
            "Ressalva": "-",
        },
        {
            "Hipótese": "HE-02 (Q1)",
            "Descrição": "A diferença de desperdício associada ao armazenamento depende do tipo de alimento.",
            "Achado": "Sem diferença na média geral (6,88% vs. 6,86%). Na AED (descritiva), Baked Goods/Dairy pioram ~1,3-1,6 p.p. em temp. ambiente, mas o teste de Welch formal por alimento não confirma significância (p = 0,076 em Baked Goods; p = 0,058 em Dairy Products; demais alimentos também não significativos).",
            "Situação": "Rejeitada",
            "Ressalva": "Padrão descritivo sugestivo (mesma direção em 2 de 5 alimentos), mas não sustentado pelo teste formal ao nível de 5%; tratar como hipótese em aberto, não como achado confirmado.",
        },
        {
            "Hipótese": "HE-03 (Q3)",
            "Descrição": "Pricing High está associado a maior taxa de desperdício.",
            "Achado": "8,81% (High) vs. 5,46% (Low) e 5,84% (Moderate).",
            "Situação": "Confirmada",
            "Ressalva": "-",
        },
        {
            "Hipótese": "HE-04 (Q3)",
            "Descrição": "Maior quantidade produzida se associa a maior taxa de desperdício.",
            "Achado": "7,54% (Alta) vs. 6,28% (Baixa); correlação r = 0,25 (fraca a moderada).",
            "Situação": "Confirmada",
            "Ressalva": "Associação fraca a moderada; quantidade isolada não é bom preditor.",
        },
        {
            "Hipótese": "HE-05 (Q4)",
            "Descrição": "Existem perfis operacionais que concentram maior risco de desperdício.",
            "Achado": "'Pequeno | Sit-down Dinner | High' lidera com ~11,1% (18 eventos); High + Sit-down Dinner é o perfil de maior taxa observada em todo porte.",
            "Situação": "Confirmada",
            "Ressalva": "Perfil-líder tem amostra pequena (18 eventos); ler com cautela.",
        },
        {
            "Hipótese": "HE-06 (Q2)",
            "Descrição": "O porte do evento, isolado, é bom preditor do desperdício por convidado.",
            "Achado": "Desperdício por convidado quase constante entre portes (0,088 a 0,092).",
            "Situação": "Rejeitada",
            "Ressalva": "-",
        },
    ]
    st.table(pd.DataFrame(hipoteses).set_index("Hipótese"))

    st.subheader("Conclusões técnicas")
    st.markdown(
        """
        - O método de preparo (`preparation_method`) está associado a
          diferenças consistentes na taxa média de desperdício: Sit-down
          Dinner desperdiça mais que Buffet e Finger Food, em todas as
          faixas de pricing.
        - Na exploração descritiva, a diferença de desperdício associada à
          condição de armazenamento (`storage_conditions`) parece não ser
          uniforme entre tipos de alimento (Baked Goods e Dairy Products
          com taxas mais altas em temperatura ambiente), mas o teste
          formal por alimento não confirma essa diferença como
          estatisticamente significativa (HE-02, ver tabela de hipóteses
          acima) — tratar como hipótese em aberto para investigação futura.
        - A faixa de preço (`pricing`) é a variável isolada com maior poder
          de discriminação encontrada na análise: eventos High têm taxa de
          desperdício bem acima de Low e Moderate.
        - A quantidade produzida tem relação positiva, porém fraca a
          moderada, com a taxa de desperdício (r = 0,25); não deve ser
          usada isoladamente para prever desperdício.
        - Perfis operacionais que combinam pricing High com Sit-down Dinner
          concentram os maiores riscos de desperdício, especialmente em
          eventos pequenos, e justificam atenção operacional direcionada
          (página *Perfis de risco*).
        - O porte do evento (`event_size`), isoladamente, não explica bem o
          desperdício por convidado; diferenças de tipo de evento e pricing
          parecem pesar mais.
        """
    )

    st.subheader("Limitações e cuidados de interpretação")
    st.markdown(
        """
        - O dataset é **observacional**: as associações descritas aqui não
          devem ser lidas como relações de causa e efeito.
        - Perfis operacionais com poucos eventos (ver coluna "baixa
          confiança" na página *Perfis de risco*) têm médias mais instáveis
          e sensíveis a valores extremos.
        - Os indicadores mudam conforme os filtros aplicados; comparações
          entre páginas só são válidas quando os mesmos filtros estão ativos.
        - Este dashboard resume os achados; os testes estatísticos formais
          (intervalos de confiança, p-valor, tamanho de efeito) estão
          documentados em `analysis/analise_estatistica.py` e nos relatórios
          gerados por ele.
        - Algumas categorias são sub-representadas na base (ex.: método
          Buffet e histórico de compra "Occasional"), o que reduz a
          estabilidade de rankings e médias que dependam delas.
        - O dataset tem origem sintética/educacional (Kaggle); os padrões
          encontrados ilustram o método de análise, mas não devem ser
          generalizados diretamente para operações reais sem validação
          adicional.
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Desperdício de Alimentos em Buffets",
        page_icon="🍽️",
        layout="wide",
    )
    inject_custom_css()
    render_hero_banner()

    try:
        df = load_data()
    except (FileNotFoundError, ValueError) as exc:
        st.title("Desperdício de alimentos em serviços de buffet")
        st.error(str(exc))
        st.stop()
        return

    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Ir para", PAGES, label_visibility="collapsed")

    col_glossario, col_leitura = st.sidebar.columns(2)
    if col_glossario.button("📖 Glossário", use_container_width=True):
        glossario_modal()
    if col_leitura.button("🔎 Como ler", use_container_width=True):
        interpretacao_modal()

    selections = render_sidebar_filters(df)
    df_filtered = apply_filters(df, selections)

    if page == "Contexto e problema":
        page_contexto(df)
    elif page == "Indicadores gerais":
        page_indicadores(df_filtered)
    elif page == "Análises por pergunta":
        page_perguntas(df_filtered)
    elif page == "Perfis de risco":
        page_perfis(df_filtered)
    elif page == "Conclusões e limitações":
        page_conclusoes()


if __name__ == "__main__":
    main()
