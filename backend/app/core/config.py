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
    
    # Database connection string (Defaults to SQLite for local development)
    DATABASE_URL: str = "sqlite+aiosqlite:///./neurodesk.db"

    # LLM Platform Configurations
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-2.5-flash"
    DEFAULT_LLM_PROVIDER: str = "mock"
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    MAX_CONTEXT_TOKENS: int = 32000
    
    # DAMS Core Configuration
    STORAGE_LOCAL_ROOT: str = "storage/uploads"
    STORAGE_TEMP_DIR: str = "storage/temp"
    DEFAULT_STORAGE_PROVIDER: str = "local"
    MAX_UPLOAD_SIZE_BYTES: int = 104857600  # 100 MB Limit

    ALLOWED_EXTENSIONS: List[str] = [
        # Documents & Reports
        "txt", "pdf", "doc", "docx", "md", "rtf", "html", "prompt", "log",
        # Source Code & Scripts
        "py", "js", "ts", "jsx", "tsx", "cpp", "c", "h", "java", "go", "rs", "sh", "yaml", "yml",
        # Spreadsheets & Datasets
        "csv", "xlsx", "xls", "ods", "json", "parquet", "arrow", "feather", "h5", "hdf5",
        # Images
        "jpg", "jpeg", "png", "gif", "webp", "svg",
        # Audio & Video
        "mp3", "wav", "ogg", "mp4", "webm", "avi",
        # AI Models
        "pt", "pth", "onnx", "safetensors", "bin", "tflite"
    ]

    ALLOWED_MIME_TYPES: List[str] = [
        "text/plain", "text/csv", "text/markdown", "text/html", "application/pdf",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/json", "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/x-parquet", "application/octet-stream",
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
        "audio/mpeg", "audio/wav", "audio/ogg",
        "video/mp4", "video/webm", "video/x-msvideo"
    ]
    
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
            if "sqlite" in self.DATABASE_URL or "neurodesk_secret_password" in self.DATABASE_URL:
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
