"""Lectura local post-descarga para Visualizar — sin preview remoto parcial."""
from __future__ import annotations

import tempfile
from pathlib import Path

from core.result import Err, Ok, Result
from core.sftp_errors import PreviewNotSupported, PreviewTooLarge, SftpError
from core.sftp_types import VisualizeResult
from core.visualization_policy import TEXT_HEAD_MAX_BYTES

VIEWABLE_EXTENSIONS = frozenset({".csv", ".txt", ".json", ".log", ".md", ".env", ".tsv", ".psv"})

# Límite de lectura completa en memoria (archivos pequeños / no tabulares)
DEFAULT_VISUALIZE_MAX_BYTES = 209_715_200  # 200 MiB


def is_viewable_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in VIEWABLE_EXTENSIONS


def visualize_local_path(filename: str) -> Path:
    base = Path(tempfile.gettempdir()) / "pde-desktop" / "visualize"
    return base / Path(filename).name


def read_visualize_file(
    path: Path,
    *,
    max_display_lines: int = 500,
    max_bytes: int = DEFAULT_VISUALIZE_MAX_BYTES,
) -> Result[VisualizeResult, SftpError]:
    if not path.is_file():
        return Err(PreviewNotSupported(f"Archivo local no encontrado: {path}", path=str(path)))

    ext = path.suffix.lower()
    if ext not in VIEWABLE_EXTENSIONS:
        return Err(
            PreviewNotSupported(
                f"Visualización no soportada para {ext or '(sin ext)'}",
                path=str(path),
            )
        )

    file_size = path.stat().st_size
    if file_size > max_bytes:
        return read_text_head_preview(
            path,
            max_read_bytes=TEXT_HEAD_MAX_BYTES,
            max_display_lines=max_display_lines,
            text_fallback=True,
        )

    try:
        payload = path.read_bytes()
    except OSError as exc:
        from core.sftp_errors import SftpPathError

        return Err(SftpPathError(f"No se pudo leer archivo local:\n{exc}", path=str(path)))

    return Ok(
        _visualize_from_payload(
            path,
            payload,
            file_size,
            max_display_lines=max_display_lines,
        )
    )


def read_text_head_preview(
    path: Path,
    *,
    max_read_bytes: int = TEXT_HEAD_MAX_BYTES,
    max_display_lines: int = 500,
    text_fallback: bool = False,
) -> Result[VisualizeResult, SftpError]:
    """Lee solo el inicio del archivo — para tabular grande sin pandas."""
    if not path.is_file():
        return Err(PreviewNotSupported(f"Archivo local no encontrado: {path}", path=str(path)))

    file_size = path.stat().st_size
    read_size = min(file_size, max_read_bytes)
    try:
        with path.open("rb") as handle:
            payload = handle.read(read_size)
    except OSError as exc:
        from core.sftp_errors import SftpPathError

        return Err(SftpPathError(f"No se pudo leer archivo local:\n{exc}", path=str(path)))

    if not payload and file_size > 0:
        return Err(
            PreviewTooLarge(
                f"No se pudo leer vista previa de {_format_size(file_size)}.",
                path=str(path),
                bytes_read=0,
                limit_bytes=max_read_bytes,
            )
        )

    view = _visualize_from_payload(
        path,
        payload,
        file_size,
        max_display_lines=max_display_lines,
        head_truncated=file_size > read_size,
        text_fallback=text_fallback,
    )
    return Ok(view)


def _visualize_from_payload(
    path: Path,
    payload: bytes,
    file_size: int,
    *,
    max_display_lines: int,
    head_truncated: bool = False,
    text_fallback: bool = False,
) -> VisualizeResult:
    content = payload.decode("utf-8", errors="replace")
    lines = content.splitlines()
    line_count = len(lines) if lines else (1 if content else 0)
    screen_truncated = line_count > max_display_lines
    display_truncated = head_truncated or screen_truncated
    display = content if not screen_truncated else "\n".join(lines[:max_display_lines])

    if head_truncated and line_count <= max_display_lines:
        line_count = max(line_count, max_display_lines + 1)

    return VisualizeResult(
        local_path=path,
        content=display,
        file_size=file_size,
        line_count=line_count,
        display_truncated=display_truncated,
        tabular=False,
        text_fallback=text_fallback,
    )


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"
