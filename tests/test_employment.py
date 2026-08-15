from datetime import date

import pytest

from healthfoundry import (
    EmploymentEpisode,
    EmploymentEpisodeId,
    Organization,
    OrganizationalUnit,
    Person,
)


def test_employment_episode_tracks_person_and_unit() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    person = Person.create("Ada", "Lovelace")
    episode = EmploymentEpisode.create(
        person_id=person.id,
        organization_id=organization.id,
        unit_id=unit.id,
        start_date=date(2026, 1, 1),
    )

    assert isinstance(episode.id, EmploymentEpisodeId)
    assert episode.is_active_on(date(2026, 6, 1))
    assert not episode.is_active_on(date(2025, 12, 31))


def test_ended_employment_episode_is_inactive_on_end_date() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    person = Person.create("Ada", "Lovelace")
    episode = EmploymentEpisode.create(
        person.id,
        organization.id,
        unit.id,
        date(2026, 1, 1),
        date(2027, 1, 1),
    )

    assert episode.is_active_on(date(2026, 12, 31))
    assert not episode.is_active_on(date(2027, 1, 1))


def test_employment_episode_rejects_invalid_date_range() -> None:
    organization = Organization.create("North Valley Hospital")
    unit = OrganizationalUnit.create(organization.id, "Laboratory")
    person = Person.create("Ada", "Lovelace")

    with pytest.raises(ValueError, match="end date must be after"):
        EmploymentEpisode.create(
            person.id,
            organization.id,
            unit.id,
            date(2026, 1, 1),
            date(2026, 1, 1),
        )

