import pytest

from healthfoundry import HierarchyConfig


def test_hierarchy_config_normalizes_names_to_tuple() -> None:
    config = HierarchyConfig.from_names(["Hospital", "Laboratory"])

    assert config.unit_names == ("Hospital", "Laboratory")


@pytest.mark.parametrize(
    "unit_names",
    [(), ("Hospital", "Hospital"), ("Hospital", "")],
)
def test_hierarchy_config_rejects_invalid_names(unit_names: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        HierarchyConfig(unit_names)
