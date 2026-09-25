"""SFTP domain types and profile loading."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal


class SessionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class SftpProfile:
    profile_id: str
    host: str
    port: int
    user: str
    private_key_path: Path
    ssh_keys_dir: Path = field(default_factory=lambda: Path("~/.ssh"))
    default_remote_path: str = ""
    download_dir: Path = field(default_factory=lambda: Path("./downloads"))
    connect_timeout_seconds: int = 30
    preview_max_bytes: int = 524_288
    preview_max_lines: int = 500

    @classmethod
    def from_profile_json(cls, data: dict[str, Any]) -> SftpProfile:
        profile_id = data["profile_id"]
        sftp = data["sftp"]
        return cls(
            profile_id=profile_id,
            host=sftp["host"],
            port=int(sftp.get("port", 22)),
            user=sftp["user"],
            private_key_path=Path(sftp["private_key_path"]).expanduser(),
            ssh_keys_dir=Path(sftp.get("ssh_keys_dir", "~/.ssh")).expanduser(),
            default_remote_path=_normalize_remote_path(
                sftp.get("default_remote_path", "")
            ),
            download_dir=Path(sftp.get("download_dir", "./downloads")).expanduser(),
            connect_timeout_seconds=int(sftp.get("connect_timeout_seconds", 30)),
            preview_max_bytes=int(sftp.get("preview_max_bytes", 524_288)),
            preview_max_lines=int(sftp.get("preview_max_lines", 500)),
        )

    @classmethod
    def load_json_file(cls, path: Path) -> SftpProfile:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_profile_json(data)

    def normalized_default_remote_path(self) -> str:
        return _normalize_remote_path(self.default_remote_path)


@dataclass(frozen=True, slots=True)
class RemoteEntry:
    name: str
    entry_type: Literal["file", "dir"]
    size: int
    modified: datetime | None = None


@dataclass(frozen=True, slots=True)
class SftpListing:
    remote_path: str
    entries: list[RemoteEntry]
    display_path: str = ""


@dataclass(frozen=True, slots=True)
class PreviewResult:
    content: str
    truncated: bool
    bytes_read: int
    line_count: int


@dataclass(frozen=True, slots=True)
class VisualizeResult:
    """Archivo descargado completo; content puede truncarse solo para pantalla."""

    local_path: Path
    content: str
    file_size: int
    line_count: int
    display_truncated: bool
    tabular: bool = False
    text_fallback: bool = False


@dataclass(frozen=True, slots=True)
class KeyCandidate:
    path: Path
    label: str


@dataclass(frozen=True, slots=True)
class KeyPairInfo:
    private_path: Path
    public_path: Path
    fingerprint: str
    key_type: str


@dataclass(frozen=True, slots=True)
class KeyWarning:
    code: str
    message: str


def _normalize_remote_path(path: str) -> str:
    p = path.strip().replace("\\", "/")
    while "//" in p:
        p = p.replace("//", "/")
    return p.strip("/")
