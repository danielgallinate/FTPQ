"""Motor de validación — modo Probar (reglas v2.0 sobre grid tabular)."""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from shell.validation_progress import RowProgressCallback, emit_row_progress

from .minibase_lookup import MinibaseLookup
from .validation_models import (
    KEY_VALUE_SEPARATOR,
    RowField,
    TemplateKey,
    ValidationRule,
    ValidationTemplate,
    normalize_cell_value,
)


@dataclass(frozen=True)
class RuleCheckResult:
    rule_id: str
    passed: bool
    message: str


@dataclass
class CellValidationState:
    row_index: int
    field_id: str
    column: str
    evaluated: bool
    passed: bool
    failed_rule_ids: list[str] = field(default_factory=list)

    @property
    def is_green(self) -> bool:
        return self.evaluated and self.passed


@dataclass
class KeyValidationState:
    row_index: int
    key_id: str
    label: str
    passed: bool
    failed_rule_ids: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


@dataclass
class ValidationSummary:
    total_cells: int
    passed_cells: int
    percent: float
    total_rows: int
    rows_with_key_errors: int
    alerts: list[str] = field(default_factory=list)

    @property
    def has_key_errors(self) -> bool:
        return self.rows_with_key_errors > 0


@dataclass
class ValidationRunResult:
    cells: list[CellValidationState]
    keys: list[KeyValidationState]
    summary: ValidationSummary

    def cell_state(self, row_index: int, column: str) -> CellValidationState | None:
        for item in self.cells:
            if item.row_index == row_index and item.column == column:
                return item
        return None

    def is_green(self, row_index: int, column: str) -> bool:
        state = self.cell_state(row_index, column)
        return state.is_green if state else False

    def failed_keys(self) -> list[KeyValidationState]:
        return [item for item in self.keys if not item.passed]

    def evaluated_columns(self) -> set[str]:
        return {item.column for item in self.cells if item.evaluated}


@dataclass
class _FileContext:
    rows: list[dict[str, Any]]
    key_counts: dict[str, dict[str, int]]
    minibase_fingerprints: set[str]

    @classmethod
    def build(cls, template: ValidationTemplate, rows: list[dict[str, Any]]) -> _FileContext:
        key_counts: dict[str, dict[str, int]] = {}
        for template_key in template.header.keys:
            counts: dict[str, int] = {}
            for row in rows:
                fingerprint = template.fingerprint_for_row(template_key, row)
                counts[fingerprint] = counts.get(fingerprint, 0) + 1
            key_counts[template_key.key_id] = counts
        return cls(
            rows=rows,
            key_counts=key_counts,
            minibase_fingerprints=template.minibase.fingerprints(),
        )


def _default_message(rule: ValidationRule, fallback: str) -> str:
    return rule.message.strip() or fallback


def _field_value(row_field: RowField, row: dict[str, Any]) -> str:
    return normalize_cell_value(row.get(row_field.column))


def _evaluate_not_empty(value: str) -> bool:
    return value != ""


def _evaluate_regex(value: str, pattern: str) -> bool:
    if not pattern:
        return True
    return re.search(pattern, value) is not None


def _evaluate_in_list(value: str, allowed: list[Any]) -> bool:
    normalized = {normalize_cell_value(item) for item in allowed}
    return value in normalized


def _key_in_scope(template_key: TemplateKey, template: ValidationTemplate, evaluated: set[str]) -> bool:
    for field_id in template_key.field_ids:
        row_field = template.header.field_by_id(field_id)
        if not row_field or row_field.column not in evaluated:
            return False
    return True


def _field_in_scope(row_field: RowField, evaluated: set[str]) -> bool:
    return row_field.column in evaluated


def _rules_for_field(rules: list[ValidationRule], field_id: str) -> list[ValidationRule]:
    return [
        rule
        for rule in rules
        if rule.target_type == "field" and rule.target_id == field_id
    ]


def _rules_for_key(rules: list[ValidationRule], key_id: str) -> list[ValidationRule]:
    return [
        rule
        for rule in rules
        if rule.target_type == "key" and rule.target_id == key_id
    ]


def _evaluate_field_rule(
    rule: ValidationRule,
    row_field: RowField,
    row: dict[str, Any],
) -> RuleCheckResult:
    value = _field_value(row_field, row)
    fallback = f"Campo {row_field.label}"
    if rule.type == "not_empty":
        passed = _evaluate_not_empty(value)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: valor vacío"))
    if rule.type == "regex":
        pattern = str(rule.params.get("pattern") or "")
        passed = _evaluate_regex(value, pattern)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: no coincide patrón"))
    if rule.type == "in_list":
        values_raw = rule.params.get("values") or []
        allowed = list(values_raw) if isinstance(values_raw, list) else []
        passed = _evaluate_in_list(value, allowed)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: valor no permitido"))
    return RuleCheckResult(rule.rule_id, True, "")


