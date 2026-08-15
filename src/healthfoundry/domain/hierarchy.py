"""Validated organization hierarchy aggregate."""

from __future__ import annotations

from dataclasses import dataclass

from healthfoundry.domain.organization import (
    OrganizationId,
    OrganizationalUnit,
    OrganizationUnitId,
)


@dataclass(frozen=True, slots=True)
class OrganizationHierarchy:
    """An immutable, validated tree of units belonging to one organization."""

    organization_id: OrganizationId
    units: tuple[OrganizationalUnit, ...] = ()

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def empty(cls, organization_id: OrganizationId) -> "OrganizationHierarchy":
        """Create an empty hierarchy for an organization."""

        return cls(organization_id=organization_id)

    def add(self, unit: OrganizationalUnit) -> "OrganizationHierarchy":
        """Return a new hierarchy containing ``unit``."""

        return OrganizationHierarchy(
            organization_id=self.organization_id,
            units=(*self.units, unit),
        )

    def _validate(self) -> None:
        units_by_id: dict[OrganizationUnitId, OrganizationalUnit] = {}

        for unit in self.units:
            if unit.organization_id != self.organization_id:
                raise ValueError("All units must belong to the hierarchy organization")
            if unit.id in units_by_id:
                raise ValueError(f"Duplicate organizational unit id: {unit.id}")
            units_by_id[unit.id] = unit

        for unit in self.units:
            if unit.parent_id is not None and unit.parent_id not in units_by_id:
                raise ValueError(f"Parent unit does not exist: {unit.parent_id}")

            visited: set[OrganizationUnitId] = set()
            current_id: OrganizationUnitId | None = unit.id
            while current_id is not None:
                if current_id in visited:
                    raise ValueError("Organization hierarchy cannot contain cycles")
                visited.add(current_id)
                current = units_by_id[current_id]
                current_id = current.parent_id

