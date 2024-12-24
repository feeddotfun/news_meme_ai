from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NEWS_API_KEY: str = ""
    NEWS_BASE_URL: str = ""
    AI_API_KEY: str = ""
    REDIS_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()