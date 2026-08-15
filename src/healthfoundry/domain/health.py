"""Health-state domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from healthfoundry.domain.person import PersonId


@dataclass(frozen=True, slots=True)
class HealthState:
    """A person's explicitly modeled health state at one point in time."""

    person_id: PersonId
    as_of: date
    condition_codes: frozenset[str] = frozenset()
    risk_factors: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        for label, values in (
            ("condition code", self.condition_codes),
            ("risk factor", self.risk_factors),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"Health {label} must not be empty")


@dataclass(frozen=True, slots=True)
class HealthTrajectory:
    """An immutable, chronological sequence of states for one person."""

    person_id: PersonId
    states: tuple[HealthState, ...] = ()

    def __post_init__(self) -> None:
        previous_date: date | None = None
        for state in self.states:
            if state.person_id != self.person_id:
                raise ValueError("All trajectory states must belong to the same person")
            if previous_date is not None and state.as_of <= previous_date:
                raise ValueError("Health trajectory states must be strictly chronological")
            previous_date = state.as_of

    @classmethod
    def empty(cls, person_id: PersonId) -> "HealthTrajectory":
        return cls(person_id)

    def add(self, state: HealthState) -> "HealthTrajectory":
        return HealthTrajectory(self.person_id, (*self.states, state))

    def state_at(self, on_date: date) -> HealthState | None:
        """Return the latest known state on or before ``on_date``."""

        known_states = [state for state in self.states if state.as_of <= on_date]
        return known_states[-1] if known_states else None
