"""Modelos JSON v2.0 — template de validación tabular + minibase."""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

RuleTargetType = Literal["field", "key"]
RuleType = Literal[
    "not_empty",
    "regex",
    "in_list",
    "unique_in_file",
    "exists_in_minibase",
    "not_in_minibase",
]
DedupStrategy = Literal["composite_key"]

KEY_VALUE_SEPARATOR = "\x1f"
SCHEMA_VERSION = "2.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str = "") -> str:
    token = uuid.uuid4().hex[:12]
    return f"{prefix}{token}" if prefix else token


def normalize_cell_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def compute_key_fingerprint(field_values: list[str]) -> str:
    """Fingerprint estable para dedup — ver iteracion-02-template-schema.md."""
    payload = KEY_VALUE_SEPARATOR.join(normalize_cell_value(v) for v in field_values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class TemplateMeta:
    schema_version: str
    template_id: str
    knowledge_base_id: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TemplateMeta:
        now = _utc_now_iso()
        return cls(
            schema_version=str(raw.get("schema_version") or SCHEMA_VERSION),
            template_id=str(raw.get("template_id") or new_id("tpl_")),
            knowledge_base_id=str(raw.get("knowledge_base_id") or "default"),
            created_at=str(raw.get("created_at") or now),
            updated_at=str(raw.get("updated_at") or now),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RowField:
    field_id: str
    label: str
    column: str
    required: bool = False
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> RowField:
        return cls(
            field_id=str(raw.get("field_id") or new_id("fld_")),
            label=str(raw.get("label") or "").strip(),
            column=str(raw.get("column") or "").strip(),
            required=bool(raw.get("required", False)),
            notes=str(raw.get("notes") or "").strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not self.notes:
            data.pop("notes", None)
        return data


@dataclass
class TemplateKey:
    key_id: str
    label: str
    field_ids: list[str]
    primary: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TemplateKey:
        ids_raw = raw.get("field_ids") or []
        field_ids = [str(item).strip() for item in ids_raw if str(item).strip()]
        return cls(
            key_id=str(raw.get("key_id") or new_id("key_")),
            label=str(raw.get("label") or "").strip(),
            field_ids=field_ids,
            primary=bool(raw.get("primary", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def is_composite(self) -> bool:
        return len(self.field_ids) > 1


@dataclass
class ValidationRule:
    rule_id: str
    target_type: RuleTargetType
    target_id: str
    type: RuleType
    params: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ValidationRule:
        params_raw = raw.get("params")
        params = dict(params_raw) if isinstance(params_raw, dict) else {}
        target_type = raw.get("target_type")
        if target_type not in ("field", "key"):
            target_type = "field"
        rule_type = str(raw.get("type") or "not_empty")
        return cls(
            rule_id=str(raw.get("rule_id") or new_id("rule_")),
            target_type=target_type,  # type: ignore[arg-type]
            target_id=str(raw.get("target_id") or "").strip(),
            type=rule_type,  # type: ignore[arg-type]
            params=params,
            message=str(raw.get("message") or "").strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not self.params:
            data.pop("params", None)
        if not self.message:
            data.pop("message", None)
        return data


@dataclass
class EvaluationDefaults:
    columns: list[str] = field(default_factory=list)
    show_only_evaluated: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> EvaluationDefaults:
        if not isinstance(raw, dict):
            return cls()
        cols_raw = raw.get("columns") or []
        columns = [str(item).strip() for item in cols_raw if str(item).strip()]
        return cls(
            columns=columns,
            show_only_evaluated=bool(raw.get("show_only_evaluated", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileHints:
    extensions: list[str] = field(default_factory=list)
    filename_contains: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> FileHints:
        if not isinstance(raw, dict):
            return cls()
        ext_raw = raw.get("extensions") or []
        name_raw = raw.get("filename_contains") or []
        return cls(
            extensions=[str(item).strip() for item in ext_raw if str(item).strip()],
            filename_contains=[str(item).strip() for item in name_raw if str(item).strip()],
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.extensions:
            data["extensions"] = self.extensions
        if self.filename_contains:
            data["filename_contains"] = self.filename_contains
        return data


@dataclass
class TemplateEncryption:
    key_id: str
    alg: str = "AES-256-GCM"
    record_count: int | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> TemplateEncryption | None:
        if not isinstance(raw, dict):
            return None
        key_id = str(raw.get("key_id") or "").strip()
        if not key_id:
            return None
        record_count_raw = raw.get("record_count")
        record_count = int(record_count_raw) if record_count_raw is not None else None
        return cls(
            key_id=key_id,
            alg=str(raw.get("alg") or "AES-256-GCM"),
            record_count=record_count,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "key_id": self.key_id,
            "alg": self.alg,
        }
        if self.record_count is not None:
            data["record_count"] = self.record_count
        return data


@dataclass
class TemplateHeader:
    name: str
    description: str = ""
    file_hints: FileHints = field(default_factory=FileHints)
    fields: list[RowField] = field(default_factory=list)
    keys: list[TemplateKey] = field(default_factory=list)
    rules: list[ValidationRule] = field(default_factory=list)
    evaluation: EvaluationDefaults = field(default_factory=EvaluationDefaults)
    encryption: TemplateEncryption | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TemplateHeader:
        fields_raw = raw.get("fields") or []
        keys_raw = raw.get("keys") or []
        rules_raw = raw.get("rules") or []
        return cls(
            name=str(raw.get("name") or "Sin nombre").strip(),
            description=str(raw.get("description") or "").strip(),
            file_hints=FileHints.from_dict(raw.get("file_hints")),
            fields=[RowField.from_dict(item) for item in fields_raw if isinstance(item, dict)],
            keys=[TemplateKey.from_dict(item) for item in keys_raw if isinstance(item, dict)],
            rules=[ValidationRule.from_dict(item) for item in rules_raw if isinstance(item, dict)],
            evaluation=EvaluationDefaults.from_dict(raw.get("evaluation")),
            encryption=TemplateEncryption.from_dict(raw.get("encryption")),
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "fields": [item.to_dict() for item in self.fields],
            "keys": [item.to_dict() for item in self.keys],
        }
        if self.description:
            data["description"] = self.description
        hints = self.file_hints.to_dict()
        if hints:
            data["file_hints"] = hints
        if self.rules:
            data["rules"] = [item.to_dict() for item in self.rules]
        if self.evaluation.columns or self.evaluation.show_only_evaluated:
            data["evaluation"] = self.evaluation.to_dict()
        if self.encryption is not None:
            data["encryption"] = self.encryption.to_dict()
        return data

    def field_by_id(self, field_id: str) -> RowField | None:
        for item in self.fields:
            if item.field_id == field_id:
                return item
        return None

    def key_by_id(self, key_id: str) -> TemplateKey | None:
        for item in self.keys:
            if item.key_id == key_id:
                return item
        return None

    def primary_key(self) -> TemplateKey | None:
        for item in self.keys:
            if item.primary:
                return item
        return self.keys[0] if self.keys else None


@dataclass
class RecordSource:
    file_name: str = ""
    file_path: str = ""
    row_index: int | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> RecordSource:
        if not isinstance(raw, dict):
            return cls()
        row_index = raw.get("row_index")
        return cls(
            file_name=str(raw.get("file_name") or "").strip(),
            file_path=str(raw.get("file_path") or "").strip(),
            row_index=int(row_index) if row_index is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.file_name:
            data["file_name"] = self.file_name
        if self.file_path:
            data["file_path"] = self.file_path
        if self.row_index is not None:
            data["row_index"] = self.row_index
        return data


@dataclass
class RecordValidationSnapshot:
    passed: bool = True
    failed_rule_ids: list[str] = field(default_factory=list)
    evaluated_columns: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> RecordValidationSnapshot:
        if not isinstance(raw, dict):
            return cls()
        failed_raw = raw.get("failed_rule_ids") or []
        cols_raw = raw.get("evaluated_columns") or []
        return cls(
            passed=bool(raw.get("passed", True)),
            failed_rule_ids=[str(item) for item in failed_raw],
            evaluated_columns=[str(item).strip() for item in cols_raw if str(item).strip()],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MinibaseRecord:
    record_id: str
    key_fingerprint: str
    key_id: str
    saved_at: str
    values: dict[str, str]
    source: RecordSource = field(default_factory=RecordSource)
    validation: RecordValidationSnapshot = field(default_factory=RecordValidationSnapshot)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MinibaseRecord:
        values_raw = raw.get("values") or {}
        values = {
            str(key): normalize_cell_value(val)
            for key, val in values_raw.items()
            if isinstance(key, str)
        }
        return cls(
            record_id=str(raw.get("record_id") or new_id("rec_")),
            key_fingerprint=str(raw.get("key_fingerprint") or ""),
            key_id=str(raw.get("key_id") or ""),
            saved_at=str(raw.get("saved_at") or _utc_now_iso()),
            values=values,
            source=RecordSource.from_dict(raw.get("source")),
            validation=RecordValidationSnapshot.from_dict(raw.get("validation")),
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "record_id": self.record_id,
            "key_fingerprint": self.key_fingerprint,
            "key_id": self.key_id,
            "saved_at": self.saved_at,
            "values": self.values,
        }
        source = self.source.to_dict()
        if source:
            data["source"] = source
        validation = self.validation.to_dict()
        if validation.get("failed_rule_ids") or validation.get("evaluated_columns") or not validation.get("passed", True):
            data["validation"] = validation
        elif validation:
            data["validation"] = validation
        return data


@dataclass
class DedupPolicy:
    key_id: str
    strategy: DedupStrategy = "composite_key"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> DedupPolicy:
        if not isinstance(raw, dict):
            return cls(key_id="")
        strategy = raw.get("strategy") or "composite_key"
        if strategy != "composite_key":
            strategy = "composite_key"
        return cls(
            key_id=str(raw.get("key_id") or "").strip(),
            strategy=strategy,  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MinibaseSection:
    dedup: DedupPolicy
    records: list[MinibaseRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> MinibaseSection:
        if not isinstance(raw, dict):
            return cls(dedup=DedupPolicy(key_id=""), records=[])
        records_raw = raw.get("records") or []
        return cls(
            dedup=DedupPolicy.from_dict(raw.get("dedup")),
            records=[MinibaseRecord.from_dict(item) for item in records_raw if isinstance(item, dict)],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dedup": self.dedup.to_dict(),
            "records": [item.to_dict() for item in self.records],
        }

    def fingerprints(self) -> set[str]:
        return {item.key_fingerprint for item in self.records if item.key_fingerprint}

    def has_fingerprint(self, fingerprint: str) -> bool:
        return fingerprint in self.fingerprints()


@dataclass
class ValidationTemplate:
    meta: TemplateMeta
    header: TemplateHeader
    minibase: MinibaseSection

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ValidationTemplate:
        meta_raw = raw.get("_meta") if isinstance(raw.get("_meta"), dict) else {}
        header_raw = raw.get("header") if isinstance(raw.get("header"), dict) else {}
        minibase_raw = raw.get("minibase") if isinstance(raw.get("minibase"), dict) else {}
        return cls(
            meta=TemplateMeta.from_dict(meta_raw),
            header=TemplateHeader.from_dict(header_raw),
            minibase=MinibaseSection.from_dict(minibase_raw),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "_meta": self.meta.to_dict(),
            "header": self.header.to_dict(),
            "minibase": self.minibase.to_dict(),
        }

    @property
    def template_id(self) -> str:
        return self.meta.template_id

    @property
    def is_encrypted(self) -> bool:
        return self.header.encryption is not None

    def dedup_key(self) -> TemplateKey | None:
        policy = self.minibase.dedup
        if policy.key_id:
            found = self.header.key_by_id(policy.key_id)
            if found:
                return found
        return self.header.primary_key()

    def key_values_from_row(self, key: TemplateKey, row: dict[str, Any]) -> list[str]:
        values: list[str] = []
        for field_id in key.field_ids:
            field = self.header.field_by_id(field_id)
            if not field:
                values.append("")
                continue
            values.append(normalize_cell_value(row.get(field.column)))
        return values

    def fingerprint_for_row(self, key: TemplateKey, row: dict[str, Any]) -> str:
        return compute_key_fingerprint(self.key_values_from_row(key, row))

    def field_values_from_row(self, row: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for field in self.header.fields:
            result[field.field_id] = normalize_cell_value(row.get(field.column))
        return result

    def is_duplicate_row(self, row: dict[str, Any]) -> bool:
        key = self.dedup_key()
        if not key:
            return False
        fingerprint = self.fingerprint_for_row(key, row)
        return self.minibase.has_fingerprint(fingerprint)

    def append_record(
        self,
        row: dict[str, Any],
        *,
        source: RecordSource | None = None,
        validation: RecordValidationSnapshot | None = None,
    ) -> MinibaseRecord:
        key = self.dedup_key()
        if not key:
            raise ValueError("Template sin llave de deduplicación")
        fingerprint = self.fingerprint_for_row(key, row)
        if self.minibase.has_fingerprint(fingerprint):
            raise DuplicateRecordError(fingerprint=fingerprint, key_id=key.key_id)
        record = MinibaseRecord(
            record_id=new_id("rec_"),
            key_fingerprint=fingerprint,
            key_id=key.key_id,
            saved_at=_utc_now_iso(),
            values=self.field_values_from_row(row),
            source=source or RecordSource(),
            validation=validation or RecordValidationSnapshot(),
        )
        self.minibase.records.append(record)
        self.meta.updated_at = _utc_now_iso()
        return record


class DuplicateRecordError(ValueError):
    def __init__(self, *, fingerprint: str, key_id: str) -> None:
        self.fingerprint = fingerprint
        self.key_id = key_id
        super().__init__(f"Registro duplicado para llave {key_id}")
