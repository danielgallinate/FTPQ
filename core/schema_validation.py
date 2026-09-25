"""Validación estructural de columnas — tipos, null, modo estricto."""
from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from core.schema_catalog_types import SchemaCatalog, SchemaColumnSpec

RowProgressCallback = Callable[[int, int], None]

_TRUE_VALUES = frozenset({"1", "true", "t", "yes", "y", "si", "sí"})
_FALSE_VALUES = frozenset({"0", "false", "f", "no", "n"})


def is_null_cell(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip()
    if not text:
        return True
    if text.casefold() in ("<na>", "nan", "none", "null", "nat"):
        return True
    return False


def _cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _parse_date(text: str, date_format: str) -> bool:
    if not text:
        return False
    fmt = date_format.strip() or "%Y-%m-%d"
    try:
        datetime.strptime(text, fmt)
        return True
    except ValueError:
        return False


def _has_time_component(text: str) -> bool:
    """Un datetime exige hora; una fecha sola (``2024-04-28``) no cumple el tipo."""
    if ":" in text:
        return True
    return re.search(r"[T ]\d{6}(?:[.,]\d+)?$", text) is not None


def _parse_datetime(text: str, date_format: str) -> bool:
    if not text:
        return False
    if date_format.strip():
        try:
            datetime.strptime(text, date_format.strip())
            return True
        except ValueError:
            return False
    if not _has_time_component(text):
        return False
    normalized = text.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            datetime.strptime(text, fmt)
            return True
        except ValueError:
            continue
    return False


def cell_matches_type(value: Any, spec: SchemaColumnSpec) -> bool:
    if is_null_cell(value):
        return spec.allows_null
    text = _cell_text(value)
    data_type = spec.data_type
    if data_type == "string":
        return True
    if data_type == "integer":
        if re.fullmatch(r"[+-]?\d+", text) is None:
            return False
        try:
            int(text)
        except ValueError:
            return False
        return True
    if data_type == "decimal":
        try:
            Decimal(text)
        except InvalidOperation:
            return False
        return True
    if data_type == "boolean":
        token = text.casefold()
        return token in _TRUE_VALUES or token in _FALSE_VALUES
    if data_type == "date":
        return _parse_date(text, spec.date_format)
    if data_type == "datetime":
        return _parse_datetime(text, spec.date_format)
    return True


def _unique_value_key(value: Any) -> str | None:
    if is_null_cell(value):
        return None
    return _cell_text(value).casefold()


def _apply_unique_constraints(
    specs: list[SchemaColumnSpec],
    rows: list[dict[str, object]],
    name_to_index: dict[str, int],
    result: SchemaValidationResult,
) -> None:
    for spec in specs:
        if not spec.unique or not spec.enabled or not spec.name.strip():
            continue
        col_index = name_to_index.get(spec.name)
        if col_index is None:
            continue
        grouped: dict[str, list[tuple[int, int]]] = {}
        for row_index, row in enumerate(rows):
            key = _unique_value_key(row.get(spec.name))
            if key is None:
                continue
            grouped.setdefault(key, []).append((row_index, col_index))
        for coords in grouped.values():
            if len(coords) <= 1:
                continue
            for coord in coords:
                result.passed_cells.discard(coord)
                result.failed_cells.add(coord)
            result.alerts.append(
                f"duplicate value in unique column {spec.name}: {len(coords)} rows"
            )


@dataclass
class SchemaValidationResult:
    passed_cells: set[tuple[int, int]] = field(default_factory=set)
    failed_cells: set[tuple[int, int]] = field(default_factory=set)
    gray_cells: set[tuple[int, int]] = field(default_factory=set)
    percent: float = 0.0
    passed_count: int = 0
    total_count: int = 0
    alerts: list[str] = field(default_factory=list)
    structural_errors: list[str] = field(default_factory=list)
    coverage_columns: list[str] = field(default_factory=list)
    evaluated_columns: set[str] = field(default_factory=set)

    @property
    def conflict_cells(self) -> set[tuple[int, int]]:
        return set()

    @property
    def rows_with_key_errors(self) -> int:
        return 0


def validate_schema_catalog(
    catalog: SchemaCatalog,
    rows: list[dict[str, object]],
    *,
    file_columns: list[str],
    name_to_index: dict[str, int],
    on_progress: RowProgressCallback | None = None,
) -> SchemaValidationResult:
    result = SchemaValidationResult()
    file_set = set(file_columns)
    expected_names = catalog.expected_column_names()
    enabled_specs = catalog.enabled_columns()

    if catalog.strict and expected_names:
        if file_set != expected_names:
            missing = sorted(expected_names - file_set)
            extra = sorted(file_set - expected_names)
            parts: list[str] = []
            if missing:
                parts.append(f"missing: {', '.join(missing)}")
            if extra:
                parts.append(f"extra: {', '.join(extra)}")
            message = "strict column mismatch"
            if parts:
                message += f" ({'; '.join(parts)})"
            result.structural_errors.append(message)
            result.alerts.append(message)

    for column_name in sorted(file_set - expected_names):
        result.coverage_columns.append(column_name)
        col_index = name_to_index.get(column_name)
        if col_index is None:
            continue
        for row_index in range(len(rows)):
            result.gray_cells.add((row_index, col_index))

    for spec in catalog.columns:
        if not spec.name.strip():
            continue
        if not spec.enabled:
            col_index = name_to_index.get(spec.name)
            if col_index is not None:
                for row_index in range(len(rows)):
                    result.gray_cells.add((row_index, col_index))
            continue

        col_index = name_to_index.get(spec.name)
        if col_index is None:
            if not catalog.strict or spec.name not in expected_names:
                result.structural_errors.append(f"missing column: {spec.name}")
                result.alerts.append(f"missing column: {spec.name}")
            continue

        result.evaluated_columns.add(spec.name)
        row_total = len(rows)
        for row_index, row in enumerate(rows):
            if on_progress is not None and row_index % 500 == 0:
                on_progress(row_index, row_total)
            value = row.get(spec.name)
            coord = (row_index, col_index)
            if cell_matches_type(value, spec):
                result.passed_cells.add(coord)
            else:
                result.failed_cells.add(coord)

    if on_progress is not None and rows:
        on_progress(len(rows), len(rows))

    _apply_unique_constraints(enabled_specs, rows, name_to_index, result)

    judged = len(result.passed_cells) + len(result.failed_cells)
    result.passed_count = len(result.passed_cells)
    result.total_count = judged
    if judged:
        result.percent = round(100.0 * result.passed_count / judged, 2)

    if result.coverage_columns:
        result.alerts.insert(
            0,
            f"coverage gap columns ({len(result.coverage_columns)}): "
            + ", ".join(result.coverage_columns[:12])
            + ("…" if len(result.coverage_columns) > 12 else ""),
        )

    disabled = [
        spec.name
        for spec in catalog.columns
        if spec.name.strip() and not spec.enabled
    ]
    if disabled:
        result.alerts.append(
            "unevaluated schema columns: "
            + ", ".join(disabled[:12])
            + ("…" if len(disabled) > 12 else "")
        )

    return result
