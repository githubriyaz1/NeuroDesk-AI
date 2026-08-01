import os
import mimetypes
from typing import BinaryIO, Tuple
from fastapi import HTTPException, status

from app.core.config import settings


class AssetValidationService:
    """Centralized validation engine for asset uploads."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizes filename, preventing path traversal and illegal characters."""
        if not filename or not filename.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty.",
            )

        # Extract basename to strip paths
        clean_name = os.path.basename(filename.strip())

        # Check for path traversal markers
        if ".." in clean_name or "/" in clean_name or "\\" in clean_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsafe filename containing path traversal characters.",
            )

        # Strip unprintable or dangerous characters
        safe_chars = "".join(c for c in clean_name if c.isalnum() or c in "._- ")
        final_name = safe_chars.strip()

        if not final_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename contains invalid characters.",
            )
        return final_name

    @staticmethod
    def validate_file(
        file_obj: BinaryIO,
        original_filename: str,
        client_mime_type: str = None,
    ) -> Tuple[str, str, str]:
        """Validates filename, extension, file size, non-emptiness, and MIME type server-side."""
        safe_filename = AssetValidationService.sanitize_filename(original_filename)

        ext = os.path.splitext(safe_filename)[1].lower().lstrip(".")
        if not ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a valid extension.",
            )

        # Validate allowed extension
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '.{ext}'.",
            )

        # Server-side MIME type verification
        server_mime, _ = mimetypes.guess_type(safe_filename)
        mime_type = server_mime or client_mime_type or "application/octet-stream"

        # Validate non-empty file
        try:
            file_obj.seek(0, os.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(0)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to read upload stream (corrupted file stream).",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty files (0 bytes) are not allowed.",
            )

        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size} bytes) exceeds maximum limit of {max_mb}MB.",
            )

        return safe_filename, ext, mime_type


asset_validation_service = AssetValidationService()
