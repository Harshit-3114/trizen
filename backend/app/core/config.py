from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Trizen Photo Sharing Platform"
    APP_ENV: str = "development"  # development | production | test
    DATABASE_URL: str = "sqlite:///./trizen.db"
    SECRET_KEY: str = "changeme-in-production-use-long-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12h, suitable for event shoots

    # CORS (comma-separated in env, e.g. "http://localhost:3000,https://app.example.com")
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Object/file storage. "local" for dev; "s3" for AWS S3 / Supabase S3-compatible.
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 10
    S3_BUCKET: str = ""
    S3_REGION: str = ""
    S3_ENDPOINT_URL: str = ""  # e.g. Supabase S3 endpoint when using Supabase storage
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    # Legacy Supabase names (mapped if S3_* empty)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_BUCKET: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


    @model_validator(mode="after")
    def _guard_production(self):
        if self.APP_ENV == "production" and self.DATABASE_URL.startswith("sqlite"):
            raise ValueError(
                "SQLite cannot be used in production (serverless filesystems are "
                "ephemeral). Set DATABASE_URL to Postgres (e.g. Neon)."
            )
        return self


settings = Settings()
