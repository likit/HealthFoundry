# Tutorial 9: Generate Follow-Up Events

This tutorial creates a diagnostic visit and automatically generates a follow-up visit 30 days later.

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/09_follow_up_events/generate_follow_up.py
```

## What it demonstrates

- One-time schedules with `Schedule.once()`
- Relative triggers with `AfterEvent`
- Day-level delays
- Event causality through `caused_by`

The engine generates the complete timeline offline. It does not wait 30 real days.

