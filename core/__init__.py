"""PDE Desktop — dominio sin UI ni adapters."""

from core.result import Err, Ok, Result
from core.sftp_errors import (
    KeyFormatError,
    KeyNotFoundError,
    PreviewNotSupported,
    PreviewTooLarge,
    SftpAuthError,
    SftpConnectionError,
    SftpError,
    SftpPathError,
)
from core.sftp_types import (
    KeyCandidate,
    KeyPairInfo,
    KeyWarning,
    PreviewResult,
    RemoteEntry,
    SessionState,
    SftpProfile,
)

__all__ = [
    "Err",
    "KeyCandidate",
    "KeyFormatError",
    "KeyNotFoundError",
    "KeyPairInfo",
    "KeyWarning",
    "Ok",
    "PreviewNotSupported",
    "PreviewTooLarge",
    "PreviewResult",
    "RemoteEntry",
    "Result",
    "SessionState",
    "SftpAuthError",
    "SftpConnectionError",
    "SftpError",
    "SftpPathError",
    "SftpProfile",
]
