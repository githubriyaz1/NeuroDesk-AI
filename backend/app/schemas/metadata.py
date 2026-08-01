from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator


class MetadataItemSchema(BaseModel):
    key: str
    value: Optional[str] = None
    value_type: str
    extracted_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def populate_key_and_value(cls, data: Any) -> Any:
        if hasattr(data, "metadata_key"):
            return {
                "key": getattr(data, "metadata_key"),
                "value": getattr(data, "metadata_value", None),
                "value_type": getattr(data, "value_type", "string"),
                "extracted_at": getattr(data, "extracted_at"),
            }
        if isinstance(data, dict):
            if "metadata_key" in data and "key" not in data:
                data["key"] = data["metadata_key"]
            if "metadata_value" in data and "value" not in data:
                data["value"] = data["metadata_value"]
        return data


class MetadataGroupSchema(BaseModel):
    category: str
    items: List[MetadataItemSchema]


class AssetMetadataResponse(BaseModel):
    asset_id: UUID
    groups: List[MetadataGroupSchema]
    items: List[MetadataItemSchema]
    total_keys: int

    model_config = ConfigDict(from_attributes=True)
