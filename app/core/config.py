from typing import Optional
from urllib.parse import quote, urlparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # API
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    api_title: str = "FastAPI Beyond"
    api_version: str = "0.1.0"
    api_description: str = "FastAPI Beyond CRUD Full Course - A FastAPI Course"

    # Database
    db_url: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None

    cors_origins: list[str] = []
    debug: bool = False

    # Security
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_db: Optional[int] = None
    redis_password: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Return the database URL from env or construct from components"""
        if self.db_url:
            return self.db_url

        user = self.db_user or "user"
        password = self.db_password or "password"
        host = self.db_host or "localhost"
        port = self.db_port or 5432
        name = self.db_name or "bookly_db"

        return (
            f"postgresql+asyncpg://{user}:{quote(password, safe='')}"
            f"@{host}:{port}/{name}"
        )

    @property
    def redis_url(self) -> str:
        """Return the Redis URL from env or construct from components"""
        if self.redis_host and self.redis_port is not None:
            password_part = f":{quote(self.redis_password, safe='')}" if self.redis_password else ""
            return f"redis://{password_part}@{self.redis_host}:{self.redis_port}/{self.redis_db or 0}"
        return ""

    @property
    def broker_url(self) -> str:
        """Return the broker URL for Celery"""
        return self.redis_url

    @property
    def result_url(self) -> str:
        """Return the result URL for Celery"""
        return self.redis_url

    def _parse_db_url(self) -> None:
        """Parse DATABASE_URL and populate db_* fields if they're not already set"""
        if not self.db_url:
            return

        try:
            parsed = urlparse(self.db_url)
            if not self.db_user and parsed.username:
                self.db_user = parsed.username
            if not self.db_password and parsed.password:
                self.db_password = parsed.password
            if not self.db_host and parsed.hostname:
                self.db_host = parsed.hostname
            if not self.db_port and parsed.port:
                self.db_port = parsed.port
            if not self.db_name and parsed.path:
                self.db_name = parsed.path.lstrip("/")
        except Exception:
            pass  # If parsing fails, just use the url as-is

    def model_post_init(self, __context):
        """Called after model initialization"""
        self._parse_db_url()


settings = Settings()
