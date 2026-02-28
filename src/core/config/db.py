from pydantic import PostgresDsn, SecretStr

from .base import BaseConfig


class DatabaseConfig(BaseConfig, env_prefix="DB_"):
    host: str = "localhost"
    port: int = 5432
    name: str = "pravschool"
    user: str = "pravschool_bot"
    password: SecretStr

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 30
    max_overflow: int = 30
    pool_timeout: int = 10
    pool_recycle: int = 3600

    @property
    def dsn(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.name,
        ).unicode_string()