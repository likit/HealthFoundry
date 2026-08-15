# Tutorial 6: Export a World to SQLite

This tutorial builds a small workforce world, exports it through SQLAlchemy, and queries the resulting SQLite database.

## Install the SQL export dependency

```bash
.venv/bin/python -m pip install -e ".[sql]"
```

## Run it

From the repository root:

```bash
.venv/bin/python tutorials/06_sqlite_export/export_sqlite.py
```

The database is written to `tutorial_output/world.sqlite`.

## What it demonstrates

- Calling `world.to_sql_tables(engine)`
- Creating a SQLite database through SQLAlchemy
- Querying exported tables with SQL

