"""CSS customizado do dashboard, na mesma paleta verde/neutra dos gráficos.

Mantido separado de `app.py` para que o ajuste visual (cabeçalho colorido,
cartões de métrica, cabeçalhos de seção, sidebar, badges) fique isolado do
conteúdo das páginas.
"""

from __future__ import annotations

import streamlit as st

from utils.palette import PRIMARY_GREEN, PRIMARY_GREEN_DARK, PRIMARY_GREEN_LIGHT, RISK_BADGE_COLORS

_CSS = f"""
<style>
/* Barra superior nativa do Streamlit (antes vazia/transparente): degrade
   verde, com icones do menu em branco para manter contraste. */
header[data-testid="stHeader"] {{
    background: linear-gradient(90deg, {PRIMARY_GREEN_DARK} 0%, {PRIMARY_GREEN} 100%);
}}
header[data-testid="stHeader"] svg {{
    fill: white;
}}
header[data-testid="stHeader"] span {{
    color: white;
}}

/* Reduz o espaco vazio entre o cabecalho e o banner/titulo da pagina. */
.block-container {{
    padding-top: 4rem;
}}

/* Banner de identidade visual, renderizado por render_hero_banner(). */
.hero-banner {{
    background: linear-gradient(90deg, {PRIMARY_GREEN_DARK} 0%, {PRIMARY_GREEN} 100%);
    border-radius: 12px;
    padding: 1.1rem 1.5rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 2px 10px color-mix(in srgb, {PRIMARY_GREEN_DARK} 40%, transparent);
}}
.hero-banner .hero-title {{
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1.3;
}}
.hero-banner .hero-subtitle {{
    opacity: 0.9;
    font-size: 0.92rem;
    margin-top: 0.15rem;
}}

/* Cartoes de indicador (st.metric): borda colorida + leve destaque de fundo */
div[data-testid="stMetric"] {{
    background: color-mix(in srgb, {PRIMARY_GREEN} 6%, transparent);
    border: 1px solid color-mix(in srgb, {PRIMARY_GREEN} 25%, transparent);
    border-left: 4px solid {PRIMARY_GREEN};
    border-radius: 10px;
    padding: 0.85rem 1rem 0.7rem 1rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}}
div[data-testid="stMetric"]:hover {{
    border-left-color: {PRIMARY_GREEN_LIGHT};
    transform: translateY(-1px);
}}
div[data-testid="stMetricValue"] {{
    color: {PRIMARY_GREEN};
}}

/* Cartoes/containers com borda nativa (st.container(border=True)) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 12px !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"]) {{
    border-color: color-mix(in srgb, {PRIMARY_GREEN} 30%, transparent) !important;
}}

/* Cabecalhos de secao (st.subheader / st.header) com friso verde */
h2, h3 {{
    border-left: 4px solid {PRIMARY_GREEN};
    padding-left: 0.6rem;
}}

/* Sidebar: friso sutil para reforcar a identidade visual */
section[data-testid="stSidebar"] {{
    border-right: 2px solid color-mix(in srgb, {PRIMARY_GREEN} 30%, transparent);
}}

/* Abas (st.tabs): mais respiro entre os rotulos */
button[data-baseweb="tab"] {{
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}}

/* Botoes: leve efeito de elevacao no hover */
div[data-testid="stButton"] > button {{
    border-radius: 8px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div[data-testid="stButton"] > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 3px 10px color-mix(in srgb, {PRIMARY_GREEN} 35%, transparent);
}}

/* Badges de risco (usados nos modais e na pagina de perfis) */
.badge-risco {{
    display: inline-block;
    padding: 0.15rem 0.65rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
}}
.badge-baixo {{ background-color: {RISK_BADGE_COLORS["baixo"]}; color: #0b2818; }}
.badge-medio {{ background-color: {RISK_BADGE_COLORS["medio"]}; }}
.badge-alto  {{ background-color: {RISK_BADGE_COLORS["alto"]}; }}
</style>
"""


def inject_custom_css() -> None:
    """Injeta o CSS customizado do dashboard. Chamar uma vez em `main()`."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero_banner() -> None:
    """Banner colorido de identidade visual, exibido no topo de toda página."""
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🍽️ Grupo 03 — Investigação do Desperdício de Alimentos</div>
            <div class="hero-subtitle">Dashboard interativo de serviços de buffet · Introdução à Ciência de Dados</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge_html(nivel: str, texto: str) -> str:
    """HTML de um badge colorido (`nivel` em {'baixo', 'medio', 'alto'})."""
    classe = {"baixo": "badge-baixo", "medio": "badge-medio", "alto": "badge-alto"}.get(
        nivel, "badge-medio"
    )
    return f'<span class="badge-risco {classe}">{texto}</span>'
