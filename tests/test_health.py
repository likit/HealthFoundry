from datetime import date

import pytest

from healthfoundry import HealthState, HealthTrajectory, Person


def test_health_state_is_a_point_in_time_snapshot() -> None:
    person = Person.create("Ada", "Lovelace")
    state = HealthState(
        person_id=person.id,
        as_of=date(2026, 1, 1),
        condition_codes=frozenset({"hypertension"}),
        risk_factors=frozenset({"family_history"}),
    )

    assert state.person_id == person.id
    assert "hypertension" in state.condition_codes
    assert "family_history" in state.risk_factors


def test_health_state_rejects_blank_codes() -> None:
    person = Person.create("Ada", "Lovelace")

    with pytest.raises(ValueError, match="condition code must not be empty"):
        HealthState(person.id, date(2026, 1, 1), frozenset({" "}))


def test_health_trajectory_returns_latest_known_state() -> None:
    person = Person.create("Ada", "Lovelace")
    first = HealthState(person.id, date(2026, 1, 1))
    second = HealthState(person.id, date(2027, 1, 1), frozenset({"hypertension"}))
    trajectory = HealthTrajectory.empty(person.id).add(first).add(second)

    assert trajectory.state_at(date(2026, 6, 1)) == first
    assert trajectory.state_at(date(2028, 1, 1)) == second
    assert trajectory.state_at(date(2025, 1, 1)) is None


def test_health_trajectory_rejects_wrong_person_and_duplicate_dates() -> None:
    person = Person.create("Ada", "Lovelace")
    other_person = Person.create("Grace", "Hopper")
    first = HealthState(person.id, date(2026, 1, 1))

    with pytest.raises(ValueError, match="same person"):
        HealthTrajectory(person.id, (HealthState(other_person.id, date(2026, 1, 1)),))
    with pytest.raises(ValueError, match="strictly chronological"):
        HealthTrajectory(person.id, (first, first))
