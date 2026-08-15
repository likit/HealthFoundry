# Tutorial 4: Run a Health Assessment Laboratory Workflow

This tutorial creates a completed preventive assessment for one person and generates a small laboratory panel with specimens and observations.

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/04_health_assessment_laboratory/run_assessment.py
```

## What it demonstrates

- Selecting a person from a generated world
- Creating a general `HealthAssessment`
- Defining laboratory tests and a reusable panel
- Generating orders, specimens, and observations
- Adding the workflow artifacts back to `World`

The result distribution is explicit configuration, not a clinical claim. More advanced health-state-aware models can be added later.

