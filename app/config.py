from pydantic_settings import BaseSettings, SettingsConfigDict


from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str
    smax_api_token: Optional[str] = None
    smax_api_endpoint: Optional[str] = None
    chroma_dir: str = "app/vector_store"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    max_sentences: int = 2
    max_tokens_per_sentence: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore" 
    )

settings = Settings()