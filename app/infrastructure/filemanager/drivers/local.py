import os
import uuid
from pathlib import Path
from typing import Optional

from ..settings import FileManagerSettings

from .base import FileManagerBase
from ..exceptions import (
    FileManagerError,
    FileNotFound,
    FileUploadError,
    FileUpdateError,
    FileDeleteError,
    FileValidationError,
    FileAccessError,
)


class LocalFileManager(FileManagerBase):

    def __init__(self, fm_settings: FileManagerSettings):
        super().__init__(fm_settings)
        self.base_path = Path(self.settings.local.path.get_secret_value())
        self.url = "http://localhost:8000"

    def _ensure_directory(self, path: str):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            raise FileAccessError(
                message=f"Failed to create directory '{path}'",
                details=f"Error: {e}"
            )

    async def upload(self, filetype: str, file_bytes: bytes, filename: str, storage_path: str = "", content_type: Optional[str] = None) -> str:
        try:
            self._validate_file(filetype=filetype, file_bytes=file_bytes, filename=filename)
        except Exception as e:
            raise e

        # Create a unique name
        ext = filename.split(".")[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"

        # Determine the directory where the file will be saved
        normalized_storage_path = self._normalize_path(storage_path)
        safe_dir = self.base_path / normalized_storage_path

        try:
            self._ensure_directory(safe_dir)
        except FileManagerError:
            raise
        except Exception as e:
            raise FileAccessError(
                message=f"Failed to prepare directory '{safe_dir}'",
                details=f"Error: {e}"
            )

        full_path = Path(safe_dir) / unique_name

        try:
            with open(full_path, "wb") as f:
                f.write(file_bytes)
        except PermissionError:
            raise FileAccessError(
                f"Permission denied while writing file '{full_path}'."
            )
        except Exception as e:
            raise FileUploadError(
                message=f"Failed to upload file '{filename}' to '{full_path}': {e}",
                details=f"Error: {e}"
            )

        # Return a clean relative path to be used in URL construction
        relative_path_to_return = Path(normalized_storage_path) / unique_name
        return str(relative_path_to_return)

    async def update(self,
             filetype: str,
             old_file_path: str,
             file_bytes: bytes,
             filename: str,
             content_type: Optional[str] = None
         ) -> str:
        relative_path = self._normalize_path(old_file_path)
        absolute_path = Path(self.base_path) / relative_path

        # Must exist
        if not absolute_path.exists():
            raise FileNotFound(f"File '{relative_path}' does not exist.")
        if not absolute_path.is_file():
            raise FileValidationError(
                f"Path '{relative_path}' is not a file, cannot update."
            )

        # Validate the file before writing
        self._validate_file(filetype=filetype, file_bytes=file_bytes, filename=filename)

        self._validate_size(len(file_bytes), filetype=filetype)
        self._validate_mime(file_bytes, filename=absolute_path.name, filetype=filetype)

        # Ensure parent directory exists
        try:
            self._ensure_directory(str(absolute_path.parent))
        except FileManagerError:
            raise
        except Exception as e:
            raise FileAccessError(
                f"Failed to access directory for '{relative_path}'",
                details=f"Error: {e}"
            )

        # Write new content via atomic tmp file
        tmp_path = absolute_path.with_suffix(absolute_path.suffix + ".tmp")

        try:
            with open(tmp_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            raise FileUpdateError(
                f"Failed to write temporary file during update '{relative_path}'",
                details=f"Error: {e}"
            )

        try:
            os.replace(tmp_path, absolute_path)
        except Exception as e:
            raise FileUpdateError(
                f"Failed to replace old file with updated version '{relative_path}'",
                details=f"Error: {e}"
            )

        return relative_path

    async def delete(self, file_path: str) -> None:

        # User passes a full public URL; strip domain
        # Keep comment (it is correct), but improve logic
        file_path = file_path.replace(self.url, "").lstrip("/")

        relative_path = self._normalize_path(file_path)
        absolute_path = Path(self.base_path) / relative_path

        if not absolute_path.exists():
            return  # Silent skip

        if not absolute_path.is_file():
            raise FileValidationError(
                f"Path '{relative_path}' is not a file, cannot delete."
            )

        try:
            absolute_path.unlink()
        except PermissionError:
            raise FileAccessError(
                f"Permission denied while deleting file '{relative_path}'."
            )
        except Exception as e:
            raise FileDeleteError(
                f"Failed to delete file '{relative_path}': {e}",
                details=f"Error: {e}"
            )

    async def exists(self, file_path: str) -> bool:
        relative_path = self._normalize_path(file_path)
        absolute_path = Path(self.base_path) / relative_path
        return absolute_path.exists() and absolute_path.is_file()

    async def get_public_url(self, file_path: str) -> str:
        # 'file_path' is a relative file name; must be resolved inside a storage path
        relative = self._normalize_path(file_path)
        absolute = Path(self.base_path) / relative

        if not absolute.exists():
            raise FileNotFound(
                f"File '{relative}' does not exist."
            )

        # Build clean URL instead of including system paths
        # Note: static routing should map '/{filename}' -> local storage
        return f"{self.url}/{relative}"
