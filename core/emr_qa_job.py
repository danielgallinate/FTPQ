"""Job EMR QA — receta reproducible para runner CLI (schema v1)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from core.catalog_types import ColumnCatalogBinding
from core.cell_transform import CellTransform
from core.reference_compare_types import ComparePairMapping, ReferenceCompareConfig

JOB_SCHEMA_VERSION = 1
JobMode = Literal["reference", "qa", "validation", "schema"]


@dataclass
class JobThresholds:
    min_cell_ok_pct: float | None = None
    max_rows_without_match: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.min_cell_ok_pct is not None:
            data["min_cell_ok_pct"] = self.min_cell_ok_pct
        if self.max_rows_without_match is not None:
            data["max_rows_without_match"] = self.max_rows_without_match
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobThresholds:
        if not isinstance(raw, dict):
            return cls()
        min_pct = raw.get("min_cell_ok_pct")
        max_no_match = raw.get("max_rows_without_match")
        return cls(
            min_cell_ok_pct=float(min_pct) if min_pct is not None else None,
            max_rows_without_match=int(max_no_match)
            if max_no_match is not None
            else None,
        )


@dataclass
class JobTimezone:
    source_tz: str
    target_tz: str
    columns: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_tz": self.source_tz,
            "target_tz": self.target_tz,
            "columns": list(self.columns),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobTimezone | None:
        if not isinstance(raw, dict):
            return None
        columns_raw = raw.get("columns") or []
        columns = tuple(str(item) for item in columns_raw if str(item).strip())
        source = str(raw.get("source_tz") or "UTC").strip()
        target = str(raw.get("target_tz") or "").strip()
        if not columns or not target:
            return None
        return cls(source_tz=source, target_tz=target, columns=columns)


@dataclass
class JobReferenceSection:
    duplicate_policy: str = "first"
    pairs: list[ComparePairMapping] = field(default_factory=list)
    left_catalog_bindings: dict[str, ColumnCatalogBinding] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bindings = {
            column: binding.to_dict()
            for column, binding in self.left_catalog_bindings.items()
        }
        return {
            "duplicate_policy": self.duplicate_policy,
            "pairs": [pair_to_dict(pair) for pair in self.pairs],
            "left_catalog_bindings": bindings,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobReferenceSection:
        if not isinstance(raw, dict):
            return cls()
        policy = str(raw.get("duplicate_policy") or "first")
        if policy not in ("first", "ambiguous"):
            policy = "first"
        pairs_raw = raw.get("pairs") or []
        pairs = [pair_from_dict(item) for item in pairs_raw if isinstance(item, dict)]
        bindings_raw = raw.get("left_catalog_bindings") or {}
        bindings: dict[str, ColumnCatalogBinding] = {}
        if isinstance(bindings_raw, dict):
            for column, payload in bindings_raw.items():
                if isinstance(payload, dict):
                    bindings[str(column)] = ColumnCatalogBinding.from_dict(payload)
        return cls(
            duplicate_policy=policy,
            pairs=pairs,
            left_catalog_bindings=bindings,
        )


@dataclass(frozen=True)
class JobQaCatalogSpec:
    catalog_id: str
    link_column: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"catalog_id": self.catalog_id}
        if self.link_column:
            payload["link_column"] = self.link_column
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> JobQaCatalogSpec:
        return cls(
            catalog_id=str(raw.get("catalog_id") or "").strip(),
            link_column=str(raw.get("link_column") or "").strip(),
        )


@dataclass
class JobQaSection:
    template_paths: tuple[str, ...] = ()
    catalogs: tuple[JobQaCatalogSpec, ...] = ()
    highlight_mode: str = "fail_any"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "template_paths": list(self.template_paths),
            "highlight_mode": self.highlight_mode,
        }
        if self.catalogs:
            payload["catalogs"] = [item.to_dict() for item in self.catalogs]
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobQaSection:
        if not isinstance(raw, dict):
            return cls()
        paths_raw = raw.get("template_paths") or []
        mode = str(raw.get("highlight_mode") or "fail_any")
        if mode not in ("fail_any", "discrepancy"):
            mode = "fail_any"
        catalogs = _parse_qa_catalogs(raw)
        return cls(
            template_paths=tuple(str(item) for item in paths_raw if str(item).strip()),
            catalogs=catalogs,
            highlight_mode=mode,
        )


@dataclass
class JobValidationSection:
    template_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"template_path": self.template_path}

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobValidationSection:
        if not isinstance(raw, dict):
            return cls()
        return cls(template_path=str(raw.get("template_path") or "").strip())


@dataclass
class JobSchemaSection:
    schema_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"schema_id": self.schema_id}

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> JobSchemaSection:
        if not isinstance(raw, dict):
            return cls()
        return cls(schema_id=str(raw.get("schema_id") or "").strip())


@dataclass
class EmrQaJob:
    name: str
    mode: JobMode
    description: str = ""
    max_rows: int | None = None
    row_limit: str | None = None
    evaluated_columns: tuple[str, ...] | None = None
    knowledge_base_id: str = "default"
    reference: JobReferenceSection = field(default_factory=JobReferenceSection)
    qa: JobQaSection = field(default_factory=JobQaSection)
    validation: JobValidationSection = field(default_factory=JobValidationSection)
    schema: JobSchemaSection = field(default_factory=JobSchemaSection)
    timezone: JobTimezone | None = None
    thresholds: JobThresholds = field(default_factory=JobThresholds)
    file: str | None = None
    reference_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": JOB_SCHEMA_VERSION,
            "name": self.name,
            "mode": self.mode,
            "knowledge_base_id": self.knowledge_base_id,
            "description": self.description,
            "reference": self.reference.to_dict(),
            "qa": self.qa.to_dict(),
            "validation": self.validation.to_dict(),
            "schema": self.schema.to_dict(),
            "thresholds": self.thresholds.to_dict(),
        }
        if self.max_rows is not None:
            payload["max_rows"] = self.max_rows
        if self.row_limit:
            payload["row_limit"] = self.row_limit
        if self.evaluated_columns is not None:
            payload["evaluated_columns"] = list(self.evaluated_columns)
        if self.timezone is not None:
            payload["timezone"] = self.timezone.to_dict()
        if self.file:
            payload["file"] = self.file
        if self.reference_file:
            payload["reference_file"] = self.reference_file
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> EmrQaJob:
        version = int(raw.get("schema_version") or 0)
        if version != JOB_SCHEMA_VERSION:
            raise ValueError(f"unsupported job schema_version: {version}")
        mode = str(raw.get("mode") or "reference")
        if mode not in ("reference", "qa", "validation", "schema"):
            raise ValueError(f"invalid job mode: {mode}")
        columns_raw = raw.get("evaluated_columns")
        evaluated: tuple[str, ...] | None = None
        if columns_raw is not None:
            evaluated = tuple(str(item) for item in columns_raw if str(item).strip())
        max_rows_raw = raw.get("max_rows")
        max_rows = int(max_rows_raw) if max_rows_raw is not None else None
        row_limit_raw = raw.get("row_limit")
        row_limit = str(row_limit_raw).strip() if row_limit_raw is not None else None
        if row_limit == "":
            row_limit = None
        return cls(
            name=str(raw.get("name") or "job").strip() or "job",
            mode=mode,  # type: ignore[arg-type]
            description=str(raw.get("description") or "").strip(),
            max_rows=max_rows,
            row_limit=row_limit,
            evaluated_columns=evaluated,
            knowledge_base_id=str(raw.get("knowledge_base_id") or "default").strip() or "default",
            reference=JobReferenceSection.from_dict(raw.get("reference")),
            qa=JobQaSection.from_dict(raw.get("qa")),
            validation=JobValidationSection.from_dict(raw.get("validation")),
            schema=JobSchemaSection.from_dict(raw.get("schema")),
            timezone=JobTimezone.from_dict(raw.get("timezone")),
            thresholds=JobThresholds.from_dict(raw.get("thresholds")),
            file=_optional_path(raw.get("file")),
            reference_file=_optional_path(raw.get("reference_file")),
        )

    def build_reference_config(self, reference_path: Path) -> ReferenceCompareConfig:
        return ReferenceCompareConfig(
            reference_path=reference_path,
            pairs=list(self.reference.pairs),
            duplicate_policy=self.reference.duplicate_policy,  # type: ignore[arg-type]
            enabled=True,
            left_catalog_bindings=dict(self.reference.left_catalog_bindings),
            catalog_knowledge_base_id=self.knowledge_base_id,
        )

    def validate_ready(self) -> None:
        if self.row_limit:
            from core.analysis_limits import parse_job_row_limit

            try:
                parse_job_row_limit(self.row_limit, 1000)
            except ValueError as exc:
                raise ValueError(f"invalid row_limit: {exc}") from exc
        if self.mode == "reference":
            config = self.build_reference_config(Path("placeholder.csv"))
            if not config.is_ready():
                raise ValueError("reference job missing join key or compare pairs")
        elif self.mode == "qa" and not self.qa.template_paths and not self.qa.catalogs:
            raise ValueError("qa job missing template_paths or catalogs")
        elif self.mode == "validation" and not self.validation.template_path:
            raise ValueError("validation job missing template_path")
        elif self.mode == "schema" and not self.schema.schema_id:
            raise ValueError("schema job missing schema_id")


    def effective_row_limit_tag(self) -> str | None:
        tag = (self.row_limit or "").strip()
        if tag:
            return tag
        if self.max_rows is not None:
            return str(self.max_rows)
        return None


def pair_to_dict(pair: ComparePairMapping) -> dict[str, Any]:
    return {
        "left_column": pair.left_column,
        "right_column": pair.right_column,
        "enabled": pair.enabled,
        "is_join_key": pair.is_join_key,
        "left_transform": pair.left_transform.to_dict(),
        "right_transform": pair.right_transform.to_dict(),
    }


def pair_from_dict(raw: dict[str, Any]) -> ComparePairMapping:
    return ComparePairMapping(
        left_column=str(raw.get("left_column") or "").strip(),
        right_column=str(raw.get("right_column") or "").strip(),
        enabled=bool(raw.get("enabled", True)),
        is_join_key=bool(raw.get("is_join_key", False)),
        left_transform=CellTransform.from_dict(raw.get("left_transform")),
        right_transform=CellTransform.from_dict(raw.get("right_transform")),
    )


def _optional_path(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _parse_qa_catalogs(raw: dict[str, Any]) -> tuple[JobQaCatalogSpec, ...]:
    specs: list[JobQaCatalogSpec] = []
    seen: set[str] = set()

    catalogs_raw = raw.get("catalogs") or []
    if isinstance(catalogs_raw, list):
        for item in catalogs_raw:
            if isinstance(item, str) and item.strip():
                catalog_id = item.strip()
            elif isinstance(item, dict):
                spec = JobQaCatalogSpec.from_dict(item)
                catalog_id = spec.catalog_id
            else:
                continue
            if not catalog_id or catalog_id in seen:
                continue
            seen.add(catalog_id)
            if isinstance(item, dict):
                specs.append(spec)
            else:
                specs.append(JobQaCatalogSpec(catalog_id=catalog_id))

    catalog_ids_raw = raw.get("catalog_ids") or []
    if isinstance(catalog_ids_raw, list):
        for item in catalog_ids_raw:
            catalog_id = str(item or "").strip()
            if not catalog_id or catalog_id in seen:
                continue
            seen.add(catalog_id)
            specs.append(JobQaCatalogSpec(catalog_id=catalog_id))

    return tuple(specs)


def load_job(path: Path) -> EmrQaJob:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("job file must be a JSON object")
    return EmrQaJob.from_dict(raw)


def save_job(path: Path, job: EmrQaJob) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(job.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def resolve_job_paths(
    job: EmrQaJob,
    *,
    file_path: Path | None,
    reference_path: Path | None,
) -> tuple[Path, Path | None]:
    resolved_file = file_path or (Path(job.file) if job.file else None)
    if resolved_file is None:
        raise ValueError("file required: pass --file or set file in job JSON")
    resolved_reference = reference_path
    if resolved_reference is None and job.reference_file:
        resolved_reference = Path(job.reference_file)
    if job.mode == "reference" and resolved_reference is None:
        raise ValueError("reference required: pass --reference or set reference_file in job JSON")
    return resolved_file.resolve(), (
        resolved_reference.resolve() if resolved_reference is not None else None
    )
