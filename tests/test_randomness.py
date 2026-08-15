import pytest

from healthfoundry import RandomSource


def test_same_seed_produces_same_sequence() -> None:
    first = RandomSource(seed=42)
    second = RandomSource(seed=42)

    first_values = [first.integer(1, 100) for _ in range(5)]
    second_values = [second.integer(1, 100) for _ in range(5)]

    assert first_values == second_values


def test_random_source_can_choose_values_deterministically() -> None:
    first = RandomSource(seed=7)
    second = RandomSource(seed=7)
    values = ("laboratory", "radiology", "pharmacy")

    assert [first.choose(values) for _ in range(4)] == [
        second.choose(values) for _ in range(4)
    ]


def test_random_source_rejects_empty_choices() -> None:
    with pytest.raises(ValueError, match="empty sequence"):
        RandomSource(seed=1).choose(())

