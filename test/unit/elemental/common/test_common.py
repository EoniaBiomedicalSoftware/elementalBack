import pytest
from enum import Enum
from app.elemental.common.error_codes import ElementalErrorCode
from app.elemental.common.schemas.elemental import ElementalSchema

def test_elemental_error_code_structure():
    """Debe tener código HTTP y mensaje."""
    error = ElementalErrorCode.INVALID_INPUT
    assert isinstance(error.http_code, int)
    assert isinstance(error.default_message, str)
    assert error.http_code == 400

def test_elemental_error_code_to_dict():
    """Debe convertir a diccionario nombre -> código."""
    d = ElementalErrorCode.to_dict()
    assert d["INVALID_INPUT"] == 400
    assert "UNAUTHORIZED" in d

def test_elemental_schema_config():
    """Debe tener configuración base correcta."""
    class TestSchema(ElementalSchema):
        id: int
        
    # Verificar from_attributes (orm_mode en v1)
    assert TestSchema.model_config.get("from_attributes") is True
    # Verificar ignorar extras
    assert TestSchema.model_config.get("extra") == "ignore"

def test_elemental_schema_instantiation():
    """Debe instanciar correctamente e ignorar extras."""
    class TestSchema(ElementalSchema):
        name: str
        
    obj = TestSchema(name="test", extra_field="ignored")
    assert obj.name == "test"
    assert not hasattr(obj, "extra_field")
