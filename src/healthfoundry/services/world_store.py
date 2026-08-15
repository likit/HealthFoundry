"""Persistent local storage for user-created worlds."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from healthfoundry.domain.world import World


@dataclass(frozen=True, slots=True)
class WorldMetadata:
    name: str
    slug: str
    modified_at: datetime


class WorldStore:
    """Save, list, open, and delete local world snapshots."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (Path.home() / ".healthfoundry" / "worlds")
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, world: World, settings: dict | None = None) -> WorldMetadata:
        slug = _slugify(name)
        directory = self.root / slug
        directory.mkdir(parents=True, exist_ok=True)
        metadata = {"name": name, "slug": slug, "modified_at": datetime.now().isoformat()}
        if settings is not None:
            metadata["settings"] = settings
        (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        (directory / "world.json").write_text(world.to_json() + "\n", encoding="utf-8")
        return WorldMetadata(name, slug, datetime.fromisoformat(metadata["modified_at"]))

    def list(self) -> tuple[WorldMetadata, ...]:
        results = []
        for metadata_path in sorted(self.root.glob("*/metadata.json")):
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
            results.append(WorldMetadata(data["name"], data["slug"], datetime.fromisoformat(data["modified_at"])))
        return tuple(results)

    def open(self, slug: str) -> World:
        return World.from_json((self.root / slug / "world.json").read_text(encoding="utf-8"))

    def settings(self, slug: str) -> dict:
        """Return the saved GUI settings for a world, if any."""

        metadata_path = self.root / slug / "metadata.json"
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return dict(data.get("settings", {}))

    def delete(self, slug: str) -> None:
        shutil.rmtree(self.root / slug)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("World name must contain letters or numbers")
    return slug
