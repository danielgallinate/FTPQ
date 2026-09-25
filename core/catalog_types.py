"""Tipos — catálogos tabulares locales (code ↔ label)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.batch_match_types import BatchMatchSpec
from core.cell_transform import normalize_cell_text


@dataclass(frozen=True)
class CatalogMeta:
    catalog_id: str
    name: str
    key_column: str
    columns: tuple[str, ...]
    created_at: str
    updated_at: str
    source_file: str = ""
    batch_match: BatchMatchSpec | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "catalog_id": self.catalog_id,
            "name": self.name,
            "key_column": self.key_column,
            "columns": list(self.columns),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_file": self.source_file,
        }
        if self.batch_match is not None:
            batch_payload = self.batch_match.to_dict()
            if batch_payload:
                payload["batch_match"] = batch_payload
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> CatalogMeta:
        columns_raw = raw.get("columns") or []
        return cls(
            catalog_id=str(raw.get("catalog_id") or "").strip(),
            name=str(raw.get("name") or "").strip(),
            key_column=str(raw.get("key_column") or "").strip(),
            columns=tuple(str(item) for item in columns_raw),
            created_at=str(raw.get("created_at") or ""),
            updated_at=str(raw.get("updated_at") or ""),
            source_file=str(raw.get("source_file") or ""),
            batch_match=BatchMatchSpec.from_dict(raw.get("batch_match")),
        )


@dataclass(frozen=True)
class ColumnCatalogBinding:
    catalog_id: str
    match_column: str
    display_columns: tuple[str, ...]
    compare_column: str
    multi_value_separator: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "catalog_id": self.catalog_id,
            "match_column": self.match_column,
            "display_columns": list(self.display_columns),
            "compare_column": self.compare_column,
        }
        if self.multi_value_separator:
            payload["multi_value_separator"] = self.multi_value_separator
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ColumnCatalogBinding:
        display_raw = raw.get("display_columns") or []
        return cls(
            catalog_id=str(raw.get("catalog_id") or "").strip(),
            match_column=str(raw.get("match_column") or "").strip(),
            display_columns=tuple(str(item) for item in display_raw),
            compare_column=str(raw.get("compare_column") or "").strip(),
            multi_value_separator=str(raw.get("multi_value_separator") or "").strip(),
        )


@dataclass
class CatalogTable:
    meta: CatalogMeta
    rows: list[dict[str, str]] = field(default_factory=list)
    _match_index: dict[str, dict[str, str]] = field(default_factory=dict, repr=False)
    _indexed_column: str = field(default="", repr=False)

    def rebuild_index(self, match_column: str) -> None:
        index: dict[str, dict[str, str]] = {}
        for row in self.rows:
            key = normalize_cell_text(row.get(match_column, "")).casefold()
            if not key:
                continue
            index[key] = row
        self._match_index = index
        self._indexed_column = match_column

    def lookup(self, match_column: str, value: Any) -> dict[str, str] | None:
        if match_column != self._indexed_column:
            self.rebuild_index(match_column)
        key = normalize_cell_text(value).casefold()
        if not key:
            return None
        return self._match_index.get(key)


class CatalogError(Exception):
    """Error de catálogo."""


class CatalogKeyConflictError(CatalogError):
    def __init__(self, key_value: str) -> None:
        super().__init__(f"duplicate key with conflicting rows: {key_value!r}")
        self.key_value = key_value


class CatalogValidationError(CatalogError):
    pass
