"""Persistencia de catálogos de esquema columnar — junto a jobs en knowledge_bases/default/jobs/."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from core.schema_catalog_types import (
    SchemaCatalog,
    SchemaCatalogValidationError,
    SchemaColumnSpec,
)

DEFAULT_KB_ID = "default"
SCHEMA_CATALOG_SUFFIX = ".schema.json"
JOB_SUFFIX = ".job.json"
LEGACY_CATALOGS_DIR = "schema_catalogs"


def _emr_root() -> Path:
    return Path(__file__).resolve().parents[1] / "emr-qa"


def knowledge_bases_root() -> Path:
    return _emr_root() / "knowledge_bases"


def jobs_dir(knowledge_base_id: str = DEFAULT_KB_ID) -> Path:
    path = knowledge_bases_root() / knowledge_base_id / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def schema_catalogs_dir(knowledge_base_id: str = DEFAULT_KB_ID) -> Path:
    """Ruta unificada de pruebas (catálogos + jobs)."""
    return jobs_dir(knowledge_base_id)


def slugify_schema_name(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "_", name.strip().casefold()).strip("_")
    return slug or "schema"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _legacy_catalog_path(kb_id: str, schema_id: str) -> Path:
    return knowledge_bases_root() / kb_id / LEGACY_CATALOGS_DIR / f"{schema_id}.json"


def _catalog_path(kb_id: str, schema_id: str) -> Path:
    return jobs_dir(kb_id) / f"{schema_id}{SCHEMA_CATALOG_SUFFIX}"


def _schema_job_path(kb_id: str, schema_id: str) -> Path:
    return jobs_dir(kb_id) / f"{schema_id}{JOB_SUFFIX}"


def _write_schema_job(kb_id: str, catalog: SchemaCatalog) -> None:
    from core.emr_qa_job import EmrQaJob, JobSchemaSection, save_job

    job = EmrQaJob(
        name=catalog.name,
        mode="schema",
        description=f"Validación estructural — catálogo {catalog.schema_id}.",
        knowledge_base_id=kb_id,
        schema=JobSchemaSection(schema_id=catalog.schema_id),
    )
    save_job(_schema_job_path(kb_id, catalog.schema_id), job)


def _migrate_legacy_catalog(kb_id: str, schema_id: str) -> Path | None:
    legacy = _legacy_catalog_path(kb_id, schema_id)
    if not legacy.is_file():
        return None
    target = _catalog_path(kb_id, schema_id)
    if not target.is_file():
        target.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        catalog = SchemaCatalog.from_dict(json.loads(target.read_text(encoding="utf-8")))
        if not _schema_job_path(kb_id, schema_id).is_file():
            _write_schema_job(kb_id, catalog)
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return target if target.is_file() else None


def _is_schema_catalog_payload(raw: dict) -> bool:
    return isinstance(raw, dict) and "columns" in raw and bool(str(raw.get("schema_id") or "").strip())


def _find_catalog_path_by_id(kb_id: str, schema_id: str) -> Path | None:
    token = schema_id.strip()
    if not token:
        return None
    folder = jobs_dir(kb_id)
    direct = _catalog_path(kb_id, token)
    if direct.is_file():
        return direct
    plain = folder / f"{token}.json"
    if plain.is_file() and not plain.name.endswith(JOB_SUFFIX):
        try:
            raw = json.loads(plain.read_text(encoding="utf-8"))
            if _is_schema_catalog_payload(raw):
                return plain
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    for path in sorted(folder.glob(f"*{SCHEMA_CATALOG_SUFFIX}")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if str(raw.get("schema_id") or "").strip() == token:
                return path
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    legacy = _legacy_catalog_path(kb_id, token)
    if legacy.is_file():
        return legacy
    return None


def _resolve_catalog_path(kb_id: str, schema_id: str) -> Path:
    _migrate_legacy_catalog(kb_id, schema_id.strip())
    path = _find_catalog_path_by_id(kb_id, schema_id)
    if path is not None and path.is_file():
        if path.suffix == ".json" and not path.name.endswith(SCHEMA_CATALOG_SUFFIX):
            target = _catalog_path(kb_id, schema_id.strip())
            if not target.is_file():
                target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            path = target
        return path
    raise SchemaCatalogValidationError(f"schema catalog not found: {schema_id}")


def list_schema_catalog_summaries(
    knowledge_base_id: str = DEFAULT_KB_ID,
) -> list[tuple[str, str, bool]]:
    """Return (schema_id, name, strict) sorted by name."""
    folder = jobs_dir(knowledge_base_id)
    items: list[tuple[str, str, bool]] = []
    seen: set[str] = set()

    legacy_root = knowledge_bases_root() / knowledge_base_id / LEGACY_CATALOGS_DIR
    if legacy_root.is_dir():
        for path in sorted(legacy_root.glob("*.json")):
            _migrate_legacy_catalog(knowledge_base_id, path.stem)

    for path in sorted(folder.glob(f"*{SCHEMA_CATALOG_SUFFIX}")):
        schema_id = path.name[: -len(SCHEMA_CATALOG_SUFFIX)]
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            catalog = SchemaCatalog.from_dict(raw)
            if catalog.schema_id:
                items.append((catalog.schema_id, catalog.name or catalog.schema_id, catalog.strict))
                seen.add(catalog.schema_id)
        except (OSError, json.JSONDecodeError, TypeError):
            continue

    return sorted(items, key=lambda item: item[1].casefold())


class SchemaCatalogStore:
    def __init__(self, knowledge_base_id: str = DEFAULT_KB_ID) -> None:
        self.knowledge_base_id = knowledge_base_id
        self._cache: dict[str, SchemaCatalog] = {}

    def invalidate(self, schema_id: str | None = None) -> None:
        if schema_id is None:
            self._cache.clear()
            return
        self._cache.pop(schema_id, None)

    def load(self, schema_id: str) -> SchemaCatalog:
        token = schema_id.strip()
        if not token:
            raise SchemaCatalogValidationError("schema catalog not found: (empty)")
        cached = self._cache.get(token)
        if cached is not None:
            return cached
        path = _resolve_catalog_path(self.knowledge_base_id, token)
        catalog = SchemaCatalog.from_dict(json.loads(path.read_text(encoding="utf-8")))
        if not catalog.schema_id:
            raise SchemaCatalogValidationError(f"invalid schema catalog: {token}")
        self._cache[token] = catalog
        return catalog

    def save(self, catalog: SchemaCatalog) -> SchemaCatalog:
        schema_id = catalog.schema_id.strip()
        if not schema_id:
            raise SchemaCatalogValidationError("schema_id required")
        if not catalog.name.strip():
            raise SchemaCatalogValidationError("name required")
        names = [column.name.strip() for column in catalog.columns if column.name.strip()]
        if len(names) != len(set(names)):
            raise SchemaCatalogValidationError("duplicate column names in schema catalog")
        now = _utc_now()
        created = catalog.created_at or now
        payload = SchemaCatalog(
            schema_id=schema_id,
            name=catalog.name.strip(),
            strict=catalog.strict,
            columns=list(catalog.columns),
            created_at=created,
            updated_at=now,
            schema_version=catalog.schema_version,
            batch_match=catalog.batch_match,
        )
        path = _catalog_path(self.knowledge_base_id, schema_id)
        path.write_text(
            json.dumps(payload.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        _write_schema_job(self.knowledge_base_id, payload)
        legacy = _legacy_catalog_path(self.knowledge_base_id, schema_id)
        if legacy.is_file():
            legacy.unlink()
        self._cache[schema_id] = payload
        return payload

    def delete(self, schema_id: str) -> None:
        for path in (
            _catalog_path(self.knowledge_base_id, schema_id),
            _schema_job_path(self.knowledge_base_id, schema_id),
            _legacy_catalog_path(self.knowledge_base_id, schema_id),
        ):
            if path.is_file():
                path.unlink()
        self.invalidate(schema_id)

    def new_catalog(self, name: str, *, columns: list[SchemaColumnSpec] | None = None) -> SchemaCatalog:
        schema_id = slugify_schema_name(name)
        base = schema_id
        counter = 2
        while _catalog_path(self.knowledge_base_id, schema_id).exists() or _legacy_catalog_path(
            self.knowledge_base_id, schema_id
        ).exists():
            schema_id = f"{base}_{counter}"
            counter += 1
        now = _utc_now()
        return SchemaCatalog(
            schema_id=schema_id,
            name=name.strip() or schema_id,
            strict=False,
            columns=list(columns or []),
            created_at=now,
            updated_at=now,
        )
