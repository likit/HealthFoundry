"""Generate an offline event timeline from scenario rules."""

from datetime import date

from healthfoundry import (
    ActiveEmployeesSelector,
    AllPeopleSelector,
    HierarchyConfig,
    PopulationConfig,
    RandomSource,
    ScenarioEngine,
    ScenarioRule,
    Schedule,
    SimulationConfig,
    WorldBuilder,
)


def main() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 3)
    world = WorldBuilder().build(
        "North Valley Clinic",
        simulation_config,
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(
            2,
            ["Ada", "Grace"],
            ["Lovelace", "Hopper"],
        ),
    )

    rules = (
        ScenarioRule(
            name="annual_employee_assessment",
            event_type="health_assessment",
            selector=ActiveEmployeesSelector(),
            schedule=Schedule.annual(),
        ),
        ScenarioRule(
            name="biennial_population_snapshot",
            event_type="population_snapshot",
            selector=AllPeopleSelector(),
            schedule=Schedule.every_years(2),
        ),
    )
    events = ScenarioEngine(RandomSource(7)).generate_events(
        world,
        simulation_config,
        rules,
    )

    for event in events:
        print(
            f"{event.occurred_on} | {event.event_type} | "
            f"rule={event.source_rule} | person={event.person_id}"
        )


if __name__ == "__main__":
    main()
