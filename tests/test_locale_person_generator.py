import pytest

from healthfoundry import PersonGenerator, PopulationConfig, RandomSource


def test_locale_generation_reports_optional_dependency() -> None:
    pytest.importorskip("faker")
    config = PopulationConfig.from_names(1, (), (), locale="th_TH")

    person = PersonGenerator(RandomSource(42)).generate(config)[0]

    assert person.given_name
    assert person.family_name
