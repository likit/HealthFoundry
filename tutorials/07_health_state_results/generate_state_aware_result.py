"""Generate a glucose observation influenced by a health-state condition."""

from datetime import date

from healthfoundry import (
    HealthState,
    LaboratoryObservationGenerator,
    LaboratoryOrder,
    LaboratoryTestDefinition,
    Organization,
    Person,
    RandomSource,
)


def main() -> None:
    organization = Organization.create("North Valley Clinic")
    person = Person.create("Ada", "Lovelace")
    glucose = LaboratoryTestDefinition.create(
        "GLU", "Glucose", "serum", "mg/dL"
    )
    order = LaboratoryOrder.create(
        person.id,
        organization.id,
        glucose.id,
        date(2026, 1, 1),
        reason="Preventive assessment",
    )
    state = HealthState(
        person_id=person.id,
        as_of=date(2026, 1, 1),
        condition_codes=frozenset({"diabetes"}),
    )

    observation = LaboratoryObservationGenerator(RandomSource(42)).normal_for_state(
        order=order,
        test_definition=glucose,
        observed_on=date(2026, 1, 1),
        state=state,
        baseline_mean=100.0,
        standard_deviation=10.0,
        state_mean_effects={"diabetes": 30.0},
    )

    print(f"Person: {person.full_name}")
    print(f"Condition: diabetes")
    print(f"Generated glucose: {observation.value:.2f} {observation.unit}")


if __name__ == "__main__":
    main()

