"""Generate and apply a health-assessment scenario event."""

from datetime import date

from healthfoundry import (
    AllPeopleSelector,
    AssessmentContext,
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


def main() -> None:
    simulation_config = SimulationConfig(42, date(2026, 1, 1), 1)
    world = WorldBuilder().build(
        "North Valley Clinic",
        simulation_config,
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(1, ["Ada"], ["Lovelace"]),
    )
    glucose = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("BASIC", "Basic panel", (glucose.id,))
    catalog = LaboratoryCatalog(
        tests=(glucose,),
        panels=(panel,),
        result_models=(LaboratoryResultModel(glucose.id, 100.0, 10.0),),
    )
    rule = ScenarioRule(
        name="annual_assessment",
        event_type="health_assessment",
        selector=AllPeopleSelector(),
        schedule=Schedule.once(),
    )

    events = ScenarioEngine(RandomSource(7)).generate_events(
        world,
        simulation_config,
        (rule,),
    )
    world = ScenarioEventApplier(RandomSource(8)).apply(
        world,
        events,
        catalog,
        panel_code="BASIC",
        assessment_context=AssessmentContext.PREVENTIVE,
    )

    print(f"Timeline events: {len(events)}")
    print(f"Assessments in world: {len(world.assessments)}")
    for observation in world.laboratory_observations:
        print(f"Glucose result: {observation.value:.2f} {observation.unit}")


if __name__ == "__main__":
    main()

