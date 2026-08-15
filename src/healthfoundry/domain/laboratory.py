"""Canonical laboratory domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from healthfoundry.domain.organization import OrganizationId
from healthfoundry.domain.person import PersonId


@dataclass(frozen=True, slots=True)
class LaboratoryTestDefinitionId:
    value: UUID

    @classmethod
    def new(cls) -> "LaboratoryTestDefinitionId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class LaboratoryTestDefinition:
    """A catalog definition for a laboratory test."""

    id: LaboratoryTestDefinitionId
    code: str
    name: str
    specimen_type: str
    result_unit: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("code", self.code),
            ("name", self.name),
            ("specimen type", self.specimen_type),
        ):
            if not value.strip():
                raise ValueError(f"Laboratory test {field_name} must not be empty")
        if self.result_unit is not None and not self.result_unit.strip():
            raise ValueError("Laboratory test result unit must not be empty")

    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        specimen_type: str,
        result_unit: str | None = None,
    ) -> "LaboratoryTestDefinition":
        return cls(LaboratoryTestDefinitionId.new(), code, name, specimen_type, result_unit)


@dataclass(frozen=True, slots=True)
class LaboratoryPanelId:
    value: UUID

    @classmethod
    def new(cls) -> "LaboratoryPanelId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class LaboratoryPanel:
    """A reusable named bundle of laboratory tests."""

    id: LaboratoryPanelId
    code: str
    name: str
    test_definition_ids: tuple[LaboratoryTestDefinitionId, ...]

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Laboratory panel code must not be empty")
        if not self.name.strip():
            raise ValueError("Laboratory panel name must not be empty")
        if not self.test_definition_ids:
            raise ValueError("Laboratory panel must contain at least one test")
        if len(set(self.test_definition_ids)) != len(self.test_definition_ids):
            raise ValueError("Laboratory panel tests must be unique")

    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        test_definition_ids: tuple[LaboratoryTestDefinitionId, ...],
    ) -> "LaboratoryPanel":
        return cls(LaboratoryPanelId.new(), code, name, test_definition_ids)


@dataclass(frozen=True, slots=True)
class LaboratoryOrderId:
    value: UUID

    @classmethod
    def new(cls) -> "LaboratoryOrderId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class LaboratoryOrder:
    """An order for one laboratory test for one person."""

    id: LaboratoryOrderId
    person_id: PersonId
    organization_id: OrganizationId
    test_definition_id: LaboratoryTestDefinitionId
    ordered_on: date
    reason: str | None = None

    @classmethod
    def create(
        cls,
        person_id: PersonId,
        organization_id: OrganizationId,
        test_definition_id: LaboratoryTestDefinitionId,
        ordered_on: date,
        reason: str | None = None,
    ) -> "LaboratoryOrder":
        if reason is not None and not reason.strip():
            raise ValueError("Laboratory order reason must not be empty")
        return cls(
            LaboratoryOrderId.new(),
            person_id,
            organization_id,
            test_definition_id,
            ordered_on,
            reason,
        )


@dataclass(frozen=True, slots=True)
class SpecimenId:
    value: UUID

    @classmethod
    def new(cls) -> "SpecimenId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Specimen:
    """A collected biological specimen associated with a laboratory order."""

    id: SpecimenId
    order_id: LaboratoryOrderId
    specimen_type: str
    collected_on: date

    def __post_init__(self) -> None:
        if not self.specimen_type.strip():
            raise ValueError("Specimen type must not be empty")

    @classmethod
    def create(
        cls,
        order_id: LaboratoryOrderId,
        specimen_type: str,
        collected_on: date,
    ) -> "Specimen":
        return cls(SpecimenId.new(), order_id, specimen_type, collected_on)


@dataclass(frozen=True, slots=True)
class LaboratoryObservationId:
    value: UUID

    @classmethod
    def new(cls) -> "LaboratoryObservationId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class LaboratoryObservation:
    """A measured laboratory result for an ordered test."""

    id: LaboratoryObservationId
    order_id: LaboratoryOrderId
    test_definition_id: LaboratoryTestDefinitionId
    observed_on: date
    value: float | str
    unit: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.value, str) and not self.value.strip():
            raise ValueError("Laboratory observation value must not be empty")
        if self.unit is not None and not self.unit.strip():
            raise ValueError("Laboratory observation unit must not be empty")

    @classmethod
    def create(
        cls,
        order_id: LaboratoryOrderId,
        test_definition_id: LaboratoryTestDefinitionId,
        observed_on: date,
        value: float | str,
        unit: str | None = None,
    ) -> "LaboratoryObservation":
        return cls(
            LaboratoryObservationId.new(),
            order_id,
            test_definition_id,
            observed_on,
            value,
            unit,
        )
