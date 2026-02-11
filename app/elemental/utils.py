import ipaddress
from urllib.parse import urlencode, urlparse
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


def is_safe_url(url: str) -> bool:
    BLOCKED_RANGES = [
        ipaddress.ip_network("10.0.0.0/8"),  # Private Class A
        ipaddress.ip_network("172.16.0.0/12"),  # Private Class B
        ipaddress.ip_network("192.168.0.0/16"),  # Private Class C
        ipaddress.ip_network("127.0.0.0/8"),  # Loopback
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local
        ipaddress.ip_network("::1/128"),  # IPv6 loopback
        ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ]

    # Restrict to safe schemes and ports
    ALLOWED_SCHEMES = ["http", "https"]
    ALLOWED_PORTS = [80, 443, 8080, 8443]

    """Validate URL is safe to fetch - prevents SSRF attacks"""
    try:
        parsed = urlparse(url)

        # Check scheme is HTTP or HTTPS
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        # Check port is allowed
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if port not in ALLOWED_PORTS:
            return False

        # Get a hostname for validation
        import socket
        hostname = parsed.hostname
        if not hostname:
            return False

        # Block localhost variations
        if hostname in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return False

        # Resolve the hostname and check if IP is in blocked ranges
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            for blocked in BLOCKED_RANGES:
                if ip in blocked:
                    return False
        except socket.gaierror:
            return False  # DNS resolution failed

        return True

    except Exception:
        return False
