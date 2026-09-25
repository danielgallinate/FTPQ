"""Comparación tabular con pandas — multiset, cabecera idéntica."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from adapters.pandas_analyzer import _read_dataframe
from core.compare_policy import CompareAbortError, preflight_compare_paths
from core.compare_types import CompareExample, CompareFileSide, CompareResult
from core.result import Err, Ok, Result
from core.visualization_policy import TabularPolicyProfile

MAX_EXAMPLES = 5


def compare_tabular_files(
    path_a: Path,
    path_b: Path,
    *,
    label_a: str,
    label_b: str,
    profile: TabularPolicyProfile,
    keys: tuple[str, ...] = (),
) -> Result[CompareResult, CompareAbortError]:
    pre = preflight_compare_paths(
        path_a, path_b, label_a=label_a, label_b=label_b, profile=profile
    )
    if isinstance(pre, Err):
        side_a = CompareFileSide(label=label_a, path=path_a, file_size=0)
        side_b = CompareFileSide(label=label_b, path=path_b, file_size=0)
        return Ok(
            CompareResult(
                status="abort",
                file_a=side_a,
                file_b=side_b,
                abort_reason=pre.error.message,
            )
        )

    columns, side_a, side_b = pre.value
    if keys:
        missing = [key for key in keys if key not in columns]
        if missing:
            return Ok(
                CompareResult(
                    status="abort",
                    file_a=side_a,
                    file_b=side_b,
                    abort_reason=f"Llaves inválidas: {', '.join(missing)}",
                )
            )

    try:
        import pandas as pd
    except ImportError as exc:
        return Ok(
            CompareResult(
                status="abort",
                file_a=side_a,
                file_b=side_b,
                abort_reason=f"pandas no instalado: {exc}",
            )
        )

    try:
        df_a = _read_dataframe(pd, path_a)
        df_b = _read_dataframe(pd, path_b)
    except Exception as exc:  # noqa: BLE001
        return Ok(
            CompareResult(
                status="abort",
                file_a=side_a,
                file_b=side_b,
                abort_reason=f"No se pudo leer archivo: {exc}",
            )
        )

    side_a = CompareFileSide(
        label=label_a, path=path_a, file_size=side_a.file_size, row_count=len(df_a)
    )
    side_b = CompareFileSide(
        label=label_b, path=path_b, file_size=side_b.file_size, row_count=len(df_b)
    )
    column_count = len(columns)

    if keys:
        result = _compare_with_keys(
            df_a, df_b, keys, side_a, side_b, column_count=column_count
        )
    else:
        result = _compare_full_rows(
            df_a, df_b, side_a, side_b, column_count=column_count
        )
    return Ok(result)


def _cell_str(value: object) -> str:
    if value is None:
        return ""
    try:
        import pandas as pd

        if pd.isna(value):
            return ""
    except Exception:  # noqa: BLE001
        pass
    return str(value)


def _file_line(dataframe_index: int) -> int:
    """Línea en archivo: 1 = cabecera, 2 = primera fila de datos."""
    return dataframe_index + 2


def _build_row_index(
    df,
    key_cols: tuple[str, ...],
    value_cols: tuple[str, ...],
) -> tuple[Counter, dict[tuple[tuple[str, ...], tuple[str, ...]], list[int]]]:
    counter: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    line_map: dict[tuple[tuple[str, ...], tuple[str, ...]], list[int]] = defaultdict(list)
    columns = list(df.columns)
    for idx, record in enumerate(df.itertuples(index=False, name=None)):
        row = {col: record[col_idx] for col_idx, col in enumerate(columns)}
        key = tuple(_cell_str(row[col]) for col in key_cols)
        val = tuple(_cell_str(row[col]) for col in value_cols)
        signature = (key, val)
        counter[signature] += 1
        line_map[signature].append(_file_line(idx))
    return counter, line_map


def _first_line_for_key(df, key_cols: tuple[str, ...], key_tuple: tuple[str, ...]) -> int:
    columns = list(df.columns)
    for idx, record in enumerate(df.itertuples(index=False, name=None)):
        row = {col: record[col_idx] for col_idx, col in enumerate(columns)}
        key = tuple(_cell_str(row[col]) for col in key_cols)
        if key == key_tuple:
            return _file_line(idx)
    return 0


def _compare_full_rows(
    df_a, df_b, side_a, side_b, *, column_count: int
) -> CompareResult:
    cols = tuple(str(name) for name in df_a.columns)
    counter_a, lines_a = _build_row_index(df_a, (), cols)
    counter_b, lines_b = _build_row_index(df_b, (), cols)
    return _diff_counters(
        counter_a,
        counter_b,
        side_a,
        side_b,
        keys_used=(),
        lines_a=lines_a,
        lines_b=lines_b,
        column_count=column_count,
    )


def _compare_with_keys(
    df_a, df_b, keys, side_a, side_b, *, column_count: int
) -> CompareResult:
    key_cols = tuple(keys)
    val_cols = tuple(col for col in df_a.columns if col not in key_cols)
    counter_a, lines_a = _build_row_index(df_a, key_cols, val_cols)
    counter_b, lines_b = _build_row_index(df_b, key_cols, val_cols)

    keys_a = {signature[0] for signature in counter_a}
    keys_b = {signature[0] for signature in counter_b}
    examples: list[CompareExample] = []
    key_only_a = len(keys_a - keys_b)
    key_only_b = len(keys_b - keys_a)
    for key in sorted(keys_a - keys_b)[:MAX_EXAMPLES]:
        examples.append(
            CompareExample(
                kind="key_only_a",
                text=_format_key(key),
                line_a=_first_line_for_key(df_a, key_cols, key),
            )
        )
    for key in sorted(keys_b - keys_a)[:MAX_EXAMPLES]:
        examples.append(
            CompareExample(
                kind="key_only_b",
                text=_format_key(key),
                line_b=_first_line_for_key(df_b, key_cols, key),
            )
        )

    return _diff_counters(
        counter_a,
        counter_b,
        side_a,
        side_b,
        keys_used=tuple(keys),
        extra_examples=examples,
        key_only_a=key_only_a,
        key_only_b=key_only_b,
        lines_a=lines_a,
        lines_b=lines_b,
        column_count=column_count,
    )


def _format_key(key: tuple[str, ...]) -> str:
    return " | ".join(key)


def _format_row(key: tuple[str, ...], val: tuple[str, ...]) -> str:
    parts = list(key) + list(val)
    return " | ".join(parts)


def _compute_summary_stats(
    counter_a: Counter,
    counter_b: Counter,
    side_a: CompareFileSide,
    side_b: CompareFileSide,
) -> tuple[int, int, int, float, int]:
    all_keys = set(counter_a) | set(counter_b)
    matched_rows = sum(min(counter_a.get(sig, 0), counter_b.get(sig, 0)) for sig in all_keys)
    shared_signatures = sum(
        1 for sig in all_keys if counter_a.get(sig, 0) and counter_b.get(sig, 0)
    )
    row_delta = side_b.row_count - side_a.row_count
    size_delta = side_b.file_size - side_a.file_size
    denom = max(side_a.row_count, side_b.row_count, 1)
    match_pct = round(100.0 * matched_rows / denom, 2)
    return row_delta, size_delta, matched_rows, match_pct, shared_signatures


def _diff_counters(
    counter_a,
    counter_b,
    side_a: CompareFileSide,
    side_b: CompareFileSide,
    *,
    keys_used: tuple[str, ...],
    extra_examples: list[CompareExample] | None = None,
    key_only_a: int = 0,
    key_only_b: int = 0,
    lines_a: dict | None = None,
    lines_b: dict | None = None,
    column_count: int = 0,
) -> CompareResult:
    only_a = 0
    only_b = 0
    examples: list[CompareExample] = list(extra_examples or [])
    lines_a = lines_a or {}
    lines_b = lines_b or {}

    all_keys = set(counter_a) | set(counter_b)
    for signature in sorted(all_keys, key=str):
        count_a = counter_a.get(signature, 0)
        count_b = counter_b.get(signature, 0)
        key, val = signature
        if count_a > count_b:
            diff = count_a - count_b
            only_a += diff
            if len([example for example in examples if example.kind == "only_a"]) < MAX_EXAMPLES:
                line_a = lines_a.get(signature, [0])[0]
                examples.append(
                    CompareExample(
                        kind="only_a",
                        text=f"{_format_row(key, val)}  (×{diff})",
                        line_a=line_a,
                    )
                )
        elif count_b > count_a:
            diff = count_b - count_a
            only_b += diff
            if len([example for example in examples if example.kind == "only_b"]) < MAX_EXAMPLES:
                line_b = lines_b.get(signature, [0])[0]
                examples.append(
                    CompareExample(
                        kind="only_b",
                        text=f"{_format_row(key, val)}  (×{diff})",
                        line_b=line_b,
                    )
                )

    unique_a = set(counter_a)
    unique_b = set(counter_b)
    duplicate_excess = (
        unique_a == unique_b
        and counter_a != counter_b
        and side_a.row_count != side_b.row_count
    )
    if duplicate_excess and len([e for e in examples if e.kind == "duplicate_excess"]) < 1:
        examples.append(
            CompareExample(
                kind="duplicate_excess",
                text=(
                    f"Filas únicas iguales; conteos distintos "
                    f"({side_a.row_count:,} vs {side_b.row_count:,})."
                ),
            )
        )

    status = "match"
    if only_a or only_b or key_only_a or key_only_b or duplicate_excess:
        status = "diff"

    row_delta, size_delta, matched_rows, match_pct, shared_signatures = _compute_summary_stats(
        counter_a, counter_b, side_a, side_b
    )

    return CompareResult(
        status=status,
        file_a=side_a,
        file_b=side_b,
        keys_used=keys_used,
        only_in_a=only_a + key_only_a,
        only_in_b=only_b + key_only_b,
        duplicate_excess=duplicate_excess,
        examples=tuple(examples),
        row_delta=row_delta,
        size_delta=size_delta,
        matched_rows=matched_rows,
        match_pct=match_pct,
        shared_signatures=shared_signatures,
        column_count=column_count,
    )
