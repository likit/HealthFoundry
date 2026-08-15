from datetime import date

from healthfoundry import (
    LaboratoryTestDefinition,
    LaboratoryPanel,
    Organization,
    Person,
    RandomOrderGenerator,
    RandomSource,
    RuleBasedOrderGenerator,
)


def _setup():
    organization = Organization.create("North Valley Hospital")
    person = Person.create("Ada", "Lovelace")
    tests = (
        LaboratoryTestDefinition.create("CBC", "Complete blood count", "blood"),
        LaboratoryTestDefinition.create("GLU", "Glucose", "blood", "mg/dL"),
    )
    return organization, person, tests


def test_rule_based_generator_orders_every_test() -> None:
    organization, person, tests = _setup()

    orders = RuleBasedOrderGenerator().generate(
        person.id, organization.id, tests, date(2026, 1, 1), "Annual health check"
    )

    assert len(orders) == 2
    assert tuple(order.test_definition_id for order in orders) == tuple(test.id for test in tests)


def test_random_generator_is_reproducible() -> None:
    organization, person, tests = _setup()

    first = RandomOrderGenerator(RandomSource(42), 0.5).generate(
        person.id, organization.id, tests, date(2026, 1, 1)
    )
    second = RandomOrderGenerator(RandomSource(42), 0.5).generate(
        person.id, organization.id, tests, date(2026, 1, 1)
    )

    assert first == second


def test_rule_based_generator_can_order_a_panel() -> None:
    organization, person, tests = _setup()
    panel = LaboratoryPanel.create("ANNUAL", "Annual health check", tuple(test.id for test in tests))

    orders = RuleBasedOrderGenerator().generate_panel(
        person.id,
        organization.id,
        panel,
        tests,
        date(2026, 1, 1),
    )

    assert len(orders) == len(tests)
