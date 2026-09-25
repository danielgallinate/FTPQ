"""Paramiko SFTP — handshake real para test_auth."""
from __future__ import annotations

import stat
import struct
from datetime import datetime
from pathlib import Path

import paramiko
from paramiko import ECDSAKey, PKey, RSAKey
from paramiko.sftp import SFTPError
from paramiko.ssh_exception import AuthenticationException, SSHException

from core.result import Err, Ok, Result
from core.sftp_browser import ISftpBrowser
from core.sftp_errors import (
    KeyFormatError,
    KeyNotFoundError,
    PreviewNotSupported,
    SftpAuthError,
    SftpConnectionError,
    SftpPathError,
    TransferCancelledError,
)
from core.sftp_paths import list_path_candidates, resolve_list_path
from core.sftp_types import PreviewResult, RemoteEntry, SessionState, SftpProfile


class ParamikoSftpBrowser(ISftpBrowser):
    def __init__(self) -> None:
        self._client: paramiko.SSHClient | None = None
        self._sftp: paramiko.SFTPClient | None = None
        self._profile: SftpProfile | None = None
        self._state = SessionState.DISCONNECTED
        self._current_path: str | None = None
        self._transfer_aborted = False

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def current_remote_path(self) -> str | None:
        return self._current_path

    def connect(self, profile: SftpProfile) -> None:
        self.disconnect()
        key_path = profile.private_key_path.expanduser()
        if not key_path.is_file():
            raise KeyNotFoundError(
                f"Llave privada no encontrada: {key_path}",
                path=str(key_path),
            )
        try:
            pkey = _load_private_key(key_path)
        except (OSError, SSHException) as exc:
            raise KeyFormatError(
                f"No se pudo leer la llave: {key_path}",
                path=str(key_path),
            ) from exc

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=profile.host,
                port=profile.port,
                username=profile.user,
                pkey=pkey,
                timeout=profile.connect_timeout_seconds,
                allow_agent=False,
                look_for_keys=False,
            )
        except AuthenticationException as exc:
            self._state = SessionState.ERROR
            raise SftpAuthError(
                "Autenticación SFTP rechazada (user/llave).",
                user=profile.user,
            ) from exc
        except (TimeoutError, SSHException, OSError) as exc:
            self._state = SessionState.ERROR
            raise SftpConnectionError(
                f"No se pudo conectar a {profile.host}:{profile.port}",
                host=profile.host,
                timeout_seconds=float(profile.connect_timeout_seconds),
            ) from exc

        self._client = client
        transport = client.get_transport()
        if transport is not None:
            transport.set_keepalive(30)
            transport.default_window_size = max(transport.default_window_size, 4 * 1024 * 1024)
        self._profile = profile
        self._state = SessionState.CONNECTED
        from core.sftp_paths import SFTP_ROOT

        self._current_path = SFTP_ROOT

    def disconnect(self) -> None:
        if self._sftp is not None:
            try:
                self._sftp.close()
            except OSError:
                pass
            self._sftp = None
        if self._client is not None:
            self._client.close()
        self._client = None
        self._profile = None
        self._current_path = None
        self._state = SessionState.DISCONNECTED
        self._transfer_aborted = False

    def abort_transfer(self) -> None:
        """Interrumpe una descarga en curso cerrando el canal SFTP."""
        self._transfer_aborted = True
        if self._sftp is not None:
            try:
                self._sftp.close()
            except OSError:
                pass
            self._sftp = None

    def test_auth(self) -> Result[None, SftpAuthError | SftpConnectionError]:
        if self._client is None:
            return Err(SftpAuthError("Sin sesión SFTP activa."))
        transport = self._client.get_transport()
        if transport is None or not transport.is_active():
            return Err(SftpConnectionError("Transporte SSH inactivo."))
        return Ok(None)

    def list_dir(self, remote_path: str) -> list[RemoteEntry]:
        if self._client is None:
            raise SftpConnectionError("Sin sesión SFTP activa.")
        logical = resolve_list_path(self._current_path, remote_path)
        sftp = self._open_sftp()
        last_error: OSError | SFTPError | struct.error | EOFError | None = None
        attrs: list[paramiko.SFTPAttributes] = []

        for candidate in list_path_candidates(logical):
            try:
                attrs = _list_attrs_with_fallback(sftp, candidate)
                if attrs or candidate == list_path_candidates(logical)[-1]:
                    break
            except (OSError, SFTPError, struct.error, EOFError) as exc:
                last_error = exc
                continue

        if not attrs and last_error is not None:
            raise SftpPathError(
                f"No se pudo listar: {logical}",
                path=logical,
            ) from last_error

        entries: list[RemoteEntry] = []
        if _has_parent(logical):
            entries.append(RemoteEntry(name="..", entry_type="dir", size=0))

        for attr in sorted(attrs, key=lambda item: item.filename.lower()):
            if attr.filename in (".", ".."):
                continue
            entry_type = "dir" if stat.S_ISDIR(attr.st_mode or 0) else "file"
            modified = (
                datetime.fromtimestamp(attr.st_mtime) if attr.st_mtime else None
            )
            entries.append(
                RemoteEntry(
                    name=attr.filename,
                    entry_type=entry_type,
                    size=int(attr.st_size or 0),
                    modified=modified,
                )
            )

        self._current_path = logical
        return entries

    def download(
        self,
        remote_path: str,
        local_path: Path,
        *,
        on_progress=None,
        force: bool = False,
    ) -> None:
        from core.download_progress import ThrottledDownloadProgress

        sftp = self._open_sftp()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self._transfer_aborted = False
        total_size = 0
        try:
            total_size = int(sftp.stat(remote_path).st_size)
        except OSError:
            total_size = 0

        if (
            not force
            and total_size > 0
            and local_path.is_file()
            and local_path.stat().st_size == total_size
        ):
            if on_progress is not None:
                on_progress(total_size, total_size)
            return

        progress = ThrottledDownloadProgress(on_progress)
        callback = progress if on_progress is not None else None

        try:
            # AWS Transfer Family: prefetch sin límite puede colgar ~60–80% (Paramiko 3.3+)
            sftp.get(
                remote_path,
                str(local_path),
                callback=callback,
                prefetch=True,
                max_concurrent_prefetch_requests=64,
            )
        except OSError as exc:
            if self._transfer_aborted:
                raise TransferCancelledError(
                    "Descarga cancelada por el usuario."
                ) from exc
            raise SftpPathError(
                f"No se pudo descargar: {remote_path}",
                path=remote_path,
            ) from exc
        finally:
            self._transfer_aborted = False

    def preview(self, remote_path: str, max_bytes: int) -> PreviewResult:
        ext = Path(remote_path).suffix.lower()
        if ext not in _PREVIEW_EXTENSIONS:
            raise PreviewNotSupported(
                f"Vista previa no soportada para {ext or '(sin ext)'}",
                path=remote_path,
            )
        sftp = self._open_sftp()
        try:
            with sftp.open(remote_path, "rb") as handle:
                data = handle.read(max_bytes + 1)
        except OSError as exc:
            raise SftpPathError(
                f"No se pudo leer: {remote_path}",
                path=remote_path,
            ) from exc
        truncated = len(data) > max_bytes
        payload = data[:max_bytes]
        content = payload.decode("utf-8", errors="replace")
        lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        return PreviewResult(
            content=content,
            truncated=truncated,
            bytes_read=len(payload),
            line_count=lines,
        )

    def _open_sftp(self) -> paramiko.SFTPClient:
        if self._sftp is not None:
            return self._sftp
        if self._client is None:
            raise SftpConnectionError("Sin sesión SFTP activa.")
        self._sftp = self._client.open_sftp()
        return self._sftp


