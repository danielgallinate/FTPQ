"""Comparación fila a fila: archivo abierto vs referencia tabular externa."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

from core.cell_transform import CellTransform, normalize_cell_text, transform_cell
from core.catalog_store import CatalogStore, resolve_catalog_compare_value
from core.catalog_types import ColumnCatalogBinding
from core.reference_compare_types import (
    REFERENCE_MAX_ROWS,
    ComparePairMapping,
    JoinKeyMapping,
    ReferenceCompareConfig,
    ReferenceCompareResult,
)

RowProgressCallback = Callable[[int, int], None]


def expand_evaluated_columns_for_reference(
    evaluated_columns: set[str],
    config: ReferenceCompareConfig,
) -> set[str]:
    """Incluye columnas llave en el overlay aunque no estén visibles en el grid."""
    expanded = set(evaluated_columns)
    for mapping in config.resolved_join_keys():
        if mapping.left_column.strip():
            expanded.add(mapping.left_column)
    return expanded


def load_reference_row_dicts(
    path: Path,
    *,
    max_rows: int = REFERENCE_MAX_ROWS,
) -> tuple[list[str], list[dict[str, Any]], int]:
    """Lee referencia completa (hasta max_rows) — columnas + filas dict."""
    if not path.is_file():
        raise FileNotFoundError(f"Referencia no encontrada: {path}")

    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("pandas no instalado") from exc

    from adapters.pandas_analyzer import _read_dataframe

    frame = _read_dataframe(pd, path)
    total_rows = len(frame)
    if total_rows > max_rows:
        frame = frame.head(max_rows)
    columns = [str(name) for name in frame.columns]
    rows: list[dict[str, Any]] = []
    for record in frame.itertuples(index=False, name=None):
        row: dict[str, Any] = {}
        for index, name in enumerate(columns):
            value = record[index] if index < len(record) else ""
            if value is None:
                row[name] = ""
            else:
                try:
                    if pd.isna(value):
                        row[name] = ""
                        continue
                except Exception:  # noqa: BLE001
                    pass
                row[name] = value
        rows.append(row)
    return columns, rows, total_rows


def _side_cell_text(
    row: dict[str, Any],
    column: str,
    transform: CellTransform,
    *,
    binding: ColumnCatalogBinding | None,
    catalog_store: CatalogStore | None,
    coord: tuple[int, int] | None,
    cell_catalog_displays: dict[tuple[int, int], str],
    catalog_lookup_misses: set[tuple[int, int]],
) -> str:
    raw = row.get(column)
    if binding is not None and catalog_store is not None:
        compare_raw, display, found = resolve_catalog_compare_value(
            catalog_store,
            binding,
            raw,
        )
        if coord is not None and display:
            cell_catalog_displays[coord] = display
        if not found:
            if coord is not None:
                catalog_lookup_misses.add(coord)
            return transform_cell(normalize_cell_text(raw), transform)
        return transform_cell(compare_raw, transform)
    return transform_cell(raw, transform)


def _join_tuple(
    row: dict[str, Any],
    mappings: list[JoinKeyMapping],
    *,
    side: str,
    catalog_bindings: dict[str, ColumnCatalogBinding] | None = None,
    catalog_store: CatalogStore | None = None,
    row_index: int = 0,
    name_to_index: dict[str, int] | None = None,
    cell_catalog_displays: dict[tuple[int, int], str] | None = None,
    catalog_lookup_misses: set[tuple[int, int]] | None = None,
) -> tuple[str, ...]:
    bindings = catalog_bindings or {}
    displays = cell_catalog_displays if cell_catalog_displays is not None else {}
    misses = catalog_lookup_misses if catalog_lookup_misses is not None else set()
    parts: list[str] = []
    for mapping in mappings:
        if side == "left":
            column = mapping.left_column
            transform = mapping.left_transform
            binding = bindings.get(column)
        else:
            column = mapping.right_column
            transform = mapping.right_transform
            binding = bindings.get(column)
        coord: tuple[int, int] | None = None
        if side == "left" and name_to_index is not None:
            col_index = name_to_index.get(column)
            if col_index is not None:
                coord = (row_index, col_index)
        parts.append(
            _side_cell_text(
                row,
                column,
                transform,
                binding=binding,
                catalog_store=catalog_store,
                coord=coord,
                cell_catalog_displays=displays,
                catalog_lookup_misses=misses,
            )
        )
    return tuple(parts)


def _coords_for_columns(
    row_index: int,
    columns: set[str],
    name_to_index: dict[str, int],
) -> set[tuple[int, int]]:
    coords: set[tuple[int, int]] = set()
    for column in columns:
        col_index = name_to_index.get(column)
        if col_index is not None:
            coords.add((row_index, col_index))
    return coords


def _emit_progress(callback: RowProgressCallback | None, current: int, total: int) -> None:
    if callback is not None:
        callback(current, total)


def validate_reference_overlay(
    left_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
    config: ReferenceCompareConfig,
    *,
    evaluated_columns: set[str],
    name_to_index: dict[str, int],
    on_progress: RowProgressCallback | None = None,
) -> ReferenceCompareResult:
    """Overlay verde/rojo: empareja por llave mapeada y compara columnas elegidas."""
    join_keys = config.resolved_join_keys() or [
        item for item in config.join_keys if item.is_complete()
    ]
    pairs = [item for item in config.pairs if item.enabled and item.is_complete()]
    if not join_keys or not pairs:
        return ReferenceCompareResult()

    catalog_store: CatalogStore | None = None
    if config.left_catalog_bindings or config.right_catalog_bindings:
        catalog_store = CatalogStore(config.catalog_knowledge_base_id)

    key_left_columns = {item.left_column for item in join_keys}
    pair_left_columns = {item.left_column for item in pairs}

    ref_index: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for ref_index_row, ref_row in enumerate(reference_rows):
        key = _join_tuple(
            ref_row,
            join_keys,
            side="right",
            catalog_bindings=config.right_catalog_bindings,
            catalog_store=catalog_store,
        )
        if any(part != "" for part in key):
            ref_index[key].append(ref_index_row)

    duplicate_reference_keys = sum(1 for items in ref_index.values() if len(items) > 1)

    passed: set[tuple[int, int]] = set()
    failed: set[tuple[int, int]] = set()
    gray: set[tuple[int, int]] = set()
    cell_reference_values: dict[tuple[int, int], str] = {}
    cells_without_reference: set[tuple[int, int]] = set()
    cell_catalog_displays: dict[tuple[int, int], str] = {}
    catalog_lookup_misses: set[tuple[int, int]] = set()
    alerts: list[str] = []
    rows_without_match = 0
    rows_ambiguous_key = 0
    ambiguous_samples = 0
    no_match_samples = 0
    max_alert_samples = 20
    total_rows = len(left_rows)

    for row_index, left_row in enumerate(left_rows):
        key = _join_tuple(
            left_row,
            join_keys,
            side="left",
            catalog_bindings=config.left_catalog_bindings,
            catalog_store=catalog_store,
            row_index=row_index,
            name_to_index=name_to_index,
            cell_catalog_displays=cell_catalog_displays,
            catalog_lookup_misses=catalog_lookup_misses,
        )
        matches = ref_index.get(key, [])
        key_coords = _coords_for_columns(row_index, key_left_columns, name_to_index)
        key_catalog_miss = any(coord in catalog_lookup_misses for coord in key_coords)

        if key_catalog_miss:
            if key_coords:
                failed.update(key_coords)
            if len(alerts) < max_alert_samples:
                alerts.append(f"Fila {row_index + 1} · catálogo sin match en llave")
            _emit_progress(on_progress, row_index + 1, total_rows)
            continue

        if not matches:
            rows_without_match += 1
            if key_coords:
                failed.update(key_coords)
                cells_without_reference.update(key_coords)
            if no_match_samples < max_alert_samples:
                no_match_samples += 1
                alerts.append(
                    f"Fila {row_index + 1} · sin coincidencia de llave ({' | '.join(key) or '—'})"
                )
            _emit_progress(on_progress, row_index + 1, total_rows)
            continue

        if len(matches) > 1:
            if config.duplicate_policy == "ambiguous":
                rows_ambiguous_key += 1
                if key_coords:
                    failed.update(key_coords)
                    cells_without_reference.update(key_coords)
                if ambiguous_samples < max_alert_samples:
                    ambiguous_samples += 1
                    alerts.append(
                        f"Fila {row_index + 1} · llave ambigua en referencia ({len(matches)} filas)"
                    )
                _emit_progress(on_progress, row_index + 1, total_rows)
                continue

        ref_row = reference_rows[matches[0]]
        if key_coords:
            passed.update(key_coords)

        for pair in pairs:
            if pair.left_column not in evaluated_columns:
                continue
            col_index = name_to_index.get(pair.left_column)
            if col_index is None:
                continue
            coord = (row_index, col_index)
            binding = config.left_catalog_bindings.get(pair.left_column)
            left_value = _side_cell_text(
                left_row,
                pair.left_column,
                pair.left_transform,
                binding=binding,
                catalog_store=catalog_store,
                coord=coord,
                cell_catalog_displays=cell_catalog_displays,
                catalog_lookup_misses=catalog_lookup_misses,
            )
            right_binding = config.right_catalog_bindings.get(pair.right_column)
            right_value = _side_cell_text(
                ref_row,
                pair.right_column,
                pair.right_transform,
                binding=right_binding,
                catalog_store=catalog_store,
                coord=None,
                cell_catalog_displays=cell_catalog_displays,
                catalog_lookup_misses=catalog_lookup_misses,
            )
            if coord in catalog_lookup_misses:
                failed.add(coord)
                passed.discard(coord)
                if len(alerts) < max_alert_samples:
                    alerts.append(
                        f"Fila {row_index + 1} · {pair.left_column}: sin match en catálogo"
                    )
                continue
            if left_value == right_value:
                passed.add(coord)
                failed.discard(coord)
                cell_reference_values.pop(coord, None)
            else:
                failed.add(coord)
                passed.discard(coord)
                cell_reference_values[coord] = right_value
                if len(alerts) < max_alert_samples:
                    alerts.append(
                        f"Fila {row_index + 1} · {pair.left_column}: "
                        f"'{left_value}' ≠ '{right_value}' (ref)"
                    )

        for column in evaluated_columns:
            if column in pair_left_columns or column in key_left_columns:
                continue
            col_index = name_to_index.get(column)
            if col_index is not None:
                gray.add((row_index, col_index))

        _emit_progress(on_progress, row_index + 1, total_rows)

    if duplicate_reference_keys:
        alerts.insert(
            0,
            f"Referencia: {duplicate_reference_keys} llaves duplicadas "
            f"(política: {config.duplicate_policy})",
        )

    total = len(passed) + len(failed)
    percent = (100.0 * len(passed) / total) if total else 0.0
    return ReferenceCompareResult(
        passed_cells=passed,
        failed_cells=failed,
        gray_cells=gray,
        percent=round(percent, 2),
        passed_count=len(passed),
        total_count=total,
        alerts=alerts,
        rows_without_match=rows_without_match,
        rows_ambiguous_key=rows_ambiguous_key,
        duplicate_reference_keys=duplicate_reference_keys,
        cell_reference_values=cell_reference_values,
        cells_without_reference=cells_without_reference,
        cell_catalog_displays=cell_catalog_displays,
        catalog_lookup_misses=catalog_lookup_misses,
    )


def suggest_initial_pairs(
    left_columns: list[str],
    right_columns: list[str],
) -> list[ComparePairMapping]:
    """Pares por nombre coincidente; la primera llave sugerida queda marcada como join."""
    pairs = suggest_pairs_by_name(left_columns, right_columns)
    suggested_key = suggest_join_key(left_columns, right_columns)
    if suggested_key is None:
        return pairs
    marked = False
    for pair in pairs:
        if pair.left_column == suggested_key.left_column:
            pair.is_join_key = True
            marked = True
            break
    if not marked:
        pairs.insert(
            0,
            ComparePairMapping(
                left_column=suggested_key.left_column,
                right_column=suggested_key.right_column,
                enabled=True,
                is_join_key=True,
            ),
        )
    return pairs


def suggest_pairs_by_name(
    left_columns: list[str],
    right_columns: list[str],
) -> list[ComparePairMapping]:
    """Pares automáticos cuando el nombre de columna coincide (casefold)."""
    right_by_name = {name.casefold(): name for name in right_columns}
    pairs: list[ComparePairMapping] = []
    for left in left_columns:
        match = right_by_name.get(left.casefold())
        if match is not None:
            pairs.append(
                ComparePairMapping(
                    left_column=left,
                    right_column=match,
                    enabled=True,
                )
            )
    return pairs


def suggest_join_key(
    left_columns: list[str],
    right_columns: list[str],
) -> JoinKeyMapping | None:
    """Primera columna con el mismo nombre en ambos lados."""
    right_by_name = {name.casefold(): name for name in right_columns}
    for left in left_columns:
        match = right_by_name.get(left.casefold())
        if match is not None:
            return JoinKeyMapping(left_column=left, right_column=match)
    return None
