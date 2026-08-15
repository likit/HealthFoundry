from datetime import date

import pytest

from healthfoundry import SimulationConfig


def test_simulation_config_is_reproducible_input() -> None:
    config = SimulationConfig(
        random_seed=42,
        start_date=date(2026, 1, 1),
        years=5,
    )

    assert config.random_seed == 42
    assert config.start_date == date(2026, 1, 1)
    assert config.years == 5


@pytest.mark.parametrize(
    ("random_seed", "years", "message"),
    [
        (-1, 5, "Random seed must be non-negative"),
        (42, 0, "Simulation must run for at least one year"),
    ],
)
def test_simulation_config_rejects_invalid_values(
    random_seed: int,
    years: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        SimulationConfig(random_seed, date(2026, 1, 1), years)

