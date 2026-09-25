"""Tipos para comparación archivo vs referencia tabular."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from core.cell_transform import CellTransform
from core.catalog_types import ColumnCatalogBinding

DuplicateKeyPolicy = Literal["first", "ambiguous"]
REFERENCE_MAX_ROWS = 500_000


@dataclass
class JoinKeyMapping:
    left_column: str = ""
    right_column: str = ""
    left_transform: CellTransform = field(default_factory=CellTransform)
    right_transform: CellTransform = field(default_factory=CellTransform)

    def is_complete(self) -> bool:
        return bool(self.left_column.strip() and self.right_column.strip())


@dataclass
class ComparePairMapping:
    left_column: str = ""
    right_column: str = ""
    left_transform: CellTransform = field(default_factory=CellTransform)
    right_transform: CellTransform = field(default_factory=CellTransform)
    enabled: bool = True
    is_join_key: bool = False

    def is_complete(self) -> bool:
        return bool(self.left_column.strip() and self.right_column.strip())

    def as_join_key(self) -> JoinKeyMapping:
        return JoinKeyMapping(
            left_column=self.left_column,
            right_column=self.right_column,
            left_transform=self.left_transform,
            right_transform=self.right_transform,
        )


@dataclass
class ReferenceCompareConfig:
    reference_path: Path | None = None
    reference_columns: tuple[str, ...] = ()
    reference_total_rows: int = 0
    join_keys: list[JoinKeyMapping] = field(default_factory=list)
    pairs: list[ComparePairMapping] = field(default_factory=list)
    duplicate_policy: DuplicateKeyPolicy = "first"
    enabled: bool = True
    left_catalog_bindings: dict[str, ColumnCatalogBinding] = field(default_factory=dict)
    right_catalog_bindings: dict[str, ColumnCatalogBinding] = field(default_factory=dict)
    catalog_knowledge_base_id: str = "default"

    def is_ready(self) -> bool:
        if self.reference_path is None:
            return False
        if not any(
            item.is_join_key and item.enabled and item.is_complete()
            for item in self.pairs
        ):
            return False
        return any(item.enabled and item.is_complete() for item in self.pairs)

    def resolved_join_keys(self) -> list[JoinKeyMapping]:
        return [
            item.as_join_key()
            for item in self.pairs
            if item.is_join_key and item.enabled and item.is_complete()
        ]


@dataclass
class ReferenceCompareResult:
    passed_cells: set[tuple[int, int]] = field(default_factory=set)
    failed_cells: set[tuple[int, int]] = field(default_factory=set)
    gray_cells: set[tuple[int, int]] = field(default_factory=set)
    percent: float = 0.0
    passed_count: int = 0
    total_count: int = 0
    alerts: list[str] = field(default_factory=list)
    rows_without_match: int = 0
    rows_ambiguous_key: int = 0
    duplicate_reference_keys: int = 0
    cell_reference_values: dict[tuple[int, int], str] = field(default_factory=dict)
    cells_without_reference: set[tuple[int, int]] = field(default_factory=set)
    cell_catalog_displays: dict[tuple[int, int], str] = field(default_factory=dict)
    catalog_lookup_misses: set[tuple[int, int]] = field(default_factory=set)

    @property
    def rows_with_key_errors(self) -> int:
        return self.rows_without_match + self.rows_ambiguous_key
