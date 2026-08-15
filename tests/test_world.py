from datetime import date

import pytest

from healthfoundry import (
    AssessmentContext,
    AssessmentLaboratoryWorkflow,
    AssessmentStatus,
    EmploymentEpisode,
    Organization,
    OrganizationHierarchy,
    OrganizationalUnit,
    Person,
    WorkforceEvent,
    World,
    LaboratoryPanel,
    LaboratoryTestDefinition,
    RandomSource,
    HealthAssessment,
)


def test_world_can_build_a_consistent_minimal_slice() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    hierarchy = OrganizationHierarchy.empty(organization.id).add(unit)
    person = Person.create("Ada", "Lovelace")
    episode = EmploymentEpisode.create(
        person.id,
        organization.id,
        unit.id,
        date(2026, 1, 1),
    )
    event = WorkforceEvent.hire(
        person.id,
        organization.id,
        date(2026, 1, 1),
        unit.id,
    )

    world = (
        World.empty()
        .add_organization(organization)
        .add_hierarchy(hierarchy)
        .add_person(person)
        .add_employment_episode(episode)
        .add_workforce_event(event)
    )

    assert world.organizations == (organization,)
    assert world.people == (person,)
    assert world.employment_episodes == (episode,)
    assert world.workforce_events == (event,)


def test_world_rejects_episode_for_unknown_person() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    hierarchy = OrganizationHierarchy.empty(organization.id).add(unit)
    person = Person.create("Ada", "Lovelace")
    episode = EmploymentEpisode.create(
        person.id,
        organization.id,
        unit.id,
        date(2026, 1, 1),
    )

    world = World.empty().add_organization(organization).add_hierarchy(hierarchy)

    with pytest.raises(ValueError, match="must reference a person"):
        world.add_employment_episode(episode)


def test_world_can_store_assessment_laboratory_workflow() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    assessment = HealthAssessment.create(
        person.id,
        organization.id,
        date(2026, 1, 1),
        AssessmentContext.PREVENTIVE,
        AssessmentStatus.COMPLETED,
    )
    definition = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    panel = LaboratoryPanel.create("ANNUAL", "Annual assessment", (definition.id,))
    output = AssessmentLaboratoryWorkflow(RandomSource(42)).run(
        assessment, panel, (definition,), {"GLU": (100.0, 10.0)}
    )
    world = (
        World.empty()
        .add_organization(organization)
        .add_person(person)
        .add_assessment(assessment)
        .add_test_definition(definition)
        .add_laboratory_panel(panel)
        .add_laboratory_order(output.orders[0])
        .add_specimen(output.specimens[0])
        .add_laboratory_observation(output.observations[0])
    )

    assert len(world.laboratory_observations) == 1
