"""Build initial canonical worlds from configuration."""

from __future__ import annotations

from healthfoundry.config import HierarchyConfig, PopulationConfig, SimulationConfig
from healthfoundry.domain.organization import Organization, OrganizationId
from healthfoundry.domain.world import World
from healthfoundry.services.hierarchy_generator import OrganizationHierarchyGenerator
from healthfoundry.services.randomness import RandomSource
from healthfoundry.services.person_generator import PersonGenerator
from healthfoundry.services.employment_generator import EmploymentGenerator


class WorldBuilder:
    """Construct the initial organization portion of a synthetic world."""

    def build(
        self,
        organization_name: str,
        simulation_config: SimulationConfig,
        hierarchy_config: HierarchyConfig,
        population_config: PopulationConfig | None = None,
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

        world = World.empty().add_organization(organization).add_hierarchy(hierarchy)
        if population_config is not None:
            people = PersonGenerator(randomness).generate(
                population_config,
                as_of=simulation_config.start_date,
            )
            for person in people:
                world = world.add_person(person)
            episodes = EmploymentGenerator(randomness).assign_initial(
                people,
                organization.id,
                hierarchy,
                simulation_config.start_date,
            )
            for episode in episodes:
                world = world.add_employment_episode(episode)
        return world
