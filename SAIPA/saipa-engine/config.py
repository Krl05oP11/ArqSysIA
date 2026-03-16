"""
Centralised settings for saipa-engine using pydantic-settings.
All values come from environment variables / .env file.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Security
    saipa_api_token: str = ""

    # Moodle
    moodle_url: str = "http://localhost:8080"
    moodle_token: str = ""

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_timeout: int = 60

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"

    # WhatsApp
    whatsapp_provider: str = "twilio"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from: str = "whatsapp:+14155238886"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
