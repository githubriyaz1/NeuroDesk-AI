import abc
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.schemas.knowledge import RetrievedDocument


class BaseRetriever(abc.ABC):
    """Abstract interface for all knowledge retrievers.
    
    Architecture Rule: KnowledgeEngine MUST only communicate with BaseRetriever.
    New retrievers (e.g. VectorRetriever, SQLRetriever, GitHubRetriever, SharePointRetriever,
    ConfluenceRetriever, WebRetriever, APIDataRetriever) inherit from BaseRetriever without
    modifying KnowledgeEngine core.
    """

    @property
    @abc.abstractmethod
    def retriever_type(self) -> str:
        """Unique string identifier for the retriever type."""
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
        """Perform document retrieval for a query strictly scoped to owner_id."""
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
                Asset.mime_type == "application/pdf",
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            query_lower = query.lower()
            res = await db_session.execute(stmt)
            pdf_assets = res.scalars().all()

            for asset in pdf_assets:
                text_content = f"{asset.filename} {asset.description or ''}"
                if any(w in text_content.lower() for w in query_lower.split()):
                    results.append(
                        RetrievedDocument(
                            id=f"pdf-{asset.id}-p1",
                            asset_id=asset.id,
                            asset_name=asset.filename,
                            content=f"PDF Document '{asset.filename}': {asset.description or 'PDF document content'}",
                            source_type="pdf",
                            page_number=1,
                            section="Overview",
                            score=0.85,
                            metadata={"file_size": asset.file_size_bytes, "mime_type": asset.mime_type},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception:
            pass

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
                Asset.mime_type.in_(["text/csv", "application/csv"]),
            )
            if asset_ids:
                stmt = stmt.where(Asset.id.in_(asset_ids))

            query_lower = query.lower()
            res = await db_session.execute(stmt)
            csv_assets = res.scalars().all()

            for asset in csv_assets:
                if any(w in asset.filename.lower() for w in query_lower.split()):
                    results.append(
                        RetrievedDocument(
                            id=f"csv-{asset.id}-headers",
                            asset_id=asset.id,
                            asset_name=asset.filename,
                            content=f"CSV Dataset '{asset.filename}': Tabular dataset containing rows and columns.",
                            source_type="csv",
                            section="Header Summary",
                            score=0.80,
                            metadata={"file_size": asset.file_size_bytes, "mime_type": asset.mime_type},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception:
            pass

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

            query_lower = query.lower()
            res = await db_session.execute(stmt)
            excel_assets = res.scalars().all()

            for asset in excel_assets:
                if any(w in asset.filename.lower() for w in query_lower.split()):
                    results.append(
                        RetrievedDocument(
                            id=f"excel-{asset.id}-sheet1",
                            asset_id=asset.id,
                            asset_name=asset.filename,
                            content=f"Excel Workbook '{asset.filename}': Sheet 1 containing financial/analytical formulas.",
                            source_type="excel",
                            section="Sheet1",
                            score=0.82,
                            metadata={"file_size": asset.file_size_bytes, "mime_type": asset.mime_type},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception:
            pass

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

            query_lower = query.lower()
            res = await db_session.execute(stmt)
            pairs = res.all()

            for asset, meta in pairs:
                meta_json_str = str(meta.metadata_json or {}).lower()
                if any(w in meta_json_str for w in query_lower.split()):
                    results.append(
                        RetrievedDocument(
                            id=f"meta-{asset.id}",
                            asset_id=asset.id,
                            asset_name=asset.filename,
                            content=f"Asset Metadata [{asset.filename}]: {meta.summary_text or str(meta.metadata_json)}",
                            source_type="metadata",
                            section="Extracted Attributes",
                            score=0.90,
                            metadata=meta.metadata_json or {},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception:
            pass

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
            from app.schemas.search import SearchQueryRequest

            req = SearchQueryRequest(query=query, page_size=limit)
            search_res = await search_service.execute_search(db_session, owner_id, req)

            for item in search_res.items:
                results.append(
                    RetrievedDocument(
                        id=f"search-{item.id}",
                        asset_id=item.id,
                        asset_name=item.filename,
                        content=f"Search Result '{item.filename}' ({item.category}): {item.description or 'Matching asset found in index.'}",
                        source_type="search",
                        section="Workspace Index",
                        score=0.75,
                        metadata={"category": item.category, "checksum": item.checksum_sha256},
                        created_at=item.created_at,
                    )
                )
        except Exception:
            pass

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

            query_lower = query.lower()
            res = await db_session.execute(stmt)
            image_assets = res.scalars().all()

            for asset in image_assets:
                if any(w in asset.filename.lower() for w in query_lower.split()):
                    results.append(
                        RetrievedDocument(
                            id=f"img-{asset.id}",
                            asset_id=asset.id,
                            asset_name=asset.filename,
                            content=f"Image Asset '{asset.filename}': Image resolution and metadata attributes.",
                            source_type="image_metadata",
                            section="EXIF",
                            score=0.70,
                            metadata={"mime_type": asset.mime_type, "file_size": asset.file_size_bytes},
                            created_at=asset.created_at,
                        )
                    )
                if len(results) >= limit:
                    break
        except Exception:
            pass

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
