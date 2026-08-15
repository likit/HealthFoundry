from datetime import date

from healthfoundry import (
    HierarchyConfig,
    SimulationConfig,
    WorldBuilder,
)


def test_world_builder_creates_reproducible_initial_world() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 5)
    hierarchy_config = HierarchyConfig.from_names(
        ["Hospital", "Clinical Services", "Laboratory"]
    )

    first = WorldBuilder().build(
        "North Valley Hospital",
        simulation_config,
        hierarchy_config,
    )
    second = WorldBuilder().build(
        "North Valley Hospital",
        simulation_config,
        hierarchy_config,
    )

    assert first == second
    assert first.organizations[0].name == "North Valley Hospital"
    assert len(first.hierarchies[0].units) == 3
    assert first.people == ()

