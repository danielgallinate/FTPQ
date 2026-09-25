"""Factory SFTP — mock (PDE_DESKTOP_MOCK=1) o paramiko real."""
from __future__ import annotations

import os

from core.sftp_browser import ISftpBrowser


def create_sftp_browser() -> ISftpBrowser:
    if os.environ.get("PDE_DESKTOP_MOCK") == "1":
        from mocks.mock_sftp_browser import MockSftpBrowser

        return MockSftpBrowser()
    from adapters.paramiko_sftp_browser import ParamikoSftpBrowser

    return ParamikoSftpBrowser()
