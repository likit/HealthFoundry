from datetime import date

from sqlalchemy import create_engine, text

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
    SimulationConfig,
    WorldBuilder,
)


def test_world_can_export_relational_tables() -> None:
    world = WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 1),
        HierarchyConfig.from_names(["Clinical Services"]),
        PopulationConfig.from_names(2, ["Ada"], ["Lovelace"]),
    )
    engine = create_engine("sqlite://")

    metadata = world.to_sql_tables(engine)

    assert "organizations" in metadata.tables
    with engine.connect() as connection:
        assert connection.execute(text("select count(*) from organizations")).scalar() == 1
        assert connection.execute(text("select count(*) from people")).scalar() == 2
        assert connection.execute(text("select count(*) from employment_episodes")).scalar() == 2

