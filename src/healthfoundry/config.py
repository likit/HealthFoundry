"""Configuration objects for reproducible HealthFoundry experiments."""

from dataclasses import dataclass
from datetime import date
from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Stable inputs defining the time window and seed of an experiment."""

    random_seed: int
    start_date: date
    years: int

    def __post_init__(self) -> None:
        if self.random_seed < 0:
            raise ValueError("Random seed must be non-negative")
        if self.years < 1:
            raise ValueError("Simulation must run for at least one year")


@dataclass(frozen=True, slots=True)
class HierarchyConfig:
    """Configuration for generating an organization's hierarchy."""

    unit_names: tuple[str, ...]

    @classmethod
    def from_names(cls, unit_names: Sequence[str]) -> "HierarchyConfig":
        return cls(unit_names=tuple(unit_names))

    def __post_init__(self) -> None:
        if not self.unit_names:
            raise ValueError("At least one organizational unit name is required")
        if any(not name.strip() for name in self.unit_names):
            raise ValueError("Organizational unit names must not be empty")
        if len(set(self.unit_names)) != len(self.unit_names):
            raise ValueError("Organizational unit names must be unique")


@dataclass(frozen=True, slots=True)
class PopulationConfig:
    """Configuration for generating a population of people."""

    count: int
    given_names: tuple[str, ...] = ()
    family_names: tuple[str, ...] = ()
    minimum_age: int | None = None
    maximum_age: int | None = None
    locale: str | None = None

    @classmethod
    def from_names(
        cls,
        count: int,
        given_names: Sequence[str],
        family_names: Sequence[str],
        minimum_age: int | None = None,
        maximum_age: int | None = None,
        locale: str | None = None,
    ) -> "PopulationConfig":
        return cls(
            count,
            tuple(given_names),
            tuple(family_names),
            minimum_age,
            maximum_age,
            locale,
        )

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError("Population count must be at least one")
        if bool(self.given_names) != bool(self.family_names):
            raise ValueError("Given and family name pools must be configured together")
        if not self.given_names and not self.locale:
            raise ValueError("Configure name pools or a locale")
        if any(not name.strip() for name in (*self.given_names, *self.family_names)):
            raise ValueError("Configured names must not be empty")
        if (self.minimum_age is None) != (self.maximum_age is None):
            raise ValueError("Minimum and maximum age must be configured together")
        if self.minimum_age is not None and self.maximum_age is not None:
            if not 0 <= self.minimum_age <= self.maximum_age <= 120:
                raise ValueError("Age range must be between 0 and 120 years")


@dataclass(frozen=True, slots=True)
class WorkforceConfig:
    """Annual probabilities for workforce changes."""

    transfer_rate: float = 0.0
    resignation_rate: float = 0.0
    retirement_age: int | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.transfer_rate <= 1.0:
            raise ValueError("Transfer rate must be between 0 and 1")
        if not 0.0 <= self.resignation_rate <= 1.0:
            raise ValueError("Resignation rate must be between 0 and 1")
        if self.transfer_rate + self.resignation_rate > 1.0:
            raise ValueError("Transfer and resignation rates cannot sum above 1")
        if self.retirement_age is not None and not 18 <= self.retirement_age <= 100:
            raise ValueError("Retirement age must be between 18 and 100")
