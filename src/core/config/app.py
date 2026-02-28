import re
from pathlib import Path
from typing import Self

from pydantic import Field, SecretStr, field_validator

from src.core.constants import ASSETS_DIR, DOMAIN_REGEX
from src.core.enums import Locale, LogLevel
from src.core.types import LocaleList, StringList

from .base import BaseConfig
from .bot import BotConfig
from .db import DatabaseConfig
from .logging import LogConfig
from .netschool import NetschoolAPIConfig
from .redis import RedisConfig


class AppConfig(BaseConfig, env_prefix="APP_"):
    domain: SecretStr = SecretStr("example.com")
    static_url: str = "https://example.com/static/"
    host: str = "0.0.0.0"
    port: int = 8080

    locales: LocaleList = [Locale.RU]
    default_locale: Locale = Locale.RU

    assets_dir: Path = ASSETS_DIR
    temp_dir: Path = assets_dir.parent / "temp"
    log_level: LogLevel = LogLevel.DEBUG
    origins: StringList = [""]

    bot: BotConfig = Field(default_factory=BotConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    netschool: NetschoolAPIConfig = Field(default_factory=NetschoolAPIConfig)

    @property
    def translations_dir(self) -> Path:
        return self.assets_dir / "locales"

    @classmethod
    def get(cls) -> Self:
        return cls()

    def static_path(self, path: str) -> str:
        return self.static_url + path

    def temp_file_path(self, file_name: str) -> Path:
        return self.temp_dir / file_name

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, field: SecretStr) -> SecretStr:

        if not re.match(DOMAIN_REGEX, field.get_secret_value()):
            raise ValueError("APP_DOMAIN has invalid format")

        return field

    @field_validator("crypt_key")
    @classmethod
    def validate_crypt_key(cls, field: SecretStr) -> SecretStr:

        if not re.match(r"^[A-Za-z0-9+/=]{44}$", field.get_secret_value()):
            raise ValueError("APP_CRYPT_KEY must be a valid 44-character Base64 string")

        return field