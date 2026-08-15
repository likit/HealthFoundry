from datetime import date

import pytest

from healthfoundry import (
    EmploymentEpisode,
    Organization,
    OrganizationHierarchy,
    OrganizationalUnit,
    Person,
    WorkforceEvent,
    World,
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

