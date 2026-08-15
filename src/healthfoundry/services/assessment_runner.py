"""Convenience API for running an assessment laboratory workflow."""

from __future__ import annotations

from healthfoundry.domain.assessment import HealthAssessment
from healthfoundry.domain.laboratory import LaboratoryCatalog
from healthfoundry.domain.world import World
from healthfoundry.services.assessment_laboratory_workflow import (
    AssessmentLaboratoryWorkflow,
)
from healthfoundry.services.randomness import RandomSource


class AssessmentRunner:
    """Run and persist a completed assessment laboratory workflow."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def run(
        self,
        world: World,
        assessment: HealthAssessment,
        catalog: LaboratoryCatalog,
        panel_code: str,
    ) -> World:
        panel = catalog.panel_by_code(panel_code)
        test_catalog = tuple(catalog.test_by_id(test_id) for test_id in panel.test_definition_ids)
        normal_models = {
            test.code: (
                catalog.result_model_for(test.id).mean,
                catalog.result_model_for(test.id).standard_deviation,
            )
            for test in test_catalog
        }
        current = world.add_assessment(assessment)
        for definition in catalog.tests:
            current = current.add_test_definition(definition)
        current = current.add_laboratory_panel(panel)

        output = AssessmentLaboratoryWorkflow(self._randomness).run(
            assessment,
            panel,
            test_catalog,
            normal_models,
        )
        for order in output.orders:
            current = current.add_laboratory_order(order)
        for specimen in output.specimens:
            current = current.add_specimen(specimen)
        for observation in output.observations:
            current = current.add_laboratory_observation(observation)
        return current
