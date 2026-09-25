"""Log local mínimo — errores y eventos de la app de escritorio."""
from __future__ import annotations

import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

from core.app_paths import user_data_dir

_FAULT_FILE_HANDLE = None


def log_file_path() -> Path:
    return user_data_dir() / "app.log"


def log_file_display() -> str:
    return str(log_file_path().expanduser())


def _lock_file() -> Path:
    return user_data_dir() / "session.lock"


def log_line(message: str) -> None:
    try:
        log_path = log_file_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {message}\n")
    except OSError:
        pass


def log_event(message: str) -> None:
    log_line(message)


def log_exception(context: str, exc: BaseException) -> None:
    log_line(f"{context}: {type(exc).__name__}: {exc}")
    for line in traceback.format_exception(type(exc), exc, exc.__traceback__):
        for part in line.rstrip().splitlines():
            log_line(f"  {part}")


def previous_session_unclean() -> bool:
    return _lock_file().is_file()


def mark_session_started() -> None:
    try:
        lock = _lock_file()
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(f"pid={os.getpid()}\n", encoding="utf-8")
    except OSError:
        pass


def mark_session_stopped() -> None:
    try:
        _lock_file().unlink(missing_ok=True)
    except OSError:
        pass


def install_runtime_logging() -> None:
    """Hooks globales + faulthandler — llamar una vez al iniciar la app."""
    global _FAULT_FILE_HANDLE
    try:
        log_path = log_file_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _FAULT_FILE_HANDLE = log_path.open("a", encoding="utf-8")
        import faulthandler

        faulthandler.enable(file=_FAULT_FILE_HANDLE, all_threads=True)
    except OSError:
        _FAULT_FILE_HANDLE = None

    def _excepthook(exc_type, exc, tb) -> None:
        if exc is not None:
            log_exception("uncaught", exc)
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        if args.exc_value is not None:
            name = args.thread.name if args.thread else "thread"
            log_exception(f"thread {name}", args.exc_value)

    threading.excepthook = _thread_hook
    log_event("PDE Desktop iniciado")
