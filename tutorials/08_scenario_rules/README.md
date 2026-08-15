# Tutorial 8: Generate Events with Scenario Rules

This tutorial uses selectors and scheduled rules to generate an offline event timeline.

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/08_scenario_rules/generate_scenario_events.py
```

## What it demonstrates

- Selecting all people with `AllPeopleSelector`
- Selecting active employees with `ActiveEmployeesSelector`
- Creating recurring `ScenarioRule` objects
- Generating dated `TimelineEvent` records with `ScenarioEngine`
- Preserving the rule that produced each event

The engine generates the complete timeline immediately; it does not wait for real time to pass.

