"""Generate a tiny Thai-named workforce for a synthetic organization."""

from datetime import date

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
    SimulationConfig,
    WorldBuilder,
)


def main() -> None:
    simulation_config = SimulationConfig(
        random_seed=42,
        start_date=date(2026, 1, 1),
        years=1,
    )
    hierarchy_config = HierarchyConfig.from_names(
        ["Clinical Services", "Laboratory", "Radiology"]
    )
    population_config = PopulationConfig(
        count=3,
        locale="th_TH",
        minimum_age=25,
        maximum_age=60,
    )

    world = WorldBuilder().build(
        organization_name="North Valley Clinic",
        simulation_config=simulation_config,
        hierarchy_config=hierarchy_config,
        population_config=population_config,
    )

    units_by_id = {
        unit.id: unit
        for hierarchy in world.hierarchies
        for unit in hierarchy.units
    }
    people_by_id = {person.id: person for person in world.people}

    print(f"Organization: {world.organizations[0].name}")
    print("Workforce:")
    for episode in world.employment_episodes:
        person = people_by_id[episode.person_id]
        unit = units_by_id[episode.unit_id]
        print(f"- {person.full_name} -> {unit.name}")


if __name__ == "__main__":
    main()

