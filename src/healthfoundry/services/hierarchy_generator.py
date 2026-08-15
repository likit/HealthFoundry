"""Generators for organization hierarchies."""

from __future__ import annotations

from healthfoundry.config import HierarchyConfig
from healthfoundry.domain.hierarchy import OrganizationHierarchy
from healthfoundry.domain.organization import (
    OrganizationId,
    OrganizationalUnit,
    OrganizationUnitId,
)
from healthfoundry.services.randomness import RandomSource


class OrganizationHierarchyGenerator:
    """Generate a reproducible hierarchy from configured unit names."""

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness

    def generate(
        self,
        organization_id: OrganizationId,
        config: HierarchyConfig,
    ) -> OrganizationHierarchy:
        """Create a tree whose first configured unit is the root."""

        hierarchy = OrganizationHierarchy.empty(organization_id)
        created_units: list[OrganizationalUnit] = []
        for index, name in enumerate(config.unit_names):
            parent_id = (
                None
                if index == 0
                else self._randomness.choose(created_units).id
            )
            unit = OrganizationalUnit(
                id=OrganizationUnitId(self._randomness.uuid()),
                organization_id=organization_id,
                name=name,
                parent_id=parent_id,
            )
            hierarchy = hierarchy.add(unit)
            created_units.append(unit)

        return hierarchy
