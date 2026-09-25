"""Tipos para comparación tabular SFTP/local."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

CompareStatus = Literal["match", "diff", "abort"]
ExampleKind = Literal["only_a", "only_b", "duplicate_excess", "key_only_a", "key_only_b"]


@dataclass(frozen=True, slots=True)
class CompareFileSide:
    label: str
    path: Path
    file_size: int
    row_count: int = 0


@dataclass(frozen=True, slots=True)
class CompareExample:
    kind: ExampleKind
    text: str
    line_a: int = 0
    line_b: int = 0


@dataclass(frozen=True, slots=True)
class CompareResult:
    status: CompareStatus
    file_a: CompareFileSide
    file_b: CompareFileSide
    keys_used: tuple[str, ...] = ()
    only_in_a: int = 0
    only_in_b: int = 0
    duplicate_excess: bool = False
    abort_reason: str = ""
    examples: tuple[CompareExample, ...] = ()
    row_delta: int = 0
    size_delta: int = 0
    matched_rows: int = 0
    match_pct: float = 0.0
    shared_signatures: int = 0
    column_count: int = 0


@dataclass(slots=True)
class ComparePick:
    """Archivo elegido por el usuario para un lado del compare."""

    label: str
    local_path: Path | None = None
    remote_name: str | None = None
    is_remote: bool = False

    def is_tabular_candidate(self) -> bool:
        from core.analysis_types import is_tabular_extension

        name = self.remote_name or self.label
        return is_tabular_extension(name)
