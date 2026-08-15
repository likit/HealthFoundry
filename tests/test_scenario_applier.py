from datetime import date

from healthfoundry import (
    AssessmentContext,
    AllPeopleSelector,
    HierarchyConfig,
    LaboratoryCatalog,
    LaboratoryPanel,
    LaboratoryResultModel,
    LaboratoryTestDefinition,
    PopulationConfig,
    RandomSource,
    ScenarioEngine,
    ScenarioEventApplier,
    ScenarioRule,
    Schedule,
    SimulationConfig,
    WorldBuilder,
)


def test_scenario_applier_creates_assessment_and_lab_records() -> None:
    config = SimulationConfig(42, date(2026, 1, 1), 1)
    world = WorldBuilder().build(
        "North Valley Clinic",
        config,
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(1, ["Ada"], ["Lovelace"]),
    )
    person = world.people[0]
    organization = world.organizations[0]
    glucose = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("BASIC", "Basic panel", (glucose.id,))
    catalog = LaboratoryCatalog(
        tests=(glucose,),
        panels=(panel,),
        result_models=(LaboratoryResultModel(glucose.id, 100.0, 10.0),),
    )
    events = ScenarioEngine(RandomSource(7)).generate_events(
        world,
        config,
        (ScenarioRule("annual", "health_assessment", AllPeopleSelector(), Schedule.once()),),
    )

    result = ScenarioEventApplier(RandomSource(8)).apply(
        world,
        events,
        catalog,
        panel_code="BASIC",
        assessment_context=AssessmentContext.PREVENTIVE,
    )

    assert result.assessments[0].person_id == person.id
    assert result.assessments[0].organization_id == organization.id
    assert len(result.laboratory_orders) == 1
    assert len(result.laboratory_observations) == 1

