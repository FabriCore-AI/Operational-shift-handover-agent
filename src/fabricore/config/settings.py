from functools import lru_cache
import os
from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

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

    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    document_dir: str = os.getenv(
        "DOCUMENT_DIR",
        "data/synthetic/documents",
    )

    vector_store_dir: str = os.getenv(
        "VECTOR_STORE_DIR",
        "data/vector_store",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()