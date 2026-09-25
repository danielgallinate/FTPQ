"""Perfil de aplicación — SFTP + preferencias locales (un solo perfil v1)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.analysis_limits import DEFAULT_MAX_DISPLAY_ROWS, normalize_max_display_rows
from core.app_paths import path_for_json, resolve_profile_path
from core.sftp_types import SftpProfile, _normalize_remote_path
from core.ui_preferences import DEFAULT_UI_LANGUAGE, normalize_ui_language
from core.visualization_policy import (
    DEFAULT_PANDAS_MAX_BYTES,
    DEFAULT_TABULAR_MODE,
    normalize_pandas_max_bytes,
    normalize_tabular_mode,
)


@dataclass(slots=True)
class AppProfile:
    profile_id: str = "default"
    host: str = ""
    port: int = 22
    user: str = ""
    private_key_path: Path = field(default_factory=lambda: Path("~/.ssh/id_rsa"))
    ssh_keys_dir: Path = field(default_factory=lambda: Path("~/.ssh"))
    default_remote_path: str = ""
    download_dir: Path = field(default_factory=lambda: Path("./downloads"))
    max_display_rows: int = DEFAULT_MAX_DISPLAY_ROWS
    tabular_mode: str = DEFAULT_TABULAR_MODE
    pandas_max_bytes: int = DEFAULT_PANDAS_MAX_BYTES
    language: str = DEFAULT_UI_LANGUAGE

    @classmethod
    def default(cls) -> AppProfile:
        return cls()

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> AppProfile:
        sftp = data.get("sftp", {})
        visualization = data.get("visualization", {})
        ui = data.get("ui", {})
        max_rows_raw = visualization.get("max_display_rows", DEFAULT_MAX_DISPLAY_ROWS)
        try:
            max_display_rows = normalize_max_display_rows(int(max_rows_raw))
        except (TypeError, ValueError):
            max_display_rows = DEFAULT_MAX_DISPLAY_ROWS
        language = normalize_ui_language(ui.get("language", DEFAULT_UI_LANGUAGE))
        tabular_mode = normalize_tabular_mode(
            visualization.get("tabular_mode", DEFAULT_TABULAR_MODE)
        )
        try:
            pandas_max_bytes = normalize_pandas_max_bytes(
                int(visualization.get("pandas_max_bytes", DEFAULT_PANDAS_MAX_BYTES))
            )
        except (TypeError, ValueError):
            pandas_max_bytes = DEFAULT_PANDAS_MAX_BYTES
        return cls(
            profile_id=data.get("profile_id", "default"),
            host=sftp.get("host", ""),
            port=int(sftp.get("port", 22)),
            user=sftp.get("user", ""),
            private_key_path=resolve_profile_path(
                sftp.get("private_key_path", "~/.ssh/id_rsa")
            ),
            ssh_keys_dir=resolve_profile_path(sftp.get("ssh_keys_dir", "~/.ssh")),
            default_remote_path=_normalize_remote_path(sftp.get("default_remote_path", "")),
            download_dir=resolve_profile_path(sftp.get("download_dir", "./downloads")),
            max_display_rows=max_display_rows,
            tabular_mode=tabular_mode,
            pandas_max_bytes=pandas_max_bytes,
            language=language,
        )

    @classmethod
    def load_json_file(cls, path: Path) -> AppProfile:
        return cls.from_json_dict(json.loads(path.read_text(encoding="utf-8")))

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "sftp": {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "private_key_path": path_for_json(self.private_key_path),
                "ssh_keys_dir": path_for_json(self.ssh_keys_dir),
                "default_remote_path": self.default_remote_path,
                "download_dir": path_for_json(self.download_dir),
            },
            "visualization": {
                "max_display_rows": self.max_display_rows,
                "tabular_mode": self.tabular_mode,
                "pandas_max_bytes": self.pandas_max_bytes,
            },
            "ui": {
                "language": self.language,
            },
        }

    def to_sftp_profile(self) -> SftpProfile:
        return SftpProfile(
            profile_id=self.profile_id,
            host=self.host or "localhost",
            port=self.port,
            user=self.user or self.profile_id,
            private_key_path=self.private_key_path,
            ssh_keys_dir=self.ssh_keys_dir,
            default_remote_path=self.default_remote_path,
            download_dir=self.download_dir,
        )
