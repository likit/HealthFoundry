"""Run a complete assessment-to-laboratory workflow."""

from datetime import date

from healthfoundry import (
    AssessmentContext,
    AssessmentRunner,
    AssessmentStatus,
    HealthAssessment,
    HierarchyConfig,
    LaboratoryPanel,
    LaboratoryCatalog,
    LaboratoryResultModel,
    LaboratoryTestDefinition,
    PopulationConfig,
    RandomSource,
    SimulationConfig,
    WorldBuilder,
)


def main() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 1)
    world = WorldBuilder().build(
        organization_name="North Valley Clinic",
        simulation_config=simulation_config,
        hierarchy_config=HierarchyConfig.from_names(["Clinical Services"]),
        population_config=PopulationConfig.from_names(
            2,
            ["Ada", "Grace"],
            ["Lovelace", "Hopper"],
            minimum_age=25,
            maximum_age=60,
        ),
    )

    person = world.people[0]
    organization = world.organizations[0]
    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.PREVENTIVE,
        AssessmentStatus.COMPLETED,
    )
    glucose = LaboratoryTestDefinition.create(
        "GLU", "Glucose", "serum", "mg/dL"
    )
    hemoglobin = LaboratoryTestDefinition.create(
        "HGB", "Hemoglobin", "whole blood", "g/dL"
    )
    panel = LaboratoryPanel.create(
        "BASIC",
        "Basic health assessment",
        (glucose.id, hemoglobin.id),
    )

    catalog = LaboratoryCatalog(
        tests=(glucose, hemoglobin),
        panels=(panel,),
        result_models=(
            LaboratoryResultModel(glucose.id, 100.0, 10.0),
            LaboratoryResultModel(hemoglobin.id, 14.0, 1.0),
        ),
    )
    world = AssessmentRunner(RandomSource(99)).run(
        world, assessment, catalog, panel_code="BASIC"
    )

    print(f"Assessment for: {person.full_name}")
    definitions_by_id = {glucose.id: glucose, hemoglobin.id: hemoglobin}
    for observation in world.laboratory_observations:
        definition = definitions_by_id[observation.test_definition_id]
        print(
            f"- {definition.code}: "
            f"{observation.value:.2f} {observation.unit}"
        )


if __name__ == "__main__":
    main()
