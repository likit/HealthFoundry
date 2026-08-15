"""Create and display a tiny deterministic HealthFoundry organization."""

from datetime import date

from healthfoundry import HierarchyConfig, SimulationConfig, WorldBuilder


def main() -> None:
    simulation_config = SimulationConfig(
        random_seed=42,
        start_date=date(2026, 1, 1),
        years=1,
    )
    hierarchy_config = HierarchyConfig.from_names(
        ["Clinical Services", "Laboratory"]
    )

    world = WorldBuilder().build(
        organization_name="North Valley Clinic",
        simulation_config=simulation_config,
        hierarchy_config=hierarchy_config,
    )

    organization = world.organizations[0]
    hierarchy = world.hierarchies[0]
    units_by_id = {unit.id: unit for unit in hierarchy.units}

    print(f"Organization: {organization.name}")
    for unit in hierarchy.units:
        parent_name = (
            units_by_id[unit.parent_id].name if unit.parent_id is not None else "(root)"
        )
        print(f"- {unit.name} | parent: {parent_name}")


if __name__ == "__main__":
    main()

