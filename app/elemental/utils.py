from urllib.parse import urlencode
from .settings import get_settings


def build_url(
    *,
    backend_path: str,
    frontend_path: str,
    api_version: None | str = None,
    params: dict | None = None
) -> str:
    settings = get_settings()
    """
    Builds a dynamic URL based on the environment and available configuration
    """
    frontend_url = (settings.application.frontend_host_url or "").strip()

    api_version = api_version or settings.application.api_version

    # If frontend URL is available → always use it
    if frontend_url:
        base_url = frontend_url.rstrip("/")
        path = frontend_path.lstrip("/")

    # Otherwise → fallback to backend API URL
    else:
        protocol = "https" if settings.application.ssl_enabled else "http"
        host = settings.application.host
        port = settings.application.port

        base_url = f"{protocol}://{host}:{port}/api/{api_version}".rstrip("/")
        path = backend_path.lstrip("/")

    url = f"{base_url}/{path}"

    # Add query parameters
    if params:
        url += "?" + urlencode(params)

    return url
