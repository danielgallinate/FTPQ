"""Job local_cleanup — borrar coincidencias en un directorio local (sin SFTP)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

JOB_SCHEMA_VERSION = 1
JOB_KIND = "local_cleanup"


@dataclass
class LocalCleanupJob:
    name: str
    local_dir: str
    patterns: list[str]
    schema_version: int = JOB_SCHEMA_VERSION
    kind: str = JOB_KIND
    source_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "name": self.name,
            "local_dir": self.local_dir,
            "patterns": list(self.patterns),
        }

    @classmethod
    def from_dict(
        cls, raw: dict[str, Any], *, source_path: Path | None = None
    ) -> LocalCleanupJob:
        kind = str(raw.get("kind") or "").strip()
        if kind != JOB_KIND:
            raise ValueError(f"job kind must be {JOB_KIND!r}, got {kind!r}")
        name = str(raw.get("name") or "").strip()
        if not name:
            raise ValueError("job name is required")
        local_dir = str(raw.get("local_dir") or "").strip()
        patterns_raw = raw.get("patterns") or []
        if not isinstance(patterns_raw, list) or not patterns_raw:
            raise ValueError("job patterns must be a non-empty list")
        patterns = [str(item).strip() for item in patterns_raw if str(item).strip()]
        if not patterns:
            raise ValueError("job patterns must contain at least one glob")
        return cls(
            name=name,
            local_dir=local_dir,
            patterns=patterns,
            schema_version=int(raw.get("schema_version") or JOB_SCHEMA_VERSION),
            kind=JOB_KIND,
            source_path=source_path,
        )

    def resolved_local_dir(self, override: Path | None = None) -> Path:
        if override is not None:
            return override.expanduser().resolve()
        if not self.local_dir.strip():
            raise ValueError(
                "local_dir required: pass --local-dir or set local_dir in job JSON"
            )
        path = Path(self.local_dir).expanduser()
        if path.is_absolute():
            return path
        if self.source_path is not None:
            return (self.source_path.parent / path).resolve()
        return path.resolve()


def load_job(path: Path) -> LocalCleanupJob:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("job file must be a JSON object")
    return LocalCleanupJob.from_dict(raw, source_path=path.resolve())


def pattern_is_unsafe(pattern: str) -> bool:
    stripped = pattern.strip()
    if not stripped:
        return True
    if ".." in stripped or "/" in stripped or "\\" in stripped:
        return True
    return False
