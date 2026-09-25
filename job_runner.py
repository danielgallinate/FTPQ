"""Runner headless — ejecuta EmrQaJob con el mismo motor que la UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from adapters.pandas_analyzer import DEFAULT_MAX_BYTES, analyze_tabular_file
from core.analysis_limits import DEFAULT_MAX_DISPLAY_ROWS, resolve_job_display_rows
from core.catalog_store import CatalogStore
from core.emr_qa_job import EmrQaJob, resolve_job_paths
from core.reference_compare import (
    expand_evaluated_columns_for_reference,
    load_reference_row_dicts,
    validate_reference_overlay,
)
from core.result import Err, Ok
from core.timezone_transform import TimezoneTransformConfig, apply_timezone_transform
from emrqa.catalog_to_template import build_validation_template_from_catalog
from emrqa.template_key_store import TemplateKeyStore
from emrqa.validation_engine import validate_minibase_overlay
from emrqa.validation_models import ValidationTemplate
from emrqa.validation_storage import load_validation_template, templates_dir
from core.schema_catalog_store import SchemaCatalogStore
from core.schema_validation import validate_schema_catalog
from shell.reference_metrics import ReferenceCompareReport, build_reference_compare_report
from shell.tabular_rows import dataset_to_row_dicts
from shell.qa_metrics import QaMetricsReport, build_qa_metrics
from shell.schema_metrics import SchemaValidationReport, build_schema_validation_report
from shell.validation_runner import QaHighlightMode, QaValidationResult, run_multi_template_validation


@dataclass
class EmrQaJobRunResult:
    ok: bool
    mode: str
    file_path: Path
    reference_path: Path | None = None
    rows_loaded: int = 0
    rows_total: int = 0
    display_truncated: bool = False
    messages: list[str] = field(default_factory=list)
    reference_report: ReferenceCompareReport | None = None
    qa_metrics_report: QaMetricsReport | None = None
    qa_validation_result: QaValidationResult | None = None
    schema_report: SchemaValidationReport | None = None
    overlay: object | None = None
    cell_ok_pct: float | None = None
    rows_without_match: int | None = None
    threshold_failures: list[str] = field(default_factory=list)
    no_data: bool = False

    @property
    def verdict(self) -> str:
        """PASS, FAIL o NO DATA. Cero filas (incremental) nunca es FAIL."""
        if self.no_data:
            return "NO DATA"
        if not self.ok:
            return "FAIL"
        return "PASS"

    def summary_lines(self) -> list[str]:
        lines = [
            f"job: {self.mode}",
            f"file: {self.file_path}",
            f"rows: {self.rows_loaded:,} loaded of {self.rows_total:,}",
        ]
        if self.display_truncated:
            tag = self.effective_row_limit_tag()
            if tag:
                lines.append(f"warning: extract truncated by row_limit ({tag})")
            else:
                lines.append("warning: file truncated to max_rows")
        if self.reference_path is not None:
            lines.append(f"reference: {self.reference_path}")
        if self.reference_report is not None:
            report = self.reference_report
            lines.extend(
                [
                    report.headline,
                    f"cells OK: {report.cells_ok:,} · NOK: {report.cells_nok:,} "
                    f"({report.cell_match_pct:.2f}%)",
                    f"rows without key: {report.rows_without_match:,}",
                ]
            )
        for message in self.messages[:20]:
            lines.append(f"alert: {message}")
        if len(self.messages) > 20:
            lines.append(f"alert: … and {len(self.messages) - 20} more")
        for failure in self.threshold_failures:
            lines.append(f"FAIL threshold: {failure}")
        lines.append(self.verdict)
        return lines

    def to_report_text(self) -> str:
        if self.qa_metrics_report is not None:
            body = self.qa_metrics_report.to_copyable_text()
            if self.threshold_failures:
                body += "\n\n" + "\n".join(
                    f"THRESHOLD FAIL: {item}" for item in self.threshold_failures
                )
            body += "\n\n" + self.verdict
            return body
        if self.schema_report is not None:
            body = self.schema_report.to_copyable_text()
            if self.threshold_failures:
                body += "\n\n" + "\n".join(
                    f"THRESHOLD FAIL: {item}" for item in self.threshold_failures
                )
            body += "\n\n" + self.verdict
            return body
        if self.reference_report is not None:
            body = self.reference_report.to_copyable_text()
            if self.threshold_failures:
                body += "\n\n" + "\n".join(
                    f"THRESHOLD FAIL: {item}" for item in self.threshold_failures
                )
            body += "\n\n" + self.verdict
            return body
        return "\n".join(self.summary_lines())


def _emr_root() -> Path:
    return Path(__file__).resolve().parent


def _resolve_template_path(job: EmrQaJob, relative: str) -> Path:
    path = Path(relative)
    if path.is_file():
        return path.resolve()
    candidate = templates_dir(job.knowledge_base_id) / relative
    if candidate.is_file():
        return candidate.resolve()
    candidate = _emr_root() / "knowledge_bases" / job.knowledge_base_id / "templates" / relative
    if candidate.is_file():
        return candidate.resolve()
    raise FileNotFoundError(f"template not found: {relative}")


_JOB_EXTRACT_PROBE_ROWS = 10_000_000


def _apply_row_limit(dataset, job: EmrQaJob):
    from core.analysis_types import TabularDataset

    limit = resolve_job_display_rows(
        row_limit=job.row_limit,
        max_rows=job.max_rows,
        total_rows=dataset.total_rows,
    )
    if limit >= len(dataset.rows):
        if limit >= dataset.total_rows and not dataset.display_truncated:
            return dataset
        return TabularDataset(
            local_path=dataset.local_path,
            columns=dataset.columns,
            rows=dataset.rows[:limit],
            total_rows=dataset.total_rows,
            display_truncated=limit < dataset.total_rows,
            sampled=dataset.sampled,
            estimated_total_rows=dataset.estimated_total_rows,
        )
    return TabularDataset(
        local_path=dataset.local_path,
        columns=dataset.columns,
        rows=dataset.rows[:limit],
        total_rows=dataset.total_rows,
        display_truncated=True,
        sampled=dataset.sampled,
        estimated_total_rows=dataset.estimated_total_rows,
    )


def _load_dataset(path: Path, job: EmrQaJob, *, max_bytes: int = DEFAULT_MAX_BYTES):
    result = analyze_tabular_file(
        path,
        max_display_rows=_JOB_EXTRACT_PROBE_ROWS,
        max_bytes=max_bytes,
    )
    if isinstance(result, Err):
        raise ValueError(str(result.error))
    if not isinstance(result, Ok):
        raise ValueError(f"unexpected analyze result for {path}")
    return _apply_row_limit(result.value, job)


def _evaluated_columns(job: EmrQaJob, column_names: list[str]) -> set[str]:
    if job.evaluated_columns is None:
        return set(column_names)
    allowed = set(column_names)
    return {name for name in job.evaluated_columns if name in allowed}


def _load_qa_templates(job: EmrQaJob, key_store: TemplateKeyStore | None) -> list[ValidationTemplate]:
    store = key_store or TemplateKeyStore()
    templates: list[ValidationTemplate] = []
    for relative in job.qa.template_paths:
        templates.append(load_validation_template(_resolve_template_path(job, relative), key_store=store))
    if job.qa.catalogs:
        catalog_store = CatalogStore(job.knowledge_base_id)
        for spec in job.qa.catalogs:
            table = catalog_store.load(spec.catalog_id)
            link_column = spec.link_column or None
            templates.append(
                build_validation_template_from_catalog(
                    table,
                    link_column=link_column,
                )
            )
    return templates


def _apply_thresholds(job: EmrQaJob, result: EmrQaJobRunResult) -> None:
    if result.no_data:
        return
    thresholds = job.thresholds
    if thresholds.min_cell_ok_pct is not None and result.cell_ok_pct is not None:
        if result.cell_ok_pct < thresholds.min_cell_ok_pct:
            result.threshold_failures.append(
                f"cell OK {result.cell_ok_pct:.2f}% < {thresholds.min_cell_ok_pct:.2f}%"
            )
    if thresholds.max_rows_without_match is not None and result.rows_without_match is not None:
        if result.rows_without_match > thresholds.max_rows_without_match:
            result.threshold_failures.append(
                "rows without key "
                f"{result.rows_without_match} > {thresholds.max_rows_without_match}"
            )


def run_emr_qa_job(
    job: EmrQaJob,
    *,
    file_path: Path | None = None,
    reference_path: Path | None = None,
    key_store: TemplateKeyStore | None = None,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> EmrQaJobRunResult:
    job.validate_ready()
    resolved_file, resolved_reference = resolve_job_paths(
        job,
        file_path=file_path,
        reference_path=reference_path,
    )
    dataset = _load_dataset(resolved_file, job, max_bytes=max_bytes)
    # La prueba de schema juzga el archivo; solo los modos comparativos convierten zonas.
    if job.timezone is not None and job.mode != "schema":
        tz_config = TimezoneTransformConfig(
            source_tz=job.timezone.source_tz,
            target_tz=job.timezone.target_tz,
            columns=frozenset(job.timezone.columns),
        )
        dataset = apply_timezone_transform(dataset, tz_config)

    column_names = [column.name for column in dataset.columns]
    evaluated = _evaluated_columns(job, column_names)
    name_to_index = {column.name: index for index, column in enumerate(dataset.columns)}
    rows = dataset_to_row_dicts(dataset)
    store = key_store or TemplateKeyStore()

    if job.mode == "reference":
        assert resolved_reference is not None
        config = job.build_reference_config(resolved_reference)
        evaluated = expand_evaluated_columns_for_reference(evaluated, config)
        _columns, reference_rows, total_ref = load_reference_row_dicts(
            resolved_reference,
            max_rows=_JOB_EXTRACT_PROBE_ROWS,
        )
        overlay = validate_reference_overlay(
            rows,
            reference_rows,
            config,
            evaluated_columns=evaluated,
            name_to_index=name_to_index,
        )
        report = build_reference_compare_report(
            file_name=resolved_file.name,
            config=config,
            result=overlay,
            rows_compared=len(rows),
            reference_rows_loaded=len(reference_rows),
            reference_rows_total=total_ref,
            name_to_index=name_to_index,
        )
        result = EmrQaJobRunResult(
            ok=True,
            mode=job.mode,
            file_path=resolved_file,
            reference_path=resolved_reference,
            rows_loaded=len(rows),
            rows_total=dataset.total_rows,
            display_truncated=dataset.display_truncated,
            messages=list(overlay.alerts or []),
            reference_report=report,
            cell_ok_pct=report.cell_match_pct,
            rows_without_match=report.rows_without_match,
            overlay=overlay,
        )
        _apply_thresholds(job, result)
        result.ok = (
            report.cells_nok == 0 and not result.threshold_failures
        )
        return result

    if job.mode == "validation":
        template_path = _resolve_template_path(job, job.validation.template_path)
        template = load_validation_template(template_path, key_store=store)
        overlay = validate_minibase_overlay(
            template,
            rows,
            evaluated_columns=evaluated,
            name_to_index=name_to_index,
        )
        return EmrQaJobRunResult(
            ok=len(overlay.failed_cells) == 0,
            mode=job.mode,
            file_path=resolved_file,
            rows_loaded=len(rows),
            rows_total=dataset.total_rows,
            display_truncated=dataset.display_truncated,
            messages=list(overlay.alerts or []),
            cell_ok_pct=overlay.percent,
            overlay=overlay,
        )

    if job.mode == "schema":
        catalog_store = SchemaCatalogStore(job.knowledge_base_id)
        catalog = catalog_store.load(job.schema.schema_id)
        overlay = validate_schema_catalog(
            catalog,
            rows,
            file_columns=column_names,
            name_to_index=name_to_index,
        )
        report = build_schema_validation_report(
            file_name=resolved_file.name,
            catalog=catalog,
            result=overlay,
            rows_total=len(rows),
            name_to_index=name_to_index,
        )
        result = EmrQaJobRunResult(
            ok=len(overlay.failed_cells) == 0 and not overlay.structural_errors,
            mode=job.mode,
            file_path=resolved_file,
            rows_loaded=len(rows),
            rows_total=dataset.total_rows,
            display_truncated=dataset.display_truncated,
            messages=list(overlay.alerts or []),
            cell_ok_pct=report.quality_pct,
            schema_report=report,
            overlay=overlay,
            no_data=report.no_data,
        )
        _apply_thresholds(job, result)
        if result.no_data:
            result.ok = True
            result.threshold_failures = []
        return result

    templates = _load_qa_templates(job, store)
    highlight = (
        QaHighlightMode.DISCREPANCY
        if job.qa.highlight_mode == "discrepancy"
        else QaHighlightMode.FAIL_ANY
    )
    qa_result = run_multi_template_validation(
        templates,
        rows,
        evaluated_columns=evaluated,
        name_to_index=name_to_index,
        highlight_mode=highlight,
    )
    visible_columns = [
        name for name in column_names if name in evaluated or job.evaluated_columns is None
    ]
    metrics = build_qa_metrics(
        file_name=resolved_file.name,
        visible_columns=visible_columns,
        rows=rows,
        templates=templates,
        template_overlays=qa_result.template_overlays,
        merged=qa_result.overlay,
        name_to_index=name_to_index,
        highlight_mode=highlight,
    )
    result = EmrQaJobRunResult(
        ok=metrics.nok_cells == 0 and metrics.conflict_cells == 0,
        mode=job.mode,
        file_path=resolved_file,
        rows_loaded=len(rows),
        rows_total=dataset.total_rows,
        display_truncated=dataset.display_truncated,
        messages=list(qa_result.overlay.alerts or []),
        cell_ok_pct=metrics.quality_pct,
        qa_metrics_report=metrics,
        qa_validation_result=qa_result,
        overlay=qa_result.overlay,
    )
    _apply_thresholds(job, result)
    if result.threshold_failures:
        result.ok = False
    return result
