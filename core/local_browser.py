"""Explorador de archivos local — solo lectura, formatos viewables."""
from __future__ import annotations

import string
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from core.file_view import is_viewable_extension


@dataclass(frozen=True, slots=True)
class LocalEntry:
    name: str
    absolute_path: Path
    is_dir: bool
    ext: str
    size_bytes: int
    modified: datetime | None


@dataclass(frozen=True, slots=True)
class LocalListing:
    """Listado UI — ``current_path`` None = nivel raíz (unidades)."""

    current_path: Path | None
    display_path: str
    entries: tuple[LocalEntry, ...]


def storage_roots() -> tuple[Path, ...]:
    """Unidades montadas — C:/ D:/ en Windows; /Volumes/* en macOS."""
    roots: list[Path] = []
    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            drive = Path(f"{letter}:/")
            try:
                if drive.exists():
                    roots.append(drive)
            except OSError:
                continue
    else:
        volumes = Path("/Volumes")
        if volumes.is_dir():
            try:
                for entry in volumes.iterdir():
                    if entry.is_dir():
                        roots.append(entry.resolve())
            except OSError:
                pass
        if not roots:
            roots.append(Path("/"))
    return tuple(sorted(roots, key=lambda p: str(p).casefold()))


def is_storage_root(path: Path) -> bool:
    resolved = path.resolve()
    if sys.platform == "win32":
        normalized = str(resolved).replace("/", "\\").rstrip("\\") + "\\"
        return len(normalized) == 3 and normalized[1] == ":"
    return resolved in storage_roots()


def navigate_up(path: Path) -> Path | None:
    """Sube un nivel; retorna None al llegar al listado de unidades."""
    if is_storage_root(path):
        return None
    parent = path.parent
    if parent == path:
        return None
    if sys.platform != "win32" and parent == Path("/"):
        return None
    return parent.resolve()


def resolve_folder_open(current: Path | None, folder_name: str) -> Path | None:
    """Resuelve doble clic en carpeta o unidad desde ``current``."""
    name = folder_name.rstrip("/")
    if name == "..":
        if current is None:
            return None
        return navigate_up(current)
    if current is None:
        for root in storage_roots():
            if root.name == name or str(root) == name or _root_label(root) == name:
                return root
        candidate = Path(name)
        if candidate.is_dir():
            return candidate.resolve()
        return None
    target = (current / name).resolve()
    if target.is_dir():
        return target
    return None


def list_directory(path: Path | None) -> LocalListing:
    if path is None:
        return _list_roots()
    return _list_folder(path.resolve())


def default_start_path(download_dir: Path) -> Path:
    expanded = download_dir.expanduser()
    if expanded.is_dir():
        return expanded.resolve()
    home = Path.home()
    return home.resolve()


def home_path() -> Path:
    return Path.home().resolve()


def is_allowed_browser_path(path: Path) -> bool:
    resolved = path.resolve()
    home = home_path()
    if resolved == home or home in resolved.parents:
        return True
    parts = resolved.parts
    return len(parts) >= 2 and parts[0] == "/" and parts[1] == "Volumes"


def sanitize_browser_path(path: Path | None) -> Path | None:
    """Evita quedar en / o carpetas de sistema; vuelve al home del usuario."""
    if path is None:
        return None
    if is_allowed_browser_path(path):
        return path.resolve()
    return home_path()


def _list_roots() -> LocalListing:
    entries: list[LocalEntry] = []
    for root in storage_roots():
        entries.append(
            LocalEntry(
                name=_root_label(root),
                absolute_path=root,
                is_dir=True,
                ext="",
                size_bytes=0,
                modified=None,
            )
        )
    return LocalListing(
        current_path=None,
        display_path=_roots_display_label(),
        entries=tuple(entries),
    )


def _list_folder(path: Path) -> LocalListing:
    rows: list[LocalEntry] = []
    rows.append(
        LocalEntry(
            name="..",
            absolute_path=navigate_up(path) or path,
            is_dir=True,
            ext="",
            size_bytes=0,
            modified=None,
        )
    )
    try:
        children = sorted(path.iterdir(), key=lambda p: p.name.casefold())
    except OSError:
        children = []

    for child in children:
        try:
            if child.is_dir():
                rows.append(_entry_from_path(child, is_dir=True))
            elif child.is_file() and is_viewable_extension(child.name):
                rows.append(_entry_from_path(child, is_dir=False))
        except OSError:
            continue

    return LocalListing(
        current_path=path,
        display_path=str(path),
        entries=tuple(rows),
    )


def _entry_from_path(path: Path, *, is_dir: bool) -> LocalEntry:
    name = path.name
    if is_dir and name != "..":
        name = f"{name}/"
    size = 0
    modified: datetime | None = None
    if not is_dir:
        try:
            stat = path.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
        except OSError:
            pass
    else:
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            pass
    ext = "" if is_dir else (path.suffix or "")
    return LocalEntry(
        name=name,
        absolute_path=path.resolve(),
        is_dir=is_dir,
        ext=ext,
        size_bytes=size,
        modified=modified,
    )


def _root_label(root: Path) -> str:
    if sys.platform == "win32":
        return f"{root.drive}\\"
    return root.name or str(root)


def _roots_display_label() -> str:
    if sys.platform == "win32":
        return "PC"
    return "/Volumes"
