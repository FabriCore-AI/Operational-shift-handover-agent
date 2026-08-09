from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FabriCore AI"
    environment: str = "development"

    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-120b"

    groq_api_key: str = Field(min_length=1)

    data_dir: str = "data/synthetic"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()