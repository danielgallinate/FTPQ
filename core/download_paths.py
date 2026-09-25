"""Rutas locales para descargas — colisiones de nombre."""
from __future__ import annotations

from pathlib import Path


def next_versioned_path(path: Path) -> Path:
    """Genera ``nombre (1).ext``, ``nombre (2).ext``, … hasta path libre."""
    parent = path.parent
    stem = path.stem
    suffix = path.suffix
    n = 1
    while True:
        candidate = parent / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1
