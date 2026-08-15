"""Configuration objects for reproducible HealthFoundry experiments."""

from dataclasses import dataclass
from datetime import date


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

