from datetime import date

from healthfoundry import (
    AssessmentContext,
    AssessmentStatus,
    HealthAssessment,
    HealthAssessmentId,
    Organization,
    Person,
)


def test_health_assessment_supports_multiple_contexts() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")

    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.OCCUPATIONAL,
        AssessmentStatus.COMPLETED,
    )

    assert isinstance(assessment.id, HealthAssessmentId)
    assert assessment.context is AssessmentContext.OCCUPATIONAL
    assert assessment.status is AssessmentStatus.COMPLETED

