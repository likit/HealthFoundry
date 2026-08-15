"""Generate a diagnostic visit and a 30-day follow-up visit."""

from datetime import date

from healthfoundry import (
    AfterEvent,
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
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 1)
    world = WorldBuilder().build(
        "North Valley Clinic",
        simulation_config,
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(1, ["Ada"], ["Lovelace"]),
    )
    rules = (
        ScenarioRule(
            name="diagnostic_visit_rule",
            event_type="diagnostic_visit",
            selector=AllPeopleSelector(),
            schedule=Schedule.once(),
        ),
        ScenarioRule(
            name="diagnostic_follow_up_rule",
            event_type="follow_up_visit",
            selector=AllPeopleSelector(),
            after=AfterEvent("diagnostic_visit", delay_days=30),
        ),
    )

    events = ScenarioEngine(RandomSource(7)).generate_events(
        world,
        simulation_config,
        rules,
    )

    for event in events:
        caused_by = str(event.caused_by) if event.caused_by else "none"
        print(
            f"{event.occurred_on} | {event.event_type} | "
            f"rule={event.source_rule} | caused_by={caused_by}"
        )


if __name__ == "__main__":
    main()

