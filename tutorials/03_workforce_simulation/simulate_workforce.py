"""Run a small multi-year workforce simulation."""

from datetime import date

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
    SimulationConfig,
    WorkforceConfig,
    WorkforceSimulator,
    WorldBuilder,
    RandomSource,
)


def main() -> None:
    simulation_config = SimulationConfig(
        random_seed=42,
        start_date=date(2026, 1, 1),
        years=5,
    )
    hierarchy_config = HierarchyConfig.from_names(
        ["Clinical Services", "Laboratory", "Radiology"]
    )
    population_config = PopulationConfig.from_names(
        count=4,
        given_names=["Ada", "Grace", "Somchai", "Suda"],
        family_names=["Lovelace", "Hopper", "Prasert", "Siri"],
        minimum_age=40,
        maximum_age=68,
    )
    workforce_config = WorkforceConfig(
        transfer_rate=0.25,
        resignation_rate=0.15,
        retirement_age=65,
    )

    world = WorldBuilder().build(
        organization_name="North Valley Clinic",
        simulation_config=simulation_config,
        hierarchy_config=hierarchy_config,
        population_config=population_config,
    )
    world = WorkforceSimulator(RandomSource(7)).simulate(
        world,
        simulation_config,
        workforce_config,
    )

    print("Workforce events:")
    for event in world.workforce_events:
        print(f"- {event.occurred_on}: {event.event_type} ({event.person_id})")

    print("\nEmployment episodes:")
    for episode in world.employment_episodes:
        print(
            f"- {episode.person_id}: {episode.start_date} -> "
            f"{episode.end_date or 'active'}"
        )


if __name__ == "__main__":
    main()
