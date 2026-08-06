import abc
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.logging import logger
from app.schemas.knowledge import RetrievedDocument
from app.services.storage_service import storage_service


def _read_file_preview(storage_path: str, max_bytes: int = 10000) -> str:
    """Safely reads raw text preview from asset file on disk."""
    try:
        if storage_service.file_exists(storage_path):
            abs_path = storage_service.get_absolute_path(storage_path)
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes).strip()
    except Exception as exc:
        logger.warning(f"Could not read asset file from storage [{storage_path}]: {exc}")
    return ""


def _query_matches_text(query: str, text: str) -> bool:
    """Checks if query keywords match candidate document text using word stem matching."""
    if not query or not query.strip():
        return True
    clean_query = re.sub(r"[^\w\s]", " ", query.lower())
    stopwords = {"the", "and", "this", "that", "what", "how", "are", "there", "for", "with", "show", "give", "tell", "explain", "many", "which", "does", "is"}
    words = [w for w in clean_query.split() if len(w) >= 2 and w not in stopwords]
    if not words:
        return True
    text_lower = text.lower()
    for w in words:
        if w in text_lower or text_lower in w:
            return True
        stem = w.rstrip("s").rstrip("ing").rstrip("ed")
        if len(stem) >= 2 and stem in text_lower:
            return True
    tabular_intents = {"employee", "employees", "count", "average", "mean", "median", "highest", "lowest", "total", "age", "tier", "salary", "salaries", "city", "department", "rows", "summary"}
    if any(w in tabular_intents for w in words):
        return True
    return False


class BaseRetriever(abc.ABC):
    """Abstract interface for all knowledge retrievers."""

    @property
    @abc.abstractmethod
    def retriever_type(self) -> str:
        pass

    @abc.abstractmethod
    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        pass


