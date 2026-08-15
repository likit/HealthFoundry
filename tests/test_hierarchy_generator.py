from uuid import UUID

import pytest

from healthfoundry import (
    HierarchyConfig,
    OrganizationHierarchyGenerator,
    OrganizationId,
    OrganizationUnitId,
    RandomSource,
)


def test_hierarchy_generator_is_reproducible() -> None:
    organization_id = OrganizationId(UUID(int=1))
    names = ("Hospital", "Clinical Services", "Laboratory", "Radiology")
    config = HierarchyConfig.from_names(names)
    first = OrganizationHierarchyGenerator(RandomSource(42)).generate(organization_id, config)
    second = OrganizationHierarchyGenerator(RandomSource(42)).generate(organization_id, config)

    assert first == second
    assert first.units[0].parent_id is None
    assert [unit.name for unit in first.units] == list(names)


def test_hierarchy_generator_rejects_empty_or_duplicate_names() -> None:
    generator = OrganizationHierarchyGenerator(RandomSource(42))
    organization_id = OrganizationId(UUID(int=1))

    with pytest.raises(ValueError, match="At least one"):
        generator.generate(organization_id, HierarchyConfig(()))
    with pytest.raises(ValueError, match="must be unique"):
        generator.generate(organization_id, HierarchyConfig(("Hospital", "Hospital")))


def test_random_uuid_is_seeded() -> None:
    assert RandomSource(1).uuid() == RandomSource(1).uuid()
    assert isinstance(RandomSource(1).uuid(), UUID)
    assert isinstance(OrganizationUnitId(UUID(int=1)), OrganizationUnitId)


def test_explicit_hierarchy_generator_preserves_parent_relationships() -> None:
    organization_id = OrganizationId(UUID(int=1))
    hierarchy = OrganizationHierarchyGenerator(RandomSource(42)).generate_explicit(
        organization_id,
        (
            ("Clinical Services", None),
            ("Laboratory", "Clinical Services"),
            ("Radiology", "Clinical Services"),
        ),
    )

    units = {unit.name: unit for unit in hierarchy.units}
    assert units["Clinical Services"].parent_id is None
    assert units["Laboratory"].parent_id == units["Clinical Services"].id
