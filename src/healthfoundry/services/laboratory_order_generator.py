"""Strategies for generating laboratory orders."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import NAMESPACE_URL, uuid5

from healthfoundry.domain.laboratory import (
    LaboratoryOrder,
    LaboratoryOrderId,
    LaboratoryPanel,
    LaboratoryTestDefinition,
)
from healthfoundry.domain.organization import OrganizationId
from healthfoundry.domain.person import PersonId
from healthfoundry.services.randomness import RandomSource


class OrderGenerator(Protocol):
    def generate(
        self,
        person_id: PersonId,
        organization_id: OrganizationId,
        tests: Sequence[LaboratoryTestDefinition],
        ordered_on: date,
        reason: str | None = None,
    ) -> tuple[LaboratoryOrder, ...]: ...


class RuleBasedOrderGenerator:
    """Order every test in the supplied panel."""

    def generate(
        self,
        person_id: PersonId,
        organization_id: OrganizationId,
        tests: Sequence[LaboratoryTestDefinition],
        ordered_on: date,
        reason: str | None = None,
    ) -> tuple[LaboratoryOrder, ...]:
        return tuple(
            LaboratoryOrder(
                id=LaboratoryOrderId(
                    uuid5(
                        NAMESPACE_URL,
                        f"{person_id}:{organization_id}:{test.id}:{ordered_on}",
                    )
                ),
                person_id=person_id,
                organization_id=organization_id,
                test_definition_id=test.id,
                ordered_on=ordered_on,
                reason=reason,
            )
            for test in tests
        )

    def generate_panel(
        self,
        person_id: PersonId,
        organization_id: OrganizationId,
        panel: LaboratoryPanel,
        test_catalog: Sequence[LaboratoryTestDefinition],
        ordered_on: date,
        reason: str | None = None,
    ) -> tuple[LaboratoryOrder, ...]:
        definitions = {definition.id: definition for definition in test_catalog}
        try:
            tests = tuple(definitions[test_id] for test_id in panel.test_definition_ids)
        except KeyError as error:
            raise ValueError("Laboratory panel references an unknown test") from error
        return self.generate(person_id, organization_id, tests, ordered_on, reason)


class RandomOrderGenerator:
    """Order each test independently according to an inclusion rate."""

    def __init__(self, randomness: RandomSource, inclusion_rate: float) -> None:
        if not 0.0 <= inclusion_rate <= 1.0:
            raise ValueError("Inclusion rate must be between 0 and 1")
        self._randomness = randomness
        self._inclusion_rate = inclusion_rate

    def generate(
        self,
        person_id: PersonId,
        organization_id: OrganizationId,
        tests: Sequence[LaboratoryTestDefinition],
        ordered_on: date,
        reason: str | None = None,
    ) -> tuple[LaboratoryOrder, ...]:
        orders = []
        for test in tests:
            if self._randomness.probability() <= self._inclusion_rate:
                orders.append(
                    LaboratoryOrder(
                        id=LaboratoryOrderId(self._randomness.uuid()),
                        person_id=person_id,
                        organization_id=organization_id,
                        test_definition_id=test.id,
                        ordered_on=ordered_on,
                        reason=reason,
                    )
                )
        return tuple(orders)
