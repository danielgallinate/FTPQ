"""Preflight compare — cabecera, tamaño, extensión."""
from __future__ import annotations

from pathlib import Path

from core.analysis_types import is_tabular_extension
from core.compare_types import CompareResult, CompareFileSide
from core.result import Err, Ok, Result
from core.visualization_policy import PANDAS_HARD_MAX_BYTES, TabularPolicyProfile, normalize_pandas_max_bytes


class CompareAbortError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def preflight_compare_paths(
    path_a: Path,
    path_b: Path,
    *,
    label_a: str,
    label_b: str,
    profile: TabularPolicyProfile,
) -> Result[tuple[list[str], CompareFileSide, CompareFileSide], CompareAbortError]:
    try:
        columns = _validate_pair(path_a, path_b, label_a, label_b, profile)
    except CompareAbortError as exc:
        return Err(exc)

    size_a = path_a.stat().st_size
    size_b = path_b.stat().st_size
    return Ok(
        (
            columns,
            CompareFileSide(label=label_a, path=path_a, file_size=size_a),
            CompareFileSide(label=label_b, path=path_b, file_size=size_b),
        )
    )


def _validate_pair(
    path_a: Path,
    path_b: Path,
    label_a: str,
    label_b: str,
    profile: TabularPolicyProfile,
) -> list[str]:
    if not is_tabular_extension(label_a) or not is_tabular_extension(label_b):
        raise CompareAbortError("Solo se comparan archivos CSV, TSV o PSV.")

    if not path_a.is_file() or not path_b.is_file():
        raise CompareAbortError("Uno de los archivos no existe en disco.")

    threshold = min(normalize_pandas_max_bytes(profile.pandas_max_bytes), PANDAS_HARD_MAX_BYTES)
    for path, label in ((path_a, label_a), (path_b, label_b)):
        size = path.stat().st_size
        if size > threshold:
            raise CompareAbortError(
                f"{label} supera el umbral pandas ({size:,} bytes > {threshold:,})."
            )

    cols_a = _read_header(path_a)
    cols_b = _read_header(path_b)
    if cols_a != cols_b:
        if set(cols_a) != set(cols_b):
            raise CompareAbortError("Las columnas no coinciden. Compare abortado.")
        raise CompareAbortError(
            "El orden de columnas debe ser idéntico. Compare abortado."
        )
    if not cols_a:
        raise CompareAbortError("Cabecera vacía o ilegible.")
    return cols_a


def _read_header(path: Path) -> list[str]:
    import pandas as pd

    ext = path.suffix.lower()
    nullable = {"dtype_backend": "numpy_nullable"}
    if ext == ".tsv":
        frame = pd.read_csv(path, sep="\t", nrows=0, **nullable)
    elif ext == ".psv":
        frame = pd.read_csv(path, sep="|", nrows=0, **nullable)
    else:
        try:
            frame = pd.read_csv(path, sep=",", nrows=0, **nullable)
        except Exception:
            frame = pd.read_csv(path, sep=None, engine="python", nrows=0, **nullable)
    return [str(name) for name in frame.columns]
