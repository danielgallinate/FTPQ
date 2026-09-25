"""ISftpBrowser protocol — SFTP session contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from core.download_progress import DownloadProgressCallback

from core.result import Result
from core.sftp_errors import SftpError
from core.sftp_types import PreviewResult, RemoteEntry, SessionState, SftpProfile


@runtime_checkable
class ISftpBrowser(Protocol):
    @property
    def state(self) -> SessionState: ...

    @property
    def current_remote_path(self) -> str | None: ...

    def connect(self, profile: SftpProfile) -> None: ...

    def disconnect(self) -> None: ...

    def test_auth(self) -> Result[None, SftpError]: ...

    def list_dir(self, remote_path: str) -> list[RemoteEntry]: ...

    def download(
        self,
        remote_path: str,
        local_path: Path,
        *,
        on_progress: DownloadProgressCallback | None = None,
        force: bool = False,
    ) -> None: ...

    def preview(self, remote_path: str, max_bytes: int) -> PreviewResult: ...
