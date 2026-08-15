from datetime import date

from healthfoundry import HierarchyConfig, SimulationConfig, WorldBuilder, WorldStore


def test_world_store_round_trips_world(tmp_path) -> None:
    world = WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 1),
        HierarchyConfig.from_names(["Clinical Services"]),
    )
    store = WorldStore(tmp_path / "worlds")

    metadata = store.save("North Valley Clinic", world, {"population_count": "20"})
    restored = store.open(metadata.slug)

    assert store.list()[0].name == "North Valley Clinic"
    assert restored == world
    assert store.settings(metadata.slug) == {"population_count": "20"}