class PDFRetriever(BaseRetriever):
    """Retriever for PDF document pages and text sections."""

    @property
    def retriever_type(self) -> str:
        return "pdf"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.models.asset import Asset
            from sqlalchemy import select

            stmt = select(Asset).where(
                Asset.owner_id == owner_id,
                Asset.is_deleted == False,
                (Asset.mime_type == "application/pdf") | (Asset.extension == ".pdf") | (Asset.asset_type == "REPORT"),
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            res = await db_session.execute(stmt)
            pdf_assets = res.scalars().all()

            for asset in pdf_assets:
                filename = asset.original_filename or asset.name
                file_text = _read_file_preview(asset.storage_path)
                combined_text = f"{filename} {asset.description or ''} {file_text}"

                # Extract page number if specified in query
                page_match = re.search(r"\bpage\s*(\d+)\b", query.lower())
                page_num = int(page_match.group(1)) if page_match else 1

                if _query_matches_text(query, combined_text) or page_match:
                    body = file_text if file_text else (asset.description or f"PDF document '{filename}' content")
                    results.append(
                        RetrievedDocument(
                            id=f"pdf-{asset.id}-p{page_num}",
                            asset_id=asset.id,
                            asset_name=filename,
                            content=f"PDF Document '{filename}' [Page {page_num}]:\n{body}",
                            source_type="pdf",
                            page_number=page_num,
                            section=f"Page {page_num}",
                            score=0.98 if page_match else 0.92,
                            metadata={"file_size": asset.file_size, "mime_type": asset.mime_type, "target_page": page_num},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.warning(f"PDFRetriever failed: {exc}")

        return results[:limit]


class CSVRetriever(BaseRetriever):
    """Retriever for CSV tabular datasets and header structures."""

    @property
    def retriever_type(self) -> str:
        return "csv"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.models.asset import Asset
            from sqlalchemy import select

            stmt = select(Asset).where(
                Asset.owner_id == owner_id,
                Asset.is_deleted == False,
                (Asset.mime_type.in_(["text/csv", "application/csv"])) | (Asset.extension == ".csv") | (Asset.asset_type == "SPREADSHEET"),
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            res = await db_session.execute(stmt)
            csv_assets = res.scalars().all()

            for asset in csv_assets:
                filename = asset.original_filename or asset.name
                abs_path = storage_service.get_absolute_path(asset.storage_path) if storage_service.file_exists(asset.storage_path) else ""
                file_text = _read_file_preview(asset.storage_path)
                combined_text = f"{filename} {asset.description or ''} {file_text}"

                if _query_matches_text(query, combined_text):
                    body = file_text if file_text else (asset.description or f"CSV dataset '{filename}' content")
                    path_tag = f" [FILE_PATH: {abs_path}]" if abs_path else ""
                    results.append(
                        RetrievedDocument(
                            id=f"csv-{asset.id}-data",
                            asset_id=asset.id,
                            asset_name=filename,
                            content=f"CSV Dataset '{filename}'{path_tag}:\n{body}",
                            source_type="csv",
                            section="Data Rows",
                            score=0.95,
                            metadata={"file_size": asset.file_size, "mime_type": asset.mime_type, "abs_path": str(abs_path)},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.warning(f"CSVRetriever failed: {exc}")

        return results[:limit]


class ExcelRetriever(BaseRetriever):
    """Retriever for Excel spreadsheet workbooks and worksheets."""

    @property
    def retriever_type(self) -> str:
        return "excel"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.models.asset import Asset
            from sqlalchemy import select

            stmt = select(Asset).where(
                Asset.owner_id == owner_id,
                Asset.is_deleted == False,
                Asset.mime_type.in_([
                    "application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ]),
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            res = await db_session.execute(stmt)
            excel_assets = res.scalars().all()

            for asset in excel_assets:
                filename = asset.original_filename or asset.name
                file_text = _read_file_preview(asset.storage_path)
                combined_text = f"{filename} {asset.description or ''} {file_text}"

                if _query_matches_text(query, combined_text):
                    body = file_text if file_text else (asset.description or f"Excel workbook '{filename}' content")
                    results.append(
                        RetrievedDocument(
                            id=f"excel-{asset.id}-sheet1",
                            asset_id=asset.id,
                            asset_name=filename,
                            content=f"Excel Workbook '{filename}':\n{body}",
                            source_type="excel",
                            section="Sheet1",
                            score=0.88,
                            metadata={"file_size": asset.file_size, "mime_type": asset.mime_type},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.warning(f"ExcelRetriever failed: {exc}")

        return results[:limit]


class MetadataRetriever(BaseRetriever):
    """Retriever for asset key-value metadata properties."""

    @property
    def retriever_type(self) -> str:
        return "metadata"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.models.asset import Asset
            from app.models.asset_metadata import AssetMetadata
            from sqlalchemy import select

            stmt = select(Asset, AssetMetadata).join(AssetMetadata, Asset.id == AssetMetadata.asset_id).where(
                Asset.owner_id == owner_id,
                Asset.is_deleted == False,
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            res = await db_session.execute(stmt)
            pairs = res.all()

            for asset, meta in pairs:
                filename = asset.original_filename or asset.name
                abs_path = storage_service.get_absolute_path(asset.storage_path) if storage_service.file_exists(asset.storage_path) else ""
                path_tag = f" [FILE_PATH: {abs_path}]" if abs_path else ""
                meta_str = f"{meta.metadata_key}: {meta.metadata_value or ''}"
                if _query_matches_text(query, meta_str):
                    results.append(
                        RetrievedDocument(
                            id=f"meta-{asset.id}-{meta.id}",
                            asset_id=asset.id,
                            asset_name=filename,
                            content=f"Asset Metadata [{filename}]{path_tag}: {meta.metadata_key} = {meta.metadata_value}",
                            source_type="metadata",
                            section="Extracted Attributes",
                            score=0.85,
                            metadata={meta.metadata_key: meta.metadata_value, "value_type": meta.value_type, "abs_path": str(abs_path)},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.warning(f"MetadataRetriever failed: {exc}")

        return results[:limit]


class SearchRetriever(BaseRetriever):
    """Retriever connecting directly to the Search & Discovery Platform."""

    @property
    def retriever_type(self) -> str:
        return "search"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.services.search_service import search_service

            search_res = await search_service.search(
                db=db_session,
                user_id=owner_id,
                q=query,
                page=1,
                page_size=limit,
            )

            for item in search_res.items:
                asset = item.asset
                if asset_ids and asset.id not in asset_ids:
                    continue
                filename = asset.original_filename or asset.name
                abs_path = storage_service.get_absolute_path(asset.storage_path) if storage_service.file_exists(asset.storage_path) else ""
                path_tag = f" [FILE_PATH: {abs_path}]" if abs_path else ""
                file_text = _read_file_preview(asset.storage_path)
                body = file_text[:500] if file_text else (asset.description or 'Matching workspace asset.')
                results.append(
                    RetrievedDocument(
                        id=f"search-{asset.id}",
                        asset_id=asset.id,
                        asset_name=filename,
                        content=f"Search Result '{filename}' ({asset.asset_type}){path_tag}:\n{body}",
                        source_type="search",
                        section="Workspace Index",
                        score=0.80,
                        metadata={"asset_type": asset.asset_type, "checksum": asset.checksum, "abs_path": str(abs_path)},
                        created_at=asset.created_at,
                    )
                )
        except Exception as exc:
            logger.warning(f"SearchRetriever failed: {exc}")

        return results[:limit]


class ImageMetadataRetriever(BaseRetriever):
    """Retriever for image metadata, resolution, and EXIF attributes."""

    @property
    def retriever_type(self) -> str:
        return "image_metadata"

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        results = []
        if not db_session:
            return results

        try:
            from app.models.asset import Asset
            from sqlalchemy import select

            stmt = select(Asset).where(
                Asset.owner_id == owner_id,
                Asset.is_deleted == False,
                Asset.mime_type.like("image/%"),
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            res = await db_session.execute(stmt)
            image_assets = res.scalars().all()

            for asset in image_assets:
                filename = asset.original_filename or asset.name
                if _query_matches_text(query, filename):
                    results.append(
                        RetrievedDocument(
                            id=f"img-{asset.id}",
                            asset_id=asset.id,
                            asset_name=filename,
                            content=f"Image Asset '{filename}': Image resolution and metadata attributes.",
                            source_type="image_metadata",
                            section="EXIF",
                            score=0.70,
                            metadata={"mime_type": asset.mime_type, "file_size": asset.file_size},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.warning(f"ImageMetadataRetriever failed: {exc}")

        return results[:limit]


class FutureRetriever(BaseRetriever):
    """Extension hook retriever for third-party knowledge sources (VectorDB, SQL, GitHub, SharePoint, Confluence)."""

    def __init__(self, provider_name: str = "future_extension"):
        self._provider_name = provider_name

    @property
    def retriever_type(self) -> str:
        return self._provider_name

    async def retrieve(
        self,
        query: str,
        owner_id: UUID,
        limit: int = 5,
        asset_ids: Optional[List[UUID]] = None,
        db_session: Optional[Any] = None,
    ) -> List[RetrievedDocument]:
        return []
