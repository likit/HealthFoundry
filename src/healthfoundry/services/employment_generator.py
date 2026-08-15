"""Generate initial employment episodes for a population."""

from __future__ import annotations

from datetime import date

from healthfoundry.domain.employment import EmploymentEpisode, EmploymentEpisodeId
from healthfoundry.domain.hierarchy import OrganizationHierarchy
from healthfoundry.domain.organization import OrganizationId
from healthfoundry.domain.person import Person
from healthfoundry.services.randomness import RandomSource


class EmploymentGenerator:
    """Assign people to units at the beginning of a simulation."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def assign_initial(
        self,
        people: tuple[Person, ...],
        organization_id: OrganizationId,
        hierarchy: OrganizationHierarchy,
        start_date: date,
    ) -> tuple[EmploymentEpisode, ...]:
        if hierarchy.organization_id != organization_id:
            raise ValueError("Hierarchy must belong to the organization")
        if not hierarchy.units and people:
            raise ValueError("Cannot assign people without organizational units")

        return tuple(
            EmploymentEpisode(
                id=EmploymentEpisodeId(self._randomness.uuid()),
                person_id=person.id,
                organization_id=organization_id,
                unit_id=self._randomness.choose(hierarchy.units).id,
                start_date=start_date,
            )
            for person in people
        )
