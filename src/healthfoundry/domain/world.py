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
from healthfoundry.domain.organization import (
    Organization,
    OrganizationId,
    OrganizationalUnit,
    OrganizationUnitId,
)
from healthfoundry.domain.person import Person, PersonId
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

    @classmethod
    def from_json(cls, value: str) -> "World":
        """Reconstruct a world from JSON produced by :meth:`to_json`."""

        import json
        from datetime import date
        from uuid import UUID

        from healthfoundry.domain.assessment import (
            AssessmentContext,
            AssessmentStatus,
            HealthAssessmentId,
        )
        from healthfoundry.domain.employment import EmploymentEpisodeId
        from healthfoundry.domain.laboratory import (
            LaboratoryObservationId,
            LaboratoryOrderId,
            LaboratoryPanelId,
            LaboratoryTestDefinitionId,
            SpecimenId,
        )
        from healthfoundry.domain.workforce import (
            WorkforceEventId,
            WorkforceEventType,
        )
        from healthfoundry.domain.timeline import TimelineEventId

        data = json.loads(value)
        organizations = tuple(
            Organization(OrganizationId(UUID(item["id"])), item["name"])
            for item in data["organizations"]
        )
        hierarchies = tuple(
            OrganizationHierarchy(
                OrganizationId(UUID(item["organization_id"])),
                tuple(
                    OrganizationalUnit(
                        OrganizationUnitId(UUID(unit["id"])),
                        OrganizationId(UUID(unit["organization_id"])),
                        unit["name"],
                        OrganizationUnitId(UUID(unit["parent_id"])) if unit["parent_id"] else None,
                    )
                    for unit in item["units"]
                ),
            )
            for item in data["hierarchies"]
        )
        people = tuple(
            Person(
                PersonId(UUID(item["id"])),
                item["given_name"],
                item["family_name"],
                date.fromisoformat(item["date_of_birth"]) if item["date_of_birth"] else None,
            )
            for item in data["people"]
        )
        episodes = tuple(
            EmploymentEpisode(
                EmploymentEpisodeId(UUID(item["id"])),
                PersonId(UUID(item["person_id"])),
                OrganizationId(UUID(item["organization_id"])),
                OrganizationUnitId(UUID(item["unit_id"])),
                date.fromisoformat(item["start_date"]),
                date.fromisoformat(item["end_date"]) if item["end_date"] else None,
            )
            for item in data["employment_episodes"]
        )
        events = tuple(
            WorkforceEvent(
                WorkforceEventId(UUID(item["id"])),
                PersonId(UUID(item["person_id"])),
                OrganizationId(UUID(item["organization_id"])),
                date.fromisoformat(item["occurred_on"]),
                WorkforceEventType(item["event_type"]),
                OrganizationUnitId(UUID(item["unit_id"])) if item["unit_id"] else None,
                OrganizationUnitId(UUID(item["from_unit_id"])) if item["from_unit_id"] else None,
                OrganizationUnitId(UUID(item["to_unit_id"])) if item["to_unit_id"] else None,
            )
            for item in data["workforce_events"]
        )
        assessments = tuple(
            HealthAssessment(
                HealthAssessmentId(UUID(item["id"])),
                PersonId(UUID(item["person_id"])),
                OrganizationId(UUID(item["organization_id"])),
                date.fromisoformat(item["assessed_on"]),
                AssessmentContext(item["context"]),
                AssessmentStatus(item["status"]),
            )
            for item in data["assessments"]
        )
        definitions = tuple(
            LaboratoryTestDefinition(
                LaboratoryTestDefinitionId(UUID(item["id"])),
                item["code"], item["name"], item["specimen_type"], item["result_unit"],
            )
            for item in data["test_definitions"]
        )
        panels = tuple(
            LaboratoryPanel(
                LaboratoryPanelId(UUID(item["id"])),
                item["code"], item["name"],
                tuple(LaboratoryTestDefinitionId(UUID(test_id)) for test_id in item["test_definition_ids"]),
            )
            for item in data["laboratory_panels"]
        )
        orders = tuple(
            LaboratoryOrder(
                LaboratoryOrderId(UUID(item["id"])),
                PersonId(UUID(item["person_id"])),
                OrganizationId(UUID(item["organization_id"])),
                LaboratoryTestDefinitionId(UUID(item["test_definition_id"])),
                date.fromisoformat(item["ordered_on"]), item["reason"],
            )
            for item in data["laboratory_orders"]
        )
        specimens = tuple(
            Specimen(
                SpecimenId(UUID(item["id"])), LaboratoryOrderId(UUID(item["order_id"])),
                item["specimen_type"], date.fromisoformat(item["collected_on"]),
            )
            for item in data["specimens"]
        )
        observations = tuple(
            LaboratoryObservation(
                LaboratoryObservationId(UUID(item["id"])),
                LaboratoryOrderId(UUID(item["order_id"])),
                LaboratoryTestDefinitionId(UUID(item["test_definition_id"])),
                date.fromisoformat(item["observed_on"]), item["value"], item["unit"],
            )
            for item in data["laboratory_observations"]
        )
        return cls(
            organizations, hierarchies, people, episodes, events, assessments,
            definitions, panels, orders, specimens, observations,
        )

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

    def replace_hierarchy(self, hierarchy: OrganizationHierarchy) -> "World":
        """Replace one organization's hierarchy and clear unit-dependent records."""

        hierarchies = tuple(
            hierarchy if item.organization_id == hierarchy.organization_id else item
            for item in self.hierarchies
        )
        if not any(item.organization_id == hierarchy.organization_id for item in self.hierarchies):
            hierarchies = (*hierarchies, hierarchy)
        return World(
            organizations=self.organizations,
            hierarchies=hierarchies,
            people=self.people,
            employment_episodes=(),
            workforce_events=(),
            assessments=self.assessments,
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=self.laboratory_orders,
            specimens=self.specimens,
            laboratory_observations=self.laboratory_observations,
        )

    def remove_organization(self, organization_id: OrganizationId) -> "World":
        """Remove an organization and records that belong to it."""

        removed_order_ids = {
            order.id
            for order in self.laboratory_orders
            if order.organization_id == organization_id
        }
        return World(
            organizations=tuple(item for item in self.organizations if item.id != organization_id),
            hierarchies=tuple(item for item in self.hierarchies if item.organization_id != organization_id),
            people=self.people,
            employment_episodes=tuple(item for item in self.employment_episodes if item.organization_id != organization_id),
            workforce_events=tuple(item for item in self.workforce_events if item.organization_id != organization_id),
            assessments=tuple(item for item in self.assessments if item.organization_id != organization_id),
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=tuple(item for item in self.laboratory_orders if item.organization_id != organization_id),
            specimens=tuple(item for item in self.specimens if item.order_id not in removed_order_ids),
            laboratory_observations=tuple(item for item in self.laboratory_observations if item.order_id not in removed_order_ids),
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

    def replace_people(
        self,
        people: tuple[Person, ...],
        employment_episodes: tuple[EmploymentEpisode, ...] = (),
    ) -> "World":
        """Replace the population and reset records belonging to the old population."""

        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=people,
            employment_episodes=employment_episodes,
            workforce_events=(),
            assessments=(),
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=(),
            specimens=(),
            laboratory_observations=(),
        )

    def replace_organization_people(
        self,
        organization_id: OrganizationId,
        people: tuple[Person, ...],
        employment_episodes: tuple[EmploymentEpisode, ...],
    ) -> "World":
        """Replace one organization's population while preserving other organizations."""

        replaced_person_ids = {
            episode.person_id
            for episode in self.employment_episodes
            if episode.organization_id == organization_id
        }
        removed_order_ids = {
            order.id
            for order in self.laboratory_orders
            if order.organization_id == organization_id
        }
        return World(
            organizations=self.organizations,
            hierarchies=self.hierarchies,
            people=tuple(person for person in self.people if person.id not in replaced_person_ids) + people,
            employment_episodes=tuple(item for item in self.employment_episodes if item.organization_id != organization_id) + employment_episodes,
            workforce_events=tuple(item for item in self.workforce_events if item.organization_id != organization_id),
            assessments=tuple(item for item in self.assessments if item.organization_id != organization_id),
            test_definitions=self.test_definitions,
            laboratory_panels=self.laboratory_panels,
            laboratory_orders=tuple(item for item in self.laboratory_orders if item.organization_id != organization_id),
            specimens=tuple(item for item in self.specimens if item.order_id not in removed_order_ids),
            laboratory_observations=tuple(item for item in self.laboratory_observations if item.order_id not in removed_order_ids),
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
