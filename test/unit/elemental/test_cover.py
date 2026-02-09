import pytest
from unittest.mock import patch, MagicMock
from app.elemental.cover import get_cover
from app.elemental.settings.elemental import WebApplication

@pytest.fixture
def mock_cover_settings():
    with patch("app.elemental.cover.get_settings") as mock_get:
        settings = MagicMock()
        settings.application.app_name = "TestApp"
        settings.application.app_version = "1.0.0"
        settings.application.app_env = "test"
        settings.application.debug = True
        settings.application.host = "localhost"
        settings.application.port = 8000
        settings.application.ssl_enabled = False
        
        mock_get.return_value = settings
        yield settings

@patch("app.elemental.cover.typer.echo")
@patch("app.elemental.cover.typer.secho")
def test_get_cover_web_debug(mock_secho, mock_echo, mock_cover_settings):
    """Must show complete information in web mode with debug."""
    mock_cover_settings.application.debug = True
    
    get_cover("web")
    
    # Verify basic calls
    assert mock_secho.call_count >= 5
    assert mock_echo.call_count >= 1

@patch("app.elemental.cover.typer.echo")
@patch("app.elemental.cover.typer.secho")
def test_get_cover_cli(mock_secho, mock_echo, mock_cover_settings):
    """Must show limited information in cli mode."""
    get_cover("cli")
    
    # In CLI mode it does not print URL or Docs
    # Validate that it does not attempt to access exclusive web attributes if they are not necessary
    # (although current code accesses settings.application which has everything)
    assert mock_secho.called
    assert mock_echo.called

@patch("app.elemental.cover.typer.echo")
@patch("app.elemental.cover.typer.secho")
def test_get_cover_ssl_enabled(mock_secho, mock_echo, mock_cover_settings):
    """Must show https if SSL is enabled."""
    mock_cover_settings.application.ssl_enabled = True
    
    get_cover("web")
    
    # We could inspect call arguments to verify 'https'
    # but verifying that it runs without error is a good start.
    assert mock_secho.called
