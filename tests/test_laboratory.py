from datetime import date

import pytest

from healthfoundry import (
    LaboratoryOrder,
    LaboratoryOrderId,
    LaboratoryTestDefinition,
    LaboratoryTestDefinitionId,
    LaboratoryPanel,
    LaboratoryObservation,
    LaboratoryObservationId,
    Specimen,
    SpecimenId,
    Organization,
    Person,
)


def test_laboratory_definition_and_order() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    definition = LaboratoryTestDefinition.create(
        "CBC", "Complete blood count", "whole blood", "cells/uL"
    )
    order = LaboratoryOrder.create(
        person.id, organization.id, definition.id, date(2026, 1, 1), "Annual health check"
    )

    assert isinstance(definition.id, LaboratoryTestDefinitionId)
    assert isinstance(order.id, LaboratoryOrderId)
    assert order.test_definition_id == definition.id
    assert order.reason == "Annual health check"


def test_laboratory_models_reject_blank_values() -> None:
    with pytest.raises(ValueError, match="code must not be empty"):
        LaboratoryTestDefinition.create("", "Complete blood count", "whole blood")

    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    definition = LaboratoryTestDefinition.create("CBC", "Complete blood count", "blood")
    with pytest.raises(ValueError, match="reason must not be empty"):
        LaboratoryOrder.create(
            person.id, organization.id, definition.id, date(2026, 1, 1), "   "
        )


def test_laboratory_panel_contains_reusable_test_bundle() -> None:
    first = LaboratoryTestDefinition.create("CBC", "Complete blood count", "blood")
    second = LaboratoryTestDefinition.create("GLU", "Glucose", "blood", "mg/dL")

    panel = LaboratoryPanel.create(
        "ANNUAL",
        "Annual health check",
        (first.id, second.id),
    )

    assert panel.test_definition_ids == (first.id, second.id)


def test_specimen_and_observation_follow_an_order() -> None:
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    definition = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
    order = LaboratoryOrder.create(
        person.id,
        organization.id,
        definition.id,
        date(2026, 1, 1),
    )
    specimen = Specimen.create(order.id, definition.specimen_type, date(2026, 1, 1))
    observation = LaboratoryObservation.create(
        order.id,
        definition.id,
        date(2026, 1, 2),
        96.0,
        definition.result_unit,
    )

    assert isinstance(specimen.id, SpecimenId)
    assert isinstance(observation.id, LaboratoryObservationId)
    assert specimen.order_id == order.id
    assert observation.test_definition_id == definition.id
