from uuid import UUID

from healthfoundry import (
    Organization,
    OrganizationId,
    OrganizationalUnit,
    OrganizationUnitId,
)


def test_new_organization_id_is_uuid_and_round_trips() -> None:
    organization_id = OrganizationId.new()

    assert isinstance(organization_id.value, UUID)
    assert OrganizationId.from_string(str(organization_id)) == organization_id


def test_organization_id_is_immutable() -> None:
    organization_id = OrganizationId.new()

    try:
        organization_id.value = UUID(int=0)  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("OrganizationId should be immutable")


def test_organization_create_generates_identity() -> None:
    organization = Organization.create("North Valley Hospital")

    assert organization.name == "North Valley Hospital"
    assert isinstance(organization.id, OrganizationId)


def test_organization_rejects_blank_name() -> None:
    try:
        Organization.create("   ")
    except ValueError as error:
        assert str(error) == "Organization name must not be empty"
    else:
        raise AssertionError("Organization should reject a blank name")


def test_organizational_unit_can_reference_parent() -> None:
    organization = Organization.create("North Valley Hospital")
    division = OrganizationalUnit.create(organization.id, "Clinical Services")
    department = OrganizationalUnit.create(
        organization.id,
        "Laboratory",
        parent_id=division.id,
    )

    assert isinstance(department.id, OrganizationUnitId)
    assert department.organization_id == organization.id
    assert department.parent_id == division.id


def test_organizational_unit_rejects_blank_name() -> None:
    organization = Organization.create("North Valley Hospital")

    try:
        OrganizationalUnit.create(organization.id, "")
    except ValueError as error:
        assert str(error) == "Organizational unit name must not be empty"
    else:
        raise AssertionError("OrganizationalUnit should reject a blank name")
