"""Optional progressive desktop interface for creating HealthFoundry worlds."""

from __future__ import annotations

from datetime import date
from pathlib import Path


def _run_settings(sg, store, world_name: str, initial_world=None, initial_settings=None) -> None:
    """Run the settings window for one selected world."""

    from healthfoundry import (
        ActiveEmployeesSelector,
        AfterEvent,
        AssessmentContext,
        EmploymentGenerator,
        HierarchyConfig,
        LaboratoryCatalog,
        LaboratoryPanel,
        LaboratoryResultModel,
        LaboratoryTestDefinition,
        Organization,
        OrganizationHierarchy,
        OrganizationHierarchyGenerator,
        OrganizationId,
        OrganizationalUnit,
        PersonGenerator,
        PopulationConfig,
        RandomSource,
        ScenarioEngine,
        ScenarioEventApplier,
        ScenarioRule,
        Schedule,
        SimulationConfig,
        WorkforceConfig,
        WorkforceSimulator,
        World,
    )

    label_font = ("Any", 14)
    input_font = ("Any", 14)
    button_font = ("Any", 14)
    world = initial_world or World.empty()
    initial_settings = initial_settings or {}

    setting_defaults = {
        "organization": "North Valley Clinic",
        "people_organization": "",
        "seed": "42",
        "years": "5",
        "population_count": "10",
        "locale": "th_TH",
        "minimum_age": "20",
        "maximum_age": "70",
        "transfer_rate": "0.10",
        "resignation_rate": "0.05",
        "retirement_age": "65",
        "assessment_schedule": "Annual",
        "assessment_offset": "0",
        "assessment_trigger_mode": "Scheduled",
        "trigger_event": "diagnostic_visit",
        "trigger_delay_days": "30",
    }

    def setting(key: str):
        value = initial_settings.get(key)
        return setting_defaults[key] if value in (None, "", "None") else value
    simulation_config = SimulationConfig(
        random_seed=int(setting("seed")),
        start_date=date.today(),
        years=int(setting("years")),
    )

    world_tab = [
        [sg.Text("World settings", font=("Any", 18))],
        [sg.Text("Random seed", font=label_font), sg.Input(setting("seed"), key="seed", font=input_font)],
        [sg.Text("Simulation years", font=label_font), sg.Input(setting("years"), key="years", font=input_font)],
    ]
    selected_organization_id = None
    selected_unit_id = None
    saved_people_settings = initial_settings.get("people_settings", {})
    people_settings_by_organization = {
        str(key): dict(value)
        for key, value in saved_people_settings.items()
        if isinstance(value, dict)
    }

    def organization_rows():
        if world is None:
            return []
        hierarchy_by_organization = {
            hierarchy.organization_id: hierarchy for hierarchy in world.hierarchies
        }
        return [
            [
                str(organization.id),
                organization.name,
                len(hierarchy_by_organization.get(organization.id, ()).units)
                if organization.id in hierarchy_by_organization
                else 0,
            ]
            for organization in world.organizations
        ]

    def organization_names():
        return [organization.name for organization in (world.organizations if world else ())]

    initial_people_name = setting("people_organization")
    initial_people_organization = next(
        (item for item in (world.organizations if world else ()) if item.name == initial_people_name),
        (world.organizations[0] if world and world.organizations else None),
    )
    selected_people_organization_id = (
        initial_people_organization.id if initial_people_organization else None
    )

    def people_setting(key: str):
        defaults = {item: setting(item) for item in ("population_count", "locale", "minimum_age", "maximum_age")}
        saved = people_settings_by_organization.get(str(selected_people_organization_id), {})
        value = saved.get(key, defaults[key])
        return defaults[key] if value in (None, "", "None") else value

    def hierarchy_tree_data(organization_id=None):
        tree_data = sg.TreeData()
        if world is None or organization_id is None:
            return tree_data
        hierarchy = next(
            (item for item in world.hierarchies if item.organization_id == organization_id),
            None,
        )
        if hierarchy is None:
            return tree_data
        remaining = list(hierarchy.units)
        inserted = {""}
        while remaining:
            progress = False
            for unit in remaining[:]:
                parent_key = str(unit.parent_id) if unit.parent_id else ""
                if parent_key not in inserted:
                    continue
                tree_data.Insert(parent_key, str(unit.id), unit.name, [])
                inserted.add(str(unit.id))
                remaining.remove(unit)
                progress = True
            if not progress:
                raise ValueError("Organization hierarchy contains an unresolved parent")
        return tree_data

    organization_tab = [
        [sg.Text("Define the organization", font=("Any", 18))],
        [sg.Text("Organizations", font=label_font)],
        [sg.Table(
            organization_rows(),
            headings=["ID", "Name", "Units"],
            key="organization_table",
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            auto_size_columns=False,
            col_widths=[38, 28, 8],
            num_rows=5,
            font=input_font,
        )],
        [sg.Text("New organization name", font=label_font), sg.Input("", key="new_organization_name", font=input_font)],
        [sg.Button("Add Organization", key="add_organization", font=button_font), sg.Button("Delete Organization", key="delete_organization", font=button_font)],
        [sg.Text("Selected organization: none", key="selected_organization", font=label_font)],
        [sg.Text("Structure preview", font=label_font)],
        [sg.Checkbox("Advanced: Edit as text", key="show_text_editor", enable_events=True, font=label_font)],
        [sg.Tree(
            hierarchy_tree_data(),
            headings=[],
            key="hierarchy_tree",
            enable_events=True,
            show_expanded=True,
            num_rows=7,
            col0_width=45,
            font=input_font,
        )],
        [sg.Button("Add Unit", key="add_unit", font=button_font), sg.Button("Edit Unit", key="edit_unit", font=button_font), sg.Button("Delete Unit", key="delete_unit", font=button_font)],
        [sg.pin(sg.Column([
            [sg.Text("One unit per line: unit | parent", font=label_font)],
            [sg.Multiline("", size=(60, 8), key="hierarchy", font=input_font)],
        ], key="text_editor_column", visible=False, pad=(0, 0)))],
    ]
    people_tab = [
        [sg.Text("Add people", font=("Any", 18))],
        [sg.Text("Organization", font=label_font), sg.Combo(
            organization_names(),
            default_value=(initial_people_organization.name if initial_people_organization else ""),
            key="people_organization",
            enable_events=True,
            readonly=True,
            font=input_font,
        )],
        [sg.Text("Population count", font=label_font), sg.Input(people_setting("population_count"), key="population_count", font=input_font)],
        [sg.Text("Locale", font=label_font), sg.Input(people_setting("locale"), key="locale", font=input_font)],
        [sg.Text("Minimum age", font=label_font), sg.Input(people_setting("minimum_age"), key="minimum_age", font=input_font)],
        [sg.Text("Maximum age", font=label_font), sg.Input(people_setting("maximum_age"), key="maximum_age", font=input_font)],
        [sg.Button("Generate People", key="generate_people", font=button_font), sg.Button("Preview People", key="preview_people", font=button_font)],
    ]
    workforce_tab = [
        [sg.Text("Workforce simulation", font=("Any", 18))],
        [sg.Text("Transfer rate (0-1)", font=label_font), sg.Input(setting("transfer_rate"), key="transfer_rate", font=input_font)],
        [sg.Text("Resignation rate (0-1)", font=label_font), sg.Input(setting("resignation_rate"), key="resignation_rate", font=input_font)],
        [sg.Text("Retirement age", font=label_font), sg.Input(setting("retirement_age"), key="retirement_age", font=input_font)],
        [sg.Button("Run Workforce Simulation", key="simulate_workforce", font=button_font)],
    ]
    assessment_tab = [
        [sg.Text("Health assessments", font=("Any", 18))],
        [sg.Text("Generate scheduled preventive assessments and run a basic GLU/HGB panel.", font=label_font)],
        [sg.Text("Schedule", font=label_font), sg.Combo(["Annual", "Every 2 Years", "Once"], default_value=setting("assessment_schedule"), key="assessment_schedule", readonly=True, font=input_font)],
        [sg.Text("Start offset (years)", font=label_font), sg.Input(setting("assessment_offset"), key="assessment_offset", font=input_font)],
        [sg.Text("Trigger mode", font=label_font), sg.Combo(["Scheduled", "After Event"], default_value=setting("assessment_trigger_mode"), key="assessment_trigger_mode", readonly=True, font=input_font)],
        [sg.Text("Trigger event", font=label_font), sg.Input(setting("trigger_event"), key="trigger_event", font=input_font)],
        [sg.Text("Trigger delay (days)", font=label_font), sg.Input(setting("trigger_delay_days"), key="trigger_delay_days", font=input_font)],
        [sg.Button("Run Scheduled Assessments", key="run_assessments", font=button_font)],
    ]
    export_tab = [
        [sg.Text("Review and export", font=("Any", 18))],
        [sg.Button("Export JSON", key="export_json", font=button_font, disabled=True), sg.Button("Export SQLite", key="export_sqlite", font=button_font, disabled=True)],
        [sg.Multiline(size=(80, 14), key="output", disabled=True, font=input_font)],
    ]
    layout = [
        [sg.Text("HealthFoundry", font=("Any", 24))],
        [sg.TabGroup([[sg.Tab("World", world_tab), sg.Tab("Organization", organization_tab), sg.Tab("People", people_tab), sg.Tab("Workforce", workforce_tab), sg.Tab("Assessments", assessment_tab), sg.Tab("Export", export_tab)]], font=("Any", 16), expand_x=True)],
        [sg.Text("", key="status", font=label_font, size=(100, 2))],
        [sg.Button("Save", key="save_world", font=button_font)],
        [sg.Button("Exit", font=button_font)],
    ]
    window = sg.Window("HealthFoundry", layout, resizable=True, finalize=True)
    window["hierarchy_tree"].Widget.bind(
        "<Double-1>",
        lambda _event: window.write_event_value("edit_unit", None),
    )

    def update_organization_table() -> None:
        window["organization_table"].update(values=organization_rows())

    def update_people_organizations(selected_name=None) -> None:
        names = organization_names()
        window["people_organization"].update(
            values=names,
            value=selected_name if selected_name in names else (names[0] if names else ""),
        )

    def capture_people_settings(values) -> None:
        if selected_people_organization_id is None or not values:
            return
        current = people_settings_by_organization.setdefault(
            str(selected_people_organization_id), {}
        )
        for key in ("population_count", "locale", "minimum_age", "maximum_age"):
            value = values.get(key)
            if value not in (None, "", "None"):
                current[key] = str(value)

    def update_people_fields() -> None:
        for key in ("population_count", "locale", "minimum_age", "maximum_age"):
            window[key].update(people_setting(key))

    def update_hierarchy_tree() -> None:
        # Use the positional form for compatibility across FreeSimpleGUI versions.
        window["hierarchy_tree"].update(hierarchy_tree_data(selected_organization_id))

    def load_selected_organization() -> bool:
        if world is None or selected_organization_id is None:
            show("Select an organization first")
            return False
        hierarchy = next(
            (item for item in world.hierarchies if item.organization_id == selected_organization_id),
            None,
        )
        if hierarchy is None:
            show("The selected organization has no structure")
            return False
        unit_names = {unit.id: unit.name for unit in hierarchy.units}
        structure = "\n".join(
            f"{unit.name} | {unit_names[unit.parent_id] if unit.parent_id else ''}"
            for unit in hierarchy.units
        )
        window["hierarchy"].update(structure)
        update_hierarchy_tree()
        return True

    def hierarchy_text(hierarchy) -> str:
        unit_names = {unit.id: unit.name for unit in hierarchy.units}
        return "\n".join(
            f"{unit.name} | {unit_names[unit.parent_id] if unit.parent_id else ''}"
            for unit in hierarchy.units
        )

    def replace_selected_hierarchy(hierarchy) -> None:
        nonlocal world
        world = world.replace_hierarchy(hierarchy)
        window["hierarchy"].update(hierarchy_text(hierarchy))
        update_hierarchy_tree()
        update_organization_table()

    def add_unit() -> None:
        if world is None or selected_organization_id is None:
            show("Select an organization first")
            return
        hierarchy = next(
            item for item in world.hierarchies
            if item.organization_id == selected_organization_id
        )
        name = sg.popup_get_text("Unit name", title="Add Unit")
        if not name or not name.strip():
            return
        if any(unit.name == name.strip() for unit in hierarchy.units):
            show("Unit names must be unique")
            return
        unit = OrganizationalUnit.create(hierarchy.organization_id, name.strip())
        replace_selected_hierarchy(
            OrganizationHierarchy(hierarchy.organization_id, (*hierarchy.units, unit))
        )
        show(f"Unit added: {unit.name}")

    def delete_unit() -> None:
        nonlocal selected_unit_id
        if world is None or selected_organization_id is None or selected_unit_id is None:
            show("Select a unit first")
            return
        hierarchy = next(
            item for item in world.hierarchies
            if item.organization_id == selected_organization_id
        )
        unit = next((item for item in hierarchy.units if str(item.id) == selected_unit_id), None)
        if unit is None:
            show("The selected unit no longer exists")
            return
        if any(item.parent_id == unit.id for item in hierarchy.units):
            show("Delete child units first")
            return
        if sg.popup_yes_no(f"Delete unit '{unit.name}'?") != "Yes":
            return
        selected_unit_id = None
        replace_selected_hierarchy(
            OrganizationHierarchy(
                hierarchy.organization_id,
                tuple(item for item in hierarchy.units if item.id != unit.id),
            )
        )
        show(f"Unit deleted: {unit.name}")

    def edit_unit() -> None:
        if world is None or selected_organization_id is None or selected_unit_id is None:
            show("Select a unit first")
            return
        hierarchy = next(
            item for item in world.hierarchies
            if item.organization_id == selected_organization_id
        )
        unit = next((item for item in hierarchy.units if str(item.id) == selected_unit_id), None)
        if unit is None:
            show("The selected unit no longer exists")
            return
        descendants = set()
        changed = True
        while changed:
            changed = False
            for item in hierarchy.units:
                if item.parent_id == unit.id or item.parent_id in descendants:
                    if item.id not in descendants:
                        descendants.add(item.id)
                        changed = True
        choices = ["(Top level)"] + [
            item.name for item in hierarchy.units
            if item.id != unit.id and item.id not in descendants
        ]
        modal = sg.Window(
            "Choose Parent",
            [
                [sg.Text("Unit name", font=label_font), sg.Input(unit.name, key="name", font=input_font)],
                [sg.Text(f"Parent for {unit.name}", font=label_font)],
                [sg.Combo(choices, default_value=next((item.name for item in hierarchy.units if item.id == unit.parent_id), "(Top level)"), key="parent", readonly=True, font=input_font)],
                [sg.Button("Apply", font=button_font), sg.Button("Cancel", font=button_font)],
            ],
            modal=True,
        )
        modal_event, modal_values = modal.read()
        modal.close()
        if modal_event != "Apply":
            return
        name = (modal_values["name"] or "").strip()
        if not name:
            show("Unit names must not be empty")
            return
        if any(item.id != unit.id and item.name == name for item in hierarchy.units):
            show("Unit names must be unique")
            return
        parent_name = modal_values["parent"]
        parent_id = next((item.id for item in hierarchy.units if item.name == parent_name), None)
        updated_unit = OrganizationalUnit(unit.id, unit.organization_id, name, parent_id)
        replace_selected_hierarchy(
            OrganizationHierarchy(
                hierarchy.organization_id,
                tuple(updated_unit if item.id == unit.id else item for item in hierarchy.units),
            )
        )
        show(f"Unit updated: {name}")

    def show(message: str) -> None:
        window["output"].update(message)
        window["status"].update(message)

    def enable_exports() -> None:
        window["export_json"].update(disabled=False)
        window["export_sqlite"].update(disabled=False)

    def current_settings(values) -> dict:
        values = values or {}
        capture_people_settings(values)
        settings = {
            key: str(
                values.get(key)
                if values.get(key) not in (None, "", "None")
                else setting(key)
            )
            for key in setting_defaults
        }
        selected_people = next(
            (item.name for item in (world.organizations if world else ()) if item.id == selected_people_organization_id),
            "",
        )
        settings["people_organization"] = selected_people
        settings["people_settings"] = people_settings_by_organization
        return settings

    def update_simulation_config(values) -> None:
        nonlocal simulation_config
        values = values or {}
        seed = values.get("seed")
        years = values.get("years")
        if seed in (None, "", "None") or years in (None, "", "None"):
            return
        simulation_config = SimulationConfig(
            random_seed=int(seed),
            start_date=simulation_config.start_date,
            years=int(years),
        )

    def apply_edited_structure(values) -> bool:
        """Apply the visible structure editor before the single global save."""

        nonlocal world
        if world is None or selected_organization_id is None or not values:
            return True
        hierarchy_text = values.get("hierarchy")
        if hierarchy_text is None:
            return True
        relationships = []
        for line in hierarchy_text.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split("|", 1)]
            relationships.append((parts[0], parts[1] if len(parts) == 2 and parts[1] else None))
        if not relationships:
            show("Enter at least one organizational unit before saving")
            return False
        hierarchy = OrganizationHierarchyGenerator(
            RandomSource(simulation_config.random_seed + 1)
        ).generate_explicit(selected_organization_id, relationships)
        world = world.replace_hierarchy(hierarchy)
        return True

    def save_current_world(values) -> bool:
        if world is None:
            show("Create or update the world before saving")
            return False
        update_simulation_config(values)
        if not apply_edited_structure(values):
            return False
        update_hierarchy_tree()
        store.save(world_name, world, current_settings(values))
        show(f"World saved: {world_name}")
        return True

    def regenerate_people(values) -> bool:
        nonlocal world
        if world is None or simulation_config is None or not world.organizations:
            show("Create an organization first")
            return False
        organization_name = values.get("people_organization")
        organization = next(
            (item for item in world.organizations if item.name == organization_name),
            None,
        )
        if organization is None:
            show("Select an organization first")
            return False
        hierarchy = next(
            (item for item in world.hierarchies if item.organization_id == organization.id),
            None,
        )
        if hierarchy is None or not hierarchy.units:
            show("Add organizational units before generating people")
            return False
        organization_seed = organization.id.value.int
        population = PopulationConfig(
            count=int(values["population_count"]),
            locale=values["locale"].strip(),
            minimum_age=int(values["minimum_age"]),
            maximum_age=int(values["maximum_age"]),
        )
        people = PersonGenerator(
            RandomSource(simulation_config.random_seed + 2 + organization_seed)
        ).generate(population, simulation_config.start_date)
        episodes = EmploymentGenerator(
            RandomSource(simulation_config.random_seed + 3 + organization_seed)
        ).assign_initial(
            people,
            organization.id,
            hierarchy,
            simulation_config.start_date,
        )
        world = world.replace_organization_people(
            organization.id,
            tuple(people),
            tuple(episodes),
        )
        show(f"Replaced population for {organization.name} with {len(people)} people")
        enable_exports()
        return True

    def preview_people(settings_values) -> None:
        if world is None:
            show("Create or generate people first")
            return
        selected_organization = next(
            (item for item in world.organizations if item.id == selected_people_organization_id),
            None,
        )
        if selected_organization is None:
            show("Select an organization first")
            return

        def people_rows():
            unit_names = {
                unit.id: unit.name
                for hierarchy in world.hierarchies
                for unit in hierarchy.units
            }
            organization_names_by_id = {
                organization.id: organization.name
                for organization in world.organizations
            }
            rows = []
            for person in world.people:
                episodes = [
                    episode
                    for episode in world.employment_episodes
                    if episode.person_id == person.id
                    and episode.organization_id == selected_people_organization_id
                ]
                if not episodes:
                    continue
                organizations = "; ".join(
                    organization_names_by_id.get(episode.organization_id, str(episode.organization_id))
                    for episode in episodes
                )
                employment = "; ".join(
                    f"{unit_names.get(episode.unit_id, str(episode.unit_id))} "
                    f"({episode.start_date} to {episode.end_date or 'active'})"
                    for episode in episodes
                )
                rows.append([
                    str(person.id),
                    organizations,
                    person.given_name,
                    person.family_name,
                    str(person.date_of_birth or ""),
                    employment,
                ])
            return rows

        rows = people_rows()

        preview_window = sg.Window(
            "People Preview",
            [
                [sg.Text(f"{selected_organization.name} — People: {len(rows)}", key="people_count", font=("Any", 18))],
                [sg.Table(
                    rows,
                    key="people_table",
                    headings=["ID", "Organization", "Given name", "Family name", "Date of birth", "Employment"],
                    auto_size_columns=False,
                    col_widths=[38, 28, 16, 16, 14, 50],
                    expand_x=True,
                    expand_y=True,
                    num_rows=max(5, min(20, len(rows) or 5)),
                    justification="left",
                    font=input_font,
                )],
                [sg.Button("Regenerate People", key="regenerate_people", font=button_font), sg.Button("Close", font=button_font)],
            ],
            resizable=True,
            finalize=True,
        )
        while True:
            preview_event, _ = preview_window.read()
            if preview_event in (sg.WIN_CLOSED, "Close"):
                break
            if preview_event == "regenerate_people" and regenerate_people(settings_values):
                refreshed_rows = people_rows()
                preview_window["people_table"].update(values=refreshed_rows)
                preview_window["people_count"].update(
                    f"{selected_organization.name} — People: {len(refreshed_rows)}"
                )
        preview_window.close()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        try:
            if event == "new_world":
                simulation_config = SimulationConfig(
                    random_seed=int(values["seed"]),
                    start_date=date.today(),
                    years=int(values["years"]),
                )
                world = World.empty()
                selected_organization_id = None
                selected_unit_id = None
                selected_people_organization_id = None
                update_organization_table()
                update_people_organizations()
                window["selected_organization"].update("Selected organization: none")
                update_hierarchy_tree()
                show("New empty world created. Add an organization next.")

            elif event == "organization_table":
                selected = values.get("organization_table", [])
                if selected and world is not None:
                    selected_organization_id = world.organizations[selected[0]].id
                    selected_unit_id = None
                    selected_organization = world.organizations[selected[0]]
                    window["selected_organization"].update(
                        f"Selected organization: {selected_organization.name}"
                    )
                    load_selected_organization()

            elif event == "hierarchy_tree":
                selected = values.get("hierarchy_tree", [])
                selected_unit_id = str(selected[0]) if selected else None

            elif event == "people_organization":
                capture_people_settings(values)
                selected_people_organization_id = next(
                    (item.id for item in world.organizations if item.name == values.get("people_organization")),
                    None,
                )
                update_people_fields()

            elif event == "show_text_editor":
                window["text_editor_column"].update(
                    visible=bool(values.get("show_text_editor"))
                )

            elif event == "add_unit":
                add_unit()

            elif event == "delete_unit":
                delete_unit()

            elif event == "edit_unit":
                edit_unit()

            elif event == "add_organization":
                if world is None or simulation_config is None:
                    show("Create a new world first")
                    continue
                update_simulation_config(values)
                organization_name = (values.get("new_organization_name") or "").strip()
                if not organization_name:
                    show("Enter an organization name first")
                    continue
                relationships = []
                hierarchy_text = values.get("hierarchy") or ""
                for line in hierarchy_text.splitlines():
                    if not line.strip():
                        continue
                    parts = [part.strip() for part in line.split("|", 1)]
                    relationships.append((parts[0], parts[1] if len(parts) == 2 and parts[1] else None))
                if not relationships:
                    show("Enter at least one organizational unit first")
                    continue
                organization_randomness = RandomSource(
                    simulation_config.random_seed + len(world.organizations) + 1
                )
                organization_id = OrganizationId(organization_randomness.uuid())
                existing_ids = {item.id for item in world.organizations}
                while organization_id in existing_ids:
                    organization_id = OrganizationId(organization_randomness.uuid())
                organization = Organization(
                    organization_id,
                    organization_name,
                )
                hierarchy = OrganizationHierarchyGenerator(
                    RandomSource(simulation_config.random_seed + len(world.organizations) + 2)
                ).generate_explicit(organization.id, relationships)
                world = world.add_organization(organization).add_hierarchy(hierarchy)
                selected_organization_id = organization.id
                selected_people_organization_id = organization.id
                window["organization_table"].update(
                    values=organization_rows(),
                    select_rows=[len(world.organizations) - 1],
                )
                window["new_organization_name"].update("")
                window["selected_organization"].update(
                    f"Selected organization: {organization.name}"
                )
                update_people_organizations(organization.name)
                update_people_fields()
                update_hierarchy_tree()
                window["hierarchy"].set_focus()
                show(f"Organization added with {len(hierarchy.units)} organizational units")
                enable_exports()

            elif event == "load_organization":
                if load_selected_organization():
                    show("Organization structure loaded for editing")

            elif event == "delete_organization":
                if world is None or selected_organization_id is None:
                    show("Select an organization first")
                    continue
                organization = next(
                    (item for item in world.organizations if item.id == selected_organization_id),
                    None,
                )
                if organization is None:
                    show("The selected organization no longer exists")
                    continue
                if sg.popup_yes_no(f"Delete '{organization.name}' and its dependent records?") != "Yes":
                    continue
                world = world.remove_organization(selected_organization_id)
                selected_organization_id = None
                if selected_people_organization_id == organization.id:
                    selected_people_organization_id = None
                update_organization_table()
                update_people_organizations()
                if selected_people_organization_id is None and world.organizations:
                    selected_people_organization_id = world.organizations[0].id
                update_people_fields()
                window["selected_organization"].update("Selected organization: none")
                window["hierarchy"].update("")
                update_hierarchy_tree()
                show(f"Organization deleted: {organization.name}")
                enable_exports()

            elif event == "generate_people":
                update_simulation_config(values)
                regenerate_people(values)

            elif event == "preview_people":
                preview_people(values)

            elif event == "simulate_workforce":
                update_simulation_config(values)
                if world is None or simulation_config is None or not world.people:
                    show("Generate people first")
                    continue
                workforce_config = WorkforceConfig(
                    transfer_rate=float(values["transfer_rate"]),
                    resignation_rate=float(values["resignation_rate"]),
                    retirement_age=int(values["retirement_age"]),
                )
                world = WorkforceSimulator(
                    RandomSource(simulation_config.random_seed + 4)
                ).simulate(world, simulation_config, workforce_config)
                show(f"Workforce simulation complete\nEvents: {len(world.workforce_events)}\nEmployment episodes: {len(world.employment_episodes)}")
                enable_exports()

            elif event == "run_assessments":
                update_simulation_config(values)
                if world is None or simulation_config is None or not world.people:
                    show("Generate people first")
                    continue
                glucose = LaboratoryTestDefinition.create("GLU", "Glucose", "serum", "mg/dL")
                hemoglobin = LaboratoryTestDefinition.create("HGB", "Hemoglobin", "whole blood", "g/dL")
                panel = LaboratoryPanel.create("BASIC", "Basic preventive panel", (glucose.id, hemoglobin.id))
                catalog = LaboratoryCatalog(
                    tests=(glucose, hemoglobin),
                    panels=(panel,),
                    result_models=(LaboratoryResultModel(glucose.id, 100.0, 10.0), LaboratoryResultModel(hemoglobin.id, 14.0, 1.0)),
                )
                offset = int(values["assessment_offset"])
                schedule_name = values["assessment_schedule"]
                if schedule_name == "Annual":
                    schedule = Schedule(interval_years=1, start_offset_years=offset)
                elif schedule_name == "Every 2 Years":
                    schedule = Schedule(interval_years=2, start_offset_years=offset)
                else:
                    schedule = Schedule.once(start_offset_years=offset)
                assessment_rule = ScenarioRule("preventive_assessment", "health_assessment", ActiveEmployeesSelector(), schedule=schedule)
                rules = (assessment_rule,)
                if values["assessment_trigger_mode"] == "After Event":
                    trigger_event = values["trigger_event"].strip()
                    rules = (
                        ScenarioRule("scenario_trigger_event", trigger_event, ActiveEmployeesSelector(), schedule=Schedule.once(start_offset_years=offset)),
                        ScenarioRule("preventive_assessment_after_event", "health_assessment", ActiveEmployeesSelector(), after=AfterEvent(trigger_event, int(values["trigger_delay_days"]))),
                    )
                events = ScenarioEngine(RandomSource(simulation_config.random_seed + 5)).generate_events(world, simulation_config, rules)
                world = ScenarioEventApplier(RandomSource(simulation_config.random_seed + 6)).apply(world, events, catalog, "BASIC", AssessmentContext.OCCUPATIONAL)
                show(f"Assessments: {len(world.assessments)}\nOrders: {len(world.laboratory_orders)}\nObservations: {len(world.laboratory_observations)}")
                enable_exports()

            elif event == "export_json":
                if world is None:
                    show("Create a world first")
                    continue
                path = sg.popup_get_file("Save JSON", save_as=True, default_extension=".json", file_types=(("JSON Files", "*.json"),))
                if path:
                    Path(path).write_text(world.to_json() + "\n", encoding="utf-8")
                    show(f"JSON exported to {path}")

            elif event == "save_world":
                save_current_world(values)

            elif event == "export_sqlite":
                if world is None:
                    show("Create a world first")
                    continue
                path = sg.popup_get_file("Save SQLite database", save_as=True, default_extension=".sqlite", file_types=(("SQLite Database", "*.sqlite"),))
                if path:
                    from sqlalchemy import create_engine

                    world.to_sql_tables(create_engine(f"sqlite:///{path}"))
                    show(f"SQLite exported to {path}")
        except (ImportError, RuntimeError, TypeError, ValueError) as error:
            show(f"Error: {error}")

    window.close()
    if world is not None and apply_edited_structure(values):
        store.save(world_name, world, current_settings(values))


