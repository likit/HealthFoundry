"""Providers for person names."""

from __future__ import annotations

from typing import Protocol

from healthfoundry.services.randomness import RandomSource


class PersonNameProvider(Protocol):
    def name(self) -> tuple[str, str]: ...


class FakerNameProvider:
    """Locale-aware names backed by the optional Faker dependency."""

    def __init__(self, locale: str, randomness: RandomSource) -> None:
        try:
            from faker import Faker
        except ImportError as error:
            raise RuntimeError(
                "Locale-based names require the optional dependency: "
                "pip install 'healthfoundry[faker]'"
            ) from error

        self._faker = Faker(locale)
        self._faker.seed_instance(randomness.integer(0, 2**32 - 1))

    def name(self) -> tuple[str, str]:
        return self._faker.first_name(), self._faker.last_name()

