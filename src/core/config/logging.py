from src.core.enums import LogLevel

from .base import BaseConfig


class LogConfig(BaseConfig, env_prefix="LOG_"):
    to_file: bool = False
    level: LogLevel = LogLevel.DEBUG
    rotation: str = "1GB"  # "00:00"
    compression: str = "zip"
    retention: str = "3 days"
    chat_id: int = 0