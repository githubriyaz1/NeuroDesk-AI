import hashlib
from typing import BinaryIO, Tuple


class ChecksumService:
    """Dedicated service for calculating cryptographic file hashes."""

    @staticmethod
    def calculate_sha256(file_obj: BinaryIO, chunk_size: int = 8192) -> Tuple[str, int]:
        """Calculates SHA-256 hex digest and total byte count from a file stream."""
        hasher = hashlib.sha256()
        total_size = 0
        
        try:
            initial_pos = file_obj.tell()
        except (AttributeError, OSError):
            initial_pos = None

        while chunk := file_obj.read(chunk_size):
            total_size += len(chunk)
            hasher.update(chunk)

        if initial_pos is not None:
            try:
                file_obj.seek(initial_pos)
            except (AttributeError, OSError):
                pass

        return hasher.hexdigest(), total_size

    @staticmethod
    def calculate_bytes_sha256(content: bytes) -> str:
        """Calculates SHA-256 hex digest directly from in-memory byte buffer."""
        return hashlib.sha256(content).hexdigest()


checksum_service = ChecksumService()
