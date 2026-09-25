"""Llave única opcional para cifrado de minibase en templates."""
from __future__ import annotations

import base64
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .template_crypto import KEY_BYTE_LENGTH, derive_key_id

ROOT = Path(__file__).resolve().parents[1]  # emr-qa/
DEFAULT_KEY_PATH = ROOT / "config" / "template_encryption.key"


class NoActiveKeyError(Exception):
    """No hay llave activa cargada."""


class InvalidKeyFileError(ValueError):
    """Archivo de llave inválido."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_key_file(raw: dict[str, Any]) -> tuple[str, bytes]:
    key_id = str(raw.get("key_id") or "").strip()
    key_b64 = str(raw.get("key_b64") or "").strip()
    if not key_id or not key_b64:
        raise InvalidKeyFileError("Faltan key_id o key_b64")
    try:
        key_bytes = base64.b64decode(key_b64, validate=True)
    except Exception as exc:
        raise InvalidKeyFileError("key_b64 inválido") from exc
    if len(key_bytes) != KEY_BYTE_LENGTH:
        raise InvalidKeyFileError(f"La llave debe tener {KEY_BYTE_LENGTH} bytes")
    expected_id = derive_key_id(key_bytes)
    if key_id != expected_id:
        raise InvalidKeyFileError("key_id no coincide con la llave")
    return key_id, key_bytes


class TemplateKeyStore:
    def __init__(self, default_path: Path | None = None) -> None:
        self._default_path = default_path or DEFAULT_KEY_PATH
        self._key_id: str | None = None
        self._key_bytes: bytes | None = None
        self._source_path: Path | None = None
        self.try_load_default()

    @property
    def default_path(self) -> Path:
        return self._default_path

    @property
    def source_path(self) -> Path | None:
        return self._source_path

    def has_active_key(self) -> bool:
        return self._key_bytes is not None

    def active_key_id(self) -> str | None:
        return self._key_id

    def active_key_bytes(self) -> bytes:
        if self._key_bytes is None:
            raise NoActiveKeyError("No hay llave activa")
        return self._key_bytes

    def clear(self) -> None:
        self._key_id = None
        self._key_bytes = None
        self._source_path = None

    def try_load_default(self) -> bool:
        path = self._default_path
        if not path.is_file():
            return False
        try:
            self.load_from_file(path, persist_default=False)
        except (OSError, InvalidKeyFileError, json.JSONDecodeError):
            return False
        return True

    def load_from_file(self, path: Path, *, persist_default: bool = True) -> str:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise InvalidKeyFileError("El archivo debe ser un objeto JSON")
        key_id, key_bytes = _parse_key_file(raw)
        self._key_id = key_id
        self._key_bytes = key_bytes
        self._source_path = path.resolve()
        if persist_default and path.resolve() != self._default_path.resolve():
            self._write_key_file(self._default_path, key_id, key_bytes)
            self._source_path = self._default_path.resolve()
        return key_id

    def generate_and_save(self, path: Path | None = None) -> str:
        target = path or self._default_path
        key_bytes = secrets.token_bytes(KEY_BYTE_LENGTH)
        key_id = derive_key_id(key_bytes)
        self._write_key_file(target, key_id, key_bytes)
        self._key_id = key_id
        self._key_bytes = key_bytes
        self._source_path = target.resolve()
        return key_id

    def export_to_file(self, path: Path) -> None:
        key_bytes = self.active_key_bytes()
        key_id = self._key_id or derive_key_id(key_bytes)
        self._write_key_file(path, key_id, key_bytes)

    @staticmethod
    def _write_key_file(path: Path, key_id: str, key_bytes: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "key_id": key_id,
            "key_b64": base64.b64encode(key_bytes).decode("ascii"),
            "created_at": _utc_now_iso(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
