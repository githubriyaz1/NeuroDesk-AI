import json
from typing import List, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "NeuroDesk AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "super_secret_jwt_key_neurodesk_2026_enterprise"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # PostgreSQL connection string
    DATABASE_URL: str = "postgresql+asyncpg://neurodesk:neurodesk_secret_password@localhost:5432/neurodesk_db"
    
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    LOG_LEVEL: str = "INFO"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforces mandatory secure configuration in production environment."""
        if self.ENVIRONMENT.lower() in ("production", "prod"):
            if (
                self.SECRET_KEY == "super_secret_jwt_key_neurodesk_2026_enterprise"
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production mode, SECRET_KEY must be explicitly defined and at least 32 characters long."
                )
            if "localhost" in self.DATABASE_URL or "neurodesk_secret_password" in self.DATABASE_URL:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production mode, DATABASE_URL must be configured with secure production database credentials."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
