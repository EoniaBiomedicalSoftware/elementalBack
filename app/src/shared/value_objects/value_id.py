import uuid
from uuid import uuid4
from typing import Annotated
from pydantic import BeforeValidator, Field

from app.elemental.exceptions import InvalidFormatError


def validate_uuid_v4(value: object) -> str:
    val = str(value).strip() if value else ""

    if not val:
        raise InvalidFormatError(
            field_name="id",
            value=val,
            expected_format="A non-empty UUID v4 string"
        )

    try:
        uuid_obj = uuid.UUID(hex=val, version=4)
        return str(uuid_obj)
    except (ValueError, AttributeError, TypeError):
        raise InvalidFormatError(
            field_name="id",
            value=val,
            expected_format="Valid UUID v4 (e.g., 550e8400-e29b-41d4-a716-446655440000)"
        )


ValueId = Annotated[
    str,
    BeforeValidator(validate_uuid_v4),
    Field(
        default_factory=lambda: ValueId(uuid4().hex),
        description="Unique identifier in UUID v4 format"
    )
]