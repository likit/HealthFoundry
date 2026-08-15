"""Annual workforce simulation."""

from __future__ import annotations

from datetime import date

from healthfoundry.config import SimulationConfig, WorkforceConfig
from healthfoundry.domain.employment import EmploymentEpisode, EmploymentEpisodeId
from healthfoundry.domain.workforce import (
    WorkforceEvent,
    WorkforceEventId,
    WorkforceEventType,
)
from healthfoundry.domain.world import World
from healthfoundry.services.randomness import RandomSource


class WorkforceSimulator:
    """Advance workforce history with deterministic annual events."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def simulate(
        self,
        world: World,
        simulation_config: SimulationConfig,
        workforce_config: WorkforceConfig,
    ) -> World:
        """Return a world with workforce events through the simulation window."""

        current = world
        for year_offset in range(1, simulation_config.years):
            current = self._advance_year(
                current,
                _anniversary(simulation_config.start_date, year_offset),
                workforce_config,
            )
        return current

    def _advance_year(
        self,
        world: World,
        occurred_on: date,
        config: WorkforceConfig,
    ) -> World:
        current = world
        active_episodes = [
            episode
            for episode in world.employment_episodes
            if episode.is_active_on(occurred_on)
        ]
        people_by_id = {person.id: person for person in current.people}
        for episode in active_episodes:
            person = people_by_id[episode.person_id]
            if (
                config.retirement_age is not None
                and person.date_of_birth is not None
                and _age_on(person.date_of_birth, occurred_on) >= config.retirement_age
            ):
                current = _close_episode(current, episode, occurred_on)
                current = current.add_workforce_event(
                    WorkforceEvent(
                        id=WorkforceEventId(self._randomness.uuid()),
                        person_id=episode.person_id,
                        organization_id=episode.organization_id,
                        occurred_on=occurred_on,
                        event_type=WorkforceEventType.RETIREMENT,
                    )
                )
                continue
            draw = self._randomness.probability()
            if draw < config.resignation_rate:
                current = _close_episode(current, episode, occurred_on)
                current = current.add_workforce_event(
                    WorkforceEvent(
                        id=WorkforceEventId(self._randomness.uuid()),
                        person_id=episode.person_id,
                        organization_id=episode.organization_id,
                        occurred_on=occurred_on,
                        event_type=WorkforceEventType.RESIGNATION,
                    )
                )
            elif draw < config.resignation_rate + config.transfer_rate:
                hierarchy = next(
                    hierarchy
                    for hierarchy in current.hierarchies
                    if hierarchy.organization_id == episode.organization_id
                )
                destinations = tuple(
                    unit for unit in hierarchy.units if unit.id != episode.unit_id
                )
                if not destinations:
                    continue
                destination = self._randomness.choose(destinations)
                current = _close_episode(current, episode, occurred_on)
                current = current.add_employment_episode(
                    EmploymentEpisode(
                        id=EmploymentEpisodeId(self._randomness.uuid()),
                        person_id=episode.person_id,
                        organization_id=episode.organization_id,
                        unit_id=destination.id,
                        start_date=occurred_on,
                    )
                )
                current = current.add_workforce_event(
                    WorkforceEvent(
                        id=WorkforceEventId(self._randomness.uuid()),
                        person_id=episode.person_id,
                        organization_id=episode.organization_id,
                        occurred_on=occurred_on,
                        event_type=WorkforceEventType.TRANSFER,
                        from_unit_id=episode.unit_id,
                        to_unit_id=destination.id,
                    )
                )
        return current


def _close_episode(
    world: World,
    episode: EmploymentEpisode,
    end_date: date,
) -> World:
    replacement = EmploymentEpisode(
        id=episode.id,
        person_id=episode.person_id,
        organization_id=episode.organization_id,
        unit_id=episode.unit_id,
        start_date=episode.start_date,
        end_date=end_date,
    )
    episodes = tuple(
        replacement if candidate.id == episode.id else candidate
        for candidate in world.employment_episodes
    )
    return World(
        organizations=world.organizations,
        hierarchies=world.hierarchies,
        people=world.people,
        employment_episodes=episodes,
        workforce_events=world.workforce_events,
    )


def _anniversary(start_date: date, year_offset: int) -> date:
    try:
        return start_date.replace(year=start_date.year + year_offset)
    except ValueError:
        # Treat February 29 as February 28 in non-leap years.
        return start_date.replace(month=2, day=28, year=start_date.year + year_offset)


def _age_on(date_of_birth: date, on_date: date) -> int:
    years = on_date.year - date_of_birth.year
    birthday = (on_date.month, on_date.day) >= (date_of_birth.month, date_of_birth.day)
    return years if birthday else years - 1
