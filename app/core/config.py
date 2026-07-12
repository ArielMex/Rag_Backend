from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # ── Aplicación ──────────────────────────────
    APP_NAME: str = "Auth Module"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ── Base de datos ────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:admin2468@localhost:5432/rag_db"

    # ── JWT ──────────────────────────────────────
    SECRET_KEY: str = "cambia-esto-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ── Gemini / RAG ─────────────────────────────
    GEMINI_API_KEY: str

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
