import json
from datetime import date

from healthfoundry import (
    HierarchyConfig,
    SimulationConfig,
    WorldBuilder,
    WorldJsonExporter,
)


def test_world_json_export_is_structured_and_deterministic() -> None:
    world = WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 1),
        HierarchyConfig.from_names(["Clinical Services"]),
    )
    exporter = WorldJsonExporter()

    first = exporter.to_json(world)
    second = exporter.to_json(world)
    via_world = world.to_json()
    document = json.loads(first)

    assert first == second
    assert via_world == first
    assert document["organizations"][0]["name"] == "North Valley Clinic"
    assert document["hierarchies"][0]["units"][0]["name"] == "Clinical Services"
