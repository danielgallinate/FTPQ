"""Conversión de columnas datetime entre zonas horarias."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from core.analysis_types import ColumnSummary, TabularDataset

UTC_NAME = "UTC"
_NA_TOKENS = frozenset({"", "NA", "N/A", "<NA>", "NULL", "NONE", "NAN"})

_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y/%m/%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%d",
)

# Fechas sin hora: no tienen zona horaria, convertirlas desplazaría el día.
_DATE_ONLY_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
)

_UTC_NAME_PATTERN = re.compile(r"(^|[_\W])UTC($|[_\W])|_UTC$", re.IGNORECASE)


@dataclass
class TimezoneTransformConfig:
    source_tz: str = UTC_NAME
    target_tz: str = ""
    columns: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_active(self) -> bool:
        return bool(self.columns) and bool(self.source_tz.strip()) and bool(self.target_tz.strip())


def default_target_timezone() -> str:
    local = datetime.now().astimezone().tzinfo
    if isinstance(local, ZoneInfo):
        return local.key
    return UTC_NAME


def common_timezone_options() -> list[str]:
    preferred = [
        UTC_NAME,
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "America/Bogota",
        "America/Mexico_City",
        "America/Sao_Paulo",
        "Europe/Madrid",
        "Europe/London",
    ]
    all_names = sorted(available_timezones())
    ordered: list[str] = []
    seen: set[str] = set()
    for name in preferred + all_names:
        if name in seen:
            continue
        seen.add(name)
        ordered.append(name)
    return ordered


def column_name_suggests_utc(name: str) -> bool:
    return bool(_UTC_NAME_PATTERN.search(name))


def parse_datetime_cell(value: str) -> datetime | None:
    text = str(value or "").strip()
    if text.upper() in _NA_TOKENS:
        return None
    if text.endswith("Z") and "T" in text:
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
        return parsed.replace(tzinfo=None) if parsed.tzinfo is not None else parsed
    except ValueError:
        pass
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def is_date_only_cell(value: str) -> bool:
    """Fecha sin componente de hora (``2024-04-28``), no convertible entre zonas."""
    text = str(value or "").strip()
    if not text or text.upper() in _NA_TOKENS:
        return False
    if ":" in text:
        return False
    for fmt in _DATE_ONLY_FORMATS:
        try:
            datetime.strptime(text, fmt)
            return True
        except ValueError:
            continue
    return False


def _sample_rows(dataset: TabularDataset, limit: int = 200) -> tuple[tuple[str, ...], ...]:
    if len(dataset.rows) <= limit:
        return dataset.rows
    return dataset.rows[:limit]


def guess_datetime_columns(
    dataset: TabularDataset,
    *,
    sample_limit: int = 200,
    min_parse_ratio: float = 0.6,
) -> list[str]:
    """Detecta columnas datetime; prioriza nombres con UTC."""
    samples = _sample_rows(dataset, sample_limit)
    if not samples:
        return [column.name for column in dataset.columns if column_name_suggests_utc(column.name)]

    guessed: list[str] = []
    for col_index, column in enumerate(dataset.columns):
        name_hint = column_name_suggests_utc(column.name)
        parsed = 0
        checked = 0
        date_only = 0
        for row in samples:
            if col_index >= len(row):
                continue
            raw = str(row[col_index] or "").strip()
            if raw.upper() in _NA_TOKENS:
                continue
            checked += 1
            if parse_datetime_cell(raw) is not None:
                parsed += 1
            if is_date_only_cell(raw):
                date_only += 1
        if checked and date_only == checked:
            continue
        ratio = (parsed / checked) if checked else 0.0
        if name_hint or ratio >= min_parse_ratio:
            guessed.append(column.name)
    return guessed


def convert_datetime_cell(value: str, *, source_tz: str, target_tz: str) -> str:
    if is_date_only_cell(value):
        return value
    parsed = parse_datetime_cell(value)
    if parsed is None:
        return value
    source = ZoneInfo(source_tz)
    target = ZoneInfo(target_tz)
    if parsed.tzinfo is None:
        localized = parsed.replace(tzinfo=source)
    else:
        localized = parsed.astimezone(source)
    converted = localized.astimezone(target)
    if parsed.microsecond:
        return converted.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip("0").rstrip(".")
    return converted.strftime("%Y-%m-%d %H:%M:%S")


def apply_timezone_transform(
    dataset: TabularDataset,
    config: TimezoneTransformConfig,
) -> TabularDataset:
    if not config.is_active:
        return dataset
    selected = config.columns
    if not selected:
        return dataset
    name_to_index = {column.name: idx for idx, column in enumerate(dataset.columns)}
    target_indices = {
        name_to_index[name]
        for name in selected
        if name in name_to_index
    }
    if not target_indices:
        return dataset

    new_rows: list[tuple[str, ...]] = []
    for row in dataset.rows:
        values = list(row)
        for col_index in target_indices:
            if col_index < len(values):
                values[col_index] = convert_datetime_cell(
                    values[col_index],
                    source_tz=config.source_tz,
                    target_tz=config.target_tz,
                )
        new_rows.append(tuple(values))

    return TabularDataset(
        local_path=dataset.local_path,
        columns=dataset.columns,
        rows=tuple(new_rows),
        total_rows=dataset.total_rows,
        display_truncated=dataset.display_truncated,
        sampled=dataset.sampled,
        estimated_total_rows=dataset.estimated_total_rows,
    )
