"""Employment domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from healthfoundry.domain.organization import (
    OrganizationId,
    OrganizationUnitId,
)
from healthfoundry.domain.person import PersonId


@dataclass(frozen=True, slots=True)
class EmploymentEpisodeId:
    """Stable identity for an employment episode."""

    value: UUID

    @classmethod
    def new(cls) -> "EmploymentEpisodeId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class EmploymentEpisode:
    """A person's continuous employment in one organization unit."""

    id: EmploymentEpisodeId
    person_id: PersonId
    organization_id: OrganizationId
    unit_id: OrganizationUnitId
    start_date: date
    end_date: date | None = None

    def __post_init__(self) -> None:
        if self.end_date is not None and self.end_date <= self.start_date:
            raise ValueError("Employment episode end date must be after its start date")

    @classmethod
    def create(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        unit_id: OrganizationUnitId,
        start_date: date,
        end_date: date | None = None,
    ) -> "EmploymentEpisode":
        """Create an employment episode with a generated identity."""

        return cls(
            id=EmploymentEpisodeId.new(),
            person_id=person_id,
            organization_id=organization_id,
            unit_id=unit_id,
            start_date=start_date,
            end_date=end_date,
        )

    def is_active_on(self, at: date) -> bool:
        """Return whether the episode includes the given date."""

        return self.start_date <= at and (
            self.end_date is None or at < self.end_date
        )

