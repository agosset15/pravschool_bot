from .base import BaseConfig


class NetschoolAPIConfig(BaseConfig, env_prefix="NS_"):
    url: str
    school_id: int = 1