from pydantic import (
    BaseModel,
    ConfigDict
)


class ElementalSchema(BaseModel):
    """Base schema for all Elemental schemas."""
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )