"""Paleta de cores central do dashboard (verde-escuro + neutros).

Usada tanto pelos graficos Plotly (`app/components/charts.py`) quanto
pelo CSS customizado (`app/utils/styling.py`), para garantir que os
graficos e a interface usem exatamente as mesmas cores.
"""

from __future__ import annotations

# Shades de verde usadas em graficos categoricos (boxplot/violin/scatter).
CATEGORICAL_PALETTE = [
    "#1B4332",  # verde muito escuro
    "#40916C",  # verde medio
    "#95D5B2",  # verde claro
    "#588157",  # verde oliva
    "#344E41",  # verde quase preto
    "#A3B18A",  # verde acinzentado (neutro)
]

PRIMARY_GREEN = "#2D6A4F"
PRIMARY_GREEN_LIGHT = "#74C69D"
PRIMARY_GREEN_DARK = "#1B4332"
NEUTRAL_DARK = "#1B1B1B"

GREEN_SCALE = "Greens"

PRICING_COLOR_MAP = {
    "Low": "#95D5B2",
    "Moderate": "#40916C",
    "High": "#1B4332",
}

# Badges de risco (do perfil menos ao mais arriscado), na mesma familia
# de verdes usada no ranking (app/components/charts.py:risk_ranking_bar).
RISK_BADGE_COLORS = {
    "baixo": "#95D5B2",
    "medio": "#40916C",
    "alto": "#1B4332",
}
