"""Generators for organization hierarchies."""

from __future__ import annotations

from collections.abc import Sequence

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

    def generate_explicit(
        self,
        organization_id: OrganizationId,
        relationships: Sequence[tuple[str, str | None]],
    ) -> OrganizationHierarchy:
        """Create a hierarchy from explicit ``(unit, parent)`` relationships."""

        if not relationships:
            raise ValueError("At least one organizational unit is required")
        names = [name for name, _ in relationships]
        if any(not name.strip() for name in names):
            raise ValueError("Organizational unit names must not be empty")
        if len(set(names)) != len(names):
            raise ValueError("Organizational unit names must be unique")
        known_names = set(names)
        if any(parent is not None and parent not in known_names for _, parent in relationships):
            raise ValueError("Organizational unit parent must be defined in the hierarchy")

        ids = {name: OrganizationUnitId(self._randomness.uuid()) for name in names}
        return OrganizationHierarchy(
            organization_id,
            tuple(
                OrganizationalUnit(
                    id=ids[name],
                    organization_id=organization_id,
                    name=name,
                    parent_id=ids[parent] if parent else None,
                )
                for name, parent in relationships
            ),
        )