def _evaluate_key_rule(
    rule: ValidationRule,
    template_key: TemplateKey,
    template: ValidationTemplate,
    row: dict[str, Any],
    file_ctx: _FileContext,
) -> RuleCheckResult:
    fallback = f"Llave {template_key.label}"
    fingerprint = template.fingerprint_for_row(template_key, row)

    if rule.type == "unique_in_file":
        count = file_ctx.key_counts.get(template_key.key_id, {}).get(fingerprint, 0)
        passed = count == 1
        return RuleCheckResult(
            rule.rule_id,
            passed,
            _default_message(rule, f"{fallback}: duplicada en archivo ({count} veces)"),
        )
    if rule.type == "exists_in_minibase":
        passed = fingerprint in file_ctx.minibase_fingerprints
        return RuleCheckResult(
            rule.rule_id,
            passed,
            _default_message(rule, f"{fallback}: no existe en minibase"),
        )
    if rule.type == "not_in_minibase":
        passed = fingerprint not in file_ctx.minibase_fingerprints
        return RuleCheckResult(
            rule.rule_id,
            passed,
            _default_message(rule, f"{fallback}: ya existe en minibase"),
        )
    if rule.type == "not_empty":
        values = template.key_values_from_row(template_key, row)
        passed = all(_evaluate_not_empty(value) for value in values)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: componente vacío"))
    if rule.type == "regex":
        pattern = str(rule.params.get("pattern") or "")
        values = template.key_values_from_row(template_key, row)
        joined = KEY_VALUE_SEPARATOR.join(values)
        passed = _evaluate_regex(joined, pattern)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: patrón no coincide"))
    if rule.type == "in_list":
        values_raw = rule.params.get("values") or []
        allowed = list(values_raw) if isinstance(values_raw, list) else []
        values = template.key_values_from_row(template_key, row)
        passed = all(value in {normalize_cell_value(item) for item in allowed} for value in values)
        return RuleCheckResult(rule.rule_id, passed, _default_message(rule, f"{fallback}: valor no permitido"))
    return RuleCheckResult(rule.rule_id, True, "")


def _resolve_evaluated_columns(
    template: ValidationTemplate,
    evaluated_columns: set[str] | None,
    file_columns: set[str],
) -> set[str]:
    if evaluated_columns is not None:
        return {column for column in evaluated_columns if column in file_columns}
    defaults = set(template.header.evaluation.columns)
    if defaults:
        return {column for column in defaults if column in file_columns}
    return {row_field.column for row_field in template.header.fields if row_field.column in file_columns}


