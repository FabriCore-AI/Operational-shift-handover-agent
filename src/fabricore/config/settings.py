
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FabriCore AI"
    environment: str = "development"

    # Handover generation
    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-120b"

    # Evaluation (kept separate from generation)
    eval_llm_provider: str = "groq"
    eval_llm_model: str = "openai/gpt-oss-120b"

    # Backward compatibility for code that still reads eval_model
    eval_model: str = "openai/gpt-oss-120b"

    # Provider credentials; validate when building the relevant client
    groq_api_key: str = ""
    openai_api_key: str = ""

    # Legacy generic key, retained for existing code
    api_key: str = ""

    data_dir: str = "data/synthetic"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    document_dir: str = "data/synthetic/documents"
    vector_store_dir: str = "data/vector_store"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
