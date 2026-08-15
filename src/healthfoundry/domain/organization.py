"""Organization-related domain primitives."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class OrganizationId:
    """Stable identity for an organization in a generated healthcare world."""

    value: UUID

    @classmethod
    def new(cls) -> "OrganizationId":
        """Create a new organization identity."""

        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "OrganizationId":
        """Parse an organization identity from its canonical UUID string."""

        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Organization:
    """A healthcare organization in a canonical synthetic world."""

    id: OrganizationId
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Organization name must not be empty")

    @classmethod
    def create(cls, name: str) -> "Organization":
        """Create a new organization with a generated identity."""

        return cls(id=OrganizationId.new(), name=name)


@dataclass(frozen=True, slots=True)
class OrganizationUnitId:
    """Stable identity for a unit within an organization hierarchy."""

    value: UUID

    @classmethod
    def new(cls) -> "OrganizationUnitId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class OrganizationalUnit:
    """A department, team, or other node in an organization hierarchy."""

    id: OrganizationUnitId
    organization_id: OrganizationId
    name: str
    parent_id: OrganizationUnitId | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Organizational unit name must not be empty")

    @classmethod
    def create(
        cls,
        organization_id: OrganizationId,
        name: str,
        parent_id: OrganizationUnitId | None = None,
    ) -> "OrganizationalUnit":
        """Create a hierarchy unit with a generated identity."""

        return cls(
            id=OrganizationUnitId.new(),
            organization_id=organization_id,
            name=name,
            parent_id=parent_id,
        )
