from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "osint-intelligence-platform"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite:///./osint.db"
    redis_url: str = "redis://localhost:6379/0"
    api_prefix: str = "/api/v1"
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:5173"
    read_timeout_seconds: int = 30
    write_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
