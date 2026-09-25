"""Mapeo rutas lógicas PDE ↔ paths SFTP (chroot Transfer Family)."""
from __future__ import annotations

DELIVERY_FOLDERS = frozenset({"scheduled", "requested", "archived"})
SFTP_ROOT = "."


def display_path(user: str, sftp_path: str) -> str:
    """Etiqueta navegador: user / [subcarpeta…]."""
    label = user.strip() or "SFTP"
    path = sftp_path.strip().strip("/")
    if not path or path == ".":
        return f"{label} /"
    return f"{label} / {path.replace('/', ' / ')}"



def to_sftp_path(logical_path: str) -> str:
    """config/{name}/{folder}/… → {folder} bajo home del usuario SFTP."""
    parts = [part for part in logical_path.strip("/").split("/") if part]
    if len(parts) >= 3 and parts[0] == "config" and parts[2] in DELIVERY_FOLDERS:
        return parts[2]
    if parts and parts[0] in DELIVERY_FOLDERS:
        return parts[0]
    return "/".join(parts) if parts else "."


def list_path_candidates(logical_path: str) -> list[str]:
    """Orden de intento: chroot relativo, lógica completa, absoluta."""
    if logical_path.strip() in (".", ""):
        return ["."]
    logical = logical_path.strip("/")
    candidates: list[str] = []
    sftp_rel = to_sftp_path(logical_path)
    for path in (sftp_rel, logical, f"/{logical}" if logical else ""):
        if path and path not in candidates:
            candidates.append(path)
    return candidates or ["."]


def resolve_list_path(current: str | None, remote_path: str) -> str:
    raw = remote_path.strip().replace("\\", "/")
    if raw == "..":
        if not current or current == ".":
            return "."
        parts = [part for part in current.split("/") if part]
        if len(parts) <= 1:
            return "."
        return "/".join(parts[:-1])
    if raw in (".", ""):
        return "."
    parts = [part for part in raw.strip("/").split("/") if part]
    return "/".join(parts) if parts else "."


def join_remote_path(current: str | None, name: str) -> str:
    """Une carpeta SFTP actual con nombre de archivo o subcarpeta."""
    stem = name.strip().strip("/")
    if stem == "..":
        return ".."
    base = (current or ".").strip().strip("/")
    if not base or base == ".":
        return stem
    return f"{base}/{stem}"
