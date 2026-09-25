"""Tipos — catálogos de esquema columnar (estructura / tipos / null)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from core.batch_match_types import BatchMatchSpec

SchemaDataType = Literal["string", "integer", "decimal", "boolean", "date", "datetime"]
SCHEMA_CATALOG_VERSION = 1

DATA_TYPES: tuple[SchemaDataType, ...] = (
    "string",
    "integer",
    "decimal",
    "boolean",
    "date",
    "datetime",
)


@dataclass
class SchemaColumnSpec:
    name: str
    data_type: SchemaDataType = "string"
    allows_null: bool = True
    unique: bool = False
    date_format: str = ""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "data_type": self.data_type,
            "allows_null": self.allows_null,
            "enabled": self.enabled,
        }
        if self.unique:
            payload["unique"] = True
        if self.date_format:
            payload["date_format"] = self.date_format
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SchemaColumnSpec:
        data_type = str(raw.get("data_type") or "string").strip().casefold()
        if data_type not in DATA_TYPES:
            data_type = "string"
        return cls(
            name=str(raw.get("name") or "").strip(),
            data_type=data_type,  # type: ignore[assignment]
            allows_null=bool(raw.get("allows_null", True)),
            unique=bool(raw.get("unique", False)),
            date_format=str(raw.get("date_format") or "").strip(),
            enabled=bool(raw.get("enabled", True)),
        )


@dataclass
class SchemaCatalog:
    schema_id: str
    name: str
    strict: bool = False
    columns: list[SchemaColumnSpec] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    schema_version: int = SCHEMA_CATALOG_VERSION
    batch_match: BatchMatchSpec | None = None

    def enabled_columns(self) -> list[SchemaColumnSpec]:
        return [column for column in self.columns if column.enabled and column.name.strip()]

    def expected_column_names(self) -> set[str]:
        return {column.name.strip() for column in self.columns if column.name.strip()}

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "name": self.name,
            "strict": self.strict,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "columns": [column.to_dict() for column in self.columns],
        }
        if self.batch_match is not None:
            batch_payload = self.batch_match.to_dict()
            if batch_payload:
                payload["batch_match"] = batch_payload
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SchemaCatalog:
        columns_raw = raw.get("columns") or []
        columns = [
            SchemaColumnSpec.from_dict(item)
            for item in columns_raw
            if isinstance(item, dict)
        ]
        return cls(
            schema_version=int(raw.get("schema_version") or SCHEMA_CATALOG_VERSION),
            schema_id=str(raw.get("schema_id") or "").strip(),
            name=str(raw.get("name") or "").strip(),
            strict=bool(raw.get("strict", False)),
            columns=columns,
            created_at=str(raw.get("created_at") or ""),
            updated_at=str(raw.get("updated_at") or ""),
            batch_match=BatchMatchSpec.from_dict(raw.get("batch_match")),
        )


class SchemaCatalogError(Exception):
    """Error de catálogo de esquema."""


class SchemaCatalogValidationError(SchemaCatalogError):
    pass
