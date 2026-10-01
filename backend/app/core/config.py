from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    LLM_API_KEY: str
    LLM_MODEL: str
    LLM_BASE_URL: str
    KAGGLE_API_TOKEN: str | None = None
    HF_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()