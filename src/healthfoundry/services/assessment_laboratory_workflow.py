"""Laboratory workflow for completed health assessments."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from healthfoundry.domain.assessment import AssessmentStatus, HealthAssessment
from healthfoundry.domain.laboratory import (
    LaboratoryObservation,
    LaboratoryObservationId,
    LaboratoryOrder,
    LaboratoryPanel,
    LaboratoryTestDefinition,
    Specimen,
    SpecimenId,
)
from healthfoundry.services.laboratory_observation_generator import (
    LaboratoryObservationGenerator,
)
from healthfoundry.services.laboratory_order_generator import RuleBasedOrderGenerator
from healthfoundry.services.randomness import RandomSource


@dataclass(frozen=True, slots=True)
class AssessmentLaboratoryOutput:
    orders: tuple[LaboratoryOrder, ...]
    specimens: tuple[Specimen, ...]
    observations: tuple[LaboratoryObservation, ...]


class AssessmentLaboratoryWorkflow:
    """Create a panel-based laboratory record for a completed assessment."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def run(
        self,
        assessment: HealthAssessment,
        panel: LaboratoryPanel,
        test_catalog: Sequence[LaboratoryTestDefinition],
        normal_models: Mapping[str, tuple[float, float]],
    ) -> AssessmentLaboratoryOutput:
        if assessment.status is not AssessmentStatus.COMPLETED:
            raise ValueError("Laboratory workflow requires a completed assessment")

        definitions = {definition.id: definition for definition in test_catalog}
        tests = tuple(definitions[test_id] for test_id in panel.test_definition_ids)
        orders = RuleBasedOrderGenerator().generate(
            assessment.person_id,
            assessment.organization_id,
            tests,
            assessment.assessed_on,
            reason=panel.name,
        )
        observations = []
        specimens = []
        observation_generator = LaboratoryObservationGenerator(self._randomness)
        for order, test in zip(orders, tests):
            specimens.append(
                Specimen(
                    id=SpecimenId(self._randomness.uuid()),
                    order_id=order.id,
                    specimen_type=test.specimen_type,
                    collected_on=assessment.assessed_on,
                )
            )
            try:
                mean, standard_deviation = normal_models[test.code]
            except KeyError as error:
                raise ValueError(f"No result model configured for test: {test.code}") from error
            observation = observation_generator.normal(
                order,
                test,
                assessment.assessed_on,
                mean,
                standard_deviation,
            )
            observations.append(observation)

        return AssessmentLaboratoryOutput(tuple(orders), tuple(specimens), tuple(observations))

