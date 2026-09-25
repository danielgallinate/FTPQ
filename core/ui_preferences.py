"""Preferencias de UI persistidas en perfil."""
from __future__ import annotations

DEFAULT_UI_LANGUAGE = "es"
SUPPORTED_UI_LANGUAGES = frozenset({"es", "en"})


def normalize_ui_language(code: str) -> str:
    normalized = str(code).strip().lower()
    if normalized in SUPPORTED_UI_LANGUAGES:
        return normalized
    return DEFAULT_UI_LANGUAGE
