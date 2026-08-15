"""Canonical synthetic healthcare world aggregate."""

from __future__ import annotations

from dataclasses import dataclass

from healthfoundry.domain.employment import EmploymentEpisode
from healthfoundry.domain.hierarchy import OrganizationHierarchy
from healthfoundry.domain.organization import Organization, OrganizationUnitId
from healthfoundry.domain.person import Person
from healthfoundry.domain.workforce import WorkforceEvent


@dataclass(frozen=True, slots=True)
class World:
    """An immutable, internally consistent collection of domain entities."""

    organizations: tuple[Organization, ...] = ()
    hierarchies: tuple[OrganizationHierarchy, ...] = ()
    people: tuple[Person, ...] = ()
    employment_episodes: tuple[EmploymentEpisode, ...] = ()
    workforce_events: tuple[WorkforceEvent, ...] = ()

    @classmethod
    def empty(cls) -> "World":
        return cls()

    def add_organization(self, organization: Organization) -> "World":
        return World(
            organizations=(*self.organizations, organization),
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
        )

    def add_hierarchy(self, hierarchy: OrganizationHierarchy) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=(*self.hierarchies, hierarchy),
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
        )

    def add_person(self, person: Person) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=(*self.people, person),
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
        )

    def add_employment_episode(self, episode: EmploymentEpisode) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=(*self.employment_episodes, episode),
            workforce_events=self.workforce_events,
        )

    def add_workforce_event(self, event: WorkforceEvent) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=(*self.workforce_events, event),
        )

    def _validate(self) -> None:
        organization_ids = self._unique_ids(
            (organization.id for organization in self.organizations),
            "organization",
        )
        person_ids = self._unique_ids(
            (person.id for person in self.people),
            "person",
        )
        self._unique_ids(
            (episode.id for episode in self.employment_episodes),
            "employment episode",
        )
        self._unique_ids(
            (event.id for event in self.workforce_events),
            "workforce event",
        )

        hierarchy_by_organization = {}
        for hierarchy in self.hierarchies:
            if hierarchy.organization_id not in organization_ids:
                raise ValueError("Hierarchy must reference an organization in the world")
            if hierarchy.organization_id in hierarchy_by_organization:
                raise ValueError("World cannot contain duplicate organization hierarchies")
            hierarchy_by_organization[hierarchy.organization_id] = hierarchy

        for episode in self.employment_episodes:
            if episode.person_id not in person_ids:
                raise ValueError("Employment episode must reference a person in the world")
            if episode.organization_id not in organization_ids:
                raise ValueError("Employment episode must reference an organization in the world")
            if not self._unit_exists(
                hierarchy_by_organization.get(episode.organization_id), episode.unit_id
            ):
                raise ValueError("Employment episode must reference a unit in the world")

        for event in self.workforce_events:
            if event.person_id not in person_ids:
                raise ValueError("Workforce event must reference a person in the world")
            if event.organization_id not in organization_ids:
                raise ValueError("Workforce event must reference an organization in the world")
            hierarchy = hierarchy_by_organization.get(event.organization_id)
            for unit_id in (event.unit_id, event.from_unit_id, event.to_unit_id):
                if unit_id is not None and not self._unit_exists(hierarchy, unit_id):
                    raise ValueError("Workforce event must reference units in the world")

    @staticmethod
    def _unique_ids(ids, label: str) -> set:
        values = list(ids)
        if len(values) != len(set(values)):
            raise ValueError(f"World cannot contain duplicate {label} ids")
        return set(values)

    @staticmethod
    def _unit_exists(
        hierarchy: OrganizationHierarchy | None,
        unit_id: OrganizationUnitId,
    ) -> bool:
        return hierarchy is not None and any(unit.id == unit_id for unit in hierarchy.units)

    def __post_init__(self) -> None:
        self._validate()

