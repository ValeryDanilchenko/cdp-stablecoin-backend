from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    reload: bool = Field(default=True)
    environment: Literal["dev", "test", "prod"] = Field(default="dev")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="standard")  # "standard" or "json"

    # Database
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="cdp_demo")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # EVM
    evm_rpc_url: str = Field(default="http://localhost:8545")
    liquidation_executor_address: str = Field(default="0x0000000000000000000000000000000000000000")

settings = Settings()
