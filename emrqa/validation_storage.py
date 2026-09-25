"""Persistencia JSON — templates v2.0 de validación tabular."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .template_crypto import ENCRYPTION_ALG, DecryptionError, SealedBlob, seal_minibase, unseal_minibase
from .template_key_store import NoActiveKeyError, TemplateKeyStore
from .validation_models import SCHEMA_VERSION, MinibaseSection, TemplateEncryption, ValidationTemplate, new_id

ROOT = Path(__file__).resolve().parents[1]  # emr-qa/
KNOWLEDGE_BASES = ROOT / "knowledge_bases"


class TemplateKeyMismatchError(ValueError):
    def __init__(self, *, expected_key_id: str, active_key_id: str | None) -> None:
        self.expected_key_id = expected_key_id
        self.active_key_id = active_key_id
        active = active_key_id or "(sin llave)"
        super().__init__(
            f"Template cifrado con llave {expected_key_id}; llave activa: {active}"
        )


class TemplateRequiresKeyError(ValueError):
    def __init__(self, *, expected_key_id: str) -> None:
        self.expected_key_id = expected_key_id
        super().__init__(f"Template cifrado con llave {expected_key_id}; no hay llave activa")


@dataclass(frozen=True)
class TemplateSummary:
    path: Path
    template_id: str
    name: str
    record_count: int
    encrypted: bool = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_validation_template(raw: dict) -> bool:
    meta = raw.get("_meta")
    if isinstance(meta, dict):
        return str(meta.get("schema_version")) == SCHEMA_VERSION
    return False


def is_encrypted_template_raw(raw: dict[str, Any]) -> bool:
    header = raw.get("header") if isinstance(raw.get("header"), dict) else {}
    encryption = header.get("encryption") if isinstance(header.get("encryption"), dict) else {}
    key_id = str(encryption.get("key_id") or "").strip()
    return bool(key_id) and isinstance(raw.get("minibase_sealed"), dict)


def knowledge_base_dir(kb_id: str) -> Path:
    path = KNOWLEDGE_BASES / kb_id
    path.mkdir(parents=True, exist_ok=True)
    (path / "templates").mkdir(exist_ok=True)
    return path


def slugify_template_name(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "_", name.strip().casefold())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or new_id("tpl")


def template_filename(template: ValidationTemplate) -> str:
    stem = slugify_template_name(template.header.name)
    return f"{stem}.json"


def _resolve_key_store(key_store: TemplateKeyStore | None) -> TemplateKeyStore:
    return key_store if key_store is not None else TemplateKeyStore()


def _record_count_from_raw(raw: dict[str, Any]) -> int:
    if is_encrypted_template_raw(raw):
        header = raw.get("header") if isinstance(raw.get("header"), dict) else {}
        encryption = header.get("encryption") if isinstance(header.get("encryption"), dict) else {}
        count_raw = encryption.get("record_count")
        if count_raw is not None:
            try:
                return int(count_raw)
            except (TypeError, ValueError):
                return 0
        return 0
    minibase = raw.get("minibase") if isinstance(raw.get("minibase"), dict) else {}
    records = minibase.get("records") if isinstance(minibase.get("records"), list) else []
    return len(records)


def _decrypt_raw_minibase(raw: dict[str, Any], key_store: TemplateKeyStore) -> dict[str, Any]:
    header = raw.get("header") if isinstance(raw.get("header"), dict) else {}
    encryption_raw = header.get("encryption") if isinstance(header.get("encryption"), dict) else {}
    expected_key_id = str(encryption_raw.get("key_id") or "").strip()
    if not expected_key_id:
        raise ValueError("Template sellado sin key_id en header.encryption")
    sealed_raw = raw.get("minibase_sealed")
    if not isinstance(sealed_raw, dict):
        raise ValueError("Template cifrado sin minibase_sealed")
    if not key_store.has_active_key():
        raise TemplateRequiresKeyError(expected_key_id=expected_key_id)
    active_key_id = key_store.active_key_id()
    if active_key_id != expected_key_id:
        raise TemplateKeyMismatchError(expected_key_id=expected_key_id, active_key_id=active_key_id)
    try:
        return unseal_minibase(SealedBlob.from_dict(sealed_raw), key_store.active_key_bytes())
    except DecryptionError as exc:
        raise TemplateKeyMismatchError(
            expected_key_id=expected_key_id,
            active_key_id=active_key_id,
        ) from exc


def _disk_dict_from_template(template: ValidationTemplate, key_store: TemplateKeyStore) -> dict[str, Any]:
    header_dict = template.header.to_dict()
    data: dict[str, Any] = {
        "_meta": template.meta.to_dict(),
        "header": header_dict,
    }
    if template.is_encrypted:
        encryption = template.header.encryption
        if encryption is None:
            raise ValueError("Template marcado cifrado sin metadata de encryption")
        if not key_store.has_active_key():
            raise NoActiveKeyError("No hay llave activa para guardar template cifrado")
        active_key_id = key_store.active_key_id()
        if active_key_id != encryption.key_id:
            raise TemplateKeyMismatchError(
                expected_key_id=encryption.key_id,
                active_key_id=active_key_id,
            )
        record_count = len(template.minibase.records)
        encryption.record_count = record_count
        header_dict["encryption"] = encryption.to_dict()
        data["header"] = header_dict
        sealed = seal_minibase(template.minibase.to_dict(), key_store.active_key_bytes())
        data["minibase_sealed"] = sealed.to_dict()
    else:
        data["minibase"] = template.minibase.to_dict()
    return data


def encrypt_template_minibase(template: ValidationTemplate, key_store: TemplateKeyStore) -> None:
    if template.is_encrypted:
        return
    key_id = key_store.active_key_id()
    if not key_store.has_active_key() or key_id is None:
        raise NoActiveKeyError("No hay llave activa para cifrar la minibase")
    template.header.encryption = TemplateEncryption(
        key_id=key_id,
        alg=ENCRYPTION_ALG,
        record_count=len(template.minibase.records),
    )
    template.meta.updated_at = _utc_now_iso()


def save_validation_template(
    template: ValidationTemplate,
    *,
    key_store: TemplateKeyStore | None = None,
) -> Path:
    store = _resolve_key_store(key_store)
    kb_id = template.meta.knowledge_base_id
    base = knowledge_base_dir(kb_id)
    path = base / "templates" / template_filename(template)
    template.meta.updated_at = _utc_now_iso()
    if template.is_encrypted and template.header.encryption is not None:
        template.header.encryption.record_count = len(template.minibase.records)
    disk_dict = _disk_dict_from_template(template, store)
    path.write_text(
        json.dumps(disk_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def load_validation_template(
    path: Path,
    *,
    key_store: TemplateKeyStore | None = None,
) -> ValidationTemplate:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not is_validation_template(raw):
        raise ValueError(f"No es template v{SCHEMA_VERSION}: {path}")
    store = _resolve_key_store(key_store)
    if is_encrypted_template_raw(raw):
        minibase_raw = _decrypt_raw_minibase(raw, store)
        parsed = dict(raw)
        parsed["minibase"] = minibase_raw
        parsed.pop("minibase_sealed", None)
        return ValidationTemplate.from_dict(parsed)
    return ValidationTemplate.from_dict(raw)


def list_validation_templates(kb_id: str) -> list[Path]:
    folder = templates_dir(kb_id)
    results: list[Path] = []
    for path in sorted(folder.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if is_validation_template(raw):
            results.append(path)
    return results


def templates_dir(kb_id: str) -> Path:
    path = knowledge_base_dir(kb_id) / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_template_summaries(kb_id: str = "default") -> list[TemplateSummary]:
    summaries: list[TemplateSummary] = []
    for path in sorted(templates_dir(kb_id).glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not is_validation_template(raw):
            continue
        meta = raw.get("_meta") if isinstance(raw.get("_meta"), dict) else {}
        header = raw.get("header") if isinstance(raw.get("header"), dict) else {}
        encrypted = is_encrypted_template_raw(raw)
        summaries.append(
            TemplateSummary(
                path=path,
                template_id=str(meta.get("template_id") or path.stem),
                name=str(header.get("name") or path.stem).strip(),
                record_count=_record_count_from_raw(raw),
                encrypted=encrypted,
            )
        )
    return summaries
