"""General health-assessment domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from healthfoundry.domain.organization import OrganizationId
from healthfoundry.domain.person import PersonId


class AssessmentContext(StrEnum):
    """Why a health assessment takes place."""

    OCCUPATIONAL = "occupational"
    PREVENTIVE = "preventive"
    DIAGNOSTIC = "diagnostic"
    RESEARCH = "research"
    EDUCATIONAL = "educational"


class AssessmentStatus(StrEnum):
    """Lifecycle status of an assessment."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    DECLINED = "declined"


@dataclass(frozen=True, slots=True)
class HealthAssessmentId:
    value: UUID

    @classmethod
    def new(cls) -> "HealthAssessmentId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class HealthAssessment:
    """A general-purpose assessment event for one person."""

    id: HealthAssessmentId
    person_id: PersonId
    organization_id: OrganizationId
    assessed_on: date
    context: AssessmentContext
    status: AssessmentStatus = AssessmentStatus.SCHEDULED

    @classmethod
    def create(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        assessed_on: date,
        context: AssessmentContext,
        status: AssessmentStatus = AssessmentStatus.SCHEDULED,
    ) -> "HealthAssessment":
        return cls(
            HealthAssessmentId.new(),
            person_id,
            organization_id,
            assessed_on,
            context,
            status,
        )

