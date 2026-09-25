"""Errores del módulo de análisis tabular."""
from __future__ import annotations


class AnalysisError(Exception):
    """Base para errores de análisis local."""


class AnalysisFormatError(AnalysisError):
    def __init__(self, message: str, *, path: str) -> None:
        super().__init__(message)
        self.path = path


class AnalysisTooLargeError(AnalysisError):
    def __init__(
        self,
        message: str,
        *,
        path: str,
        file_size: int,
        limit_bytes: int,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.file_size = file_size
        self.limit_bytes = limit_bytes
