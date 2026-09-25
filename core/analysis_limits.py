"""Límites configurables para visualización tabular."""
from __future__ import annotations

import re
from dataclasses import dataclass

DISPLAY_ROW_PRESETS: tuple[int, ...] = (5_000, 10_000, 25_000, 50_000, 100_000)
RELOAD_VOLUME_PRESETS: tuple[int, ...] = (50_000, 100_000, 200_000)
DEFAULT_MAX_DISPLAY_ROWS = DISPLAY_ROW_PRESETS[0]
# Tope pandas del CLI headless (run_emr_qa_job.sh). La UI sigue en 200 MiB.
CLI_PANDAS_MAX_BYTES = 1_073_741_824  # 1 GiB
# Filas máximas que la UI lee de un archivo que supera el tope de bytes.
UI_SAMPLE_MAX_ROWS = DISPLAY_ROW_PRESETS[-1]
REFERENCE_COLUMN_COUNT = 20
MANAGEABLE_CELL_BUDGET = DEFAULT_MAX_DISPLAY_ROWS * REFERENCE_COLUMN_COUNT
SAMPLE_ROW_MIN = 10


@dataclass(frozen=True)
class ReloadRowChoice:
    rows: int
    kind: str  # total | pct50 | pct10 | preset


def normalize_max_display_rows(value: int) -> int:
    """Ajusta al preset permitido más cercano (hacia arriba) o al máximo."""
    if value in DISPLAY_ROW_PRESETS:
        return value
    for preset in DISPLAY_ROW_PRESETS:
        if value <= preset:
            return preset
    return DISPLAY_ROW_PRESETS[-1]


def reference_column_count(column_count: int) -> int:
    """Columnas usadas solo para estimar volumen (tope {REFERENCE_COLUMN_COUNT})."""
    return min(max(column_count, 1), REFERENCE_COLUMN_COUNT)


def estimate_cell_volume(total_rows: int, column_count: int) -> int:
    """Filas × min(columnas reales, referencia). No limita columnas del archivo."""
    return total_rows * reference_column_count(column_count)


def exceeds_manageable_volume(rows: int, column_count: int) -> bool:
    return estimate_cell_volume(rows, column_count) > MANAGEABLE_CELL_BUDGET


def suggested_max_display_rows(column_count: int, total_rows: int) -> int:
    """Filas sugeridas para mantener el volumen estimado dentro del umbral manejable."""
    if total_rows <= 0:
        return DEFAULT_MAX_DISPLAY_ROWS
    cap = MANAGEABLE_CELL_BUDGET // reference_column_count(column_count)
    if total_rows <= cap:
        return total_rows
    return min(total_rows, cap)


def display_row_options(total_rows: int) -> tuple[int, ...]:
    """Presets de filas disponibles hasta el total del archivo."""
    if total_rows <= 0:
        return DISPLAY_ROW_PRESETS
    options = [preset for preset in DISPLAY_ROW_PRESETS if preset <= total_rows]
    if total_rows not in options:
        options.append(total_rows)
    return tuple(sorted(set(options)))


def clamp_reload_rows(value: int, total_rows: int, *, min_rows: int = SAMPLE_ROW_MIN) -> int:
    if total_rows <= 0:
        return max(min_rows, value)
    return max(min_rows, min(value, total_rows))


def reload_row_choices(
    total_rows: int,
    *,
    min_rows: int = SAMPLE_ROW_MIN,
) -> tuple[ReloadRowChoice, ...]:
    """Opciones ordenadas: total, 50%, 10%, presets 50k/100k/200k (sin duplicados)."""
    if total_rows <= min_rows:
        return ()
    ordered: list[tuple[str, int]] = [
        ("total", total_rows),
        ("pct50", max(min_rows, int(total_rows * 0.5))),
        ("pct10", max(min_rows, int(total_rows * 0.1))),
    ]
    for preset in RELOAD_VOLUME_PRESETS:
        ordered.append(("preset", min(preset, total_rows)))
    result: list[ReloadRowChoice] = []
    seen: set[int] = set()
    for kind, raw_rows in ordered:
        rows = clamp_reload_rows(raw_rows, total_rows, min_rows=min_rows)
        if rows in seen:
            continue
        seen.add(rows)
        result.append(ReloadRowChoice(rows=rows, kind=kind))
    return tuple(result)


def reload_row_options(
    total_rows: int,
    *,
    min_rows: int = SAMPLE_ROW_MIN,
) -> tuple[int, ...]:
    """Valores numéricos de las opciones de recarga."""
    return tuple(choice.rows for choice in reload_row_choices(total_rows, min_rows=min_rows))


def parse_job_row_limit(
    text: str,
    total_rows: int,
    *,
    min_rows: int = 1,
) -> int:
    """Interpreta tag de job: ``100`` filas absolutas; ``10%`` porcentaje del total."""
    raw = text.strip()
    if not raw:
        return clamp_reload_rows(total_rows, total_rows, min_rows=min_rows)
    pct_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*%\s*$", raw)
    if pct_match:
        pct = float(pct_match.group(1).replace(",", "."))
        value = int(total_rows * pct / 100.0)
        return clamp_reload_rows(value, total_rows, min_rows=min_rows)
    cleaned = re.sub(r"[^\d]", "", raw)
    if not cleaned:
        raise ValueError(f"invalid row_limit tag: {text!r}")
    try:
        value = int(cleaned)
    except ValueError as exc:
        raise ValueError(f"invalid row_limit tag: {text!r}") from exc
    return clamp_reload_rows(value, total_rows, min_rows=min_rows)


def resolve_job_display_rows(
    *,
    row_limit: str | None,
    max_rows: int | None,
    total_rows: int,
    min_rows: int = 1,
) -> int:
    """Resuelve filas a cargar del extract (referencia/catálogo van aparte, siempre completos)."""
    tag = (row_limit or "").strip()
    if tag:
        return parse_job_row_limit(tag, total_rows, min_rows=min_rows)
    if max_rows is not None:
        return clamp_reload_rows(max_rows, total_rows, min_rows=min_rows)
    return total_rows


def parse_reload_row_input(
    text: str,
    total_rows: int,
    *,
    min_rows: int = SAMPLE_ROW_MIN,
) -> int | None:
    """Interpreta texto del combo (preset, porcentaje o número libre)."""
    raw = text.strip()
    if not raw:
        return None
    pct_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*%", raw)
    if pct_match:
        pct = float(pct_match.group(1).replace(",", "."))
        value = int(total_rows * pct / 100.0)
        return clamp_reload_rows(value, total_rows, min_rows=min_rows)
    paren = re.search(r"\(([\d,.\s]+)\)", raw)
    if paren:
        raw = paren.group(1)
    cleaned = re.sub(r"[^\d]", "", raw)
    if not cleaned:
        return None
    try:
        value = int(cleaned)
    except ValueError:
        return None
    return clamp_reload_rows(value, total_rows, min_rows=min_rows)


def should_offer_row_reload(total_rows: int, shown_rows: int) -> bool:
    """Barra de recarga si hay truncamiento o si el archivo supera el mínimo de muestra."""
    if total_rows <= 0:
        return False
    if shown_rows < total_rows:
        return True
    return total_rows > SAMPLE_ROW_MIN
