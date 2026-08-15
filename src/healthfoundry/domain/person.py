"""Person-related domain primitives."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class PersonId:
    """Stable identity for a person in a synthetic healthcare world."""

    value: UUID

    @classmethod
    def new(cls) -> "PersonId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Person:
    """A person represented in the canonical world."""

    id: PersonId
    given_name: str
    family_name: str

    def __post_init__(self) -> None:
        if not self.given_name.strip():
            raise ValueError("Person given name must not be empty")
        if not self.family_name.strip():
            raise ValueError("Person family name must not be empty")

    @classmethod
    def create(cls, given_name: str, family_name: str) -> "Person":
        """Create a person with a generated identity."""

        return cls(
            id=PersonId.new(),
            given_name=given_name,
            family_name=family_name,
        )

    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"

