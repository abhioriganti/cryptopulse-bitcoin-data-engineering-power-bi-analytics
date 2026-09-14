"""Typed application configuration loaded exclusively from environment variables."""

from enum import StrEnum

from pydantic import Field, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Runtime settings. Secrets are intentionally never given defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CRYPTOPULSE_", extra="ignore")

    environment: Environment = Environment.DEVELOPMENT
    log_level: str = "INFO"
    symbol: str = "BTC-USD"
    kafka_bootstrap_servers: str = "localhost:19092"
    kafka_topic: str = "market-events"
    postgres_dsn: PostgresDsn = PostgresDsn(
        "postgresql://cryptopulse:cryptopulse@localhost:15432/cryptopulse"
    )
    s3_endpoint: HttpUrl = HttpUrl("http://localhost:9000")
    s3_bucket: str = "cryptopulse-lakehouse"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    mlflow_tracking_uri: HttpUrl = HttpUrl("http://localhost:5000")
    provider_timeout_seconds: int = Field(default=20, ge=1, le=120)
    allowed_lateness_minutes: int = Field(default=15, ge=0, le=1440)
    provider_api_key: str | None = None
    llm_api_key: str | None = None
    llm_base_url: HttpUrl | None = None


def get_settings() -> Settings:
    """Construct settings on demand so tests can isolate environment state."""
    return Settings()
