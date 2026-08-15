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


def test_world_replace_people_removes_records_from_previous_population() -> None:
    organization = Organization.create("Clinic")
    old_person = Person.create("Old", "Person")
    new_person = Person.create("New", "Person")
    world = World.empty().add_organization(organization).add_person(old_person)

    replaced = world.replace_people((new_person,))

    assert replaced.people == (new_person,)
    assert replaced.employment_episodes == ()
    assert replaced.workforce_events == ()
    assert replaced.assessments == ()
    assert replaced.laboratory_orders == ()


def test_world_replace_hierarchy_replaces_units_and_clears_unit_dependent_records() -> None:
    organization = Organization.create("Clinic")
    old_unit = OrganizationalUnit.create(organization.id, "Old Unit")
    new_unit = OrganizationalUnit.create(organization.id, "New Unit")
    world = (
        World.empty()
        .add_organization(organization)
        .add_hierarchy(OrganizationHierarchy.empty(organization.id).add(old_unit))
    )

    replaced = world.replace_hierarchy(
        OrganizationHierarchy.empty(organization.id).add(new_unit)
    )

    assert replaced.hierarchies[0].units == (new_unit,)
    assert replaced.employment_episodes == ()
    assert replaced.workforce_events == ()


def test_world_remove_organization_removes_its_structure_and_people_records() -> None:
    organization = Organization.create("Clinic")
    unit = OrganizationalUnit.create(organization.id, "Unit")
    world = (
        World.empty()
        .add_organization(organization)
        .add_hierarchy(OrganizationHierarchy.empty(organization.id).add(unit))
    )

    removed = world.remove_organization(organization.id)

    assert removed.organizations == ()
    assert removed.hierarchies == ()


def test_world_replace_organization_people_preserves_other_organizations() -> None:
    first = Organization.create("First")
    second = Organization.create("Second")
    first_unit = OrganizationalUnit.create(first.id, "Unit")
    second_unit = OrganizationalUnit.create(second.id, "Unit")
    old_person = Person.create("Old", "First")
    other_person = Person.create("Other", "Second")
    new_person = Person.create("New", "First")
    world = (
        World.empty()
        .add_organization(first)
        .add_organization(second)
        .add_hierarchy(OrganizationHierarchy.empty(first.id).add(first_unit))
        .add_hierarchy(OrganizationHierarchy.empty(second.id).add(second_unit))
        .add_person(old_person)
        .add_person(other_person)
        .add_employment_episode(EmploymentEpisode.create(old_person.id, first.id, first_unit.id, date(2026, 1, 1)))
        .add_employment_episode(EmploymentEpisode.create(other_person.id, second.id, second_unit.id, date(2026, 1, 1)))
    )

    replaced = world.replace_organization_people(
        first.id,
        (new_person,),
        (EmploymentEpisode.create(new_person.id, first.id, first_unit.id, date(2026, 1, 1)),),
    )

    assert replaced.people == (other_person, new_person)
    assert {episode.organization_id for episode in replaced.employment_episodes} == {first.id, second.id}


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
