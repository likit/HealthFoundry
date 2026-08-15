from datetime import date

import pytest

from healthfoundry import (
    ActiveEmployeesSelector,
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


def _world():
    return WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 3),
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(2, ["Ada", "Grace"], ["Lovelace", "Hopper"]),
    )


def test_scenario_engine_generates_annual_events_for_active_employees() -> None:
    world = _world()
    config = SimulationConfig(42, date(2026, 1, 1), 3)
    rule = ScenarioRule(
        "annual_assessment",
        "health_assessment",
        ActiveEmployeesSelector(),
        Schedule.annual(),
    )

    events = ScenarioEngine(RandomSource(7)).generate_events(world, config, (rule,))

    assert len(events) == 6
    assert [event.occurred_on for event in events[:2]] == [date(2026, 1, 1)] * 2
    assert all(event.source_rule == "annual_assessment" for event in events)


def test_all_people_selector_includes_people_without_employment() -> None:
    world = _world()
    unemployed = world.people[0]
    world = type(world)(organizations=world.organizations, people=(unemployed,))

    assert AllPeopleSelector().select(world, date(2026, 1, 1)) == (unemployed,)
    assert ActiveEmployeesSelector().select(world, date(2026, 1, 1)) == ()


def test_scenario_rule_rejects_invalid_interval() -> None:
    with pytest.raises(ValueError, match="at least one year"):
        ScenarioRule("annual", "assessment", AllPeopleSelector(), Schedule(interval_years=0))


def test_schedule_can_generate_one_time_events() -> None:
    world = _world()
    config = SimulationConfig(42, date(2026, 1, 1), 3)
    rule = ScenarioRule(
        "baseline_snapshot",
        "population_snapshot",
        AllPeopleSelector(),
        Schedule.once(start_offset_years=1),
    )

    events = ScenarioEngine(RandomSource(7)).generate_events(world, config, (rule,))

    assert {event.occurred_on for event in events} == {date(2027, 1, 1)}


def test_scenario_engine_generates_day_level_follow_up() -> None:
    world = _world()
    config = SimulationConfig(42, date(2026, 1, 1), 1)
    rules = (
        ScenarioRule(
            "diagnostic_visit_rule",
            "diagnostic_visit",
            AllPeopleSelector(),
            schedule=Schedule.once(),
        ),
        ScenarioRule(
            "diagnostic_follow_up",
            "follow_up_visit",
            AllPeopleSelector(),
            after=AfterEvent("diagnostic_visit", delay_days=30),
        ),
    )

    events = ScenarioEngine(RandomSource(7)).generate_events(world, config, rules)

    assert len(events) == 4
    assert events[2].occurred_on == date(2026, 1, 31)
    assert events[2].caused_by is not None
