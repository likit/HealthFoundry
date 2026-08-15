# Tutorial 7: Generate Health-State-Aware Results

This tutorial shows how an explicit `HealthState` can influence a laboratory result.

The example uses a simple configured effect: diabetes shifts the glucose mean upward. This is a transparent synthetic rule, not a clinically validated model.

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/07_health_state_results/generate_state_aware_result.py
```

## What it demonstrates

- Creating a `HealthState`
- Creating a laboratory order
- Defining a baseline result distribution
- Applying a condition-specific mean effect
- Generating a deterministic observation

