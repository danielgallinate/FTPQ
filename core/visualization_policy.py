"""Umbrales y modo de visualización tabular (pandas vs texto)."""
from __future__ import annotations

from typing import Protocol

PANDAS_HARD_MAX_BYTES = 209_715_200  # 200 MiB — tope absoluto pandas
TEXT_HEAD_MAX_BYTES = 2_097_152  # 2 MiB leídos del disco en modo texto
DEFAULT_PANDAS_MAX_BYTES = 52_428_800  # 50 MiB — umbral auto

PANDAS_THRESHOLD_PRESETS: tuple[int, ...] = (
    10_485_760,  # 10 MiB
    52_428_800,  # 50 MiB
    104_857_600,  # 100 MiB
    209_715_200,  # 200 MiB
)

TABULAR_MODE_AUTO = "auto"
TABULAR_MODE_FULL = "full"
TABULAR_MODE_TEXT = "text_only"
TABULAR_MODES: tuple[str, ...] = (TABULAR_MODE_AUTO, TABULAR_MODE_FULL, TABULAR_MODE_TEXT)
DEFAULT_TABULAR_MODE = TABULAR_MODE_AUTO


class TabularPolicyProfile(Protocol):
    tabular_mode: str
    pandas_max_bytes: int


def normalize_tabular_mode(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized in TABULAR_MODES:
        return normalized
    return DEFAULT_TABULAR_MODE


def normalize_pandas_max_bytes(value: int) -> int:
    if value in PANDAS_THRESHOLD_PRESETS:
        return value
    for preset in PANDAS_THRESHOLD_PRESETS:
        if value <= preset:
            return preset
    return PANDAS_THRESHOLD_PRESETS[-1]


def tabular_uses_pandas(profile: TabularPolicyProfile, file_size: int) -> bool:
    """True si conviene parsear CSV/TSV/PSV con pandas."""
    mode = normalize_tabular_mode(profile.tabular_mode)
    if mode == TABULAR_MODE_TEXT:
        return False
    if file_size > PANDAS_HARD_MAX_BYTES:
        return False
    if mode == TABULAR_MODE_FULL:
        return True
    threshold = normalize_pandas_max_bytes(profile.pandas_max_bytes)
    return file_size <= threshold


def format_bytes_label(size_bytes: int) -> str:
    if size_bytes >= 1_048_576:
        mb = size_bytes / 1_048_576
        if mb == int(mb):
            return f"{int(mb)} MB"
        return f"{mb:.0f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes // 1024} KB"
    return f"{size_bytes} B"
