"""Application configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load .env from backend folder (same dir as run.py) - do this before Settings
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "tinyllama"
    DATABASE_URL: str = "sqlite:///./sql_generator.db"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
