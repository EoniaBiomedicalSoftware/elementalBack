import aiosmtplib

from aiosmtplib import (
    SMTPRecipientsRefused,
    SMTPSenderRefused,
    SMTPDataError,
    SMTPException,
    SMTP
)

from logging import Logger
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base import EmailServiceBase
from ..settings import EmailSettings
from ..exceptions import (
    EmailConnectionError,
    EmailRecipientsRefused,
    EmailSenderRefused,
    EmailDataError,
    EmailError,
)


class EmailServiceManager(EmailServiceBase):
    def __init__(
        self,
        templates_dir: Path,
        templates_context: Dict[str, Dict[str, Any]],
        settings: EmailSettings,
        logger: Optional[Logger | str] = None
    ):
        super().__init__(
            templates_dir=templates_dir,
            templates_context=templates_context,
            settings=settings,
            logger=logger
        )


        try:
            self._server = settings.server
            self._port = settings.port
            self._use_ssl = settings.use_ssl
            self._use_tls = settings.use_tls
            self._timeout = settings.timeout
        except Exception as e:
            self.logger.error(f"Failed to initialize AIOSEmailService: {e}")

        self.logger.info("AIOSEmailService initialized")

    async def init_connection(self) -> SMTP:
        return aiosmtplib.SMTP(
            hostname=self._server,
            port=self._port,
            timeout=self._timeout,
            use_tls=self._use_ssl,
            start_tls=self._use_tls
        )

    async def test_connection(self) -> bool:
        try:
            async with await self.init_connection() as smtp:
                if self.settings.username and self.settings.password:
                    await smtp.login(
                        self.settings.username,
                        self.settings.password.get_secret_value()
                    )
                await smtp.noop()
                self.logger.info(f"SMTP connection test passed for {self.settings.server}")
                return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False

    async def send(
        self,
        template_name: str,
        context: Dict[str, Any],
        recipients: List[str],
        attachments: Optional[List[Path]] = None
    ) -> None:
        self._validate_context(template_name, context)
        html_content = self._fill_template(template_name, context)

        try:
            subject = self.templates_context[template_name]["subject"]
        except KeyError:
            self.logger.warning(f"Subject not found for {template_name}, using default.")
            subject = "No Subject"

        # 2. Message Construction
        # This uses your existing _create_message with MIMEMultipart
        message = self._create_message(
            recipients,
            subject,
            html_content,
            attachments
        )

        try:
            async with await self.init_connection() as smtp:
                if self.settings.username and self.settings.password:
                    await smtp.login(
                        self.settings.username,
                        self.settings.password.get_secret_value()
                    )
                await smtp.send_message(message)

        except SMTPRecipientsRefused as e:
            self.logger.error(f"SMTP error: Recipients refused: {e}")
            raise EmailRecipientsRefused(f"Recipients refused by server: {e}") from e

        except SMTPSenderRefused as e:
            self.logger.error(f"SMTP error: Sender refused: {e}")
            raise EmailSenderRefused(f"Sender refused by server: {e}") from e

        except SMTPDataError as e:
            self.logger.error(f"SMTP error: Data refused: {e}")
            raise EmailDataError(f"Email content refused by server: {e}") from e

        except SMTPException as e:
            self.logger.error(f"Generic SMTP error during transmission: {e}")
            raise EmailConnectionError(f"SMTP communication error: {e}") from e

        except Exception as e:
            self.logger.error(f"Unexpected error in EmailService: {e}")
            raise EmailError(f"Unexpected email transmission error: {e}") from e
