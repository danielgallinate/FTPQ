"""Rutas de datos — dev (repo), instalado (~/.pde-desktop) o portable (./data)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

PORTABLE_MARKER = "portable.marker"
DATA_DIR_NAME = "data"


def _env_portable_flag() -> bool:
    return os.environ.get("PDE_DESKTOP_PORTABLE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def frozen_executable_dir() -> Path | None:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return None


def find_portable_root(start: Path | None = None) -> Path | None:
    if start is None:
        exe_dir = frozen_executable_dir()
        start = exe_dir if exe_dir is not None else _repo_root()
    current = start.resolve()
    for path in (current, *current.parents):
        if (path / PORTABLE_MARKER).is_file():
            return path
    return None


def is_portable() -> bool:
    if _env_portable_flag():
        return True
    return find_portable_root() is not None


def portable_root() -> Path | None:
    if _env_portable_flag():
        found = find_portable_root()
        if found is not None:
            return found
        exe_dir = frozen_executable_dir()
        if exe_dir is not None:
            return exe_dir.parent if sys.platform == "win32" else exe_dir
        return _repo_root()
    return find_portable_root()


def user_data_dir() -> Path:
    root = portable_root()
    if root is not None:
        directory = root / DATA_DIR_NAME
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return Path.home() / ".pde-desktop"


def resolve_profiles_dir() -> Path:
    if is_portable() or getattr(sys, "frozen", False):
        directory = user_data_dir() / "profiles"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return _repo_root() / "profiles"


def default_downloads_dir() -> Path:
    if is_portable() or getattr(sys, "frozen", False):
        directory = user_data_dir() / "downloads"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return _repo_root() / "downloads"


def portable_ssh_dir() -> Path:
    directory = user_data_dir() / "ssh"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def resolve_profile_path(raw: str | Path) -> Path:
    text = str(raw).strip()
    if not text:
        return Path(text)
    path = Path(text)
    if text.startswith("~") or path.is_absolute():
        return path.expanduser()
    root = portable_root()
    if root is not None:
        return (root / path).resolve()
    return path.expanduser()


def path_for_json(path: Path) -> str:
    expanded = path.expanduser()
    root = portable_root()
    if root is not None:
        try:
            rel = expanded.resolve().relative_to(root.resolve())
            return rel.as_posix()
        except ValueError:
            pass
    try:
        rel = expanded.resolve().relative_to(Path.home().resolve())
        return "~/" + rel.as_posix()
    except ValueError:
        return expanded.as_posix()
