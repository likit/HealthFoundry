from datetime import date

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
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


def test_world_builder_can_include_population() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 5)
    hierarchy_config = HierarchyConfig.from_names(["Hospital", "Laboratory"])
    population_config = PopulationConfig.from_names(
        2,
        ["Ada", "Grace"],
        ["Lovelace", "Hopper"],
    )

    world = WorldBuilder().build(
        "North Valley Hospital",
        simulation_config,
        hierarchy_config,
        population_config,
    )

    assert len(world.people) == 2
    assert {person.full_name for person in world.people} <= {
        "Ada Lovelace",
        "Ada Hopper",
        "Grace Lovelace",
        "Grace Hopper",
    }
    assert len(world.employment_episodes) == 2
    assert all(
        episode.start_date == date(2026, 1, 1)
        for episode in world.employment_episodes
    )
