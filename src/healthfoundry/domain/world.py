"""Canonical synthetic healthcare world aggregate."""

from __future__ import annotations

from dataclasses import dataclass

from healthfoundry.domain.employment import EmploymentEpisode
from healthfoundry.domain.hierarchy import OrganizationHierarchy
from healthfoundry.domain.assessment import HealthAssessment
from healthfoundry.domain.laboratory import (
    LaboratoryObservation,
    LaboratoryOrder,
    LaboratoryPanel,
    LaboratoryTestDefinition,
    Specimen,
)
from healthfoundry.domain.organization import Organization, OrganizationUnitId
from healthfoundry.domain.person import Person
from healthfoundry.domain.workforce import WorkforceEvent


@dataclass(frozen=True, slots=True)
class World:
    """An immutable, internally consistent collection of domain entities."""

    organizations: tuple[Organization, ...] = ()
    hierarchies: tuple[OrganizationHierarchy, ...] = ()
    people: tuple[Person, ...] = ()
    employment_episodes: tuple[EmploymentEpisode, ...] = ()
    workforce_events: tuple[WorkforceEvent, ...] = ()
    assessments: tuple[HealthAssessment, ...] = ()
    test_definitions: tuple[LaboratoryTestDefinition, ...] = ()
    laboratory_panels: tuple[LaboratoryPanel, ...] = ()
    laboratory_orders: tuple[LaboratoryOrder, ...] = ()
    specimens: tuple[Specimen, ...] = ()
    laboratory_observations: tuple[LaboratoryObservation, ...] = ()

    @classmethod
    def empty(cls) -> "World":
        return cls()

    def to_dict(self) -> dict:
        """Return this world in canonical serialized form."""

        from healthfoundry.services.export import WorldJsonExporter

        return WorldJsonExporter().to_dict(self)

    def to_json(self) -> str:
        """Return this world as deterministic canonical JSON."""

        from healthfoundry.services.export import WorldJsonExporter

        return WorldJsonExporter().to_json(self)

    def to_sql_tables(self, engine):
        """Write a relational projection to a SQLAlchemy engine."""

        from healthfoundry.services.sql_export import WorldSqlExporter

        return WorldSqlExporter().to_sql_tables(self, engine)

    def add_organization(self, organization: Organization) -> "World":
        return World(
            organizations=(*self.organizations, organization),
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_hierarchy(self, hierarchy: OrganizationHierarchy) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=(*self.hierarchies, hierarchy),
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_person(self, person: Person) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=(*self.people, person),
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_employment_episode(self, episode: EmploymentEpisode) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=(*self.employment_episodes, episode),
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_workforce_event(self, event: WorkforceEvent) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=(*self.workforce_events, event),
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_assessment(self, assessment: HealthAssessment) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=(*self.assessments, assessment),
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_test_definition(self, definition: LaboratoryTestDefinition) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=(*self.test_definitions, definition),
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_laboratory_panel(self, panel: LaboratoryPanel) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=(*self.laboratory_panels, panel),
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_laboratory_order(self, order: LaboratoryOrder) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=(*self.laboratory_orders, order),
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def add_specimen(self, specimen: Specimen) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=(*self.specimens, specimen),
            laboratory_observations=self.laboratory_observations,
        )

    def add_laboratory_observation(self, observation: LaboratoryObservation) -> "World":
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=self.people,
            employment_episodes=self.employment_episodes,
            workforce_events=self.workforce_events,
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=(*self.laboratory_observations, observation),
        )

    def _validate(self) -> None:
        organization_ids = self._unique_ids(
            (organization.id for organization in self.organizations),
            "organization",
        )
        person_ids = self._unique_ids(
            (person.id for person in self.people),
            "person",
        )
        self._unique_ids(
            (episode.id for episode in self.employment_episodes),
            "employment episode",
        )
        self._unique_ids(
            (event.id for event in self.workforce_events),
            "workforce event",
        )
        assessment_ids = self._unique_ids(
            (assessment.id for assessment in self.assessments), "assessment"
        )
        test_definition_ids = self._unique_ids(
            (definition.id for definition in self.test_definitions), "test definition"
        )
        panel_ids = self._unique_ids(
            (panel.id for panel in self.laboratory_panels), "laboratory panel"
        )
        order_ids = self._unique_ids(
            (order.id for order in self.laboratory_orders), "laboratory order"
        )
        specimen_ids = self._unique_ids(
            (specimen.id for specimen in self.specimens), "specimen"
        )
        self._unique_ids(
            (observation.id for observation in self.laboratory_observations),
            "laboratory observation",
        )

        hierarchy_by_organization = {}
        for hierarchy in self.hierarchies:
            if hierarchy.organization_id not in organization_ids:
                raise ValueError("Hierarchy must reference an organization in the world")
            if hierarchy.organization_id in hierarchy_by_organization:
                raise ValueError("World cannot contain duplicate organization hierarchies")
            hierarchy_by_organization[hierarchy.organization_id] = hierarchy

        for episode in self.employment_episodes:
            if episode.person_id not in person_ids:
                raise ValueError("Employment episode must reference a person in the world")
            if episode.organization_id not in organization_ids:
                raise ValueError("Employment episode must reference an organization in the world")
            if not self._unit_exists(
                hierarchy_by_organization.get(episode.organization_id), episode.unit_id
            ):
                raise ValueError("Employment episode must reference a unit in the world")

        for event in self.workforce_events:
            if event.person_id not in person_ids:
                raise ValueError("Workforce event must reference a person in the world")
            if event.organization_id not in organization_ids:
                raise ValueError("Workforce event must reference an organization in the world")
            hierarchy = hierarchy_by_organization.get(event.organization_id)
            for unit_id in (event.unit_id, event.from_unit_id, event.to_unit_id):
                if unit_id is not None and not self._unit_exists(hierarchy, unit_id):
                    raise ValueError("Workforce event must reference units in the world")

        for assessment in self.assessments:
            if assessment.id not in assessment_ids:
                raise ValueError("Invalid assessment identity")
            if assessment.person_id not in person_ids or assessment.organization_id not in organization_ids:
                raise ValueError("Assessment must reference entities in the world")
        for panel in self.laboratory_panels:
            if any(test_id not in test_definition_ids for test_id in panel.test_definition_ids):
                raise ValueError("Laboratory panel must reference tests in the world")
        for order in self.laboratory_orders:
            if order.id not in order_ids:
                raise ValueError("Invalid laboratory order identity")
            if order.person_id not in person_ids or order.organization_id not in organization_ids:
                raise ValueError("Laboratory order must reference entities in the world")
            if order.test_definition_id not in test_definition_ids:
                raise ValueError("Laboratory order must reference a test in the world")
        for specimen in self.specimens:
            if specimen.order_id not in order_ids:
                raise ValueError("Specimen must reference an order in the world")
        for observation in self.laboratory_observations:
            if observation.order_id not in order_ids:
                raise ValueError("Observation must reference an order in the world")
            if observation.test_definition_id not in test_definition_ids:
                raise ValueError("Observation must reference a test in the world")

    @staticmethod
    def _unique_ids(ids, label: str) -> set:
        values = list(ids)
        if len(values) != len(set(values)):
            raise ValueError(f"World cannot contain duplicate {label} ids")
        return set(values)

    @staticmethod
    def _unit_exists(
        hierarchy: OrganizationHierarchy | None,
        unit_id: OrganizationUnitId,
    ) -> bool:
        return hierarchy is not None and any(unit.id == unit_id for unit in hierarchy.units)

    def __post_init__(self) -> None:
        self._validate()
