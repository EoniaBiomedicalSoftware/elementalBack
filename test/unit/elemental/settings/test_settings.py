import pytest
from unittest.mock import MagicMock
from app.elemental.settings.elemental import ElementalSettings, CliApplication, WebApplication
from app.elemental.settings.state import init_settings, get_settings, _settings

# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_settings_state():
    """Resetear estado global antes de cada test."""
    # Accedemos a la variable global mediante el módulo importado
    import app.elemental.settings.state as state_module
    state_module._settings = None
    yield
    state_module._settings = None

# --- ElementalSettings Tests ---

def test_web_application_defaults():
    """Debe tener defaults correctos para Web."""
    web_app = WebApplication()
    assert web_app.app_type == "web"
    assert web_app.cors.allow_credentials is True
    # SSL disabled by default
    assert web_app.ssl_enabled is False

def test_cli_application_defaults():
    """Debe tener defaults correctos para CLI."""
    cli_app = CliApplication()
    assert cli_app.app_type == "cli"

def test_elemental_settings_discrimination(monkeypatch):
    """Debe discriminar correctamente entre Web y CLI usando app_type."""
    # FORZAR carga de init_settings seteando la variable de entorno que activa la lógica estándar
    # Ver elemental.py:66
    monkeypatch.setenv("elementalback_application__app_env", "test")

    # Caso Web
    settings_web = ElementalSettings(
        application={"app_type": "web", "app_name": "WebTest"}
    )
    assert isinstance(settings_web.application, WebApplication)
    assert settings_web.application.app_type == "web"

    # Caso CLI
    settings_cli = ElementalSettings(
        application={"app_type": "cli", "app_name": "CliTest"}
    )
    assert isinstance(settings_cli.application, CliApplication)
    assert settings_cli.application.app_type == "cli"

def test_elemental_settings_env_override(monkeypatch):
    """Debe permitir override por variables de entorno."""
    # El método settings_customise_sources busca explícitamente esta variable en minúsculas en la línea 66 de elemental.py
    monkeypatch.setenv("elementalback_application__app_env", "custom_env")
    
    # Pydantic v2 lee variables de entorno estándar (usualmente mayúsculas) para los campos
    monkeypatch.setenv("elementalback_application__app_name", "EnvApp")
    monkeypatch.setenv("elementalback_application__app_type", "web")
    
    settings = ElementalSettings()
    assert settings.application.app_name == "EnvApp"

# --- State Tests ---

def test_init_and_get_settings():
    """Debe inicializar y recuperar settings globalmente."""
    s = ElementalSettings(application={"app_type": "web"})
    init_settings(s)
    
    retrieved = get_settings()
    assert retrieved is s

def test_get_settings_uninitialized():
    """Debe lanzar RuntimeError si no se inicializó."""
    with pytest.raises(RuntimeError):
        get_settings()
