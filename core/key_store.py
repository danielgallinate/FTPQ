"""IKeyStore protocol — local SSH key operations."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from core.sftp_types import KeyCandidate, KeyPairInfo, KeyWarning


@runtime_checkable
class IKeyStore(Protocol):
    def discover(self, keys_dir: Path) -> list[KeyCandidate]: ...

    def fingerprint(self, private_key_path: Path) -> str: ...

    def generate(
        self,
        path: Path,
        key_type: Literal["rsa", "ecdsa"],
        bits: int | None = None,
    ) -> KeyPairInfo: ...

    def validate(self, private_key_path: Path) -> list[KeyWarning]: ...
