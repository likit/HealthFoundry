from datetime import date

import pytest

from healthfoundry import (
    Organization,
    OrganizationalUnit,
    Person,
    WorkforceEvent,
    WorkforceEventType,
)


def test_workforce_event_factories_create_typed_events() -> None:
    organization = Organization.create("North Valley Hospital")
    laboratory = OrganizationalUnit.create(organization.id, "Laboratory")
    radiology = OrganizationalUnit.create(organization.id, "Radiology")
    person = Person.create("Ada", "Lovelace")

    hire = WorkforceEvent.hire(person.id, organization.id, date(2026, 1, 1), laboratory.id)
    transfer = WorkforceEvent.transfer(
        person.id,
        organization.id,
        date(2027, 1, 1),
        laboratory.id,
        radiology.id,
    )
    resignation = WorkforceEvent.resignation(person.id, organization.id, date(2028, 1, 1))
    retirement = WorkforceEvent.retirement(person.id, organization.id, date(2029, 1, 1))

    assert hire.event_type is WorkforceEventType.HIRE
    assert transfer.to_unit_id == radiology.id
    assert resignation.event_type is WorkforceEventType.RESIGNATION
    assert retirement.event_type is WorkforceEventType.RETIREMENT


def test_transfer_requires_different_units() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    person = Person.create("Ada", "Lovelace")

    with pytest.raises(ValueError, match="different source and destination"):
        WorkforceEvent.transfer(
            person.id,
            organization.id,
            date(2027, 1, 1),
            unit.id,
            unit.id,
        )

