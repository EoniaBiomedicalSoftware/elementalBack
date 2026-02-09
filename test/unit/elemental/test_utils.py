import pytest
from unittest.mock import MagicMock, patch
from app.elemental.utils import build_url

@pytest.fixture
def mock_settings():
    """Mock completo de la configuración."""
    with patch("app.elemental.utils.get_settings") as mock_get:
        settings_mock = MagicMock()
        # Configuración por defecto para backend
        settings_mock.application.frontend_host_url = ""
        settings_mock.application.api_version = "v1"
        settings_mock.application.ssl_enabled = False
        settings_mock.application.host = "localhost"
        settings_mock.application.port = 8000
        
        mock_get.return_value = settings_mock
        yield settings_mock

def test_build_url_backend_default(mock_settings):
    """Debe construir la URL usando la configuración del backend si no hay frontend URL."""
    url = build_url(backend_path="/users", frontend_path="/login")
    assert url == "http://localhost:8000/api/v1/users"

def test_build_url_with_frontend_host(mock_settings):
    """Debe usar la URL del frontend si está configurada."""
    mock_settings.application.frontend_host_url = "https://mi-frontend.com"
    
    url = build_url(backend_path="/users", frontend_path="/login")
    assert url == "https://mi-frontend.com/login"

def test_build_url_with_params(mock_settings):
    """Debe añadir parámetros de consulta correctamente."""
    url = build_url(
        backend_path="/search",
        frontend_path="/buscar",
        params={"q": "test", "page": 1}
    )
    assert url == "http://localhost:8000/api/v1/search?q=test&page=1"

def test_build_url_custom_api_version(mock_settings):
    """Debe respetar una versión de API personalizada."""
    url = build_url(
        backend_path="/test",
        frontend_path="/test",
        api_version="v2"
    )
    assert url == "http://localhost:8000/api/v2/test"

def test_build_url_ssl_enabled(mock_settings):
    """Debe usar https si ssl_enabled es True en el backend."""
    mock_settings.application.ssl_enabled = True
    
    url = build_url(backend_path="/secure", frontend_path="/secure")
    assert url == "https://localhost:8000/api/v1/secure"
