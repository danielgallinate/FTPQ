"""Callback de progreso para descargas SFTP — (bytes_transferidos, bytes_totales)."""
from __future__ import annotations

import time
from typing import Callable

DownloadProgressCallback = Callable[[int, int], None]


class ThrottledDownloadProgress:
    """Reduce callbacks (Paramiko + UI) — evita miles de señales por archivo."""

    def __init__(
        self,
        callback: DownloadProgressCallback | None,
        *,
        min_interval_seconds: float = 0.25,
    ) -> None:
        self._callback = callback
        self._min_interval = min_interval_seconds
        self._last_at = 0.0
        self._last_pct = -1

    def __call__(self, transferred: int, total: int) -> None:
        if self._callback is None:
            return
        if total <= 0:
            self._callback(transferred, total)
            return
        pct = min(100, transferred * 100 // total)
        now = time.monotonic()
        if transferred < total:
            if pct == self._last_pct and now - self._last_at < self._min_interval:
                return
        self._last_at = now
        self._last_pct = pct
        self._callback(transferred, total)