def validate_rows(
    template: ValidationTemplate,
    rows: list[dict[str, Any]],
    *,
    evaluated_columns: set[str] | None = None,
    on_progress: RowProgressCallback | None = None,
) -> ValidationRunResult:
    """Evalúa reglas del template sobre filas del archivo abierto."""
    file_columns = set()
    for row in rows:
        file_columns.update(str(key) for key in row.keys())

    evaluated = _resolve_evaluated_columns(template, evaluated_columns, file_columns)
    rules = template.header.rules
    file_ctx = _FileContext.build(template, rows)

    cells: list[CellValidationState] = []
    keys: list[KeyValidationState] = []
    row_key_failed: set[int] = set()
    alerts: list[str] = []

    key_pass_by_row: dict[tuple[int, str], bool] = {}

    total_rows = len(rows)

    for row_index, row in enumerate(rows):
        for template_key in template.header.keys:
            if not _key_in_scope(template_key, template, evaluated):
                continue
            key_rules = _rules_for_key(rules, template_key.key_id)
            failed_ids: list[str] = []
            messages: list[str] = []
            for rule in key_rules:
                result = _evaluate_key_rule(rule, template_key, template, row, file_ctx)
                if not result.passed:
                    failed_ids.append(result.rule_id)
                    if result.message:
                        messages.append(result.message)
            if template.minibase.records:
                dedup_key = template.dedup_key()
                if dedup_key is not None and dedup_key.key_id == template_key.key_id:
                    fingerprint = template.fingerprint_for_row(template_key, row)
                    if fingerprint in file_ctx.minibase_fingerprints:
                        if not failed_ids:
                            passed = True
                    else:
                        failed_ids.append("__minibase__")
                        messages.append(
                            f"Tupla no encontrada en minibase ({template_key.label})"
                        )
            passed = not failed_ids
            key_pass_by_row[(row_index, template_key.key_id)] = passed
            keys.append(
                KeyValidationState(
                    row_index=row_index,
                    key_id=template_key.key_id,
                    label=template_key.label,
                    passed=passed,
                    failed_rule_ids=failed_ids,
                    messages=messages,
                )
            )
            if not passed:
                row_key_failed.add(row_index)
                for message in messages:
                    alerts.append(f"Fila {row_index + 1} · {message}")

    for row_index, row in enumerate(rows):
        for row_field in template.header.fields:
            in_scope = _field_in_scope(row_field, evaluated)
            if not in_scope:
                cells.append(
                    CellValidationState(
                        row_index=row_index,
                        field_id=row_field.field_id,
                        column=row_field.column,
                        evaluated=False,
                        passed=False,
                    )
                )
                continue

            failed_ids: list[str] = []
            for rule in _rules_for_field(rules, row_field.field_id):
                result = _evaluate_field_rule(rule, row_field, row)
                if not result.passed:
                    failed_ids.append(result.rule_id)
                    if result.message:
                        alerts.append(f"Fila {row_index + 1} · {result.message}")

            if row_field.required and not _evaluate_not_empty(_field_value(row_field, row)):
                failed_ids.append("__required__")

            keys_ok = True
            for template_key in template.header.keys:
                if row_field.field_id not in template_key.field_ids:
                    continue
                if not _key_in_scope(template_key, template, evaluated):
                    continue
                if not key_pass_by_row.get((row_index, template_key.key_id), True):
                    keys_ok = False

            passed = not failed_ids and keys_ok
            cells.append(
                CellValidationState(
                    row_index=row_index,
                    field_id=row_field.field_id,
                    column=row_field.column,
                    evaluated=True,
                    passed=passed,
                    failed_rule_ids=failed_ids,
                )
            )
        emit_row_progress(on_progress, row_index + 1, total_rows)

    evaluated_cells = [item for item in cells if item.evaluated]
    passed_cells = [item for item in evaluated_cells if item.passed]
    total = len(evaluated_cells)
    passed_count = len(passed_cells)
    percent = (100.0 * passed_count / total) if total else 100.0

    summary = ValidationSummary(
        total_cells=total,
        passed_cells=passed_count,
        percent=round(percent, 2),
        total_rows=len(rows),
        rows_with_key_errors=len(row_key_failed),
        alerts=alerts,
    )
    return ValidationRunResult(cells=cells, keys=keys, summary=summary)


@dataclass
class MinibaseOverlayResult:
    passed_cells: set[tuple[int, int]] = field(default_factory=set)
    failed_cells: set[tuple[int, int]] = field(default_factory=set)
    gray_cells: set[tuple[int, int]] = field(default_factory=set)
    percent: float = 0.0
    passed_count: int = 0
    total_count: int = 0
    alerts: list[str] = field(default_factory=list)


def _find_associated_record(
    template: ValidationTemplate,
    dedup_key: TemplateKey,
    row: dict[str, Any],
    row_fingerprint: str,
    lookup: MinibaseLookup,
):
    """Registro con coincidencia parcial de llave (resto de campos se comparan)."""
    best_record = None
    best_partial = 0
    for record in lookup.candidate_records(template, dedup_key, row):
        if row_fingerprint == record.key_fingerprint:
            continue
        partial = 0
        has_key_mismatch = False
        for field_id in dedup_key.field_ids:
            field = template.header.field_by_id(field_id)
            if field is None:
                continue
            row_value = normalize_cell_value(row.get(field.column))
            saved = record.values.get(field_id, "")
            if row_value and saved and row_value == saved:
                partial += 1
            elif row_value != saved:
                has_key_mismatch = True
        if partial > 0 and has_key_mismatch and partial > best_partial:
            best_partial = partial
            best_record = record
    return best_record


def _partial_key_conflict(
    template: ValidationTemplate,
    dedup_key: TemplateKey,
    row: dict[str, Any],
    row_fingerprint: str,
    record,
) -> bool:
    if row_fingerprint == record.key_fingerprint:
        return False
    matches = 0
    for field_id in dedup_key.field_ids:
        field = template.header.field_by_id(field_id)
        if field is None:
            continue
        row_value = normalize_cell_value(row.get(field.column))
        saved = record.values.get(field_id, "")
        if row_value and saved and row_value == saved:
            matches += 1
    return matches > 0


def _coords_for_field_ids(
    row_index: int,
    template: ValidationTemplate,
    field_ids: list[str],
    evaluated_columns: set[str],
    name_to_index: dict[str, int],
) -> set[tuple[int, int]]:
    coords: set[tuple[int, int]] = set()
    for field_id in field_ids:
        field = template.header.field_by_id(field_id)
        if field is None or field.column not in evaluated_columns:
            continue
        col_index = name_to_index.get(field.column)
        if col_index is not None:
            coords.add((row_index, col_index))
    return coords


