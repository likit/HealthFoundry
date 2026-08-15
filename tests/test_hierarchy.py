import pytest

from healthfoundry import Organization, OrganizationHierarchy, OrganizationalUnit


def test_hierarchy_adds_root_and_child_units() -> None:
    organization = Organization.create("North Valley Hospital")
    hierarchy = OrganizationHierarchy.empty(organization.id)
    root = OrganizationalUnit.create(organization.id, "Clinical Services")
    child = OrganizationalUnit.create(
        organization.id,
        "Laboratory",
        parent_id=root.id,
    )

    hierarchy = hierarchy.add(root).add(child)

    assert hierarchy.units == (root, child)


def test_hierarchy_rejects_missing_parent() -> None:
    organization = Organization.create("North Valley Hospital")
    other_root = OrganizationalUnit.create(organization.id, "Unknown")
    child = OrganizationalUnit.create(
        organization.id,
        "Laboratory",
        parent_id=other_root.id,
    )

    with pytest.raises(ValueError, match="Parent unit does not exist"):
        OrganizationHierarchy(organization.id, (child,))


def test_hierarchy_rejects_cycles() -> None:
    organization = Organization.create("North Valley Hospital")
    first = OrganizationalUnit.create(organization.id, "First")
    second = OrganizationalUnit.create(
        organization.id,
        "Second",
        parent_id=first.id,
    )
    cyclic_first = OrganizationalUnit(
        id=first.id,
        organization_id=organization.id,
        name=first.name,
        parent_id=second.id,
    )

    with pytest.raises(ValueError, match="cannot contain cycles"):
        OrganizationHierarchy(organization.id, (cyclic_first, second))
