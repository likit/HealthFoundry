"""Generators for deterministic synthetic people."""

from __future__ import annotations

from datetime import date

from healthfoundry.config import PopulationConfig
from healthfoundry.domain.person import Gender, Person, PersonId
from healthfoundry.services.randomness import RandomSource
from healthfoundry.services.person_provider import FakerNameProvider, PersonNameProvider


class PersonGenerator:
    """Generate people from configured name pools and a seeded source."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def generate(
        self,
        config: PopulationConfig,
        as_of: date | None = None,
    ) -> tuple[Person, ...]:
        if config.minimum_age is not None and as_of is None:
            raise ValueError("An as-of date is required when an age range is configured")

        name_provider: PersonNameProvider
        if config.given_names:
            name_provider = _ConfiguredNameProvider(
                config.given_names,
                config.family_names,
                self._randomness,
            )
        else:
            name_provider = FakerNameProvider(config.locale or "en_US", self._randomness)

        female_count = round(config.count * config.female_proportion)
        remaining_genders = [Gender.FEMALE] * female_count + [Gender.MALE] * (config.count - female_count)
        people = []
        for _ in range(config.count):
            given_name, family_name = name_provider.name()
            date_of_birth = None
            if as_of is not None and config.minimum_age is not None:
                date_of_birth = self._random_birth_date(
                    as_of,
                    config.minimum_age,
                    config.maximum_age,
                )
            gender_index = self._randomness.integer(0, len(remaining_genders) - 1)
            gender = remaining_genders.pop(gender_index)
            people.append(
                Person(
                    id=PersonId(self._randomness.uuid()),
                    given_name=given_name,
                    family_name=family_name,
                    date_of_birth=date_of_birth,
                    gender=gender,
                )
            )
        return tuple(people)

    def _random_birth_date(
        self,
        as_of: date,
        minimum_age: int,
        maximum_age: int,
    ) -> date:
        earliest = _anniversary(as_of, -(maximum_age + 1))
        earliest = date.fromordinal(earliest.toordinal() + 1)
        latest = _anniversary(as_of, -minimum_age)
        ordinal = self._randomness.integer(earliest.toordinal(), latest.toordinal())
        return date.fromordinal(ordinal)


class _ConfiguredNameProvider:
    def __init__(
        self,
        given_names: tuple[str, ...],
        family_names: tuple[str, ...],
        randomness: RandomSource,
    ) -> None:
        self._given_names = given_names
        self._family_names = family_names
        self._randomness = randomness

    def name(self) -> tuple[str, str]:
        return (
            self._randomness.choose(self._given_names),
            self._randomness.choose(self._family_names),
        )


def _anniversary(value: date, year_offset: int) -> date:
    try:
        return value.replace(year=value.year + year_offset)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + year_offset)
