from datetime import date

import pytest

from healthfoundry import (
    AssessmentContext,
    AssessmentLaboratoryWorkflow,
    AssessmentStatus,
    HealthAssessment,
    LaboratoryPanel,
    LaboratoryTestDefinition,
    Organization,
    Person,
    RandomSource,
)


def test_completed_assessment_creates_orders_specimens_and_observations() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.PREVENTIVE,
        AssessmentStatus.COMPLETED,
    )
    glucose = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("ANNUAL", "Annual assessment", (glucose.id,))

    result = AssessmentLaboratoryWorkflow(RandomSource(42)).run(
        assessment,
        panel,
        (glucose,),
        {"GLU": (100.0, 10.0)},
    )

    assert len(result.orders) == len(result.specimens) == len(result.observations) == 1
    assert result.specimens[0].order_id == result.orders[0].id
    assert result.observations[0].order_id == result.orders[0].id
    assert result.observations[0].unit == "mg/dL"


def test_assessment_workflow_requires_completed_assessment() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.PREVENTIVE,
    )
    glucose = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("ANNUAL", "Annual assessment", (glucose.id,))

    with pytest.raises(ValueError, match="completed assessment"):
        AssessmentLaboratoryWorkflow(RandomSource(42)).run(
            assessment, panel, (glucose,), {"GLU": (100.0, 10.0)}
        )