def main() -> None:
    """Launch the World Manager and per-world settings windows."""

    try:
        import FreeSimpleGUI as sg
    except ImportError as error:
        raise SystemExit(
            "The GUI requires the optional dependency. "
            "Install it with: pip install 'healthfoundry[gui]'"
        ) from error

    from healthfoundry import WorldStore

    store = WorldStore()
    label_font = ("Any", 14)
    button_font = ("Any", 14)

    def get_rows():
        metadata = store.list()
        rows = [
            [item.name, item.modified_at.strftime("%Y-%m-%d %H:%M")]
            for item in metadata
        ]
        return metadata, rows

    metadata, display_rows = get_rows()
    layout = [
        [sg.Text("HealthFoundry Worlds", font=("Any", 24))],
        [sg.Text("Select a saved world to open its settings.", font=label_font)],
        [sg.Table(
            display_rows,
            headings=["World", "Modified"],
            key="world_list",
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            auto_size_columns=True,
            expand_x=True,
            num_rows=10,
            font=label_font,
        )],
        [
            sg.Button("New World", key="new_world", font=button_font),
            sg.Button("Open", key="open_world", font=button_font),
            sg.Button("Delete", key="delete_world", font=button_font),
            sg.Button("Exit", key="exit", font=button_font),
        ],
    ]
    window = sg.Window("HealthFoundry World Manager", layout, resizable=True, finalize=True)
    window["world_list"].Widget.bind(
        "<Double-1>",
        lambda _event: window.write_event_value("open_world", None),
    )

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "exit"):
            break
        if event == "new_world":
            name = sg.popup_get_text("World name", title="Create World")
            if name and name.strip():
                _run_settings(sg, store, name.strip())
                metadata, display_rows = get_rows()
                window["world_list"].update(values=display_rows)
        elif event in ("open_world", "delete_world"):
            selected = values.get("world_list", [])
            if not selected:
                sg.popup("Select a world first")
                continue
            selected_metadata = metadata[selected[0]]
            if event == "open_world":
                _run_settings(
                    sg,
                    store,
                    selected_metadata.name,
                    store.open(selected_metadata.slug),
                    store.settings(selected_metadata.slug),
                )
            elif sg.popup_yes_no(f"Delete '{selected_metadata.name}'?") == "Yes":
                store.delete(selected_metadata.slug)
            metadata, display_rows = get_rows()
            window["world_list"].update(values=display_rows)

    window.close()
