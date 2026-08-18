from datetime import datetime
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    api_status: str = "healthy"
    database_status: str = "connected"
    storage_status: str = "writable"
    app_name: str
    version: str
    environment: str
    timestamp: datetime
