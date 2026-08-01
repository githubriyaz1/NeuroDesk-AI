import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, BinaryIO
from uuid import UUID, uuid4
from app.core.config import settings
from app.core.logging import logger
from app.services.checksum_service import checksum_service


class StorageProvider(ABC):
    """Abstract interface for pluggable storage providers (Local, S3, GCS, Azure)."""

    @abstractmethod
    async def save_file(
        self, user_id: UUID, original_filename: str, file_obj: BinaryIO
    ) -> Tuple[str, int, str]:
        """Save file content and return (relative_storage_path, file_size_bytes, sha256_checksum)."""
        pass

    @abstractmethod
    def get_absolute_path(self, relative_storage_path: str) -> Path:
        """Resolve relative storage path to absolute filesystem path safely."""
        pass

    @abstractmethod
    async def delete_file(self, relative_storage_path: str) -> bool:
        """Physically delete file from storage."""
        pass

    @abstractmethod
    def file_exists(self, relative_storage_path: str) -> bool:
        """Check if file exists in storage."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local Filesystem Storage Provider storing files under storage/uploads/{user_id}/{year}/{month}/."""

    def __init__(self, base_dir: str = None):
        target_dir = base_dir or getattr(settings, "STORAGE_LOCAL_ROOT", "storage/uploads")
        self.base_path = Path(target_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize client-provided filename to prevent path traversal or unsafe characters."""
        safe_name = os.path.basename(filename)
        clean = "".join(c for c in safe_name if c.isalnum() or c in "._- ")
        return clean.strip() or "unnamed_asset"

    async def save_file(
        self, user_id: UUID, original_filename: str, file_obj: BinaryIO
    ) -> Tuple[str, int, str]:
        now = datetime.now(timezone.utc)
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        safe_name = self._sanitize_filename(original_filename)
        unique_name = f"{uuid4().hex}_{safe_name}"

        relative_dir = Path(str(user_id)) / year / month
        target_dir = (self.base_path / relative_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file_path = (target_dir / unique_name).resolve()

        # Security check: ensure target file is strictly inside base_path
        if not str(target_file_path).startswith(str(self.base_path)):
            raise ValueError("Path traversal attempt detected in storage provider.")

        # Compute SHA256 checksum and size using ChecksumService
        checksum_hex, file_size = checksum_service.calculate_sha256(file_obj)

        with open(target_file_path, "wb") as out_file:
            file_obj.seek(0)
            while chunk := file_obj.read(8192):
                out_file.write(chunk)

        relative_path_str = str(relative_dir / unique_name).replace("\\", "/")

        logger.info(f"LocalStorageProvider saved file: {relative_path_str} ({file_size} bytes)")
        return relative_path_str, file_size, checksum_hex

    def get_absolute_path(self, relative_storage_path: str) -> Path:
        resolved = (self.base_path / relative_storage_path).resolve()
        if not str(resolved).startswith(str(self.base_path)):
            raise ValueError("Path traversal attempt detected in path resolution.")
        return resolved

    async def delete_file(self, relative_storage_path: str) -> bool:
        try:
            abs_path = self.get_absolute_path(relative_storage_path)
            if abs_path.exists() and abs_path.is_file():
                abs_path.unlink()
                logger.info(f"LocalStorageProvider deleted file: {relative_storage_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file from storage: {relative_storage_path} - {e}")
            return False

    def file_exists(self, relative_storage_path: str) -> bool:
        try:
            abs_path = self.get_absolute_path(relative_storage_path)
            return abs_path.exists() and abs_path.is_file()
        except Exception:
            return False


class StorageService:
    """Enterprise Storage Service wrapping the active StorageProvider."""

    def __init__(self, provider: StorageProvider = None):
        self.provider = provider or LocalStorageProvider()

    async def save_file(
        self, user_id: UUID, original_filename: str, file_obj: BinaryIO
    ) -> Tuple[str, int, str]:
        return await self.provider.save_file(user_id, original_filename, file_obj)

    def get_absolute_path(self, relative_storage_path: str) -> Path:
        return self.provider.get_absolute_path(relative_storage_path)

    async def delete_file(self, relative_storage_path: str) -> bool:
        return await self.provider.delete_file(relative_storage_path)

    def file_exists(self, relative_storage_path: str) -> bool:
        return self.provider.file_exists(relative_storage_path)


storage_service = StorageService()
