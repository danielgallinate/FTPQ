"""IKeyStore — operaciones locales con Paramiko."""
from __future__ import annotations

import stat
from pathlib import Path

from paramiko import ECDSAKey, PKey, RSAKey
from paramiko.ssh_exception import SSHException

from core.sftp_types import KeyCandidate, KeyPairInfo, KeyWarning

_PRIVATE_MARKERS = (
    "BEGIN RSA PRIVATE KEY",
    "BEGIN EC PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN PRIVATE KEY",
)


class LocalKeyStore:
    def discover(self, keys_dir: Path) -> list[KeyCandidate]:
        directory = keys_dir.expanduser()
        if not directory.is_dir():
            return []
        candidates: list[KeyCandidate] = []
        for path in sorted(directory.iterdir()):
            if not path.is_file() or path.suffix == ".pub":
                continue
            if _is_private_key_file(path):
                candidates.append(KeyCandidate(path=path, label=path.name))
        return candidates

    def fingerprint(self, private_key_path: Path) -> str:
        key = _load_private_key(private_key_path.expanduser())
        digest = key.get_fingerprint().hex()
        return ":".join(digest[i : i + 2] for i in range(0, len(digest), 2))

    def generate(
        self,
        path: Path,
        key_type: str,
        bits: int | None = None,
    ) -> KeyPairInfo:
        private = path.expanduser()
        private.parent.mkdir(parents=True, exist_ok=True)
        if key_type == "rsa":
            key = RSAKey.generate(bits=bits or 4096)
            type_label = "rsa"
        elif key_type == "ecdsa":
            key = ECDSAKey.generate(bits=bits or 256)
            type_label = "ecdsa"
        else:
            raise ValueError(f"Tipo de llave no soportado: {key_type}")

        key.write_private_key_file(str(private))
        public = Path(f"{private}.pub")
        with public.open("w", encoding="utf-8") as fh:
            fh.write(f"{key.get_name()} {key.get_base64()}\n")

        return KeyPairInfo(
            private_path=private,
            public_path=public,
            fingerprint=self.fingerprint(private),
            key_type=type_label,
        )

    def validate(self, private_key_path: Path) -> list[KeyWarning]:
        path = private_key_path.expanduser()
        warnings: list[KeyWarning] = []
        if not path.is_file():
            warnings.append(KeyWarning("missing", f"No existe: {path}"))
            return warnings
        try:
            _load_private_key(path)
        except OSError as exc:
            warnings.append(KeyWarning("unreadable", str(exc)))
            return warnings

        if hasattr(path, "stat"):
            mode = path.stat().st_mode
            if mode & (stat.S_IRGRP | stat.S_IROTH | stat.S_IWGRP | stat.S_IWOTH):
                warnings.append(
                    KeyWarning(
                        "permissions",
                        "Permisos demasiado abiertos; recomendado 600.",
                    )
                )
        return warnings


def _is_private_key_file(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:200]
    except OSError:
        return False
    return any(marker in head for marker in _PRIVATE_MARKERS)


def _load_private_key(path: Path) -> PKey:
    last: Exception | None = None
    for loader in (RSAKey, ECDSAKey):
        try:
            return loader.from_private_key_file(str(path))
        except (OSError, SSHException) as exc:
            last = exc
            continue
    raise OSError(f"No se pudo leer llave privada: {path}") from last
