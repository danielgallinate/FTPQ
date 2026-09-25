"""Normalización de celdas con regex opcional (compare referencia)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


def normalize_cell_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        import pandas as pd

        if pd.isna(value):
            return ""
    except Exception:  # noqa: BLE001
        pass
    text = str(value).strip()
    if text.casefold() in {"<na>", "nan", "none", "null", "nat"}:
        return ""
    return text


@dataclass(frozen=True, slots=True)
class CellTransform:
    pattern: str = ""
    replacement: str | None = None

    def is_empty(self) -> bool:
        return not self.pattern.strip()

    def uses_substitution(self) -> bool:
        return self.replacement is not None

    def to_dict(self) -> dict[str, str]:
        data: dict[str, str] = {}
        if self.pattern:
            data["pattern"] = self.pattern
        if self.replacement is not None:
            data["replacement"] = self.replacement
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> CellTransform:
        if not isinstance(raw, dict):
            return cls()
        replacement_raw = raw.get("replacement")
        replacement = None if replacement_raw is None else str(replacement_raw)
        return cls(
            pattern=str(raw.get("pattern") or "").strip(),
            replacement=replacement,
        )


def transform_cell(value: Any, transform: CellTransform | None = None) -> str:
    """Aplica trim; regex opcional (reemplazo o extracción del primer match)."""
    text = normalize_cell_text(value)
    if transform is None or transform.is_empty():
        return text
    try:
        if transform.uses_substitution():
            return re.sub(transform.pattern, transform.replacement or "", text)
        match = re.search(transform.pattern, text)
        if match is None:
            return text
        if match.lastindex and match.lastindex >= 1:
            return match.group(1)
        return match.group(0)
    except re.error:
        return text
