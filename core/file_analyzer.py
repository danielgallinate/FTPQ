"""Contrato IFileAnalyzer — análisis local sin toolkit."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from core.analysis_errors import AnalysisError
from core.analysis_types import TabularDataset
from core.result import Result


@runtime_checkable
class IFileAnalyzer(Protocol):
    def analyze_tabular(
        self,
        path: Path,
        *,
        max_display_rows: int = 5000,
        max_bytes: int = 52_428_800,
    ) -> Result[TabularDataset, AnalysisError]: ...
