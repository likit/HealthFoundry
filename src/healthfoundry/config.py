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
