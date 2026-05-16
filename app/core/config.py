from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MEDISTOCK API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey_change_in_production"
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://usuario:miContraseÑasegura123@db:5432/miBD",
        alias="POSTGRES_URL"
    )
    
    # Frontend config
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Backend config
    BACKEND_URL: str = "http://localhost:8000"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            v = v.replace("sslmode=require", "ssl=require")
            return v
        return v or ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
