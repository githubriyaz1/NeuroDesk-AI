from datetime import datetime
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    app_name: str
    version: str
    environment: str
    timestamp: datetime
