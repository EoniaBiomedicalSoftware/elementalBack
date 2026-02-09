import pytest
from enum import Enum
from app.elemental.common.error_codes import ElementalErrorCode
from app.elemental.common.schemas.elemental import ElementalSchema

def test_elemental_error_code_structure():
    """Must have HTTP code and message."""
    error = ElementalErrorCode.INVALID_INPUT
    assert isinstance(error.http_code, int)
    assert isinstance(error.default_message, str)
    assert error.http_code == 400

def test_elemental_error_code_to_dict():
    """Must convert to dictionary name -> code."""
    d = ElementalErrorCode.to_dict()
    assert d["INVALID_INPUT"] == 400
    assert "UNAUTHORIZED" in d

def test_elemental_schema_config():
    """Must have correct base configuration."""
    class TestSchema(ElementalSchema):
        id: int
        
    # Verify from_attributes (orm_mode in v1)
    assert TestSchema.model_config.get("from_attributes") is True
    # Verify ignore extras
    assert TestSchema.model_config.get("extra") == "ignore"

def test_elemental_schema_instantiation():
    """Must instantiate correctly and ignore extras."""
    class TestSchema(ElementalSchema):
        name: str
        
    obj = TestSchema(name="test", extra_field="ignored")
    assert obj.name == "test"
    assert not hasattr(obj, "extra_field")
