"""Formato legible para etiquetas de gráficos (sin notación científica)."""
from __future__ import annotations

import math

_MAX_CHART_COUNT = 500_000
_PCT_DECIMALS = 2


def floor_pct(part: int | float, total: int | float, *, decimals: int = _PCT_DECIMALS) -> float:
    """Porcentaje con truncamiento hacia abajo — evita 100% cuando hay NOK."""
    if total <= 0:
        return 0.0
    raw = 100.0 * float(part) / float(total)
    factor = 10**decimals
    return math.floor(raw * factor) / factor


def format_pct(part: int | float, total: int | float, *, decimals: int = _PCT_DECIMALS) -> str:
    return f"{floor_pct(part, total, decimals=decimals):.{decimals}f}"


def format_count(value: int | float) -> str:
    """Entero con separador de miles — legible hasta 500k filas."""
    number = int(round(value))
    if number < 0:
        return f"-{format_count(-number)}"
    if number > _MAX_CHART_COUNT:
        return f"{number:,}".replace(",", ".")
    return f"{number:,}".replace(",", ".")


def format_category_label(name: str, *, max_len: int = 18) -> str:
    text = str(name or "").strip()
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 1]}…"
