"""Workforce events in a synthetic healthcare organization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from healthfoundry.domain.organization import (
    OrganizationId,
    OrganizationUnitId,
)
from healthfoundry.domain.person import PersonId


class WorkforceEventType(StrEnum):
    """Supported changes to a person's workforce status."""

    HIRE = "hire"
    TRANSFER = "transfer"
    RESIGNATION = "resignation"
    RETIREMENT = "retirement"


@dataclass(frozen=True, slots=True)
class WorkforceEventId:
    """Stable identity for a workforce event."""

    value: UUID

    @classmethod
    def new(cls) -> "WorkforceEventId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class WorkforceEvent:
    """A dated workforce change for one person and organization."""

    id: WorkforceEventId
    person_id: PersonId
    organization_id: OrganizationId
    occurred_on: date
    event_type: WorkforceEventType
    unit_id: OrganizationUnitId | None = None
    from_unit_id: OrganizationUnitId | None = None
    to_unit_id: OrganizationUnitId | None = None

    def __post_init__(self) -> None:
        if self.event_type is WorkforceEventType.HIRE and self.unit_id is None:
            raise ValueError("Hire event requires a unit")
        if self.event_type is WorkforceEventType.TRANSFER:
            if self.from_unit_id is None or self.to_unit_id is None:
                raise ValueError("Transfer event requires source and destination units")
            if self.from_unit_id == self.to_unit_id:
                raise ValueError("Transfer event requires different source and destination units")
        if self.event_type in {
            WorkforceEventType.RESIGNATION,
            WorkforceEventType.RETIREMENT,
        } and any((self.unit_id, self.from_unit_id, self.to_unit_id)):
            raise ValueError("Separation events must not specify organizational units")

    @classmethod
    def hire(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        occurred_on: date,
        unit_id: OrganizationUnitId,
    ) -> "WorkforceEvent":
        return cls(
            id=WorkforceEventId.new(),
            person_id=person_id,
            organization_id=organization_id,
            occurred_on=occurred_on,
            event_type=WorkforceEventType.HIRE,
            unit_id=unit_id,
        )

    @classmethod
    def transfer(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        occurred_on: date,
        from_unit_id: OrganizationUnitId,
        to_unit_id: OrganizationUnitId,
    ) -> "WorkforceEvent":
        return cls(
            id=WorkforceEventId.new(),
            person_id=person_id,
            organization_id=organization_id,
            occurred_on=occurred_on,
            event_type=WorkforceEventType.TRANSFER,
            from_unit_id=from_unit_id,
            to_unit_id=to_unit_id,
        )

    @classmethod
    def resignation(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        occurred_on: date,
    ) -> "WorkforceEvent":
        return cls(
            id=WorkforceEventId.new(),
            person_id=person_id,
            organization_id=organization_id,
            occurred_on=occurred_on,
            event_type=WorkforceEventType.RESIGNATION,
        )

    @classmethod
    def retirement(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        occurred_on: date,
    ) -> "WorkforceEvent":
        return cls(
            id=WorkforceEventId.new(),
            person_id=person_id,
            organization_id=organization_id,
            occurred_on=occurred_on,
            event_type=WorkforceEventType.RETIREMENT,
        )

