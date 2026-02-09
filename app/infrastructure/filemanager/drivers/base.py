import os
import magic
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

from ..settings import FileManagerSettings
from ..exceptions import (FileValidationError)


class FileManagerBase(ABC):

    def __init__(self, settings: FileManagerSettings):
        self.settings = settings

    def _validate_extension(self, filename: str, filetype: str) -> None:

        separators = [os.sep]
        if os.altsep is not None:
            separators.append(os.altsep)

        for sep in separators:
            if sep in filename:
                raise FileValidationError("File name must not contain path separators.")

        if filetype not in self.settings.allowed_file_types:
            raise FileValidationError(f"File type '{filetype}' is not defined in settings.")

        type_settings = self.settings.allowed_file_types[filetype]

        safe_name = os.path.basename(filename)
        path = Path(safe_name)

        if not path.suffix:
            raise FileValidationError("File has no extension.")

        ext = path.suffix.lower().lstrip(".")

        if len(path.suffixes) > 1:
            raise FileValidationError("Multiple extensions are not allowed.")

        if ext not in type_settings.allowed_extensions:
            allowed = ", ".join(type_settings.allowed_extensions)
            raise FileValidationError(
                f"Extension '.{ext}' is not allowed for file type '{filetype}'. Allowed: {allowed}"
            )

    def _validate_size(self, file_size: int, filetype: str) -> None:
        if filetype not in self.settings.allowed_file_types:
            raise FileValidationError(f"File type '{filetype}' is not allowed.")

        type_settings = self.settings.allowed_file_types[filetype]

        if file_size <= 0:
            raise FileValidationError("File is empty.")

        max_size = type_settings.max_file_size
        if file_size > max_size:
            raise FileValidationError(
                f"File exceeds maximum allowed size of {max_size} bytes."
            )

    def _validate_mime(self, file_bytes: bytes, filename: str, filetype: str) -> None:
        if filetype not in self.settings.allowed_file_types:
            raise FileValidationError(f"File type '{filetype}' is not defined in settings.")

        type_settings = self.settings.allowed_file_types[filetype]

        try:
            detected_mime = magic.from_buffer(file_bytes, mime=True)
        except Exception as e:
            raise FileValidationError(
                f"Could not reliably detect MIME type for file '{os.path.basename(filename)}'."
            ) from e

        allowed_mimes = type_settings.allowed_mimes

        if detected_mime in allowed_mimes:
            return

        main_type = detected_mime.split("/")[0] + "/*"

        if main_type in allowed_mimes:
            return

        allowed_list = ", ".join(allowed_mimes)

        raise FileValidationError(
            f"MIME type '{detected_mime}' not allowed for file '{filename}' "
            f"(Type '{filetype}' allows: {allowed_list})."
        )

    @staticmethod
    def _normalize_path(path: str) -> str:
        return os.path.normpath(path).replace("\\", "/")

    @abstractmethod
    def _ensure_directory(self, path: str):
        """
        Ensures the directory exists or raises FileAccessError.
        """
        raise NotImplementedError()

    def _validate_file(self, filetype:str, file_bytes: bytes, filename: str) -> None:
        """
        Validates extension, size, and MIME type.
        Raises FileValidationError on failure.
        """
        self._validate_extension(filename, filetype)
        self._validate_size(len(file_bytes), filetype)
        self._validate_mime(file_bytes, filename, filetype)

    @abstractmethod
    async def upload(
        self,
        filetype: str,
        file_bytes: bytes,
        filename: str,
        storage_path: str = "",
        content_type: Optional[str] = None
    ) -> str:
        raise NotImplementedError()

    async def update(self,
         filetype: str,
         old_file_path: str,
         file_bytes: bytes,
         filename: str,
         content_type: Optional[str] = None
    ) -> str:
        raise NotImplementedError()


    @abstractmethod
    async def get_public_url(self, file_path: str) -> str:
        raise NotImplementedError()