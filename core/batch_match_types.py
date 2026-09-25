"""Tipos compartidos — emparejamiento batch job ↔ archivo por regex."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BatchMatchSpec:
    filename_patterns: tuple[str, ...] = ()
    filename_excludes: tuple[str, ...] = ()

    def is_configured(self) -> bool:
        return bool(self.filename_patterns)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.filename_patterns:
            payload["filename_patterns"] = list(self.filename_patterns)
        if self.filename_excludes:
            payload["filename_excludes"] = list(self.filename_excludes)
        return payload

    @classmethod
    def from_dict(cls, raw: Any) -> BatchMatchSpec | None:
        if not isinstance(raw, dict):
            return None
        patterns_raw = raw.get("filename_patterns") or []
        excludes_raw = raw.get("filename_excludes") or []
        patterns = tuple(
            str(item).strip() for item in patterns_raw if str(item).strip()
        )
        excludes = tuple(
            str(item).strip() for item in excludes_raw if str(item).strip()
        )
        if not patterns and not excludes:
            return None
        return cls(filename_patterns=patterns, filename_excludes=excludes)

    def merge(self, other: BatchMatchSpec) -> BatchMatchSpec:
        return BatchMatchSpec(
            filename_patterns=self.filename_patterns + other.filename_patterns,
            filename_excludes=self.filename_excludes + other.filename_excludes,
        )
