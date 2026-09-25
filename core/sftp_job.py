"""Job SFTP — receta headless para listar, comprobar existencia y descargar (S18/S19)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

JOB_SCHEMA_VERSION = 1
JOB_KIND = "sftp_fetch"
CollisionPolicy = Literal["fail", "overwrite"]
MatchType = Literal["glob", "regex"]


@dataclass(frozen=True)
class SftpExpect:
    pattern: str
    min_count: int = 1
    match_type: MatchType = "glob"

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern": self.pattern,
            "min_count": self.min_count,
            "match_type": self.match_type,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SftpExpect:
        pattern = str(raw.get("pattern") or "").strip()
        if not pattern:
            raise ValueError("expect.pattern is required")
        min_count = int(raw.get("min_count", 1))
        if min_count < 1:
            raise ValueError("expect.min_count must be >= 1")
        match_type = str(raw.get("match_type") or "glob").strip()
        if match_type not in ("glob", "regex"):
            raise ValueError("expect.match_type must be 'glob' or 'regex'")
        return cls(
            pattern=pattern,
            min_count=min_count,
            match_type=match_type,  # type: ignore[arg-type]
        )


@dataclass
class SftpFetchJob:
    name: str
    profile: str
    remote_dir: str
    local_dir: str
    download: bool = True
    recursive: bool = False
    destination_name: str = ""
    on_collision: CollisionPolicy = "fail"
    expect: list[SftpExpect] = field(default_factory=list)
    schema_version: int = JOB_SCHEMA_VERSION
    kind: str = JOB_KIND
    source_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "name": self.name,
            "profile": self.profile,
            "remote_dir": self.remote_dir,
            "local_dir": self.local_dir,
            "download": self.download,
            "recursive": self.recursive,
            "destination_name": self.destination_name,
            "on_collision": self.on_collision,
            "expect": [item.to_dict() for item in self.expect],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any], *, source_path: Path | None = None) -> SftpFetchJob:
        kind = str(raw.get("kind") or "").strip()
        if kind != JOB_KIND:
            raise ValueError(f"job kind must be {JOB_KIND!r}, got {kind!r}")
        version = int(raw.get("schema_version") or JOB_SCHEMA_VERSION)
        name = str(raw.get("name") or "").strip()
        if not name:
            raise ValueError("job name is required")
        profile = str(raw.get("profile") or "").strip()
        if not profile:
            raise ValueError("job profile is required")
        remote_dir = str(raw.get("remote_dir") or "").strip() or "."
        local_dir = str(raw.get("local_dir") or "").strip()
        download = bool(raw.get("download", True))
        recursive = bool(raw.get("recursive", False))
        destination_name = str(raw.get("destination_name") or "").strip()
        collision = str(raw.get("on_collision") or "fail").strip()
        if collision not in ("fail", "overwrite"):
            raise ValueError("on_collision must be 'fail' or 'overwrite'")
        expect_raw = raw.get("expect") or []
        if not isinstance(expect_raw, list) or not expect_raw:
            raise ValueError("job expect must be a non-empty list")
        expects = [
            SftpExpect.from_dict(item)
            for item in expect_raw
            if isinstance(item, dict)
        ]
        if not expects:
            raise ValueError("job expect must contain at least one pattern")
        return cls(
            name=name,
            profile=profile,
            remote_dir=remote_dir,
            local_dir=local_dir,
            download=download,
            recursive=recursive,
            destination_name=destination_name,
            on_collision=collision,  # type: ignore[arg-type]
            expect=expects,
            schema_version=version,
            kind=JOB_KIND,
            source_path=source_path,
        )

    def resolved_profile_path(self) -> Path:
        path = Path(self.profile).expanduser()
        if path.is_file():
            return path.resolve()
        if self.source_path is not None:
            relative = (self.source_path.parent / path).expanduser()
            if relative.is_file():
                return relative.resolve()
        raise FileNotFoundError(f"SFTP profile not found: {self.profile}")

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

    def resolve_destination(self, base_dir: Path, *, sftp_user: str) -> Path:
        if not self.destination_name:
            return base_dir
        try:
            name = self.destination_name.format(sftp_user=sftp_user)
        except (KeyError, ValueError) as exc:
            raise ValueError(
                "destination_name only supports the {sftp_user} placeholder"
            ) from exc
        if (
            not name.strip()
            or name in (".", "..")
            or "/" in name
            or "\\" in name
        ):
            raise ValueError("destination_name must resolve to one folder name")
        return (base_dir / name).resolve()


def load_job(path: Path) -> SftpFetchJob:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("job file must be a JSON object")
    return SftpFetchJob.from_dict(raw, source_path=path.resolve())
