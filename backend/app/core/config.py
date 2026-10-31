from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    LLM_API_KEY: str = "test-key"
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    KAGGLE_API_TOKEN: str | None = None
    HF_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()


def get_reliable_models(primary_model: str | None = None, base_url: str | None = None) -> list[str]:
    """
    Returns an ordered list of reliable models to try.
    Prioritizes the configured primary model, appending verified production fallbacks
    for Google Gemini (e.g. gemini-2.5-flash, gemini-2.0-flash, gemini-2.5-pro)
    or OpenRouter.
    """
    model = primary_model or settings.LLM_MODEL
    url = base_url or settings.LLM_BASE_URL
    models = [model]

    if "generativelanguage.googleapis.com" in url:
        for fallback in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"]:
            if fallback not in models:
                models.append(fallback)
    elif "openrouter.ai" in url:
        if "openrouter/auto" not in models:
            models.append("openrouter/auto")

    return models