"""Build initial canonical worlds from configuration."""

from __future__ import annotations

from healthfoundry.config import HierarchyConfig, SimulationConfig
from healthfoundry.domain.organization import Organization, OrganizationId
from healthfoundry.domain.world import World
from healthfoundry.services.hierarchy_generator import OrganizationHierarchyGenerator
from healthfoundry.services.randomness import RandomSource


class WorldBuilder:
    """Construct the initial organization portion of a synthetic world."""

    def build(
        self,
        organization_name: str,
        simulation_config: SimulationConfig,
        hierarchy_config: HierarchyConfig,
    ) -> World:
        randomness = RandomSource(simulation_config.random_seed)
        organization = Organization(
            id=OrganizationId(randomness.uuid()),
            name=organization_name,
        )
        hierarchy = OrganizationHierarchyGenerator(randomness).generate(
            organization.id,
            hierarchy_config,
        )

        return World.empty().add_organization(organization).add_hierarchy(hierarchy)

