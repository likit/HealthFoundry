# Tutorial 10: Apply Scenario Events to a World

This tutorial demonstrates the complete offline pipeline:

```text
ScenarioRule → TimelineEvent → ScenarioEventApplier → World
```

The applied health-assessment event also generates a laboratory order, specimen, and glucose observation.

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/10_apply_scenario_events/apply_events.py
```

## What it demonstrates

- Generating a scheduled scenario event
- Applying the event to a canonical `World`
- Creating a health assessment
- Generating laboratory data from a catalog
- Reading the resulting records from `World`

