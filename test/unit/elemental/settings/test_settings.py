import pytest
from unittest.mock import MagicMock
from app.elemental.settings.elemental import ElementalSettings, CliApplication, WebApplication
from app.elemental.settings.state import init_settings, get_settings, _settings

# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_settings_state():
    """Reset global state before each test."""
    # Access the global variable through the imported module
    import app.elemental.settings.state as state_module
    state_module._settings = None
    yield
    state_module._settings = None

# --- ElementalSettings Tests ---

def test_web_application_defaults():
    """Must have correct defaults for Web."""
    web_app = WebApplication()
    assert web_app.app_type == "web"
    assert web_app.cors.allow_credentials is True
    # SSL disabled by default
    assert web_app.ssl_enabled is False

def test_cli_application_defaults():
    """Must have correct defaults for CLI."""
    cli_app = CliApplication()
    assert cli_app.app_type == "cli"

def test_elemental_settings_discrimination(monkeypatch):
    """Must correctly discriminate between Web and CLI using app_type."""
    # FORCE init_settings load by setting the environment variable that activates standard logic
    # See elemental.py:66
    monkeypatch.setenv("elementalback_application__app_env", "test")

    # Web case
    settings_web = ElementalSettings(
        application={"app_type": "web", "app_name": "WebTest"}
    )
    assert isinstance(settings_web.application, WebApplication)
    assert settings_web.application.app_type == "web"

    # CLI case
    settings_cli = ElementalSettings(
        application={"app_type": "cli", "app_name": "CliTest"}
    )
    assert isinstance(settings_cli.application, CliApplication)
    assert settings_cli.application.app_type == "cli"

def test_elemental_settings_env_override(monkeypatch):
    """Must allow override by environment variables."""
    # The settings_customise_sources method explicitly looks for this variable in lowercase on line 66 of elemental.py
    monkeypatch.setenv("elementalback_application__app_env", "custom_env")
    
    # Pydantic v2 reads standard environment variables (usually uppercase) for fields
    monkeypatch.setenv("elementalback_application__app_name", "EnvApp")
    monkeypatch.setenv("elementalback_application__app_type", "web")
    
    settings = ElementalSettings()
    assert settings.application.app_name == "EnvApp"

# --- State Tests ---

def test_init_and_get_settings():
    """Must initialize and retrieve settings globally."""
    s = ElementalSettings(application={"app_type": "web"})
    init_settings(s)
    
    retrieved = get_settings()
    assert retrieved is s

def test_get_settings_uninitialized():
    """Must raise RuntimeError if not initialized."""
    with pytest.raises(RuntimeError):
        get_settings()