def _has_parent(path: str) -> bool:
    parts = [part for part in path.split("/") if part]
    return bool(parts) and path not in (".", "")


_PREVIEW_EXTENSIONS = frozenset({".csv", ".txt", ".json", ".log", ".md", ".env", ".tsv", ".psv"})


def _list_attrs_with_fallback(
    sftp: paramiko.SFTPClient, remote_dir: str
) -> list[paramiko.SFTPAttributes]:
    """listdir_attr con fallback listdir+stat (AWS Transfer / paramiko)."""
    try:
        return sftp.listdir_attr(remote_dir)
    except (OSError, SFTPError, struct.error, EOFError):
        result: list[paramiko.SFTPAttributes] = []
        for name in sftp.listdir(remote_dir):
            if name in (".", ".."):
                continue
            relative = (
                f"{remote_dir}/{name}"
                if remote_dir not in (".", "")
                else name
            )
            try:
                entry = sftp.stat(relative)
            except OSError:
                continue
            entry.filename = name
            result.append(entry)
        return result


def _load_private_key(path: Path) -> PKey:
    last: Exception | None = None
    for loader in (RSAKey, ECDSAKey):
        try:
            return loader.from_private_key_file(str(path))
        except (OSError, SSHException) as exc:
            last = exc
            continue
    raise OSError(f"No se pudo leer llave privada: {path}") from last
