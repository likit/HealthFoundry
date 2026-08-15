from datetime import date

import pytest

from healthfoundry import PersonGenerator, PopulationConfig, RandomSource


def test_person_generator_is_reproducible() -> None:
    config = PopulationConfig.from_names(
        3,
        ["Ada", "Grace"],
        ["Lovelace", "Hopper"],
    )

    first = PersonGenerator(RandomSource(42)).generate(config)
    second = PersonGenerator(RandomSource(42)).generate(config)

    assert first == second
    assert len(first) == 3
    assert all(person.full_name in {"Ada Lovelace", "Ada Hopper", "Grace Lovelace", "Grace Hopper"} for person in first)


def test_population_config_rejects_missing_inputs() -> None:
    try:
        PopulationConfig.from_names(0, ["Ada"], ["Lovelace"])
    except ValueError as error:
        assert str(error) == "Population count must be at least one"
    else:
        raise AssertionError("PopulationConfig should reject zero people")


def test_person_generator_creates_reproducible_birth_dates() -> None:
    config = PopulationConfig.from_names(
        3,
        ["Ada"],
        ["Lovelace"],
        minimum_age=20,
        maximum_age=40,
    )
    as_of = date(2026, 1, 1)

    first = PersonGenerator(RandomSource(42)).generate(config, as_of)
    second = PersonGenerator(RandomSource(42)).generate(config, as_of)

    assert first == second
    assert all(person.date_of_birth is not None for person in first)
    assert all(20 <= _age_on(person.date_of_birth, as_of) <= 40 for person in first)


def test_age_range_requires_as_of_date() -> None:
    config = PopulationConfig.from_names(1, ["Ada"], ["Lovelace"], 20, 40)

    with pytest.raises(ValueError, match="as-of date"):
        PersonGenerator(RandomSource(42)).generate(config)


def _age_on(date_of_birth: date, as_of: date) -> int:
    years = as_of.year - date_of_birth.year
    return years - ((as_of.month, as_of.day) < (date_of_birth.month, date_of_birth.day))
