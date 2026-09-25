"""Tipos para visualización tabular y estadísticas de columnas."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ColumnSummary:
    name: str
    dtype: str
    null_count: int
    unique_count: int
    sum_value: float | None = None
    mean_value: float | None = None
    min_value: float | None = None
    max_value: float | None = None


@dataclass(frozen=True, slots=True)
class TabularDataset:
    """Dataset listo para UI — filas de pantalla + stats sobre archivo completo."""

    local_path: Path
    columns: tuple[ColumnSummary, ...]
    rows: tuple[tuple[str, ...], ...]
    total_rows: int
    display_truncated: bool
    # sampled: columnas y total_rows describen la muestra leída, no el archivo entero.
    sampled: bool = False
    estimated_total_rows: int | None = None


TABULAR_EXTENSIONS = frozenset({".csv", ".tsv", ".psv", ".xlsx", ".xlsm", ".xls"})

# Sufijo regex para batch_match.filename_patterns (sin anclar al path completo).
BATCH_TABULAR_EXTENSION_SUFFIX = r"\.(?:csv|tsv|psv|xlsx|xlsm|xls)$"

BATCH_TABULAR_GLOB_SUFFIXES = ("*.csv", "*.tsv", "*.psv", "*.xlsx", "*.xlsm", "*.xls")


def is_tabular_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in TABULAR_EXTENSIONS


def collect_tabular_files(data_dir: Path, *, recursive: bool = False) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for suffix in BATCH_TABULAR_GLOB_SUFFIXES:
        pattern = f"**/{suffix}" if recursive else suffix
        for path in data_dir.glob(pattern):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(path)
    return sorted(files, key=lambda item: str(item).casefold())
