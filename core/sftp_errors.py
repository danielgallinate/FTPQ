"""Typed SFTP and key errors — no secrets in messages."""
from __future__ import annotations


class SftpError(Exception):
    """Base for SFTP module errors."""


class SftpAuthError(SftpError):
    def __init__(self, message: str, *, user: str | None = None) -> None:
        super().__init__(message)
        self.user = user


class SftpConnectionError(SftpError):
    def __init__(
        self,
        message: str,
        *,
        host: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.host = host
        self.timeout_seconds = timeout_seconds


class SftpPathError(SftpError):
    def __init__(self, message: str, *, path: str) -> None:
        super().__init__(message)
        self.path = path


class KeyNotFoundError(SftpError):
    def __init__(self, message: str, *, path: str) -> None:
        super().__init__(message)
        self.path = path


class KeyFormatError(SftpError):
    def __init__(self, message: str, *, path: str) -> None:
        super().__init__(message)
        self.path = path


class PreviewNotSupported(SftpError):
    def __init__(self, message: str, *, path: str) -> None:
        super().__init__(message)
        self.path = path


class PreviewTooLarge(SftpError):
    def __init__(
        self,
        message: str,
        *,
        path: str,
        bytes_read: int,
        limit_bytes: int,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.bytes_read = bytes_read
        self.limit_bytes = limit_bytes


class TransferCancelledError(SftpError):
    """Descarga o visualización interrumpida por el usuario."""

    def __init__(self, message: str = "Operación cancelada.") -> None:
        super().__init__(message)
