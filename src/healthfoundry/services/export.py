"""Canonical serialization for generated worlds."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID

from healthfoundry.domain.world import World


class WorldJsonExporter:
    """Export a canonical world as deterministic JSON."""

    def to_dict(self, world: World) -> dict[str, Any]:
        return _serialize(world)

    def to_json(self, world: World) -> str:
        return json.dumps(
            self.to_dict(world),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        dataclass_fields = fields(value)
        if len(dataclass_fields) == 1 and dataclass_fields[0].name == "value":
            identifier = getattr(value, "value")
            if isinstance(identifier, UUID):
                return str(identifier)
        return {
            field.name: _serialize(getattr(value, field.name))
            for field in dataclass_fields
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (UUID, date)):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_serialize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_serialize(item) for item in value)
    return value
