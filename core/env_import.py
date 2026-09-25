"""Importar perfil desde .env — solo campos SFTP soportados."""
from __future__ import annotations

import os
import re
from pathlib import Path

from core.app_profile import AppProfile

_ENV_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")

# Claves DB legacy ignoradas al importar (no se almacenan en PDE Desktop).
_IGNORED_ENV_KEYS = frozenset(
    {
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_RO_USER",
        "DB_RO_PASSWORD",
        "DB_SSLMODE",
    }
)


def discover_env_files() -> list[Path]:
    root = Path(__file__).resolve().parents[1]
    candidates = [
        Path.home() / ".pde-desktop" / "pde.env",
        root / ".env",
        root.parent / "file validator PDE" / ".env",
        root.parent / "pde-sftp-validator" / ".env",
        root.parent / "premium-data-extracts" / ".env",
    ]
    extra = os.environ.get("PDE_DESKTOP_ENV", "").strip()
    if extra:
        candidates.insert(0, Path(extra).expanduser())
    seen: set[Path] = set()
    found: list[Path] = []
    for path in candidates:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            found.append(resolved)
    return found


def parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _ENV_LINE.match(line)
        if match is None:
            continue
        key, raw = match.group(1), match.group(2)
        if key in _IGNORED_ENV_KEYS:
            continue
        values[key] = raw.strip().strip('"').strip("'")
    return values


def profile_from_env(values: dict[str, str]) -> AppProfile:
    config_name = values.get("CONFIG_NAME", "").strip() or "default"
    user = values.get("SFTP_USER", "").strip() or config_name
    default_folder = values.get("DEFAULT_FOLDER", "").strip()

    return AppProfile(
        profile_id=config_name,
        host=values.get("SFTP_HOST", "").strip(),
        port=22,
        user=user,
        private_key_path=Path(values.get("SFTP_KEY_PATH", "~/.ssh/id_rsa")).expanduser(),
        ssh_keys_dir=Path("~/.ssh"),
        default_remote_path=_remote_path(user or config_name, default_folder),
        download_dir=Path(values.get("DOWNLOAD_DIR", "./downloads")).expanduser(),
    )


def import_env_file(path: Path) -> AppProfile:
    text = path.read_text(encoding="utf-8")
    return profile_from_env(parse_env_text(text))


def merge_missing(base: AppProfile, incoming: AppProfile) -> AppProfile:
    """Completa campos vacíos del perfil local con valores del .env."""
    if not base.host.strip() and incoming.host.strip():
        base.host = incoming.host
    if not base.user.strip() and incoming.user.strip():
        base.user = incoming.user
    if base.profile_id == "default" and incoming.profile_id != "default":
        base.profile_id = incoming.profile_id
    if not base.private_key_path.expanduser().is_file() and incoming.private_key_path:
        base.private_key_path = incoming.private_key_path
    elif str(base.private_key_path).endswith("id_rsa") and incoming.private_key_path:
        base.private_key_path = incoming.private_key_path
    if not base.default_remote_path.strip() and incoming.default_remote_path.strip():
        base.default_remote_path = incoming.default_remote_path
    if not str(base.download_dir).strip() or str(base.download_dir) == "./downloads":
        base.download_dir = incoming.download_dir
    return base


def apply_env_import(base: AppProfile, incoming: AppProfile) -> AppProfile:
    """Import explícito Settings → Import .env — sustituye SFTP del validator."""
    if incoming.host.strip():
        base.host = incoming.host
    if incoming.user.strip():
        base.user = incoming.user
    if incoming.profile_id.strip() and incoming.profile_id != "default":
        base.profile_id = incoming.profile_id
    if incoming.private_key_path:
        base.private_key_path = incoming.private_key_path
    if incoming.default_remote_path.strip():
        base.default_remote_path = incoming.default_remote_path
    if incoming.download_dir:
        base.download_dir = incoming.download_dir
    return base


def sync_config_name(profile: AppProfile) -> AppProfile:
    """Alinea profile_id con SFTP_USER (= CONFIG_NAME en nonprod)."""
    user = profile.user.strip()
    if user:
        profile.profile_id = user
    return profile


def _remote_path(config_name: str, default_folder: str) -> str:
    folder = default_folder.strip().strip("/") or "scheduled"
    name = config_name.strip()
    if not name:
        return folder
    if folder.startswith("config/"):
        return folder
    return f"config/{name}/{folder}"
