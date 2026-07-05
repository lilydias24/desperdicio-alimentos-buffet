"""Funcoes de formatacao de numeros usadas nos indicadores do dashboard."""

from __future__ import annotations


def format_percent(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{decimals}f}%"


def format_number(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:,.{decimals}f}".replace(",", ".")


def format_delta_percent(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "-"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f} p.p."
