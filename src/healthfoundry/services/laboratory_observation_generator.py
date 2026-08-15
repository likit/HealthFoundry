"""Deterministic laboratory observation generation."""

from __future__ import annotations

from datetime import date
from collections.abc import Mapping

from healthfoundry.domain.laboratory import (
    LaboratoryObservation,
    LaboratoryObservationId,
    LaboratoryOrder,
    LaboratoryTestDefinition,
)
from healthfoundry.domain.health import HealthState
from healthfoundry.services.randomness import RandomSource


class LaboratoryObservationGenerator:
    """Generate observations from explicit result distributions or values."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def fixed(
        self,
        order: LaboratoryOrder,
        test_definition: LaboratoryTestDefinition,
        observed_on: date,
        value: float | str,
    ) -> LaboratoryObservation:
        return self._observation(order, test_definition, observed_on, value)

    def normal(
        self,
        order: LaboratoryOrder,
        test_definition: LaboratoryTestDefinition,
        observed_on: date,
        mean: float,
        standard_deviation: float,
    ) -> LaboratoryObservation:
        if standard_deviation <= 0:
            raise ValueError("Standard deviation must be greater than zero")
        value = self._randomness.normal(mean, standard_deviation)
        return self._observation(order, test_definition, observed_on, value)

    def normal_for_state(
        self,
        order: LaboratoryOrder,
        test_definition: LaboratoryTestDefinition,
        observed_on: date,
        state: HealthState,
        baseline_mean: float,
        standard_deviation: float,
        state_mean_effects: Mapping[str, float],
    ) -> LaboratoryObservation:
        """Generate a result whose mean reflects configured health-state effects."""

        if state.person_id != order.person_id:
            raise ValueError("Health state must belong to the ordered person")
        mean = baseline_mean + sum(
            state_mean_effects.get(code, 0.0)
            for code in (*state.condition_codes, *state.risk_factors)
        )
        return self.normal(
            order,
            test_definition,
            observed_on,
            mean,
            standard_deviation,
        )

    def _observation(
        self,
        order: LaboratoryOrder,
        test_definition: LaboratoryTestDefinition,
        observed_on: date,
        value: float | str,
    ) -> LaboratoryObservation:
        return LaboratoryObservation(
            id=LaboratoryObservationId(self._randomness.uuid()),
            order_id=order.id,
            test_definition_id=test_definition.id,
            observed_on=observed_on,
            value=value,
            unit=test_definition.result_unit,
        )
