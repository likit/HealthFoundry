from datetime import date

import pytest

from healthfoundry import Organization, Person, TimelineEvent, TimelineEventId


def test_timeline_event_records_scope_and_provenance() -> None:
    organization = Organization.create("North Valley Clinic")
    person = Person.create("Ada", "Lovelace")
    event = TimelineEvent.create(
        occurred_on=date(2026, 2, 14),
        event_type="diagnostic_visit",
        source_rule="abnormal_glucose",
        person_id=person.id,
        organization_id=organization.id,
        sequence=2,
    )

    assert isinstance(event.id, TimelineEventId)
    assert event.person_id == person.id
    assert event.source_rule == "abnormal_glucose"
    assert event.sort_key[:2] == (date(2026, 2, 14), 2)


def test_timeline_event_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="event type must not be empty"):
        TimelineEvent.create(date(2026, 1, 1), " ", "rule")
    with pytest.raises(ValueError, match="sequence must be non-negative"):
        TimelineEvent.create(date(2026, 1, 1), "visit", "rule", sequence=-1)

