# Tutorial 1: Create a Tiny Organization

This tutorial creates a small organization with three hierarchy units:

```text
North Valley Clinic
└── Clinical Services
    └── Laboratory
```

The example uses a fixed random seed, so it produces the same organization and hierarchy every time it runs.

## Install the local package

From the repository root, install HealthFoundry into your active virtual environment:

```bash
python -m pip install -e .
```

## Run it

After installation, run from the repository root:

```bash
python tutorials/01_tiny_organization/create_tiny_organization.py
```

If you prefer not to install the package, use the `src` path explicitly:

```bash
PYTHONPATH=src python tutorials/01_tiny_organization/create_tiny_organization.py
```

## What it demonstrates

- Creating `SimulationConfig`
- Defining a `HierarchyConfig`
- Building an initial `World`
- Reading the generated organization and hierarchy

This tutorial does not generate people or simulate workforce events yet.
