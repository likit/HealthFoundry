# Tutorial 2: Create a Tiny Workforce

This tutorial extends the tiny organization by generating a small Thai-named workforce and assigning each person to an organizational unit.

## Run it

Install the local package and Faker into the active virtual environment if needed:

```bash
python -m pip install -e ".[faker]"
```

Then run from the repository root:

```bash
python tutorials/02_tiny_workforce/create_tiny_workforce.py
```

Or, using the project virtual environment explicitly:

```bash
.venv/bin/python -m pip install -e ".[faker]"
.venv/bin/python tutorials/02_tiny_workforce/create_tiny_workforce.py
```

## What it demonstrates

- Locale-aware Thai person generation
- Population configuration
- Initial employment assignment
- Reading people and employment episodes from the `World`

