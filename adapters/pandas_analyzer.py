"""Análisis tabular con pandas — import lazy (P-R1)."""
from __future__ import annotations

from pathlib import Path

from core.analysis_limits import DEFAULT_MAX_DISPLAY_ROWS
from core.analysis_errors import AnalysisFormatError, AnalysisTooLargeError
from core.analysis_types import ColumnSummary, TabularDataset
from core.result import Err, Ok, Result


DEFAULT_MAX_BYTES = 209_715_200  # 200 MiB — alineado con file_view; HIPAA después
_ROW_ESTIMATE_PROBE_BYTES = 4_194_304  # 4 MiB
_DELIMITED_EXTENSIONS = frozenset({".csv", ".tsv", ".psv"})


def analyze_tabular_file(
    path: Path,
    *,
    max_display_rows: int = DEFAULT_MAX_DISPLAY_ROWS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    sample_rows: int | None = None,
) -> Result[TabularDataset, AnalysisFormatError | AnalysisTooLargeError]:
    if not path.is_file():
        return Err(AnalysisFormatError(f"Archivo no encontrado: {path}", path=str(path)))

    file_size = path.stat().st_size
    sampled = file_size > max_bytes
    if sampled and not sample_rows:
        return Err(
            AnalysisTooLargeError(
                f"Archivo demasiado grande para analizar ({_format_size(file_size)}). "
                f"Límite: {_format_size(max_bytes)}.",
                path=str(path),
                file_size=file_size,
                limit_bytes=max_bytes,
            )
        )

    try:
        import pandas as pd
    except ImportError:
        return Err(
            AnalysisFormatError(
                "pandas no está instalado. Ejecute: pip install pandas",
                path=str(path),
            )
        )

    try:
        dataframe = _read_dataframe(pd, path, nrows=sample_rows if sampled else None)
    except Exception as exc:  # noqa: BLE001 — convertir a error de dominio
        return Err(
            AnalysisFormatError(
                f"No se pudo leer archivo tabular:\n{exc}",
                path=str(path),
            )
        )

    if dataframe.empty and len(dataframe.columns) == 0:
        return Err(
            AnalysisFormatError("Archivo tabular vacío o sin columnas.", path=str(path))
        )

    summaries = tuple(_summarize_column(dataframe[name]) for name in dataframe.columns)
    total_rows = len(dataframe)
    display = dataframe.head(max_display_rows)
    display_truncated = total_rows > max_display_rows
    rows = tuple(
        tuple("" if value is None else str(value) for value in record)
        for record in display.itertuples(index=False, name=None)
    )

    return Ok(
        TabularDataset(
            local_path=path,
            columns=summaries,
            rows=rows,
            total_rows=total_rows,
            display_truncated=display_truncated,
            sampled=sampled,
            estimated_total_rows=_estimate_total_rows(path, file_size) if sampled else None,
        )
    )


def _read_dataframe(pd, path: Path, *, nrows: int | None = None):
    ext = path.suffix.lower()
    nullable = {"dtype_backend": "numpy_nullable"}
    if ext in {".xlsx", ".xlsm"}:
        return pd.read_excel(path, engine="openpyxl", nrows=nrows)
    if ext == ".xls":
        return pd.read_excel(path, nrows=nrows)
    if ext == ".tsv":
        return pd.read_csv(path, sep="\t", engine="c", nrows=nrows, **nullable)
    if ext == ".psv":
        return pd.read_csv(path, sep="|", engine="c", nrows=nrows, **nullable)
    try:
        return pd.read_csv(path, sep=",", engine="c", nrows=nrows, **nullable)
    except Exception:
        return pd.read_csv(path, sep=None, engine="python", nrows=nrows, **nullable)


def _estimate_total_rows(path: Path, file_size: int) -> int | None:
    """Filas aproximadas por bytes/línea; solo lee la cabeza del archivo."""
    if path.suffix.lower() not in _DELIMITED_EXTENSIONS or file_size <= 0:
        return None
    try:
        with path.open("rb") as handle:
            head = handle.read(_ROW_ESTIMATE_PROBE_BYTES)
    except OSError:
        return None
    newlines = head.count(b"\n")
    if newlines <= 1:
        return None
    bytes_per_line = len(head) / newlines
    return max(int(file_size / bytes_per_line) - 1, 0)


def _summarize_column(series) -> ColumnSummary:
    import pandas as pd

    null_count = int(series.isna().sum())
    unique_count = int(series.nunique(dropna=True))
    dtype = str(series.dtype)
    sum_value = mean_value = min_value = max_value = None

    if pd.api.types.is_numeric_dtype(series):
        numeric = series.dropna()
        if len(numeric) > 0:
            sum_value = float(numeric.sum())
            mean_value = float(numeric.mean())
            min_value = float(numeric.min())
            max_value = float(numeric.max())

    return ColumnSummary(
        name=str(series.name),
        dtype=dtype,
        null_count=null_count,
        unique_count=unique_count,
        sum_value=sum_value,
        mean_value=mean_value,
        min_value=min_value,
        max_value=max_value,
    )


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"
