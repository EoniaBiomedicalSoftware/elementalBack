from typing import (
    List
)
from pathlib import Path

from .drivers import EmailServiceManager


async def safe_send_email(
    email_service: EmailServiceManager,
    template_name: str,
    context: dict,
    recipients: list
) -> None:
    """
    Safely sends an email using the specified service and template.
    """
    await email_service.send(
        template_name=template_name,
        context=context,
        recipients=recipients
    )


async def safe_send_email_with_attachments(
    email_service: EmailServiceManager,
    template_name: str,
    context: dict,
    recipients: list,
    attachments: List[Path]
) -> None:
    """
    Safely sends an email including one or more file attachments.
    """
    await email_service.send(
        template_name=template_name,
        context=context,
        recipients=recipients,
        attachments=attachments
    )