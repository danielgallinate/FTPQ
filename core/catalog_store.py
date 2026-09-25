"""Persistencia y lookup de catálogos tabulares locales."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.catalog_types import (
    CatalogKeyConflictError,
    CatalogMeta,
    CatalogTable,
    CatalogValidationError,
    ColumnCatalogBinding,
)
from core.cell_transform import normalize_cell_text

DEFAULT_KB_ID = "default"
_META_SUFFIX = ".meta.json"


def _emr_root() -> Path:
    return Path(__file__).resolve().parents[1] / "emr-qa"


def knowledge_bases_root() -> Path:
    return _emr_root() / "knowledge_bases"


def catalogs_dir(knowledge_base_id: str = DEFAULT_KB_ID) -> Path:
    path = knowledge_bases_root() / knowledge_base_id / "catalogs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify_catalog_name(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "_", name.strip().casefold()).strip("_")
    return slug or "catalog"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _meta_path(kb_id: str, catalog_id: str) -> Path:
    return catalogs_dir(kb_id) / f"{catalog_id}{_META_SUFFIX}"


def _csv_path(kb_id: str, catalog_id: str) -> Path:
    return catalogs_dir(kb_id) / f"{catalog_id}.csv"


def list_catalog_metas(knowledge_base_id: str = DEFAULT_KB_ID) -> list[CatalogMeta]:
    folder = catalogs_dir(knowledge_base_id)
    items: list[CatalogMeta] = []
    for path in sorted(folder.glob(f"*{_META_SUFFIX}")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            meta = CatalogMeta.from_dict(raw)
            if meta.catalog_id:
                items.append(meta)
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    return sorted(items, key=lambda item: item.name.casefold())


class CatalogStore:
    def __init__(self, knowledge_base_id: str = DEFAULT_KB_ID) -> None:
        self.knowledge_base_id = knowledge_base_id
        self._cache: dict[str, CatalogTable] = {}

    def invalidate(self, catalog_id: str | None = None) -> None:
        if catalog_id is None:
            self._cache.clear()
            return
        self._cache.pop(catalog_id, None)

    def load(self, catalog_id: str) -> CatalogTable:
        cached = self._cache.get(catalog_id)
        if cached is not None:
            return cached
        meta_path = _meta_path(self.knowledge_base_id, catalog_id)
        csv_path = _csv_path(self.knowledge_base_id, catalog_id)
        if not meta_path.is_file() or not csv_path.is_file():
            raise CatalogValidationError(f"catalog not found: {catalog_id}")
        meta = CatalogMeta.from_dict(json.loads(meta_path.read_text(encoding="utf-8")))
        rows = _read_csv_rows(csv_path, expected_columns=meta.columns)
        table = CatalogTable(meta=meta, rows=rows)
        self._cache[catalog_id] = table
        return table

    def lookup(
        self,
        catalog_id: str,
        match_column: str,
        value: Any,
    ) -> dict[str, str] | None:
        table = self.load(catalog_id)
        return table.lookup(match_column, value)

    def save(
        self,
        meta: CatalogMeta,
        rows: list[dict[str, str]],
        *,
        dedupe_key: str | None = None,
    ) -> None:
        key_column = dedupe_key or meta.key_column
        if not key_column:
            raise CatalogValidationError("key column required")
        if key_column not in meta.columns:
            raise CatalogValidationError(f"key column not in catalog: {key_column}")
        normalized_rows, _ = dedupe_rows(rows, columns=meta.columns, key_column=key_column)
        meta_path = _meta_path(self.knowledge_base_id, meta.catalog_id)
        csv_path = _csv_path(self.knowledge_base_id, meta.catalog_id)
        meta_path.write_text(
            json.dumps(meta.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        _write_csv_rows(csv_path, meta.columns, normalized_rows)
        self.invalidate(meta.catalog_id)

    def update_catalog_batch_match(
        self,
        catalog_id: str,
        batch_match: BatchMatchSpec | None,
    ) -> CatalogMeta:
        table = self.load(catalog_id)
        meta = table.meta
        updated = CatalogMeta(
            catalog_id=meta.catalog_id,
            name=meta.name,
            key_column=meta.key_column,
            columns=meta.columns,
            created_at=meta.created_at,
            updated_at=_utc_now(),
            source_file=meta.source_file,
            batch_match=batch_match,
        )
        self.save(updated, table.rows)
        return updated

    def delete(self, catalog_id: str) -> None:
        _meta_path(self.knowledge_base_id, catalog_id).unlink(missing_ok=True)
        _csv_path(self.knowledge_base_id, catalog_id).unlink(missing_ok=True)
        self.invalidate(catalog_id)


def dedupe_rows(
    rows: list[dict[str, Any]],
    *,
    columns: list[str] | tuple[str, ...],
    key_column: str,
    on_duplicate: str = "error",
) -> tuple[list[dict[str, str]], int]:
    """on_duplicate: error = falla si misma llave con filas distintas; keep_first = primera gana."""
    seen: dict[str, dict[str, str]] = {}
    skipped = 0
    for row in rows:
        projected = {
            column: normalize_cell_text(row.get(column, ""))
            for column in columns
        }
        key = projected[key_column]
        if not key:
            continue
        fold = key.casefold()
        if fold in seen:
            if on_duplicate == "keep_first":
                skipped += 1
                continue
            if seen[fold] != projected:
                raise CatalogKeyConflictError(key)
            skipped += 1
            continue
        seen[fold] = projected
    return list(seen.values()), skipped


def build_rows_from_dataset(
    dataset_rows: list[dict[str, Any]],
    *,
    columns: list[str],
    key_column: str,
    on_duplicate: str = "error",
) -> tuple[list[dict[str, str]], int]:
    if key_column not in columns:
        raise CatalogValidationError("key column must be included in selected columns")
    return dedupe_rows(
        dataset_rows,
        columns=columns,
        key_column=key_column,
        on_duplicate=on_duplicate,
    )


def create_catalog_from_dataset(
    *,
    name: str,
    columns: list[str],
    key_column: str,
    dataset_rows: list[dict[str, Any]],
    source_file: str = "",
    knowledge_base_id: str = DEFAULT_KB_ID,
    catalog_id: str | None = None,
    on_duplicate: str = "error",
) -> tuple[CatalogMeta, int]:
    if not name.strip():
        raise CatalogValidationError("catalog name required")
    if not columns:
        raise CatalogValidationError("select at least one column")
    chosen_id = catalog_id or slugify_catalog_name(name)
    if not chosen_id:
        raise CatalogValidationError("invalid catalog id")
    rows, skipped = build_rows_from_dataset(
        dataset_rows,
        columns=columns,
        key_column=key_column,
        on_duplicate=on_duplicate,
    )
    if not rows:
        raise CatalogValidationError("no rows after deduplication — check key column values")
    now = _utc_now()
    meta = CatalogMeta(
        catalog_id=chosen_id,
        name=name.strip(),
        key_column=key_column,
        columns=tuple(columns),
        created_at=now,
        updated_at=now,
        source_file=source_file,
    )
    store = CatalogStore(knowledge_base_id)
    store.save(meta, rows)
    return meta, skipped


def format_catalog_display(row: dict[str, str], display_columns: tuple[str, ...]) -> str:
    parts = [normalize_cell_text(row.get(column, "")) for column in display_columns]
    parts = [part for part in parts if part]
    return " · ".join(parts)


def split_catalog_cell_tokens(raw_value: Any, separator: str) -> list[str]:
    text = normalize_cell_text(raw_value)
    if not text:
        return []
    if not separator:
        return [text]
    if separator == ",":
        parts = text.split(",")
    else:
        parts = text.split(separator)
    tokens = [normalize_cell_text(part) for part in parts]
    return [token for token in tokens if token]


def _resolve_single_catalog_token(
    store: CatalogStore,
    binding: ColumnCatalogBinding,
    token: str,
) -> tuple[str, str, bool]:
    hit = store.lookup(binding.catalog_id, binding.match_column, token)
    if hit is None:
        return token, "", False
    compare_value = normalize_cell_text(hit.get(binding.compare_column, ""))
    display = format_catalog_display(hit, binding.display_columns)
    if not display:
        display = compare_value
    return compare_value, display, True


def resolve_catalog_compare_value(
    store: CatalogStore,
    binding: ColumnCatalogBinding,
    raw_value: Any,
) -> tuple[str, str, bool]:
    """Returns compare value, display text, found."""
    tokens = split_catalog_cell_tokens(raw_value, binding.multi_value_separator)
    if not tokens:
        return "", "", False
    if len(tokens) == 1:
        token = tokens[0]
        compare_value, display, found = _resolve_single_catalog_token(store, binding, token)
        if not found:
            return compare_value, "", False
        return compare_value, display, True

    compare_parts: list[str] = []
    display_parts: list[str] = []
    all_found = True
    for token in tokens:
        compare_value, display, found = _resolve_single_catalog_token(store, binding, token)
        if not found:
            all_found = False
            compare_parts.append("?")
            display_parts.append("?")
        else:
            compare_parts.append(compare_value or display or token)
            display_parts.append(display or compare_value or token)
    return ", ".join(compare_parts), ", ".join(display_parts), all_found


def build_catalog_displays(
    rows: list[tuple[str, ...]] | list[dict[str, Any]],
    bindings: dict[str, ColumnCatalogBinding],
    name_to_index: dict[str, int],
    *,
    store: CatalogStore | None = None,
    miss_label: str = "?",
) -> tuple[dict[tuple[int, int], str], set[tuple[int, int]]]:
    """Resuelve traducciones para columnas enlazadas — (fila, col) → texto entre paréntesis."""
    if not bindings:
        return {}, set()
    catalog_store = store or CatalogStore()
    displays: dict[tuple[int, int], str] = {}
    misses: set[tuple[int, int]] = set()
    for column_name, binding in bindings.items():
        col_index = name_to_index.get(column_name)
        if col_index is None:
            continue
        for row_index, row in enumerate(rows):
            if isinstance(row, dict):
                raw = row.get(column_name, "")
            else:
                raw = row[col_index] if col_index < len(row) else ""
            _compare, display, found = resolve_catalog_compare_value(
                catalog_store,
                binding,
                raw,
            )
            coord = (row_index, col_index)
            if display:
                displays[coord] = display
                if not found:
                    misses.add(coord)
            else:
                misses.add(coord)
                displays[coord] = miss_label
    return displays, misses


def _read_csv_rows(path: Path, *, expected_columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        if fieldnames != expected_columns:
            raise CatalogValidationError(
                f"catalog columns mismatch: expected {expected_columns}, got {fieldnames}"
            )
        rows: list[dict[str, str]] = []
        for raw in reader:
            rows.append(
                {column: normalize_cell_text(raw.get(column, "")) for column in expected_columns}
            )
        return rows


def _write_csv_rows(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})
