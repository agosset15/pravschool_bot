from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import BASE_DIR


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )