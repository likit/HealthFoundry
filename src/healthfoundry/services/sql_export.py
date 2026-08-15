"""SQLAlchemy export for canonical worlds."""

from __future__ import annotations

from datetime import date
from typing import Any

from healthfoundry.domain.world import World


class WorldSqlExporter:
    """Write a relational projection of a world using a SQLAlchemy engine."""

    def to_sql_tables(self, world: World, engine: Any) -> Any:
        try:
            from sqlalchemy import (
                Date,
                Float,
                ForeignKey,
                Integer,
                MetaData,
                String,
                Table,
                Column,
            )
        except ImportError as error:
            raise RuntimeError(
                "SQL export requires the optional dependency: "
                "pip install 'healthfoundry[sql]'"
            ) from error

        metadata = MetaData()
        organizations = Table(
            "organizations", metadata,
            Column("id", String, primary_key=True),
            Column("name", String, nullable=False),
        )
        organizational_units = Table(
            "organizational_units", metadata,
            Column("id", String, primary_key=True),
            Column("organization_id", String, ForeignKey("organizations.id"), nullable=False),
            Column("name", String, nullable=False),
            Column("parent_id", String, nullable=True),
        )
        people = Table(
            "people", metadata,
            Column("id", String, primary_key=True),
            Column("given_name", String, nullable=False),
            Column("family_name", String, nullable=False),
            Column("date_of_birth", Date, nullable=True),
        )
        employment_episodes = Table(
            "employment_episodes", metadata,
            Column("id", String, primary_key=True),
            Column("person_id", String, ForeignKey("people.id"), nullable=False),
            Column("organization_id", String, ForeignKey("organizations.id"), nullable=False),
            Column("unit_id", String, ForeignKey("organizational_units.id"), nullable=False),
            Column("start_date", Date, nullable=False),
            Column("end_date", Date, nullable=True),
        )
        workforce_events = Table(
            "workforce_events", metadata,
            Column("id", String, primary_key=True),
            Column("person_id", String, ForeignKey("people.id"), nullable=False),
            Column("organization_id", String, ForeignKey("organizations.id"), nullable=False),
            Column("occurred_on", Date, nullable=False),
            Column("event_type", String, nullable=False),
            Column("unit_id", String, nullable=True),
            Column("from_unit_id", String, nullable=True),
            Column("to_unit_id", String, nullable=True),
        )
        health_assessments = Table(
            "health_assessments", metadata,
            Column("id", String, primary_key=True),
            Column("person_id", String, ForeignKey("people.id"), nullable=False),
            Column("organization_id", String, ForeignKey("organizations.id"), nullable=False),
            Column("assessed_on", Date, nullable=False),
            Column("context", String, nullable=False),
            Column("status", String, nullable=False),
        )
        test_definitions = Table(
            "laboratory_test_definitions", metadata,
            Column("id", String, primary_key=True),
            Column("code", String, nullable=False),
            Column("name", String, nullable=False),
            Column("specimen_type", String, nullable=False),
            Column("result_unit", String, nullable=True),
        )
        panels = Table(
            "laboratory_panels", metadata,
            Column("id", String, primary_key=True),
            Column("code", String, nullable=False),
            Column("name", String, nullable=False),
        )
        panel_tests = Table(
            "laboratory_panel_tests", metadata,
            Column("panel_id", String, ForeignKey("laboratory_panels.id"), primary_key=True),
            Column("test_definition_id", String, ForeignKey("laboratory_test_definitions.id"), primary_key=True),
            Column("position", Integer, nullable=False),
        )
        orders = Table(
            "laboratory_orders", metadata,
            Column("id", String, primary_key=True),
            Column("person_id", String, ForeignKey("people.id"), nullable=False),
            Column("organization_id", String, ForeignKey("organizations.id"), nullable=False),
            Column("test_definition_id", String, ForeignKey("laboratory_test_definitions.id"), nullable=False),
            Column("ordered_on", Date, nullable=False),
            Column("reason", String, nullable=True),
        )
        specimens = Table(
            "specimens", metadata,
            Column("id", String, primary_key=True),
            Column("order_id", String, ForeignKey("laboratory_orders.id"), nullable=False),
            Column("specimen_type", String, nullable=False),
            Column("collected_on", Date, nullable=False),
        )
        observations = Table(
            "laboratory_observations", metadata,
            Column("id", String, primary_key=True),
            Column("order_id", String, ForeignKey("laboratory_orders.id"), nullable=False),
            Column("test_definition_id", String, ForeignKey("laboratory_test_definitions.id"), nullable=False),
            Column("observed_on", Date, nullable=False),
            Column("value_numeric", Float, nullable=True),
            Column("value_text", String, nullable=True),
            Column("unit", String, nullable=True),
        )

        metadata.create_all(engine)
        with engine.begin() as connection:
            _insert(connection, organizations, [
                {"id": str(item.id), "name": item.name} for item in world.organizations
            ])
            _insert(connection, organizational_units, [
                {
                    "id": str(unit.id),
                    "organization_id": str(unit.organization_id),
                    "name": unit.name,
                    "parent_id": str(unit.parent_id) if unit.parent_id else None,
                }
                for hierarchy in world.hierarchies
                for unit in hierarchy.units
            ])
            _insert(connection, people, [
                {
                    "id": str(person.id),
                    "given_name": person.given_name,
                    "family_name": person.family_name,
                    "date_of_birth": person.date_of_birth,
                }
                for person in world.people
            ])
            _insert(connection, employment_episodes, [
                {
                    "id": str(episode.id),
                    "person_id": str(episode.person_id),
                    "organization_id": str(episode.organization_id),
                    "unit_id": str(episode.unit_id),
                    "start_date": episode.start_date,
                    "end_date": episode.end_date,
                }
                for episode in world.employment_episodes
            ])
            _insert(connection, workforce_events, [
                {
                    "id": str(event.id),
                    "person_id": str(event.person_id),
                    "organization_id": str(event.organization_id),
                    "occurred_on": event.occurred_on,
                    "event_type": event.event_type.value,
                    "unit_id": str(event.unit_id) if event.unit_id else None,
                    "from_unit_id": str(event.from_unit_id) if event.from_unit_id else None,
                    "to_unit_id": str(event.to_unit_id) if event.to_unit_id else None,
                }
                for event in world.workforce_events
            ])
            _insert(connection, health_assessments, [
                {
                    "id": str(item.id),
                    "person_id": str(item.person_id),
                    "organization_id": str(item.organization_id),
                    "assessed_on": item.assessed_on,
                    "context": item.context.value,
                    "status": item.status.value,
                }
                for item in world.assessments
            ])
            _insert(connection, test_definitions, [
                {
                    "id": str(item.id),
                    "code": item.code,
                    "name": item.name,
                    "specimen_type": item.specimen_type,
                    "result_unit": item.result_unit,
                }
                for item in world.test_definitions
            ])
            _insert(connection, panels, [
                {"id": str(item.id), "code": item.code, "name": item.name}
                for item in world.laboratory_panels
            ])
            _insert(connection, panel_tests, [
                {
                    "panel_id": str(panel.id),
                    "test_definition_id": str(test_id),
                    "position": position,
                }
                for panel in world.laboratory_panels
                for position, test_id in enumerate(panel.test_definition_ids)
            ])
            _insert(connection, orders, [
                {
                    "id": str(item.id),
                    "person_id": str(item.person_id),
                    "organization_id": str(item.organization_id),
                    "test_definition_id": str(item.test_definition_id),
                    "ordered_on": item.ordered_on,
                    "reason": item.reason,
                }
                for item in world.laboratory_orders
            ])
            _insert(connection, specimens, [
                {
                    "id": str(item.id),
                    "order_id": str(item.order_id),
                    "specimen_type": item.specimen_type,
                    "collected_on": item.collected_on,
                }
                for item in world.specimens
            ])
            _insert(connection, observations, [
                {
                    "id": str(item.id),
                    "order_id": str(item.order_id),
                    "test_definition_id": str(item.test_definition_id),
                    "observed_on": item.observed_on,
                    "value_numeric": item.value if isinstance(item.value, (int, float)) else None,
                    "value_text": item.value if isinstance(item.value, str) else None,
                    "unit": item.unit,
                }
                for item in world.laboratory_observations
            ])
        return metadata


def _insert(connection: Any, table: Any, rows: list[dict[str, Any]]) -> None:
    if rows:
        connection.execute(table.insert(), rows)
