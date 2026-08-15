"""Export a small HealthFoundry world to canonical JSON."""

import json
from datetime import date
from pathlib import Path

from healthfoundry import HierarchyConfig, SimulationConfig, WorldBuilder


def main() -> None:
    world = WorldBuilder().build(
        "North Valley Clinic",
        SimulationConfig(42, date(2026, 1, 1), 1),
        HierarchyConfig.from_names(["Clinical Services", "Laboratory"]),
    )

    output_path = Path("tutorial_output/world.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(world.to_json() + "\n", encoding="utf-8")

    document = json.loads(output_path.read_text(encoding="utf-8"))
    print(f"Wrote: {output_path}")
    print(f"Organizations: {len(document['organizations'])}")
    print(f"Hierarchy units: {len(document['hierarchies'][0]['units'])}")


if __name__ == "__main__":
    main()

