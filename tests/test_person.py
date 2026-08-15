import pytest

from healthfoundry import Person, PersonId


def test_person_creation_and_full_name() -> None:
    person = Person.create("Ada", "Lovelace")

    assert isinstance(person.id, PersonId)
    assert person.full_name == "Ada Lovelace"


@pytest.mark.parametrize(
    ("given_name", "family_name", "message"),
    [
        ("", "Lovelace", "Person given name must not be empty"),
        ("Ada", "   ", "Person family name must not be empty"),
    ],
)
def test_person_rejects_blank_names(
    given_name: str,
    family_name: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Person.create(given_name, family_name)

