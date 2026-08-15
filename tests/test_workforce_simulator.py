from datetime import date

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
    SimulationConfig,
    WorkforceConfig,
    WorkforceEventType,
    WorkforceSimulator,
    WorldBuilder,
    RandomSource,
)


def _world():
    return WorldBuilder().build(
        "North Valley Hospital",
        SimulationConfig(42, date(2026, 1, 1), 3),
        HierarchyConfig.from_names(["Hospital", "Laboratory", "Radiology"]),
        PopulationConfig.from_names(1, ["Ada"], ["Lovelace"]),
    )


def test_workforce_simulator_records_resignation_and_closes_episode() -> None:
    world = _world()
    result = WorkforceSimulator(RandomSource(7)).simulate(
        world,
        SimulationConfig(42, date(2026, 1, 1), 3),
        WorkforceConfig(resignation_rate=1.0),
    )

    assert [event.event_type for event in result.workforce_events] == [
        WorkforceEventType.RESIGNATION,
    ]
    assert all(episode.end_date == date(2027, 1, 1) for episode in result.employment_episodes)


def test_workforce_simulator_is_reproducible() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 3)
    workforce_config = WorkforceConfig(transfer_rate=1.0)

    first = WorkforceSimulator(RandomSource(7)).simulate(
        _world(), simulation_config, workforce_config
    )
    second = WorkforceSimulator(RandomSource(7)).simulate(
        _world(), simulation_config, workforce_config
    )

    assert first == second


def test_workforce_simulator_retires_eligible_people() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 3)
    world = WorldBuilder().build(
        "North Valley Hospital",
        simulation_config,
        HierarchyConfig.from_names(["Hospital", "Laboratory"]),
        PopulationConfig.from_names(1, ["Ada"], ["Lovelace"]),
    )
    person = world.people[0]
    dated_person = type(person)(
        id=person.id,
        given_name=person.given_name,
        family_name=person.family_name,
        date_of_birth=date(1950, 1, 1),
    )
    world = type(world)(
        organizations=world.organizations,
        hierarchies=world.hierarchies,
        people=(dated_person,),
        employment_episodes=world.employment_episodes,
        workforce_events=world.workforce_events,
    )

    result = WorkforceSimulator(RandomSource(7)).simulate(
        world,
        simulation_config,
        WorkforceConfig(retirement_age=65),
    )

    assert [event.event_type for event in result.workforce_events] == [
        WorkforceEventType.RETIREMENT,
    ]
    assert result.employment_episodes[0].end_date == date(2027, 1, 1)
