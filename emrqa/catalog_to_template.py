"""Catálogo local → template de validación QA (minibase en runtime)."""
from __future__ import annotations

from core.catalog_types import CatalogTable, CatalogValidationError
from emrqa.validation_models import (
    DedupPolicy,
    EvaluationDefaults,
    MinibaseRecord,
    MinibaseSection,
    RecordSource,
    RecordValidationSnapshot,
    RowField,
    TemplateHeader,
    TemplateKey,
    TemplateMeta,
    ValidationTemplate,
    _utc_now_iso,
    compute_key_fingerprint,
    new_id,
    normalize_cell_value,
)


def build_validation_template_from_catalog(
    table: CatalogTable,
    *,
    link_column: str | None = None,
) -> ValidationTemplate:
    """Construye un template efímero cuyo minibase refleja el catálogo guardado."""
    meta = table.meta
    columns = list(meta.columns)
    if not columns:
        raise CatalogValidationError(f"catalog {meta.catalog_id!r} has no columns")
    key_column = meta.key_column.strip()
    if not key_column or key_column not in columns:
        raise CatalogValidationError(f"catalog {meta.catalog_id!r} missing key column")

    file_key_column = (link_column or key_column).strip()
    if not file_key_column:
        raise CatalogValidationError(f"catalog {meta.catalog_id!r} missing link column")

    fields: list[RowField] = []
    for column in columns:
        file_column = file_key_column if column == key_column else column
        fields.append(
            RowField(
                field_id=new_id("fld_"),
                label=column,
                column=file_column,
                required=False,
            )
        )

    key_field = next(field for field in fields if field.label == key_column)
    key = TemplateKey(
        key_id=new_id("key_"),
        label=f"PK {key_column}",
        field_ids=[key_field.field_id],
        primary=True,
    )

    evaluation_columns = sorted({field.column for field in fields})
    now = _utc_now_iso()
    template = ValidationTemplate(
        meta=TemplateMeta(
            schema_version="2.0",
            template_id=f"catalog_{meta.catalog_id}",
            knowledge_base_id="default",
            created_at=now,
            updated_at=now,
        ),
        header=TemplateHeader(
            name=meta.name or meta.catalog_id,
            description=f"catalog:{meta.catalog_id}",
            fields=fields,
            keys=[key],
            evaluation=EvaluationDefaults(columns=evaluation_columns),
        ),
        minibase=MinibaseSection(
            dedup=DedupPolicy(key_id=key.key_id),
            records=[],
        ),
    )

    source = RecordSource(
        file_name=meta.source_file or meta.catalog_id,
        file_path=meta.source_file,
    )
    for row in table.rows:
        row_payload = {column: normalize_cell_value(row.get(column, "")) for column in columns}
        fingerprint = compute_key_fingerprint([row_payload[key_column]])
        values = {
            field.field_id: row_payload[field.label]
            for field in fields
        }
        template.minibase.records.append(
            MinibaseRecord(
                record_id=new_id("rec_"),
                key_fingerprint=fingerprint,
                key_id=key.key_id,
                saved_at=now,
                values=values,
                source=source,
                validation=RecordValidationSnapshot(),
            )
        )

    if not template.minibase.records:
        raise CatalogValidationError(f"catalog {meta.catalog_id!r} has no rows")

    return template
