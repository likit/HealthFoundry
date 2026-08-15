from datetime import date

import pytest

from healthfoundry import (
    HealthState,
    LaboratoryObservationGenerator,
    LaboratoryOrder,
    LaboratoryTestDefinition,
    Organization,
    Person,
    RandomSource,
)


def _setup():
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    definition = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    order = LaboratoryOrder.create(person.id, organization.id, definition.id, date(2026, 1, 1))
    return order, definition


def test_observation_generator_supports_fixed_values() -> None:
    order, definition = _setup()

    observation = LaboratoryObservationGenerator(RandomSource(42)).fixed(
        order, definition, date(2026, 1, 2), 96.0
    )

    assert observation.value == 96.0
    assert observation.unit == "mg/dL"


def test_normal_observation_generation_is_reproducible() -> None:
    order, definition = _setup()
    first = LaboratoryObservationGenerator(RandomSource(42)).normal(
        order, definition, date(2026, 1, 2), 100.0, 10.0
    )
    second = LaboratoryObservationGenerator(RandomSource(42)).normal(
        order, definition, date(2026, 1, 2), 100.0, 10.0
    )

    assert first == second


def test_normal_observation_rejects_nonpositive_deviation() -> None:
    order, definition = _setup()

    with pytest.raises(ValueError, match="greater than zero"):
        LaboratoryObservationGenerator(RandomSource(42)).normal(
            order, definition, date(2026, 1, 2), 100.0, 0.0
        )


def test_observation_generator_can_apply_health_state_effects() -> None:
    order, definition = _setup()
    healthy = HealthState(order.person_id, date(2026, 1, 1))
    condition = HealthState(
        order.person_id,
        date(2026, 1, 1),
        condition_codes=frozenset({"diabetes"}),
    )
    generator = LaboratoryObservationGenerator(RandomSource(42))
    healthy_result = generator.normal_for_state(
        order,
        definition,
        date(2026, 1, 2),
        healthy,
        100.0,
        1.0,
        {"diabetes": 30.0},
    )
    condition_result = LaboratoryObservationGenerator(RandomSource(42)).normal_for_state(
        order,
        definition,
        date(2026, 1, 2),
        condition,
        100.0,
        1.0,
        {"diabetes": 30.0},
    )

    assert condition_result.value == healthy_result.value + 30.0
