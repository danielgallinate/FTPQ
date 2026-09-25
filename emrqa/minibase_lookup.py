"""Índices de minibase — evita escaneo O(filas × registros) en QA."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .validation_models import TemplateKey, ValidationTemplate, normalize_cell_value


@dataclass
class MinibaseLookup:
    by_fingerprint: dict[str, Any]
    records: list[Any]
    candidates_by_field: dict[str, dict[str, list[Any]]] = field(default_factory=dict)

    @classmethod
    def from_template(cls, template: ValidationTemplate) -> MinibaseLookup:
        records = list(template.minibase.records)
        by_fingerprint = {record.key_fingerprint: record for record in records}
        candidates_by_field: dict[str, dict[str, list[Any]]] = {}
        dedup_key = template.dedup_key()
        if dedup_key is not None:
            for record in records:
                for field_id in dedup_key.field_ids:
                    field = template.header.field_by_id(field_id)
                    if field is None:
                        continue
                    value = normalize_cell_value(record.values.get(field_id, ""))
                    if not value:
                        continue
                    candidates_by_field.setdefault(field_id, {}).setdefault(value, []).append(
                        record
                    )
        return cls(
            by_fingerprint=by_fingerprint,
            records=records,
            candidates_by_field=candidates_by_field,
        )

    def candidate_records(
        self,
        template: ValidationTemplate,
        dedup_key: TemplateKey,
        row: dict[str, Any],
    ) -> list[Any]:
        seen: set[str] = set()
        candidates: list[Any] = []
        for field_id in dedup_key.field_ids:
            field = template.header.field_by_id(field_id)
            if field is None:
                continue
            row_value = normalize_cell_value(row.get(field.column))
            if not row_value:
                continue
            for record in self.candidates_by_field.get(field_id, {}).get(row_value, []):
                token = record.record_id
                if token in seen:
                    continue
                seen.add(token)
                candidates.append(record)
        return candidates
