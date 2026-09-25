#!/usr/bin/env python3
"""CLI batch — ejecuta jobs EMR QA contra CSVs emparejados por regex en schema/catalog."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_EMR_QA = Path(__file__).resolve().parent
if str(_EMR_QA) not in sys.path:
    sys.path.insert(0, str(_EMR_QA))

from core.analysis_types import collect_tabular_files  # noqa: E402
from core.batch_match import filename_matches, list_batch_job_configs  # noqa: E402
from run_job import EXIT_NO_DATA as _EXIT_NO_DATA  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run EMR QA jobs against CSVs matched by schema/catalog batch regex.",
    )
    parser.add_argument("data_dir", type=Path, help="Directory containing CSV files")
    parser.add_argument(
        "--jobs-dir",
        type=Path,
        default=_REPO_ROOT / "emr-qa/knowledge_bases/default/jobs",
        help="Jobs directory (default: emr-qa/knowledge_bases/default/jobs)",
    )
    parser.add_argument(
        "--lang",
        choices=("es", "en"),
        default="es",
        help="Report language per job (default: es; also accepts eng via shell wrapper)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search CSV files in subdirectories too",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List job ↔ file pairs without executing",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="One-line summary per job (passes --short to runner)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first FAIL or error",
    )
    return parser


def _messages(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "header": "=== EMR QA batch (*_col) ===",
            "data": "Data:",
            "jobs": "Jobs:",
            "lang": "Lang:",
            "skip_no_batch": "SKIP job (no batch config):",
            "skip_no_csv": "SKIP job (no file):",
            "skip_csv": "SKIP file (no matching job):",
            "error_regex": "ERROR job (invalid batch regex):",
            "summary": "=== Summary ===",
            "dry_run": "Dry-run: %s job ↔ CSV pair(s) listed",
            "run": "Run: %s | PASS: %s | FAIL/ERROR: %s | NO DATA: %s",
            "skipped": "Jobs without CSV or batch config: %s | CSV without job: %s",
            "fail_fast": "FAIL-FAST: stopping after error in",
            "no_csv": "ERROR: no tabular files in %s",
            "jobs_missing": "ERROR: jobs directory not found: %s",
            "runner_missing": "ERROR: runner not found: %s",
        }
    return {
        "header": "=== EMR QA batch (*_col) ===",
        "data": "Datos:",
        "jobs": "Jobs:",
        "lang": "Lang:",
        "skip_no_batch": "SKIP job (sin config batch):",
        "skip_no_csv": "SKIP job (sin archivo):",
        "skip_csv": "SKIP archivo (sin job):",
        "error_regex": "ERROR job (regex batch inválido):",
        "summary": "=== Resumen ===",
        "dry_run": "Dry-run: %s par(es) job ↔ CSV listados",
        "run": "Ejecutados: %s | PASS: %s | FAIL/ERROR: %s | SIN DATOS: %s",
        "skipped": "Jobs sin CSV o sin config batch: %s | CSV sin job: %s",
        "fail_fast": "FAIL-FAST: deteniendo tras error en",
        "no_csv": "ERROR: no hay archivos tabulares en %s",
        "jobs_missing": "ERROR: carpeta de jobs no encontrada: %s",
        "runner_missing": "ERROR: runner no encontrado: %s",
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    data_dir = args.data_dir.expanduser().resolve()
    jobs_dir = args.jobs_dir.expanduser().resolve()
    lang = args.lang
    msg = _messages(lang)
    runner = _REPO_ROOT / "scripts/run_emr_qa_job.sh"

    if not data_dir.is_dir():
        print(f"ERROR: directory not found: {data_dir}", file=sys.stderr)
        return 2
    if not jobs_dir.is_dir():
        print(msg["jobs_missing"] % jobs_dir, file=sys.stderr)
        return 2
    if not runner.is_file():
        print(msg["runner_missing"] % runner, file=sys.stderr)
        return 2

    csv_files = collect_tabular_files(data_dir, recursive=args.recursive)
    if not csv_files:
        print(msg["no_csv"] % data_dir, file=sys.stderr)
        return 2

    job_configs = list_batch_job_configs(jobs_dir)

    print(msg["header"])
    print(f"{msg['data']}  {data_dir}")
    print(f"{msg['jobs']}   {jobs_dir}")
    print(f"{msg['lang']}   {lang}")
    print()

    ran = 0
    passed = 0
    failed = 0
    no_data = 0
    skipped_jobs = 0
    matched_csvs: set[Path] = set()
    pending_skips: list[str] = []

    for config in job_configs:
        job_path = config.job_path
        if config.compile_error:
            pending_skips.append(
                f"{msg['error_regex']} {job_path.name} — {config.compile_error}"
            )
            skipped_jobs += 1
            continue
        if not config.batch_configured:
            pending_skips.append(f"{msg['skip_no_batch']} {job_path.name}")
            skipped_jobs += 1
            continue
        assert config.compiled is not None
        matches = [
            csv_path
            for csv_path in csv_files
            if filename_matches(config.compiled, csv_path.name)
        ]
        if not matches:
            pending_skips.append(f"{msg['skip_no_csv']} {job_path.name}")
            skipped_jobs += 1
            continue
        for csv_path in matches:
            matched_csvs.add(csv_path.resolve())
            print("-" * 20)
            print(f"JOB:  {job_path.name}")
            print(f"FILE: {csv_path}")
            ran += 1
            if args.dry_run:
                continue

            cmd = [str(runner), str(job_path), "--file", str(csv_path), "--lang", lang]
            if args.short:
                cmd.append("--short")

            result = subprocess.run(cmd, cwd=_REPO_ROOT)
            if result.returncode == 0:
                passed += 1
            elif result.returncode == _EXIT_NO_DATA:
                no_data += 1
            else:
                failed += 1
                if args.fail_fast:
                    print(f"{msg['fail_fast']} {job_path.name}", file=sys.stderr)
                    return result.returncode or 1

    skipped_csvs = 0
    for csv_path in csv_files:
        if csv_path.resolve() not in matched_csvs:
            pending_skips.append(f"{msg['skip_csv']} {csv_path.name}")
            skipped_csvs += 1

    for line in pending_skips:
        print("-" * 20)
        print(line)

    print()
    print(msg["summary"])
    if args.dry_run:
        print(msg["dry_run"] % ran)
    else:
        print(msg["run"] % (ran, passed, failed, no_data))
    print(msg["skipped"] % (skipped_jobs, skipped_csvs))

    if args.dry_run:
        return 0
    if ran == 0:
        return 2
    if failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
