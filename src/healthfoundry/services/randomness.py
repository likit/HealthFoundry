"""Deterministic randomness for reproducible simulations."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID


ValueT = TypeVar("ValueT")


class RandomSource:
    """An isolated pseudo-random source initialized from an explicit seed."""

    def __init__(self, seed: int) -> None:
        if seed < 0:
            raise ValueError("Random seed must be non-negative")
        self._generator = random.Random(seed)

    def integer(self, minimum: int, maximum: int) -> int:
        """Return a reproducible integer in the inclusive range."""

        return self._generator.randint(minimum, maximum)

    def probability(self) -> float:
        """Return a reproducible value in the half-open interval [0, 1)."""

        return self._generator.random()

    def normal(self, mean: float, standard_deviation: float) -> float:
        """Return a reproducible value from a normal distribution."""

        return self._generator.gauss(mean, standard_deviation)

    def choose(self, values: Sequence[ValueT]) -> ValueT:
        """Return a reproducible value from a non-empty sequence."""

        if not values:
            raise ValueError("Cannot choose from an empty sequence")
        return self._generator.choice(values)

    def uuid(self) -> UUID:
        """Return a reproducible UUID generated from this source."""

        return UUID(int=self._generator.getrandbits(128))
