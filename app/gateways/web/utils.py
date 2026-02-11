import inspect
from typing import Type
from fastapi import Form
from pydantic import BaseModel

def as_form(cls: Type[BaseModel]):
    """
    Decorator to add a .as_form() method to a Pydantic model.
    """
    parameters = []
    for name, field in cls.model_fields.items():
        parameters.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Form(field.default if field.default is not None else ...),
                annotation=field.annotation,
            )
        )

    async def to_form(**data):
        return cls(**data)

    sig = inspect.Signature(parameters=parameters)
    to_form.__signature__ = sig
    cls.as_form = to_form # Inject the method
    return cls
