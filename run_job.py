#!/usr/bin/env python3
"""CLI — ejecutar job EMR QA headless (mismo motor que Probar)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_EMR_QA = Path(__file__).resolve().parent
if str(_EMR_QA) not in sys.path:
    sys.path.insert(0, str(_EMR_QA))

from core.analysis_limits import CLI_PANDAS_MAX_BYTES  # noqa: E402
from core.emr_qa_job import load_job, save_job  # noqa: E402
from job_runner import run_emr_qa_job  # noqa: E402
from ui.i18n import init_locale  # noqa: E402

# Ni éxito ni fallo: el archivo no traía filas que evaluar.
EXIT_NO_DATA = 3


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an EMR QA job JSON (reference / qa / validation / schema).",
    )
    parser.add_argument("job", type=Path, help="Path to job.json")
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="File to validate (overrides job JSON)",
    )
    parser.add_argument(
        "--reference",
        "-r",
        type=Path,
        help="Reference file (overrides job JSON; required for reference mode)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write human-readable report to this path",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Write machine summary JSON to this path",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Automation: stdout only PASS or FAIL",
    )
    parser.add_argument(
        "--short",
        "-s",
        action="store_true",
        help="Automation: one-line summary (status + key metrics)",
    )
    parser.add_argument(
        "--lang",
        choices=("es", "en"),
        default="es",
        help="Report language for QA/Reference summary (default: es)",
    )
    return parser


def _column_metrics_to_dict(metrics) -> dict:
    return {
        "column": metrics.column,
        "applicable": metrics.applicable,
        "eligible": metrics.eligible,
        "judged": metrics.judged,
        "ok": metrics.ok,
        "nok": metrics.nok,
        "conflict": metrics.conflict,
        "unevaluated": metrics.unevaluated,
        "ok_pct": metrics.ok_pct,
    }


def _template_metrics_to_dict(metrics) -> dict:
    return {
        "name": metrics.name,
        "judged": metrics.judged,
        "ok": metrics.ok,
        "nok": metrics.nok,
        "conflict": metrics.conflict,
        "eligible_cells": metrics.eligible_cells,
        "unevaluated_cells": metrics.unevaluated_cells,
        "rows_key_complete": metrics.rows_key_complete,
        "rows_located": metrics.rows_located,
        "rows_partial": metrics.rows_partial,
        "rows_orphan": metrics.rows_orphan,
        "rows_key_conflict": metrics.rows_key_conflict,
        "coverage_pct": metrics.coverage_pct,
        "localization_pct": metrics.localization_pct,
    }


def _qa_metrics_to_json(report) -> dict:
    return {
        "file_name": report.file_name,
        "generated_at": report.generated_at,
        "template_names": list(report.template_names),
        "highlight_mode": report.highlight_mode,
        "eligible_cells": report.eligible_cells,
        "judged_cells": report.judged_cells,
        "ok_cells": report.ok_cells,
        "nok_cells": report.nok_cells,
        "conflict_cells": report.conflict_cells,
        "unevaluated_cells": report.unevaluated_cells,
        "coverage_pct": report.coverage_pct,
        "quality_pct": report.quality_pct,
        "localization_pct": report.localization_pct,
        "conflict_pct": report.conflict_pct,
        "rows_total": report.rows_total,
        "rows_key_complete": report.rows_key_complete,
        "rows_located": report.rows_located,
        "rows_partial": report.rows_partial,
        "rows_orphan": report.rows_orphan,
        "rows_key_conflict": report.rows_key_conflict,
        "by_column": {
            name: _column_metrics_to_dict(metrics)
            for name, metrics in sorted(report.by_column.items())
        },
        "by_template": {
            name: _template_metrics_to_dict(metrics)
            for name, metrics in sorted(report.by_template.items())
        },
    }


def _result_to_json(result) -> dict:
    payload = {
        "ok": result.ok,
        "verdict": result.verdict,
        "no_data": result.no_data,
        "mode": result.mode,
        "file": str(result.file_path),
        "reference": str(result.reference_path) if result.reference_path else None,
        "rows_loaded": result.rows_loaded,
        "rows_total": result.rows_total,
        "display_truncated": result.display_truncated,
        "cell_ok_pct": result.cell_ok_pct,
        "rows_without_match": result.rows_without_match,
        "threshold_failures": result.threshold_failures,
        "messages": result.messages[:50],
    }
    if result.reference_report is not None:
        report = result.reference_report
        payload["reference_report"] = {
            "cells_ok": report.cells_ok,
            "cells_nok": report.cells_nok,
            "cell_match_pct": report.cell_match_pct,
            "rows_without_match": report.rows_without_match,
            "headline": report.headline,
        }
    if result.qa_metrics_report is not None:
        payload["qa_metrics"] = _qa_metrics_to_json(result.qa_metrics_report)
    if result.schema_report is not None:
        report = result.schema_report
        payload["schema_report"] = {
            "schema_id": report.schema_id,
            "schema_name": report.schema_name,
            "strict": report.strict,
            "cells_ok": report.cells_ok,
            "cells_nok": report.cells_nok,
            "cells_unevaluated": report.cells_unevaluated,
            "coverage_pct": report.coverage_pct,
            "quality_pct": report.quality_pct,
            "structural_errors": report.structural_errors,
            "coverage_columns": report.coverage_columns,
            "headline": report.headline,
        }
    return payload


def _short_line(result) -> str:
    """Una línea — patrón habitual en CI (exit code + grep)."""
    parts = [result.verdict, f"mode={result.mode}"]
    if result.qa_metrics_report is not None:
        report = result.qa_metrics_report
        parts.extend(
            [
                f"quality={report.quality_pct:.2f}",
                f"coverage={report.coverage_pct:.2f}",
                f"nok={report.nok_cells}",
                f"judged={report.judged_cells}",
            ]
        )
    elif result.reference_report is not None:
        report = result.reference_report
        parts.extend(
            [
                f"match={report.cell_match_pct:.2f}",
                f"cells_nok={report.cells_nok}",
            ]
        )
    elif result.schema_report is not None:
        report = result.schema_report
        parts.extend(
            [
                f"quality={report.quality_pct:.2f}",
                f"coverage={report.coverage_pct:.2f}",
                f"nok={report.cells_nok}",
            ]
        )
    elif result.cell_ok_pct is not None:
        parts.append(f"ok_pct={result.cell_ok_pct:.2f}")
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    init_locale(args.lang)
    job_path = args.job.resolve()
    job = load_job(job_path)
    try:
        result = run_emr_qa_job(
            job,
            file_path=args.file.resolve() if args.file else None,
            reference_path=args.reference.resolve() if args.reference else None,
            max_bytes=CLI_PANDAS_MAX_BYTES,
        )
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report_text = result.to_report_text()
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_text + "\n", encoding="utf-8")
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(_result_to_json(result), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.report is None:
        if args.quiet:
            print(result.verdict)
        elif args.short:
            print(_short_line(result))
        else:
            print(report_text)
    if result.no_data:
        return EXIT_NO_DATA
    if not result.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
