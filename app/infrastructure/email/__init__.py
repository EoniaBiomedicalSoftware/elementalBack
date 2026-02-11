from .settings import EmailSettings
from .manager import (
    get_email_service,
    init_email_service,
    is_email_service_initialized
)
from .utils import (
    safe_send_email,
    safe_send_email_with_attachments
)


__all__ = [
    'EmailSettings',
    'get_email_service',
    'init_email_service',
    'is_email_service_initialized',
    'safe_send_email_with_attachments',
    'safe_send_email'
]