def _apply_cell_match_overlay(
    *,
    row_index: int,
    row: dict[str, Any],
    record,
    template: ValidationTemplate,
    evaluated_columns: set[str],
    name_to_index: dict[str, int],
    passed: set[tuple[int, int]],
    failed: set[tuple[int, int]],
    alerts: list[str],
    dedup_key: TemplateKey,
    located_by_fingerprint: bool = True,
) -> None:
    """Llave = localizar fila; campos no-llave = comparar valor (verde/rojo)."""
    key_field_ids = set(dedup_key.field_ids)
    mismatches: list[str] = []
    for field in template.header.fields:
        if field.column not in evaluated_columns:
            continue
        col_index = name_to_index.get(field.column)
        if col_index is None:
            continue
        coord = (row_index, col_index)
        row_value = normalize_cell_value(row.get(field.column))
        saved = record.values.get(field.field_id, "")
        if field.field_id in key_field_ids:
            if located_by_fingerprint:
                passed.add(coord)
                failed.discard(coord)
                continue
        if row_value == saved:
            passed.add(coord)
            failed.discard(coord)
        else:
            failed.add(coord)
            passed.discard(coord)
            if field.field_id not in key_field_ids:
                mismatches.append(field.label or field.column)
            else:
                mismatches.append(f"{field.label or field.column} (llave)")
    if mismatches:
        alerts.append(
            f"Fila {row_index + 1} · valores distintos a la minibase "
            f"({dedup_key.label}): {', '.join(mismatches)}"
        )


def validate_minibase_overlay(
    template: ValidationTemplate,
    rows: list[dict[str, Any]],
    *,
    evaluated_columns: set[str],
    name_to_index: dict[str, int],
    on_progress: RowProgressCallback | None = None,
) -> MinibaseOverlayResult:
    """Verde = llave localizada + valor comparado OK; rojo = valor comparado falla o conflicto.

    La llave identifica el registro; al menos un campo no-llave se compara contra minibase.
    """
    dedup_key = template.dedup_key()
    if dedup_key is None or not template.minibase.records:
        return MinibaseOverlayResult()

    lookup = MinibaseLookup.from_template(template)
    passed: set[tuple[int, int]] = set()
    failed: set[tuple[int, int]] = set()
    gray: set[tuple[int, int]] = set()
    alerts: list[str] = []
    total_rows = len(rows)

    for row_index, row in enumerate(rows):
        key_coords = _coords_for_field_ids(
            row_index,
            template,
            dedup_key.field_ids,
            evaluated_columns,
            name_to_index,
        )
        if not key_coords:
            continue
        fingerprint = template.fingerprint_for_row(dedup_key, row)
        record = lookup.by_fingerprint.get(fingerprint)
        if record is not None:
            _apply_cell_match_overlay(
                row_index=row_index,
                row=row,
                record=record,
                template=template,
                evaluated_columns=evaluated_columns,
                name_to_index=name_to_index,
                passed=passed,
                failed=failed,
                alerts=alerts,
                dedup_key=dedup_key,
                located_by_fingerprint=True,
            )
            continue
        associated = _find_associated_record(
            template, dedup_key, row, fingerprint, lookup
        )
        if associated is not None:
            _apply_cell_match_overlay(
                row_index=row_index,
                row=row,
                record=associated,
                template=template,
                evaluated_columns=evaluated_columns,
                name_to_index=name_to_index,
                passed=passed,
                failed=failed,
                alerts=alerts,
                dedup_key=dedup_key,
                located_by_fingerprint=False,
            )
            continue
        candidates = lookup.candidate_records(template, dedup_key, row)
        conflict = any(
            _partial_key_conflict(template, dedup_key, row, fingerprint, mb_record)
            for mb_record in candidates
        )
        if conflict:
            failed.update(key_coords)
            for coord in key_coords:
                passed.discard(coord)
            alerts.append(
                f"Fila {row_index + 1} · conflicto de llave compuesta ({dedup_key.label})"
            )
        emit_row_progress(on_progress, row_index + 1, total_rows)

    total = len(passed) + len(failed)
    percent = (100.0 * len(passed) / total) if total else 0.0
    return MinibaseOverlayResult(
        passed_cells=passed,
        failed_cells=failed,
        gray_cells=gray,
        percent=round(percent, 2),
        passed_count=len(passed),
        total_count=total,
        alerts=alerts,
    )
