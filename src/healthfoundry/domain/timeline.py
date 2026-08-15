"""Offline scenario timeline primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from healthfoundry.domain.organization import OrganizationId
from healthfoundry.domain.person import PersonId


@dataclass(frozen=True, slots=True)
class TimelineEventId:
    """Stable identity for an event in an offline scenario timeline."""

    value: UUID

    @classmethod
    def new(cls) -> "TimelineEventId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """A dated orchestration event produced by a scenario rule."""

    id: TimelineEventId
    occurred_on: date
    event_type: str
    source_rule: str
    person_id: PersonId | None = None
    organization_id: OrganizationId | None = None
    sequence: int = 0
    caused_by: TimelineEventId | None = None

    def __post_init__(self) -> None:
        if not self.event_type.strip():
            raise ValueError("Timeline event type must not be empty")
        if not self.source_rule.strip():
            raise ValueError("Timeline event source rule must not be empty")
        if self.sequence < 0:
            raise ValueError("Timeline event sequence must be non-negative")

    @classmethod
    def create(
        cls,
        occurred_on: date,
        event_type: str,
        source_rule: str,
        person_id: PersonId | None = None,
        organization_id: OrganizationId | None = None,
        sequence: int = 0,
        caused_by: TimelineEventId | None = None,
    ) -> "TimelineEvent":
        return cls(
            id=TimelineEventId.new(),
            occurred_on=occurred_on,
            event_type=event_type,
            source_rule=source_rule,
            person_id=person_id,
            organization_id=organization_id,
            sequence=sequence,
            caused_by=caused_by,
        )

    @property
    def sort_key(self) -> tuple[date, int, str]:
        """Return the stable ordering key used by an offline scenario engine."""

        return self.occurred_on, self.sequence, str(self.id)
