"""Emparejamiento batch job ↔ CSV vía regex en schema/catalog referenciados por el job."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from core.analysis_types import BATCH_TABULAR_EXTENSION_SUFFIX
from core.batch_match_types import BatchMatchSpec
from core.catalog_store import _meta_path
from core.catalog_types import CatalogMeta
from core.emr_qa_job import EmrQaJob, load_job
from core.schema_catalog_store import SchemaCatalogStore
from core.schema_catalog_types import SchemaCatalog


EXAMPLE_FILENAME_PATTERN = f"(?i).*_PDE_Clinic_.*{BATCH_TABULAR_EXTENSION_SUFFIX}"

_TRAILING_STAMP = re.compile(r"(?:[_-]\d+)+$")


def suggest_filename_pattern(filename: str) -> str:
    """Patrón para un extracto a partir de un nombre de archivo de muestra.

    Descarta la extensión y los sellos numéricos finales (fecha y hora del
    volcado), y deja fuera el primer segmento cuando actúa como prefijo de
    entorno, de modo que el patrón sirva para cualquier corrida del extracto.
    """
    stem = Path(filename).stem.strip()
    core = _TRAILING_STAMP.sub("", stem).strip("_-")
    if not core or core.isdigit():
        return EXAMPLE_FILENAME_PATTERN
    segments = core.split("_")
    if len(segments) >= 3:
        core = "_".join(segments[1:])
    return f"(?i).*{re.escape(core)}_.*{BATCH_TABULAR_EXTENSION_SUFFIX}"


class BatchMatchCompileError(Exception):
    def __init__(self, source: str, pattern: str, message: str) -> None:
        self.source = source
        self.pattern = pattern
        self.message = message
        super().__init__(f"{source}: invalid regex {pattern!r}: {message}")


@dataclass(frozen=True)
class CompiledBatchMatch:
    includes: tuple[re.Pattern[str], ...]
    excludes: tuple[re.Pattern[str], ...]


@dataclass
class BatchJobConfig:
    job_path: Path
    job: EmrQaJob
    rules: BatchMatchSpec | None = None
    compiled: CompiledBatchMatch | None = None
    compile_error: str | None = None

    @property
    def batch_configured(self) -> bool:
        return self.rules is not None and self.rules.is_configured()

    @property
    def runnable(self) -> bool:
        return self.batch_configured and self.compiled is not None and not self.compile_error


@dataclass
class BatchPlan:
    pairs: list[tuple[Path, Path]] = field(default_factory=list)
    skipped_jobs_no_batch: list[Path] = field(default_factory=list)
    skipped_jobs_no_csv: list[Path] = field(default_factory=list)
    skipped_jobs_error: list[tuple[Path, str]] = field(default_factory=list)
    unmatched_csvs: list[Path] = field(default_factory=list)


def compile_batch_match(spec: BatchMatchSpec, source: str) -> CompiledBatchMatch:
    includes: list[re.Pattern[str]] = []
    excludes: list[re.Pattern[str]] = []
    for pattern in spec.filename_patterns:
        try:
            includes.append(re.compile(pattern))
        except re.error as exc:
            raise BatchMatchCompileError(source, pattern, str(exc)) from exc
    for pattern in spec.filename_excludes:
        try:
            excludes.append(re.compile(pattern))
        except re.error as exc:
            raise BatchMatchCompileError(source, pattern, str(exc)) from exc
    return CompiledBatchMatch(includes=tuple(includes), excludes=tuple(excludes))


def filename_matches(compiled: CompiledBatchMatch, basename: str) -> bool:
    if not compiled.includes:
        return False
    if not any(pattern.search(basename) for pattern in compiled.includes):
        return False
    if any(pattern.search(basename) for pattern in compiled.excludes):
        return False
    return True


def _load_catalog_meta(knowledge_base_id: str, catalog_id: str) -> CatalogMeta | None:
    meta_path = _meta_path(knowledge_base_id, catalog_id)
    if not meta_path.is_file():
        return None
    raw = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return CatalogMeta.from_dict(raw)


def batch_match_from_schema(catalog: SchemaCatalog) -> BatchMatchSpec | None:
    if catalog.batch_match is None or not catalog.batch_match.is_configured():
        return None
    return catalog.batch_match


def resolve_job_batch_match(job: EmrQaJob) -> BatchMatchSpec | None:
    kb_id = job.knowledge_base_id or "default"
    if job.mode == "schema":
        schema_id = job.schema.schema_id.strip()
        if not schema_id:
            return None
        catalog = SchemaCatalogStore(kb_id).load(schema_id)
        return batch_match_from_schema(catalog)

    if job.mode == "qa":
        merged: BatchMatchSpec | None = None
        for spec in job.qa.catalogs:
            catalog_id = spec.catalog_id.strip()
            if not catalog_id:
                continue
            meta = _load_catalog_meta(kb_id, catalog_id)
            if meta is None or meta.batch_match is None or not meta.batch_match.is_configured():
                continue
            merged = (
                meta.batch_match
                if merged is None
                else merged.merge(meta.batch_match)
            )
        return merged

    return None


def load_batch_job_config(job_path: Path) -> BatchJobConfig:
    job = load_job(job_path)
    rules = resolve_job_batch_match(job)
    config = BatchJobConfig(job_path=job_path.resolve(), job=job, rules=rules)
    if not config.batch_configured:
        return config
    try:
        config.compiled = compile_batch_match(rules, str(job_path))
    except BatchMatchCompileError as exc:
        config.compile_error = str(exc)
    return config


def list_batch_job_configs(jobs_dir: Path) -> list[BatchJobConfig]:
    configs: list[BatchJobConfig] = []
    for job_path in sorted(jobs_dir.glob("*.job.json"), key=lambda item: item.name.casefold()):
        configs.append(load_batch_job_config(job_path))
    return configs


def build_batch_plan(
    job_configs: list[BatchJobConfig],
    csv_paths: list[Path],
) -> BatchPlan:
    plan = BatchPlan()
    matched_csvs: set[Path] = set()

    for config in job_configs:
        if config.compile_error:
            plan.skipped_jobs_error.append((config.job_path, config.compile_error))
            continue
        if not config.batch_configured:
            plan.skipped_jobs_no_batch.append(config.job_path)
            continue
        assert config.compiled is not None
        matches = [
            csv_path
            for csv_path in csv_paths
            if filename_matches(config.compiled, csv_path.name)
        ]
        if not matches:
            plan.skipped_jobs_no_csv.append(config.job_path)
            continue
        for csv_path in matches:
            plan.pairs.append((config.job_path, csv_path))
            matched_csvs.add(csv_path.resolve())

    for csv_path in csv_paths:
        if csv_path.resolve() not in matched_csvs:
            plan.unmatched_csvs.append(csv_path)

    return plan
