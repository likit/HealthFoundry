"""Apply generated scenario events to canonical worlds."""

from __future__ import annotations

from collections.abc import Iterable

from healthfoundry.domain.assessment import (
    AssessmentContext,
    AssessmentStatus,
    HealthAssessment,
    HealthAssessmentId,
)
from healthfoundry.domain.laboratory import LaboratoryCatalog
from healthfoundry.domain.timeline import TimelineEvent
from healthfoundry.domain.world import World
from healthfoundry.services.assessment_laboratory_workflow import (
    AssessmentLaboratoryWorkflow,
)
from healthfoundry.services.randomness import RandomSource


class ScenarioEventApplier:
    """Translate supported timeline events into canonical world entities."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def apply(
        self,
        world: World,
        events: Iterable[TimelineEvent],
        catalog: LaboratoryCatalog | None = None,
        panel_code: str | None = None,
        assessment_context: AssessmentContext = AssessmentContext.PREVENTIVE,
    ) -> World:
        current = world
        for event in sorted(events, key=lambda item: item.sort_key):
            if event.event_type != "health_assessment":
                continue
            if event.person_id is None or event.organization_id is None:
                raise ValueError("Health assessment event must identify a person and organization")

            assessment = HealthAssessment(
                id=HealthAssessmentId(event.id.value),
                person_id=event.person_id,
                organization_id=event.organization_id,
                assessed_on=event.occurred_on,
                context=assessment_context,
                status=AssessmentStatus.COMPLETED,
            )
            current = current.add_assessment(assessment)

            if catalog is not None:
                if panel_code is None:
                    raise ValueError("A panel code is required when a laboratory catalog is provided")
                panel = catalog.panel_by_code(panel_code)
                tests = tuple(catalog.test_by_id(test_id) for test_id in panel.test_definition_ids)
                models = {
                    test.code: (
                        catalog.result_model_for(test.id).mean,
                        catalog.result_model_for(test.id).standard_deviation,
                    )
                    for test in tests
                }
                output = AssessmentLaboratoryWorkflow(self._randomness).run(
                    assessment,
                    panel,
                    tests,
                    models,
                )
                for definition in catalog.tests:
                    current = current.add_test_definition(definition)
                current = current.add_laboratory_panel(panel)
                for order in output.orders:
                    current = current.add_laboratory_order(order)
                for specimen in output.specimens:
                    current = current.add_specimen(specimen)
                for observation in output.observations:
                    current = current.add_laboratory_observation(observation)
        return current

