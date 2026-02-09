from abc import abstractmethod, ABC

from pathlib import Path
from logging import Logger
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, TemplateError

from app.elemental.logging import get_logger

from ..settings import EmailSettings
from ..exceptions import (
    EmailTemplateError,
    EmailContextValidationError,
    EmailAttachmentError,
)


class EmailServiceBase(ABC):
    def __init__(
        self,
        templates_dir: Path,
        templates_context: Dict[str, Dict[str, Any]],
        settings: EmailSettings,
        logger: Optional[Logger | str] = None
    ):
        self.settings = settings
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        self.templates_context: dict = templates_context

        if not logger:
            logger = get_logger("email_service")

        self.logger = logger

        self.logger.info(f"EmailService initialized with templates dir: {templates_dir}")

    @abstractmethod
    async def test_connection(self) -> bool:
        raise NotImplementedError

    def _validate_context(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:

        try:
            if template_name not in self.templates_context:
                raise EmailContextValidationError(
                    message=f"Unknown template: {template_name}"
                )

            context_model = self.templates_context[template_name]["context_model"]
            context_model(**context)

        except EmailContextValidationError:
            raise
        except Exception as e:
            raise EmailContextValidationError(
                message=f"Invalid context for {template_name}: {str(e)}",
            ) from e

    def _fill_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        try:
            template_path = self.templates_context[template_name]["template"]
            template = self.env.get_template(template_path)
            return template.render(**context)

        except TemplateError as e:
            self.logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise EmailTemplateError(
                message=f"Error rendering template {template_name}: {str(e)}",
            ) from e
        except Exception as e:
            self.logger.error(f"Unexpected error filling template {template_name}: {str(e)}")
            raise EmailTemplateError(
                message=f"Unexpected error during template filling {template_name}: {str(e)}",
            ) from e

    def _create_message(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        attachments: Optional[List[Path]] = None
    ) -> MIMEMultipart:

        message = MIMEMultipart()
        message["From"] = self.settings.sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject

        # Add HTML content
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)

        # Add attachments if they exist
        if attachments:
            for file_path in attachments:
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, "rb") as attachment_file:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment_file.read())
                            encoders.encode_base64(part)

                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {file_path.name}"
                            )
                            message.attach(part)

                        self.logger.debug(f"Attached file: {file_path.name}")

                    except Exception as e:
                        self.logger.warning(f"Failed to attach file {file_path}: {e}. Raising EmailAttachmentError.")
                        raise EmailAttachmentError(f"Failed to read or attach file {file_path}: {e}") from e
                else:
                    self.logger.warning(f"Attachment path invalid or not found: {file_path}. Raising EmailAttachmentError.")
                    raise EmailAttachmentError(f"Attachment path invalid or not found: {file_path}")

        return message

    @abstractmethod
    async def send(
        self,
        template_name: str,
        context: Dict[str, Any],
        recipients: List[str],
        attachments: Optional[List[Path]] = None
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def init_connection(self) -> None:
        raise NotImplementedError()