"""Offline scenario rules and timeline generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

from healthfoundry.config import SimulationConfig
from healthfoundry.domain.person import Person
from healthfoundry.domain.timeline import TimelineEvent, TimelineEventId
from healthfoundry.domain.world import World
from healthfoundry.services.randomness import RandomSource


class PopulationSelector(Protocol):
    """Select people eligible for a scenario rule on a date."""

    def select(self, world: World, on_date: date) -> tuple[Person, ...]: ...


class AllPeopleSelector:
    def select(self, world: World, on_date: date) -> tuple[Person, ...]:
        return world.people


class ActiveEmployeesSelector:
    def select(self, world: World, on_date: date) -> tuple[Person, ...]:
        active_person_ids = {
            episode.person_id
            for episode in world.employment_episodes
            if episode.is_active_on(on_date)
        }
        return tuple(person for person in world.people if person.id in active_person_ids)


@dataclass(frozen=True, slots=True)
class Schedule:
    """A recurring or one-time schedule expressed in simulation years."""

    interval_years: int | None = 1
    interval_days: int | None = None
    start_offset_years: int = 0
    start_offset_days: int = 0
    repeat: bool = True

    def __post_init__(self) -> None:
        if (self.interval_years is None) == (self.interval_days is None):
            raise ValueError("Schedule must specify either years or days, but not both")
        if self.interval_years is not None and self.interval_years < 1:
            raise ValueError("Schedule interval must be at least one year")
        if self.interval_days is not None and self.interval_days < 1:
            raise ValueError("Schedule interval must be at least one day")
        if self.start_offset_years < 0:
            raise ValueError("Schedule start offset must be non-negative")
        if self.start_offset_days < 0:
            raise ValueError("Schedule day offset must be non-negative")

    @classmethod
    def annual(cls) -> "Schedule":
        return cls(interval_years=1)

    @classmethod
    def every_years(cls, years: int) -> "Schedule":
        return cls(interval_years=years)

    @classmethod
    def every_days(cls, days: int) -> "Schedule":
        return cls(interval_years=None, interval_days=days)

    @classmethod
    def once(cls, start_offset_years: int = 0) -> "Schedule":
        return cls(start_offset_years=start_offset_years, repeat=False)

    @classmethod
    def once_after_days(cls, days: int) -> "Schedule":
        return cls(start_offset_days=days, repeat=False)


@dataclass(frozen=True, slots=True)
class AfterEvent:
    """Trigger a rule after another event type occurs."""

    event_type: str
    delay_days: int = 0

    def __post_init__(self) -> None:
        if not self.event_type.strip():
            raise ValueError("After-event type must not be empty")
        if self.delay_days < 0:
            raise ValueError("After-event delay must be non-negative")


@dataclass(frozen=True, slots=True)
class ScenarioRule:
    """A recurring scheduled rule that emits timeline events."""

    name: str
    event_type: str
    selector: PopulationSelector
    schedule: Schedule | None = None
    after: AfterEvent | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Scenario rule name must not be empty")
        if not self.event_type.strip():
            raise ValueError("Scenario rule event type must not be empty")
        if (self.schedule is None) == (self.after is None):
            raise ValueError("Scenario rule must specify exactly one schedule or after-event trigger")


class ScenarioEngine:
    """Generate an offline event timeline from scheduled scenario rules."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def generate_events(
        self,
        world: World,
        simulation_config: SimulationConfig,
        rules: tuple[ScenarioRule, ...],
    ) -> tuple[TimelineEvent, ...]:
        events: list[TimelineEvent] = []
        for rule in rules:
            if rule.schedule is None:
                continue
            for occurred_on in _scheduled_dates(simulation_config, rule.schedule):
                eligible_people = rule.selector.select(world, occurred_on)
                for sequence, person in enumerate(eligible_people):
                    organization_id = _organization_for_person(world, person.id, occurred_on)
                    events.append(
                        TimelineEvent(
                            id=TimelineEventId(self._randomness.uuid()),
                            occurred_on=occurred_on,
                            event_type=rule.event_type,
                            source_rule=rule.name,
                            person_id=person.id,
                            organization_id=organization_id,
                            sequence=sequence,
                        )
                    )
        pending = list(events)
        generated = list(events)
        while pending:
            source_event = pending.pop(0)
            for rule in rules:
                if rule.after is None or rule.after.event_type != source_event.event_type:
                    continue
                eligible_ids = {
                    person.id
                    for person in rule.selector.select(world, source_event.occurred_on)
                }
                if source_event.person_id not in eligible_ids:
                    continue
                occurred_on = source_event.occurred_on + timedelta(days=rule.after.delay_days)
                follow_up = TimelineEvent(
                    id=TimelineEventId(self._randomness.uuid()),
                    occurred_on=occurred_on,
                    event_type=rule.event_type,
                    source_rule=rule.name,
                    person_id=source_event.person_id,
                    organization_id=source_event.organization_id,
                    caused_by=source_event.id,
                )
                generated.append(follow_up)
                pending.append(follow_up)
        return tuple(sorted(generated, key=lambda event: event.sort_key))


def _organization_for_person(world: World, person_id, on_date: date):
    active = [
        episode
        for episode in world.employment_episodes
        if episode.person_id == person_id and episode.is_active_on(on_date)
    ]
    return active[0].organization_id if active else None


def _anniversary(start_date: date, year_offset: int) -> date:
    try:
        return start_date.replace(year=start_date.year + year_offset)
    except ValueError:
        return start_date.replace(month=2, day=28, year=start_date.year + year_offset)


def _scheduled_dates(config: SimulationConfig, schedule: Schedule) -> tuple[date, ...]:
    start = _anniversary(config.start_date, schedule.start_offset_years)
    start += timedelta(days=schedule.start_offset_days)
    if not schedule.repeat:
        return (start,) if start < _anniversary(config.start_date, config.years) else ()
    if schedule.interval_days is not None:
        end = _anniversary(config.start_date, config.years)
        dates = []
        current = start
        while current < end:
            dates.append(current)
            current += timedelta(days=schedule.interval_days)
        return tuple(dates)
    return tuple(
        _anniversary(config.start_date, offset) + timedelta(days=schedule.start_offset_days)
        for offset in range(
            schedule.start_offset_years,
            config.years,
            schedule.interval_years or 1,
        )
    )
