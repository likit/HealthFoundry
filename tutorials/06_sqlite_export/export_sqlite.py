"""Export a small workforce world to SQLite and query it with SQL."""

from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text

from healthfoundry import (
    HierarchyConfig,
    PopulationConfig,
    SimulationConfig,
    WorldBuilder,
)


def main() -> None:
    world = WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 1),
        HierarchyConfig.from_names(["Clinical Services", "Laboratory"]),
        PopulationConfig.from_names(
            3,
            ["Ada", "Grace", "Somchai"],
            ["Lovelace", "Hopper", "Prasert"],
        ),
    )

    output_path = Path("tutorial_output/world.sqlite")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{output_path}")
    world.to_sql_tables(engine)

    with engine.connect() as connection:
        people = connection.execute(text("select count(*) from people")).scalar_one()
        episodes = connection.execute(
            text("select count(*) from employment_episodes")
        ).scalar_one()

    print(f"Wrote: {output_path}")
    print(f"People: {people}")
    print(f"Employment episodes: {episodes}")


if __name__ == "__main__":
    main()

