"""Persistencia de perfil — un solo JSON local."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from core.app_profile import AppProfile
from core.app_paths import resolve_profiles_dir

DEFAULT_PROFILE_ID = "default"


@runtime_checkable
class IProfileStore(Protocol):
    def load(self) -> AppProfile: ...

    def save(self, profile: AppProfile) -> None: ...


class JsonProfileStore:
    def __init__(self, profiles_dir: Path | None = None) -> None:
        self._dir = profiles_dir or resolve_profiles_dir()
        self._path = self._dir / f"{DEFAULT_PROFILE_ID}.json"

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AppProfile:
        if not self._path.is_file():
            profile = AppProfile.default()
            profile.profile_id = DEFAULT_PROFILE_ID
            self.save(profile)
            return profile
        return AppProfile.load_json_file(self._path)

    def save(self, profile: AppProfile) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        payload = profile.to_json_dict()
        payload["profile_id"] = DEFAULT_PROFILE_ID
        self._path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
