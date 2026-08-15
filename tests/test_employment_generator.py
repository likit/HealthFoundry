from datetime import date
from uuid import UUID

from healthfoundry import (
    EmploymentGenerator,
    HierarchyConfig,
    OrganizationHierarchyGenerator,
    OrganizationId,
    Person,
    RandomSource,
)


def test_employment_generator_assigns_each_person() -> None:
    organization_id = OrganizationId(UUID(int=1))
    hierarchy = OrganizationHierarchyGenerator(RandomSource(42)).generate(
        organization_id,
        HierarchyConfig.from_names(["Hospital", "Laboratory"]),
    )
    people = (Person.create("Ada", "Lovelace"), Person.create("Grace", "Hopper"))

    episodes = EmploymentGenerator(RandomSource(42)).assign_initial(
        people,
        organization_id,
        hierarchy,
        date(2026, 1, 1),
    )

    assert tuple(episode.person_id for episode in episodes) == tuple(
        person.id for person in people
    )
    assert all(episode.end_date is None for episode in episodes)

