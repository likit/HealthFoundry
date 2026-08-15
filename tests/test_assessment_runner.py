from datetime import date

from healthfoundry import (
    AssessmentContext,
    AssessmentRunner,
    AssessmentStatus,
    HealthAssessment,
    LaboratoryPanel,
    LaboratoryCatalog,
    LaboratoryResultModel,
    LaboratoryTestDefinition,
    Organization,
    Person,
    RandomSource,
    World,
)


def test_assessment_runner_persists_complete_workflow() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    world = World.empty().add_organization(organization).add_person(person)
    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.PREVENTIVE,
        AssessmentStatus.COMPLETED,
    )
    definition = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("BASIC", "Basic panel", (definition.id,))

    catalog = LaboratoryCatalog(
        tests=(definition,),
        panels=(panel,),
        result_models=(LaboratoryResultModel(definition.id, 100.0, 10.0),),
    )
    result = AssessmentRunner(RandomSource(42)).run(
        world, assessment, catalog, panel_code="BASIC"
    )

    assert len(result.assessments) == 1
    assert len(result.laboratory_orders) == 1
    assert len(result.specimens) == 1
    assert len(result.laboratory_observations) == 1
