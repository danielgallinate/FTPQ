"""Cifrado AES-256-GCM de la minibase en templates v2.0."""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENCRYPTION_ALG = "AES-256-GCM"
KEY_BYTE_LENGTH = 32
NONCE_BYTE_LENGTH = 12
KEY_ID_HEX_LENGTH = 16


class DecryptionError(Exception):
    """Fallo al descifrar (llave incorrecta o datos corruptos)."""


@dataclass(frozen=True)
class SealedBlob:
    nonce_b64: str
    ciphertext_b64: str

    def to_dict(self) -> dict[str, str]:
        return {
            "nonce_b64": self.nonce_b64,
            "ciphertext_b64": self.ciphertext_b64,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SealedBlob:
        nonce = str(raw.get("nonce_b64") or "").strip()
        ciphertext = str(raw.get("ciphertext_b64") or "").strip()
        if not nonce or not ciphertext:
            raise ValueError("minibase_sealed incompleto")
        return cls(nonce_b64=nonce, ciphertext_b64=ciphertext)


def derive_key_id(key_bytes: bytes) -> str:
    digest = hashlib.sha256(key_bytes).hexdigest()
    return digest[:KEY_ID_HEX_LENGTH]


def _validate_key_bytes(key_bytes: bytes) -> None:
    if len(key_bytes) != KEY_BYTE_LENGTH:
        raise ValueError(f"La llave debe tener {KEY_BYTE_LENGTH} bytes")


def seal_minibase(minibase_dict: dict[str, Any], key_bytes: bytes) -> SealedBlob:
    _validate_key_bytes(key_bytes)
    payload = json.dumps(minibase_dict, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    nonce = secrets.token_bytes(NONCE_BYTE_LENGTH)
    ciphertext = AESGCM(key_bytes).encrypt(nonce, payload, None)
    return SealedBlob(
        nonce_b64=base64.b64encode(nonce).decode("ascii"),
        ciphertext_b64=base64.b64encode(ciphertext).decode("ascii"),
    )


def unseal_minibase(sealed: SealedBlob, key_bytes: bytes) -> dict[str, Any]:
    _validate_key_bytes(key_bytes)
    try:
        nonce = base64.b64decode(sealed.nonce_b64, validate=True)
        ciphertext = base64.b64decode(sealed.ciphertext_b64, validate=True)
        payload = AESGCM(key_bytes).decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise DecryptionError("No se pudo descifrar la minibase") from exc
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DecryptionError("Payload descifrado inválido") from exc
    if not isinstance(parsed, dict):
        raise DecryptionError("Payload descifrado inválido")
    return parsed
