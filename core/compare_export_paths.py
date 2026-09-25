"""Nombres sugeridos para informes compare exportados."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.compare_types import CompareStatus

_STATUS_PREFIX: dict[CompareStatus, str] = {
    "match": "MATCH",
    "diff": "DIFF",
    "abort": "ABORT",
}


def suggest_compare_export_path(
    folder: Path,
    status: CompareStatus,
    *,
    clock: datetime | None = None,
) -> Path:
    """``DIFF20260716163300.txt`` — sufijo ``00``/``01`` si ya existe."""
    prefix = _STATUS_PREFIX[status]
    stamp = (clock or datetime.now()).strftime("%Y%m%d%H%M")
    folder.mkdir(parents=True, exist_ok=True)
    for seq in range(100):
        candidate = folder / f"{prefix}{stamp}{seq:02d}.txt"
        if not candidate.exists():
            return candidate
    return folder / f"{prefix}{stamp}99.txt"
