def test_gui_module_is_importable_without_optional_dependency() -> None:
    import healthfoundry.gui

    assert callable(healthfoundry.gui.main)

